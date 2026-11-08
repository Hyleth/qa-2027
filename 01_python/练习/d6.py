# #W1-D6代码改造

# from pathlib import Path

# def load_cases():
#     file_case = (Path(__file__).parents[1] / "数据" /"cases.md").read_text(encoding="utf-8")    #获取文件路径并读取文件内容

#     list_case = [f for f in file_case.splitlines() if f.startswith("|")][2:]     #获取用例内容存入列表，去掉前面的说明及两行表头

#     get_case = []
#     for l in list_case:
#         cells = [c.strip() for c in l.split("|")]
#         get_case.append({           #给每一列对应表头
#                 "id":cells[1],
#                 "module":cells[2],
#                 "title":cells[3],
#                 "priority":cells[4],
#                 "expected":cells[5]
#             })
#     return get_case

# if __name__ == "__main__":
#     cases = load_cases()
#     print("========== 用例统计报告 ==========")
#     print(f"用例总数为 {len(cases)} 条")
#     module = ["登录","订单","支付","商品"]
#     dict_m = {}
#     for m in module:
#         t = []
#         for c in cases:
#             if c["module"] == m:
#                 t.append(c)
#         dict_m[m] = len(t)
#     print(f"按模块：{dict_m}")

#     # n = [n for m in module for c in cases if c["module"] == m]

#     priority = ["P0","P1","P2","P3"]
#     dict_p = {}
#     for p in priority:
#         t = []
#         for c in cases:
#             if c["priority"] == p:
#                 t.append(c)
#         dict_p[p] = len(t)
#     print(f"按优先级：{dict_p}")

#     l = []
#     for c in cases:
#         if len(c["expected"]) < 8:
#             l.append(c)
#     print(f"预期结果写得含糊的用例（少于 8 个字）：")
#     for t in l:
#         print(f"   -{t["id"]} {t["title"]}->{t["expected"]}")
#     print("==================================")
    
from collections import Counter
test_cases = [
    {
        "tc_id": "TC-01",
        "module": "登录",
        "title": "正确账号密码可以登录",
        "priority": "P0",
        "expect": "跳转到首页，右上角显示用户名"
    },
    {
        "tc_id": "TC-02",
        "module": "登录",
        "title": "密码错误时提示错误",
        "priority": "P0",
        "expect": "提示\"账号或密码错误\"，停留在登录页"
    },
    {
        "tc_id": "TC-03",
        "module": "登录",
        "title": "连续输错 5 次锁定账号",
        "priority": "P1",
        "expect": "提示\"账号已锁定，请 15 分钟后再试\""
    }
]

items = [
    {"name": "张三", "age": 20},
    {"name": "李四", "age": 20},
    {"name": "张三"}
]

k_sum = {}
v_sum = {}
for i in items:
    for k in i.keys():
        k_sum[k] = k_sum.get(k,0) +1    #统计每个key出现的次数
    for v in i.values():
        v_sum[v] = v_sum.get(v,0) +1    #统计每个value出现的次数

print(k_sum)
print(v_sum)
#另一种写法，使用Counter()
c1 = Counter([k for i in items for k in i.keys()])
c2 = Counter([v for i in items for v in i.values()])
print(dict(c1))     #这里需要用dict()转一下
print(dict(c2))
