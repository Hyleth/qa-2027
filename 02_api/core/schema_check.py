"""JSON Schema 校验：说清"这个接口的返回应该长什么样"。

为什么需要它
------------
普通断言只能检查"这一个字段等于这个值"，比如 amount == "199.00"。
但如果开发把字段名从 amount 改成 total_amount，你的旧断言会报 KeyError —— 报错信息
是"取不到 amount"，你无法一眼判断是"业务错了"还是"契约变了"。

Schema 是另一层保险：它描述"这个 JSON 必须有哪些字段、什么类型、什么格式"。
契约一变，schema 校验立刻报"缺少必填字段 amount"，问题一目了然。

一句话记：普通断言管"值对不对"，schema 管"结构还在不在"。
两者都要有，不能互相替代。
"""

from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft7Validator


def validate(payload: Any, schema: dict) -> list[str]:
    """校验并返回错误列表。空列表表示通过。

    故意不用 jsonschema.validate() 抛异常 —— 一次把全部错误列出来，
    比一条条试要快得多。
    """
    validator = Draft7Validator(schema)
    return [
        f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}"
        for err in sorted(validator.iter_errors(payload), key=lambda e: list(e.absolute_path))
    ]


def assert_schema(payload: Any, schema: dict, label: str = "响应体") -> None:
    """校验失败时给出人能看懂的报错。"""
    errors = validate(payload, schema)
    if errors:
        raise AssertionError(
            f"{label}不符合约定结构，共 {len(errors)} 处问题：\n"
            + "\n".join(f"  - {e}" for e in errors)
            + "\n\n实际响应：\n"
            + json.dumps(payload, ensure_ascii=False, indent=2)[:800]
        )


# ---------------------------------------------------------------- 通用片段

SUCCESS_ENVELOPE = {
    "type": "object",
    "required": ["code", "message", "data"],
    "properties": {
        "code": {"type": "integer"},
        "message": {"type": "string"},
        "data": {},
    },
}

ERROR_ENVELOPE = {
    "type": "object",
    "required": ["code", "message", "data"],
    "properties": {
        "code": {"type": "integer", "minimum": 1},
        "message": {"type": "string", "minLength": 1},
        "data": {"type": "null"},
    },
}

LOGIN_DATA = {
    "type": "object",
    "required": ["token", "user_id", "expires_in"],
    "properties": {
        "token": {"type": "string", "minLength": 8},
        "user_id": {"type": "integer", "minimum": 1},
        "expires_in": {"type": "integer", "minimum": 1},
    },
    "additionalProperties": False,
}

ORDER_DATA = {
    "type": "object",
    "required": ["order_id", "user_id", "amount", "status"],
    "properties": {
        "order_id": {"type": "string", "pattern": r"^O\d{4}$"},
        # 金额必须是字符串，且形如 199.00 —— 这条 pattern 就是在守"金额不许用浮点"的约定
        "amount": {"type": "string", "pattern": r"^\d+\.\d{2}$"},
        "user_id": {"type": "integer"},
        "status": {"type": "string", "enum": ["PAID", "REFUNDED", "CANCELLED"]},
    },
    "additionalProperties": False,
}

REFUND_DATA = {
    "type": "object",
    "required": ["refund_id", "order_id", "amount", "status"],
    "properties": {
        "refund_id": {"type": "string", "pattern": r"^R\d{4}$"},
        "order_id": {"type": "string"},
        "amount": {"type": "string", "pattern": r"^\d+\.\d{2}$"},
        "status": {"type": "string", "enum": ["SUCCESS", "FAILED", "PROCESSING"]},
    },
    "additionalProperties": False,
}
