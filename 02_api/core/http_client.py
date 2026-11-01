"""HTTP 客户端封装：把 requests 包一层，只做三件事。

1. 统一 base_url —— 用例里只写 /api/orders/O1001，不写 http://127.0.0.1:52341/...
   这样换环境（测试环境 / 预发 / 线上）只改一个地方。
2. 自动带 token —— 不用每条用例都手写 headers。
3. 统一返回 —— 用例里拿到的是 response 对象，断言直接写 resp.json()["code"] == 0。

为什么不用 requests 直接写？
  三条用例时没区别。五十条时你会发现每条都重复写 headers、拼 URL、记 base_url，
  改一处要改五十处 —— 这就是"封装"唯一的意义：把重复的东西收拢到一处。
"""

from __future__ import annotations

import json
from typing import Any

import requests


class ApiClient:
    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token: str | None = None

    # ------------------------------------------------------------ 基础
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self, extra: dict | None = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        headers: dict | None = None,
        with_auth: bool = True,
    ) -> requests.Response:
        """发请求。with_auth=False 用于测"没带 token 应该被拦"这类用例。"""
        saved = self.token
        if not with_auth:
            self.token = None
        try:
            return self.session.request(
                method,
                self._url(path),
                json=json_body,
                headers=self._headers(headers),
                timeout=self.timeout,
            )
        finally:
            self.token = saved

    # ------------------------------------------------------------ 快捷方法
    def get(self, path: str, **kwargs) -> requests.Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, json_body: dict | None = None, **kwargs) -> requests.Response:
        return self.request("POST", path, json_body=json_body, **kwargs)

    # ------------------------------------------------------------ 登录
    def login(self, username: str, password: str) -> requests.Response:
        """登录并自动把 token 记下来，后续请求自动带上。"""
        resp = self.post("/api/login", {"username": username, "password": password}, with_auth=False)
        if resp.status_code == 200:
            self.token = resp.json()["data"]["token"]
        return resp

    def logout(self) -> None:
        self.token = None

    # ------------------------------------------------------------ 调试
    def pretty(self, resp: requests.Response) -> str:
        """把响应格式化成好读的字符串，断言失败时贴到提示里。"""
        try:
            body: Any = resp.json()
            text = json.dumps(body, ensure_ascii=False, indent=2)
        except ValueError:
            text = resp.text
        return f"HTTP {resp.status_code}\n{text}"
