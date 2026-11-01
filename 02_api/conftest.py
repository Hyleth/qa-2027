"""pytest 的"装配车间"。

这个文件不用手动运行 —— pytest 收集用例时会自动读它。
它自己不产生任何输出，这是正常的（W0 时你可能困惑过这件事）。

三个 fixture 的层次关系，是这一周最该看懂的东西：

    base_url   (session)  ← 整个测试过程只启动一次服务
        └── client  (function)  ← 每条用例一个干净的客户端，互不干扰

为什么 base_url 用 session 级？
    起服务要占端口、要初始化数据，每条用例重启一次既慢又容易端口冲突。

为什么 client 必须用 function 级？
    如果全局共用一个 client，A 用例登录成 alice，B 用例登录成 bob，
    token 会互相覆盖 —— 用例单跑是绿的，一起跑就红。这就是"用例间污染"。
    函数级 = 每条用例拿到全新的，天然隔离。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from core.http_client import ApiClient  # noqa: E402
from mock_server import serve_in_background  # noqa: E402


@pytest.fixture(scope="session")
def base_url():
    """整个测试会话只启动一次 mock 服务，结束后关闭。"""
    server, url = serve_in_background()
    yield url
    server.shutdown()


@pytest.fixture()
def client(base_url):
    """未登录的客户端。"""
    return ApiClient(base_url)


@pytest.fixture()
def alice(client):
    """已登录 alice 的客户端。"""
    resp = client.login("alice", "123456")
    assert resp.status_code == 200, f"前置登录失败：{client.pretty(resp)}"
    return client


@pytest.fixture()
def bob(base_url):
    """已登录 bob 的客户端（独立实例，避免和 alice 互相覆盖 token）。"""
    c = ApiClient(base_url)
    resp = c.login("bob", "123456")
    assert resp.status_code == 200, f"前置登录失败：{c.pretty(resp)}"
    return c
