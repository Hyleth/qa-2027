#这是示例代码
'下面是示例，仅供学习'

from pathlib import Path


def read_case_count(path):
    """读文件里的用例条数。文件不存在时返回 0，不要崩。"""
    try:
        text = Path(path).read_text(encoding="utf-8")
        return len([l for l in text.split("\n") if l.startswith("|")]) - 2
    except FileNotFoundError:                 # 提示：文件不存在是哪种异常？
        print(f"没找到文件：{path}")
        return 0


def get_priority(case, index=4):
    """安全地取某一列。列不存在时返回 'UNKNOWN'。"""
    cells = case.split("|")
    try:
        return cells[index].strip()
    except IndexError:                 # 提示：下标越界是哪种异常？
        return "UNKNOWN"


if __name__ == "__main__":
    base = Path(__file__).parents[1] / "数据"

    print("正常文件：", read_case_count(base / "cases.md"))       # 期望 10
    print("不存在的文件：", read_case_count(base / "no_such.md"))  # 期望 0，且不崩

    bad_line = "| TC-99 | 登录 |"
    print("缺列的行：", get_priority(bad_line))                    # 期望 UNKNOWN



