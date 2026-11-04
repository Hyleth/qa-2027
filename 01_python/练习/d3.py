#这里是例子，下面是自己写
# from pathlib import Path


# def load_cases():
#     """读出所有用例行，返回一个列表，每个元素是 dict。"""
#     text = (Path(__file__).parents[1] / "数据" / "cases.md").read_text(encoding="utf-8")
#     rows = [l for l in text.split("\n") if l.startswith("|")][2:]

#     cases = []
#     for row in rows:
#         cells = [c.strip() for c in row.split("|")]
#         # cells: ['', 'TC-01', '登录', '正确账号密码可以登录', 'P0', '跳转到首页...', '']
#         cases.append({
#             "id": cells[1],
#             "module": cells[2],
#             "title": cells[3],
#             "priority": cells[4],
#             "expected": cells[5],
#         })
#     return cases


# cases = load_cases()
# print(f"共 {len(cases)} 条用例")

# # 列表推导式：挑出所有 P0
# p0 = [c["title"] for c in cases if c["priority"] == "P0"]
# print(f"P0 有 {len(p0)} 条：")
# for t in p0:
#     print("  -", t)

#-----------------------自己写
from pathlib import Path


def get_case():
    data_file = Path(__file__).resolve().parent.parent /"数据" /"cases.md"  #resolve()获取绝对路径  parent获取上级

    read_file = data_file.read_text(encoding="utf-8")   #read_text(encoding= )必须携带参数，否则会报错

    #1.按行切分内容；2.去掉 | 之前的内容；3.去掉再去掉前面两行表头
    lines_case = [line for line in read_file.splitlines() if line.startswith("|")][2:]

    list_case = []
    for case in lines_case:
        cells = [c.strip() for c in case.split("|")]    #1.先按 | 切分一条数据；2.再把切分的每个元素去掉两边空格
        dict_case = {           #给每一列对应表头
            "id":cells[1],
            "module":cells[2],
            "title":cells[3],
            "priority":cells[4],
            "expected":cells[5]
        }
        list_case.append(dict_case)
    return list_case


t = get_case()

s = [c["title"] for c in t if c["priority"] == "P0"]

print(f"测试用例共 {len(t)} 条")
print(f"P0级用例共 {len(s)} 条,分别是：")

for i in s:
    print(i)




    # print("测试路径是否存在：",data_file.exists())      #exists()判断是否存在
    # print("测试路径为：",data_file)
    # print(lines_file)
    # print(len(lines_file))

    #从lines_file列表中找到以“|”开头的str,添加到lines列表中
    #去掉用例编号之前的信息
    # lines = [line for line in lines_file if line.startswith("|")]   #str.startswith("参数")找到以“参数”开头的字符串
    # print(lines)

    # #另一种写法
    # # lines=[]
    # # for line in lines_file:
    # #     if line.startswith("|"):
    # #         lines.append(line)
    # # print(lines)

    # #去掉两行表头
    # list_case = lines[2:]
    # print(list_case)

    # #从用例中获取p优先级，并进行计数
    # dict_p = {}
    # for case in list_case:
    #     p = case.split("|")[4].strip()  #1.先按|进行分割，把一条用例放进1个列表 2.[]再取出优先级 3.顺便strip()去除两边空格
    #     dict_p[p] = dict_p.get(p,0) + 1     #从dict_p.get(),获取字典p的值，不存在p时默认0
    # print(dict_p)




