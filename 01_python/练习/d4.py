#这个是示例，下面自己写

# 这是一个典型的接口返回，和你 W2 会看到的格式一样
response = {
    "code": 0,
    "message": "ok",
    "data": {
        "total": 2,
        "items": [
            {"order_id": "O1001", "amount": "199.00", "status": "PAID"},
            {"order_id": "O1002", "amount": "88.50", "status": "REFUNDED"},
        ],
    },
}

print("业务码：", response["code"])
print("订单总数：", response["data"]["total"])

items = response["data"]["items"]
for it in items:
    print(f"  {it['order_id']}  金额 {it['amount']}  状态 {it['status']}")

# 算总金额。注意：金额是字符串，要先转成数字
total = sum(float(it["amount"]) for it in items)
print("合计：", total)

# 挑出已退款的订单号
refunded = [it["order_id"] for it in items if it["status"] == "REFUNDED"]
print("已退款：", refunded)
