#这是示例，下面是自己写

# from pathlib import Path

# data_file = Path(__file__).parents[1] / "数据" / "cases.md"
# print("文件路径：", data_file)
# print("文件存在吗：", data_file.exists())          # 提示：data_file.exists()

# text = data_file.read_text(encoding="utf-8")   # 提示：中文文件用 utf-8

# lines = text.split("\n")             # 提示：按换行切分，方法名是 split
# print("总行数：", len(lines))


from pathlib import Path

data_file = Path(__file__).resolve().parent.parent /"数据" /"cases.md"  #resolve()获取绝对路径  parent获取上级

read_file = data_file.read_text(encoding="utf-8")   #read_text(encoding= )必须携带参数，否则会报错

lines_file = read_file.splitlines()
print("测试路径是否存在：",data_file.exists())      #exists()判断是否存在
print("测试路径为：",data_file)
print(lines_file)
print(len(lines_file))

# print(type(read_file))    #read_text()读取的内容格式为str
# print(type(lines_file))   #split()、splitlines()切出来类型为list



