"""订单查询接口的用例。

这一组重点不是"能不能查到"，是"**不该查到的能不能被挡住**"。
真实项目里，权限类用例的漏测率最高 —— 因为它不会报错，只会安静地泄露数据。
"""

from __future__ import annotations

import pytest

from core.schema_check import ORDER_DATA, SUCCESS_ENVELOPE, assert_schema


def test_query_own_order_success(alice):
    """正向：查自己的订单，能查到且结构正确。"""
    resp = alice.get("/api/orders/O1001")
    assert resp.status_code == 200, alice.pretty(resp)

    body = resp.json()
    assert_schema(body, SUCCESS_ENVELOPE, "订单响应外壳")
    assert_schema(body["data"], ORDER_DATA, "订单响应 data")

    data = body["data"]
    assert data["order_id"] == "O1001"
    assert data["user_id"] == 1
    assert data["amount"] == "199.00", "金额必须是字符串 199.00，不能用浮点"


def test_query_without_token_is_rejected(client):
    """反例：完全不带头，必须 401。"""
    resp = client.get("/api/orders/O1001", with_auth=False)
    assert resp.status_code == 401, f"没带 token 竟然能查订单\n{client.pretty(resp)}"
    assert resp.json()["code"] == 4011


def test_query_with_invalid_token_is_rejected(client):
    """反例：头是假的，必须 401。"""
    client.token = "this-is-not-a-real-token"
    resp = client.get("/api/orders/O1001")
    assert resp.status_code == 401, f"假 token 竟然能查订单\n{client.pretty(resp)}"
    assert resp.json()["code"] == 4012


def test_query_nonexistent_order_returns_404(alice):
    """边界：订单号格式对但不存在，返回 404 而不是 500。"""
    resp = alice.get("/api/orders/O9999")
    assert resp.status_code == 404, alice.pretty(resp)
    assert resp.json()["code"] == 4040


@pytest.mark.xfail(
    reason="BUG-02：查订单没校验归属，alice 能查到 bob 的订单（越权）",
    strict=True,  # strict=True：等 bug 修好后这条会变成 XPASS（失败），提醒你摘掉标记
)
def test_query_other_users_order_is_rejected(alice):
    """越权：alice 用自己的 token 查 bob 的订单（O1002 属于 user_id=2），必须 403。"""
    resp = alice.get("/api/orders/O1002")
    assert resp.status_code == 403, (
        f"越权漏洞：alice 查到了别人的订单\n{alice.pretty(resp)}"
    )
