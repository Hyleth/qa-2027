#W1-D6代码改造

from pathlib import Path
from collections import Counter

def load_cases():
    file_case = (Path(__file__).parents[1] / "数据" /"cases.md").read_text(encoding="utf-8")    #获取文件路径并读取文件内容

    list_case = [f for f in file_case.splitlines() if f.startswith("|")][2:]     #获取用例内容存入列表，去掉前面的说明及两行表头

    get_case = []
    for l in list_case:
        cells = [c.strip() for c in l.split("|")]
        get_case.append({           #给每一列对应表头
                "id":cells[1],
                "module":cells[2],
                "title":cells[3],
                "priority":cells[4],
                "expected":cells[5]
            })
    return get_case

def by_count(key,case):
    return Counter(c[key] for c in case)

if __name__ == "__main__":
    cases = load_cases()
    print("========== 用例统计报告 ==========")
    print(f"用例总数为 {len(cases)} 条")
    
    count_module = by_count("module",cases)
    count_priority = by_count("priority",cases)
    print(f"按模块：{dict(count_module)}")
    print(f"按优先级：{dict(count_priority)}")
    l = []
    for c in cases:
        if len(c["expected"]) < 8:
            l.append(c)
    print(f"预期结果写得含糊的用例（少于 8 个字）：")
    for t in l:
        print(f"   -{t["id"]} {t["title"]}->{t["expected"]}")
    print("==================================")
    

# from collections import Counter
# items = [
#     {"name": "张三", "age": 20,"sex":"man"},
#     {"name": "李四", "age": 20,"sex":"man"},
#     {"name": "张三","sex":"woman"}
# ]
# #统计张三出现的次数
# n = []
# for i in items:
#     n.append(i["name"])
# print(n)
# n_sum = {}
# for s in n:
#     n_sum[s] = n_sum.get(s,0) +1
# print(n_sum)
# #另一种写法
# c = Counter([i["name"] for i in items])
# print(dict(c))
