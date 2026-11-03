

# from pathlib import Path

# text = (Path(__file__).parents[1] / "数据" / "cases.md").read_text(encoding="utf-8")
# lines = text.split("\n")

# # 只保留以 | 开头的行（表格行）
# table_lines = [line for line in lines if line.startswith("|")]

# # 去掉表头两行（第一行是列名，第二行是 |---|---|）
# data_lines = table_lines[2:]

# print("数据行数：", len(data_lines))

# # 每行形如： | TC-01 | 登录 | ... |
# # split("|") 之后，第 0 个是空字符串，第 1 个是编号，第 4 个是优先级
# count = {}
# for line in data_lines:
#     cells = line.split("|")
#     priority = cells[4].strip()      # 提示：优先级在第 4 列
#     count[priority] = count.get(priority, 0) + 1

# print("优先级统计：", count)



from pathlib import Path

data_file = Path(__file__).resolve().parent.parent /"数据" /"cases.md"  #resolve()获取绝对路径  parent获取上级

read_file = data_file.read_text(encoding="utf-8")   #read_text(encoding= )必须携带参数，否则会报错

lines_file = read_file.splitlines()
print("测试路径是否存在：",data_file.exists())      #exists()判断是否存在
print("测试路径为：",data_file)
print(lines_file)
print(len(lines_file))

#从lines_file列表中找到以“|”开头的str,添加到lines列表中
#去掉用例编号之前的信息
lines = [line for line in lines_file if line.startswith("|")]   #str.startswith("参数")找到以“参数”开头的字符串
print(lines)

#另一种写法
# lines=[]
# for line in lines_file:
#     if line.startswith("|"):
#         lines.append(line)
# print(lines)

#去掉两行表头
list_case = lines[2:]
print(list_case)

#从用例中获取p优先级，并进行计数
dict_p = {}
for case in list_case:
    p = case.split("|")[4].strip()  #1.先按|进行分割，把一条用例放进1个列表 2.[]再取出优先级 3.顺便strip()去除两边空格
    dict_p[p] = dict_p.get(p,0) + 1     #从dict_p.get(),获取字典p的值，不存在p时默认0
print(dict_p)





