"""登录接口的用例。数据全部来自 data/cases.yaml，本文件只负责"怎么测"。

这是数据驱动的典型结构：
    yaml 里写"输入什么、期望什么"
    这里写"怎么发请求、怎么比对"
两者分开，加用例时不用改这段代码。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from core.schema_check import LOGIN_DATA, ERROR_ENVELOPE, SUCCESS_ENVELOPE, assert_schema

CASES = yaml.safe_load((Path(__file__).parents[1] / "data" / "cases.yaml").read_text(encoding="utf-8"))
LOGIN_CASES = CASES["login"]


def _ids(case: dict) -> str:
    return f"{case['id']}-{case['title']}"


@pytest.mark.parametrize("case", LOGIN_CASES, ids=_ids)
def test_login_by_data(client, case):
    """一条代码覆盖 5 条用例 —— 这就是 parametrize 的价值。"""
    resp = client.post("/api/login", case["request"], with_auth=False)

    # 第一层：HTTP 状态码（网络层对不对）
    assert resp.status_code == case["expect"]["status"], (
        f"[{case['id']}] 状态码不符，期望 {case['expect']['status']}\n{client.pretty(resp)}"
    )

    # 第二层：业务码（业务层对不对）—— 只看 200 是不够的，很多系统错误也返 200
    body = resp.json()
    assert body["code"] == case["expect"]["code"], (
        f"[{case['id']}] 业务码不符，期望 {case['expect']['code']}\n{client.pretty(resp)}"
    )


def test_login_success_payload_shape(client):
    """成功响应必须符合约定结构：token 非空、user_id 是整数、没有多余字段。"""
    resp = client.post("/api/login", {"username": "alice", "password": "123456"}, with_auth=False)
    assert resp.status_code == 200
    body = resp.json()

    assert_schema(body, SUCCESS_ENVELOPE, "登录响应外壳")
    assert_schema(body["data"], LOGIN_DATA, "登录响应 data")


def test_login_failure_payload_shape(client):
    """失败响应也必须有稳定结构 —— 前端靠 code 判断，不能只看 HTTP 码。"""
    resp = client.post("/api/login", {"username": "alice", "password": "bad"}, with_auth=False)
    assert resp.status_code == 401

    assert_schema(resp.json(), ERROR_ENVELOPE, "登录失败响应")


def test_login_returns_new_token_each_time(client):
    """每次登录都要发新 token。如果两次一样，说明服务端复用了 token —— 这是安全问题。"""
    token1 = client.post("/api/login", {"username": "alice", "password": "123456"}, with_auth=False).json()["data"]["token"]
    token2 = client.post("/api/login", {"username": "alice", "password": "123456"}, with_auth=False).json()["data"]["token"]

    assert token1 != token2, "两次登录返回了同一个 token，存在会话复用风险"
