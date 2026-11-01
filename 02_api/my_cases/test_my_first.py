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
from core.schema_check import ORDER_DATA, assert_schema


# ---------------------------------------------------------------------------
# 第 1 条（11/19 周四）
# ---------------------------------------------------------------------------
def test_my_1_query_own_order(alice):
    """正向：alice 查自己的订单 O1001，应该拿到 200 且数据对得上。

    参照：tests/test_orders.py 第 14-26 行（test_query_own_order_success）
    """
    pytest.skip("TODO 第 1 条：删掉这一行，按下面的四步写")

    # ① 发请求
    #    alice 是 conftest.py 里已经登录好的客户端，不用你自己登录、不用拼 URL。
    #    提示：alice.get("/api/orders/O1001")
    #    resp = ____

    # ② 第一层断言：HTTP 状态码
    #    assert resp.status_code == 200, alice.pretty(resp)
    #    ↑ 第二个参数（逗号后面那部分）是"失败时打印什么"。
    #      不写它，失败时你只会看到 "200 != 500"，看不到服务端到底返回了什么。

    # ③ 第二层断言：业务码
    #    很多系统出错也返 HTTP 200，靠 body 里的 code 区分成功失败。
    #    body = resp.json()
    #    assert body["____"] == 0

    # ④ 第三层断言：字段值（三个都要断）
    #    data = body["data"]
    #    order_id  == "O1001"
    #    user_id   == 1
    #    amount    == "199.00"   ← 注意是字符串，不是浮点 199.0


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
    """反例：token 不对时必须被拦在 401，一条都不能放进来。

    参照：tests/test_orders.py 第 29-41 行（两个反例函数）。
    这里是把那两个函数合并成一个参数化版本 —— 这就是 parametrize 的价值，
    一份代码跑三组数据。
    """
    pytest.skip("TODO 第 2 条：删掉这一行，按下面的三步写")

    # ① 把 token 塞进 client
    #    client.token = ____            ← 直接用传进来的 token 参数
    #    （token 是 None 时要设成 None，不能设成字符串 "None"）

    # ② 发请求
    #    关键：with_auth 要原样传进去。传 False 时，ApiClient 会临时摘掉 token，
    #    用来模拟"请求里压根没有 Authorization 头"这种场景。
    #    resp = client.get("/api/orders/O1001", with_auth=____)

    # ③ 断言两层：HTTP 码 401 + 业务码 expected_code
    #    assert resp.status_code == ____, client.pretty(resp)
    #    assert resp.json()["code"] == ____


# ---------------------------------------------------------------------------
# 第 3 条（11/20 周五）· 契约：返回结构必须符合约定
# ---------------------------------------------------------------------------
def test_my_3_order_schema(alice):
    """契约：订单响应的结构不能变（字段没少、类型没变、状态值在枚举内）。

    参照：tests/test_orders.py 第 20-21 行（两行 assert_schema），
    以及 tests/test_login.py 里的用法。
    """
    pytest.skip("TODO 第 3 条：删掉这一行，按下面的四步写")

    # ① 请求 O1003 —— 这条订单属于 alice，状态是 PAID
    #    resp = alice.get("/____")

    # ② 先断 HTTP 200（结构断言之前必须先确认拿到的是正常响应，
    #    否则校验一个 401 的 body 会报一堆看不懂的错）
    #    assert resp.status_code == 200, alice.pretty(resp)

    # ③ 结构断言 —— 注意这里要校验两层，不是一层：
    #    body = resp.json()
    #    assert_schema(body, ____, "响应外壳")         ← 外壳：code / message / data
    #    assert_schema(body["____"], ____, "订单数据")  ← 数据本体：order_id / amount / status
    #    （两个 schema 名字：SUCCESS_ENVELOPE 和 ORDER_DATA，一个已 import，另一个自己补）

    # ④ 最后再断一个值，证明这条用例不只是"结构对"，业务值也对
    #    assert body["data"]["status"] == "____"


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
