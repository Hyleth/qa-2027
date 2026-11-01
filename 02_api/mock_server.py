"""本地 mock 服务：一个「登录 + 订单 + 退款」业务的最小后端。

为什么需要它
------------
学接口自动化，第一个难题不是写代码，是"拿什么当被测对象"。
真实公司里被测服务由开发提供；你一个人练手，就得自己造一个替身。
这个文件就是替身：纯标准库实现，不联网、不装依赖、启动不到 1 秒。

它故意埋了 2 个 bug（W3 的任务是找到并提缺陷）：
  BUG-01  退款金额没做校验，传负数也能"退款成功"
  BUG-02  查订单没校验归属，用 A 的 token 能查 B 的订单（越权）

启动方式（一般不需要手动启动，conftest.py 会自动拉起）：
  python mock_server.py
"""

from __future__ import annotations

import base64
import itertools
import json
import time
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

# ---------------------------------------------------------------- 假数据

USERS = {
    "alice": {"password": "123456", "user_id": 1},
    "bob": {"password": "123456", "user_id": 2},
}

# 金额一律用字符串传输。真实项目里必须这样 —— 浮点数算钱会丢精度（0.1 + 0.2 != 0.3）
ORDERS = {
    "O1001": {"order_id": "O1001", "user_id": 1, "amount": "199.00", "status": "PAID"},
    "O1002": {"order_id": "O1002", "user_id": 2, "amount": "88.50", "status": "PAID"},
    "O1003": {"order_id": "O1003", "user_id": 1, "amount": "50.00", "status": "PAID"},
    "O1004": {"order_id": "O1004", "user_id": 1, "amount": "30.00", "status": "REFUNDED"},
    "O1005": {"order_id": "O1005", "user_id": 1, "amount": "120.00", "status": "PAID"},
}

TOKENS: dict[str, dict] = {}
_REFUND_SEQ = itertools.count(1)
REFUNDS: list[dict] = []

TOKEN_TTL = 7200

# ---------------------------------------------------------------- 工具


def _new_token(user_id: int) -> str:
    raw = f"{user_id}:{time.time()}:{next(_REFUND_SEQ)}"
    token = base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
    TOKENS[token] = {"user_id": user_id, "exp": time.time() + TOKEN_TTL}
    return token


def _user_from_token(token: str | None) -> int | None:
    if not token:
        return None
    info = TOKENS.get(token)
    if not info:
        return None
    if time.time() > info["exp"]:
        return None
    return info["user_id"]


class Handler(BaseHTTPRequestHandler):
    # 关掉默认的访问日志，否则测试输出会被刷满
    def log_message(self, *args):  # noqa: D102
        pass

    # -------------------------------------------------------- 响应封装
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _ok(self, data: dict) -> None:
        self._send(200, {"code": 0, "message": "ok", "data": data})

    def _fail(self, status: int, code: int, message: str) -> None:
        self._send(status, {"code": code, "message": message, "data": None})

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if not length:
            return {}
        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def _auth(self) -> int | None:
        """取当前用户；失败时已经写好响应，调用方直接 return 即可。"""
        header = self.headers.get("Authorization") or ""
        if not header:
            self._fail(401, 4011, "缺少 Authorization 头")
            return None
        if not header.startswith("Bearer "):
            self._fail(401, 4012, "Authorization 格式应为 Bearer <token>")
            return None
        user_id = _user_from_token(header[7:].strip())
        if user_id is None:
            self._fail(401, 4012, "token 无效或已过期")
            return None
        return user_id

    # -------------------------------------------------------- 路由
    def do_GET(self):  # noqa: N802
        path = self.path.split("?")[0]

        if path == "/api/health":
            self._ok({"status": "up"})
            return

        if path.startswith("/api/orders/"):
            user_id = self._auth()
            if user_id is None:
                return
            order_id = path.rsplit("/", 1)[-1]
            order = ORDERS.get(order_id)
            if order is None:
                self._fail(404, 4040, f"订单 {order_id} 不存在")
                return

            # ⚠️ BUG-02：这里本该判断 order["user_id"] == user_id，
            #    现在直接返回了，导致任何登录用户都能查别人的订单（越权）。
            self._ok(order)
            return

        self._fail(404, 4040, "接口不存在")

    def do_POST(self):  # noqa: N802
        path = self.path.split("?")[0]
        body = self._body()

        if path == "/api/login":
            username = body.get("username")
            password = body.get("password")
            if not username or not password:
                self._fail(400, 4001, "用户名和密码都不能为空")
                return
            user = USERS.get(username)
            if user is None or user["password"] != password:
                self._fail(401, 4010, "用户名或密码错误")
                return
            self._ok(
                {
                    "token": _new_token(user["user_id"]),
                    "user_id": user["user_id"],
                    "expires_in": TOKEN_TTL,
                }
            )
            return

        if path == "/api/refunds":
            user_id = self._auth()
            if user_id is None:
                return
            order_id = body.get("order_id")
            amount = body.get("amount")
            if order_id is None or amount is None:
                self._fail(400, 4001, "order_id 和 amount 都不能为空")
                return
            order = ORDERS.get(order_id)
            if order is None:
                self._fail(404, 4040, f"订单 {order_id} 不存在")
                return
            if order["status"] == "REFUNDED":
                self._fail(400, 4009, "该订单已退款，不能重复退")
                return

            try:
                amount_dec = Decimal(str(amount))
            except Exception:
                self._fail(400, 4001, "amount 必须是数字")
                return

            # ⚠️ BUG-01：这里本该先判断 amount_dec <= 0 就拒绝。
            #    现在负数一路走到底，等于"退款 -50 元"，账就反了。
            if amount_dec > Decimal(order["amount"]):
                self._fail(400, 4002, f"退款金额不能超过订单金额 {order['amount']}")
                return

            order["status"] = "REFUNDED"
            refund = {
                "refund_id": f"R{next(_REFUND_SEQ):04d}",
                "order_id": order_id,
                "amount": f"{amount_dec:.2f}",
                "status": "SUCCESS",
            }
            REFUNDS.append(refund)
            self._ok(refund)
            return

        self._fail(404, 4040, "接口不存在")


# ---------------------------------------------------------------- 启动


def create_server(port: int = 0) -> ThreadingHTTPServer:
    """port=0 表示让操作系统随便挑一个空闲端口（避免端口冲突）。"""
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve_in_background() -> tuple[ThreadingHTTPServer, str]:
    server = create_server()
    Thread(target=server.serve_forever, daemon=True).start()
    host, port = server.server_address
    return server, f"http://{host}:{port}"


if __name__ == "__main__":
    srv, url = serve_in_background()
    print(f"mock 服务已启动：{url}")
    print("接口：POST /api/login | GET /api/orders/<id> | POST /api/refunds | GET /api/health")
    print("Ctrl+C 停止")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.shutdown()
        print("已停止")
