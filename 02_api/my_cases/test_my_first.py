"""自己写的第 1 组接口用例 —— 3 个测试函数，共 5 条用例。

怎么跑（在 02_api/ 目录下，不是在本目录）：
    ..\\.venv\\Scripts\\python.exe -m pytest my_cases -v

现在跑应该看到 5 skipped —— 5 = 1 + 3（参数化展开）+ 1，每条用例一个 skip。
写完之后应该是 5 passed，一条 skipped 都不剩。
写法：删掉 skip 那一行，按下面的注释补代码。
答案不在这里，在 tests/test_orders.py —— 允许打开看，不许复制。
规则和验收标准见同目录 README.md。
"""

from __future__ import annotations

import pytest

# 第 3 条会用到。这两个名字是从 core/schema_check.py 里来的，先摆在这儿省得你翻。
from core.schema_check import ORDER_DATA, assert_schema, SUCCESS_ENVELOPE


# ---------------------------------------------------------------------------
# 第 1 条（11/19 周四）
# ---------------------------------------------------------------------------
def test_my_1_query_own_order(alice):
    """正向：alice 查自己的订单 O1001，应该拿到 200 且数据对得上。"""
    resp = alice.get("/api/orders/O1001")
    assert resp.status_code == 200, alice.pretty(resp)

    assert resp.json()["code"] == 0

    data = resp.json()["data"]
    assert data["order_id"] == "O1001"
    assert data["user_id"] == 1
    assert data["amount"] == "199.00"


# ---------------------------------------------------------------------------
# 第 2 条（11/20 周五）· 参数化：三种"token 不对"的情况，期望都被拒
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "token, with_auth, expected_code",
    [
        # 三组数据的业务码不同，这不是随便编的，去看 mock_server.py 的 _auth()：
        #   完全不带 Authorization 头      → 4011
        #   头在、但 token 是假的/不存在   → 4012
        pytest.param(None, False, 4011, id="不带Authorization头"),
        pytest.param("not-a-real-token", True, 4012, id="假token"),
        pytest.param("expired-token", True, 4012, id="不存在的token(等同过期)"),
    ],
)
def test_my_2_reject_bad_token(client, token, with_auth, expected_code):
    """反例：token 不对时必须被拦在 401，一条都不能放进来。"""
    client.token = token
    resp = client.get("/api/orders/O1001", with_auth=with_auth)
    assert resp.status_code == 401, client.pretty(resp)
    assert resp.json()["code"] == expected_code


# ---------------------------------------------------------------------------
# 第 3 条（11/20 周五）· 契约：返回结构必须符合约定
# ---------------------------------------------------------------------------
def test_my_3_order_schema(alice):
    """契约：订单响应的结构不能变（字段没少、类型没变、状态值在枚举内）。"""
    resp = alice.get("/api/orders/O1003")
    assert resp.status_code == 200, alice.pretty(resp)
    body = resp.json()
    assert_schema(body, SUCCESS_ENVELOPE, "校验订单接口响应体格式")
    assert_schema(body["data"], ORDER_DATA, "校验订单接口数据内容")
    assert body["data"]["status"] == "PAID"


# ---------------------------------------------------------------------------
# 写完之后自检（不用改这里，照着敲一遍就行）
# ---------------------------------------------------------------------------
# 1. ..\.venv\Scripts\python.exe -m pytest my_cases -v
#    → 5 passed，没有 skipped
# 2. ..\.venv\Scripts\python.exe -m pytest -q
#    → 仍然是 17 passed, 2 xfailed（说明你没改坏教材）
# 3. 三个函数各自单跑一遍，都要绿：
#    ..\.venv\Scripts\python.exe -m pytest "my_cases/test_my_first.py::test_my_1_query_own_order" -v
#
# 都过了，就 git commit。commit message 参考：
#   test: 自己写的 5 条接口用例（正常 / 参数化鉴权 / Schema 契约）
