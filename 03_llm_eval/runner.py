"""评测执行器：一条命令跑完 40 条，出报告。

用法：
    python runner.py                      # mock 模型 + 规则判定（默认，不需要 Key）
    python runner.py --judge mock         # 同时跑模型裁判，看两个判定器哪里不一致
    python runner.py --backend real --judge real   # 真模型 + 真裁判（需要 DEEPSEEK_API_KEY）

产物：
    out/results.json   机器可读，用来做版本对比（v1 vs v2 哪个好）
    out/report.html    人可读，用来给面试官看 / 给老板看
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from judge.llm_judge import get_judge
from judge.rules import judge as rule_judge
from model_client import get_backend, load_evalset

ROOT = Path(__file__).parent
OUT = ROOT / "out"

CATEGORY_NAMES = {
    "fact": "事实准确性",
    "boundary": "边界与规则",
    "refuse": "拒答准确性",
    "injection": "提示词注入",
    "hallucination": "幻觉",
    "multiturn": "多轮上下文",
}

# 这四个是面试官最常问的指标，单独拎出来
CORE_METRICS = [
    ("fact", "事实准确率", "该对的对没对"),
    ("hallucination", "幻觉率", "反着看：判定为编造的占比"),
    ("refuse", "拒答准确率", "该拒绝时拒绝了没有"),
    ("injection", "注入抵抗率", "顶住了多少次攻击"),
]


def run(backend_name: str, judge_name: str | None) -> dict:
    items = load_evalset()
    backend = get_backend(backend_name)
    judge2 = get_judge(judge_name) if judge_name else None

    results = []
    for item in items:
        answer = backend.ask(item)
        verdict = rule_judge(item, answer)

        row = {
            "id": item["id"],
            "category": item["category"],
            "question": item["question"],
            "answer": answer,
            "passed": verdict["passed"],
            "reasons": verdict["reasons"],
            "note": item.get("note", ""),
        }

        if judge2 is not None:
            v2 = judge2.score(item, answer)
            row["judge"] = {"passed": v2["passed"], "score": v2["score"], "reason": v2["reason"]}
            row["judge_agrees"] = v2["passed"] == verdict["passed"]

        results.append(row)

    # ---------------------------------------------------------- 汇总
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)

    cat_stats = {}
    for cat, rows in by_cat.items():
        passed = sum(1 for r in rows if r["passed"])
        cat_stats[cat] = {
            "name": CATEGORY_NAMES.get(cat, cat),
            "total": len(rows),
            "passed": passed,
            "rate": round(passed / len(rows) * 100, 1),
        }

    overall_passed = sum(1 for r in results if r["passed"])
    summary = {
        "backend": backend_name,
        "judge": judge_name or "rules-only",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(results),
        "passed": overall_passed,
        "rate": round(overall_passed / len(results) * 100, 1),
        "by_category": cat_stats,
        "core": {},
    }

    for cat, label, _desc in CORE_METRICS:
        if cat in cat_stats:
            rate = cat_stats[cat]["rate"]
            summary["core"][label] = round(100 - rate if cat == "hallucination" else rate, 1)

    if judge2 is not None:
        agree = sum(1 for r in results if r.get("judge_agrees"))
        summary["judge_agreement"] = round(agree / len(results) * 100, 1)

    return {"summary": summary, "results": results}


# ---------------------------------------------------------------- 输出


def print_console(data: dict) -> None:
    s = data["summary"]
    print()
    print("=" * 62)
    print(f"评测完成　后端={s['backend']}　判定={s['judge']}")
    print("=" * 62)
    print(f"总用例 {s['total']} 条，通过 {s['passed']} 条，通过率 {s['rate']}%")
    print()
    print(f"{'分类':<12}{'条数':>6}{'通过':>6}{'通过率':>9}")
    print("-" * 62)
    for cat in ["fact", "boundary", "refuse", "injection", "hallucination", "multiturn"]:
        if cat not in s["by_category"]:
            continue
        st = s["by_category"][cat]
        bar = "█" * int(st["rate"] / 10) + "░" * (10 - int(st["rate"] / 10))
        print(f"{st['name']:<12}{st['total']:>6}{st['passed']:>6}{st['rate']:>8.1f}%  {bar}")
    print("-" * 62)
    print("核心指标：")
    for label, value in s["core"].items():
        print(f"  {label}：{value}%")
    if "judge_agreement" in s:
        print(f"  两个判定器一致率：{s['judge_agreement']}%（不一致的样本必须人工看）")
    print()


def write_report(data: dict) -> Path:
    OUT.mkdir(exist_ok=True)
    s = data["summary"]
    results = data["results"]

    (OUT / "results.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    order = ["fact", "boundary", "refuse", "injection", "hallucination", "multiturn"]
    cat_rows = ""
    for cat in order:
        if cat not in s["by_category"]:
            continue
        st = s["by_category"][cat]
        color = "#16a34a" if st["rate"] >= 90 else ("#d97706" if st["rate"] >= 60 else "#dc2626")
        cat_rows += f"""
        <tr>
          <td>{st['name']}</td>
          <td class="num">{st['total']}</td>
          <td class="num">{st['passed']}</td>
          <td><div class="bar"><span style="width:{st['rate']}%;background:{color}"></span></div></td>
          <td class="num" style="color:{color};font-weight:600">{st['rate']}%</td>
        </tr>"""

    core_cards = ""
    for label, value in s["core"].items():
        warn = label == "幻觉率"
        bad = (value >= 30) if warn else (value <= 50)
        color = "#dc2626" if bad else "#16a34a"
        core_cards += f"""
        <div class="card">
          <div class="card-label">{label}</div>
          <div class="card-value" style="color:{color}">{value}%</div>
        </div>"""

    fail_rows = ""
    for r in results:
        if r["passed"]:
            continue
        reason = "；".join(r["reasons"]) if r["reasons"] else "—"
        answer = r["answer"].replace("<", "&lt;")[:160]
        judge_note = ""
        if "judge" in r:
            mark = "一致" if r["judge_agrees"] else "不一致"
            judge_note = f"<div class='judge'>模型裁判：{mark}（{r['judge']['reason']}）</div>"
        fail_rows += f"""
        <tr>
          <td class="mono">{r['id']}</td>
          <td>{CATEGORY_NAMES.get(r['category'], r['category'])}</td>
          <td>{r['question'][:40]}</td>
          <td class="answer">{answer}</td>
          <td>{reason}{judge_note}</td>
        </tr>"""

    if not fail_rows:
        fail_rows = "<tr><td colspan='5'>全部通过，没有失败用例</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 客服质量评测报告</title>
<style>
  :root {{ --ink:#1f2430; --muted:#6b7280; --line:#e5e7eb; --bg:#f7f8fa; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:32px 20px 60px; background:var(--bg); color:var(--ink);
         font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif; line-height:1.6; }}
  .wrap {{ max-width:1080px; margin:0 auto; }}
  h1 {{ font-size:26px; margin:0 0 6px; }}
  .meta {{ color:var(--muted); font-size:13px; margin-bottom:26px; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:14px; margin-bottom:26px; }}
  .card {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:18px 20px; }}
  .card-label {{ font-size:13px; color:var(--muted); }}
  .card-value {{ font-size:30px; font-weight:700; margin-top:6px; letter-spacing:-.5px; }}
  .total {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:20px 24px; margin-bottom:26px;
            display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; }}
  .total b {{ font-size:34px; }}
  table {{ width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line);
           border-radius:10px; overflow:hidden; margin-bottom:26px; }}
  th,td {{ padding:11px 14px; text-align:left; font-size:14px; border-bottom:1px solid var(--line); vertical-align:top; }}
  th {{ background:#fafbfc; font-weight:600; font-size:13px; color:var(--muted); }}
  tr:last-child td {{ border-bottom:none; }}
  .num {{ text-align:right; font-variant-numeric:tabular-nums; }}
  .bar {{ background:#eef0f4; border-radius:4px; height:8px; width:110px; overflow:hidden; }}
  .bar span {{ display:block; height:100%; }}
  .mono {{ font-family:ui-monospace,Consolas,monospace; font-size:12px; color:var(--muted); }}
  .answer {{ max-width:340px; color:#374151; font-size:13px; }}
  .judge {{ margin-top:5px; font-size:12px; color:var(--muted); }}
  h2 {{ font-size:17px; margin:30px 0 12px; }}
  .note {{ background:#fff; border-left:3px solid #94a3b8; padding:12px 16px; font-size:13px;
           color:#475569; border-radius:0 6px 6px 0; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>AI 客服质量评测报告</h1>
  <div class="meta">被测后端：{s['backend']}　判定方式：{s['judge']}　生成时间：{s['time']}</div>

  <div class="total">
    <span>共 {s['total']} 条用例，通过 <b>{s['passed']}</b> 条</span>
    <span style="color:var(--muted)">总通过率</span>
    <b style="color:#2563eb">{s['rate']}%</b>
  </div>

  <div class="cards">{core_cards}</div>

  <h2>分类得分</h2>
  <table>
    <thead><tr><th>分类</th><th class="num">条数</th><th class="num">通过</th><th>分布</th><th class="num">通过率</th></tr></thead>
    <tbody>{cat_rows}</tbody>
  </table>

  <h2>失败用例明细（{s['total'] - s['passed']} 条）</h2>
  <table>
    <thead><tr><th>编号</th><th>分类</th><th>问题</th><th>模型回答</th><th>判定理由</th></tr></thead>
    <tbody>{fail_rows}</tbody>
  </table>

  <div class="note">
    <b>怎么读这份报告：</b>总通过率只是入口，真正要看的是「哪一类塌了」。
    如果事实准确率 100% 但注入抵抗率很低，说明这个产品对上正常用户很友好、对恶意输入基本不设防 ——
    这类产品不能上线，因为攻击者只需要会打字。
  </div>
</div>
</body>
</html>"""

    path = OUT / "report.html"
    path.write_text(html, encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="AI 应用质量评测")
    parser.add_argument("--backend", choices=["mock", "real"], default="mock", help="被测模型")
    parser.add_argument("--judge", choices=["mock", "real"], default=None, help="是否启用模型裁判")
    args = parser.parse_args()

    data = run(args.backend, args.judge)
    print_console(data)
    path = write_report(data)
    print(f"报告已生成：{path}")
    print(f"原始数据：{OUT / 'results.json'}（改完 prompt 重跑，对比两个文件就知道变好还是变坏）")


if __name__ == "__main__":
    main()
