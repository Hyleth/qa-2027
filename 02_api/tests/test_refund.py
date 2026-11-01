"""退款接口的用例（YAML 驱动 + 金额精度）。

这一组要带走三个认知：

1. 金额必须用字符串/Decimal，不能用 float。
   Python 里 0.1 + 0.2 == 0.30000000000000004。测试断言写成 `amount == 50.0`
   在真实系统里迟早出问题，而这类 bug 只在特定金额下复现，最难查。

2. yaml 里写了 known_bug 的用例，自动打 xfail。
   xfail = 预期失败。它不是"忽略"，是"我知道这里会红，且我知道为什么"。
   strict=True 时，一旦 bug 被修好，这条会变成 XPASS（算失败）——
   这样就逼着你回来摘标记，不会出现"bug 修了但用例还挂着不管"。

3. 状态类用例要挑不互相干扰的数据。
   REF-01 会把 O1003 置为已退款，所以 REF-03 用的是本来就已退款的 O1004。
   用例之间共用数据是测试不稳定的头号原因。
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from core.schema_check import REFUND_DATA, assert_schema

CASES = yaml.safe_load((Path(__file__).parents[1] / "data" / "cases.yaml").read_text(encoding="utf-8"))
REFUND_CASES = CASES["refund"]


def _params():
    params = []
    for case in REFUND_CASES:
        marks = ()
        if case.get("known_bug"):
            marks = (
                pytest.mark.xfail(
                    reason=f"{case['known_bug']}：{case['title']}（服务端已知缺陷）",
                    strict=True,
                ),
            )
        params.append(pytest.param(case, marks=marks, id=f"{case['id']}-{case['title']}"))
    return params


@pytest.mark.parametrize("case", _params())
def test_refund_by_data(alice, case):
    resp = alice.post("/api/refunds", case["request"])

    assert resp.status_code == case["expect"]["status"], (
        f"[{case['id']}] 状态码不符，期望 {case['expect']['status']}\n{alice.pretty(resp)}"
    )
    assert resp.json()["code"] == case["expect"]["code"], (
        f"[{case['id']}] 业务码不符，期望 {case['expect']['code']}\n{alice.pretty(resp)}"
    )


def test_refund_amount_uses_decimal(alice):
    """金额断言用 Decimal 比较 —— 避免浮点误差，也避免 "50.0" != "50.00" 这种假失败。

    Decimal("50.00") == Decimal("50.0") 为 True，
    但字符串比较 "50.00" != "50.0" 为 False —— 所以断言金额时要么比 Decimal，
    要么明确比格式化后的字符串。这条用例演示前者。
    """
    resp = alice.post("/api/refunds", {"order_id": "O1005", "amount": "20.00"})
    assert resp.status_code == 200, alice.pretty(resp)

    data = resp.json()["data"]
    assert_schema(data, REFUND_DATA, "退款响应 data")
    assert Decimal(data["amount"]) == Decimal("20.00")


def test_refund_missing_field_returns_400(alice):
    """边界：少传 amount，应该是参数错误而不是 500。"""
    resp = alice.post("/api/refunds", {"order_id": "O1002"})
    assert resp.status_code == 400, alice.pretty(resp)
    assert resp.json()["code"] == 4001
