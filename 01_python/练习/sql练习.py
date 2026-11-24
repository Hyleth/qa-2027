import sqlite3

conn = sqlite3.connect("test.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL)")

cur.execute("DELETE FROM users")
cur.execute("DELETE FROM orders")

cur.execute("INSERT INTO users VALUES (1, '张三'), (2, '李四'), (3, '王五')")
cur.execute("INSERT INTO orders VALUES (1, 1, 150.0), (2, 1, 80.0), (3, 2, 200.0), (4, 3, 50.0)")

conn.commit()
print("users 表:", cur.execute("SELECT * FROM users").fetchall())
print("orders 表:", cur.execute("SELECT * FROM orders").fetchall())
print("订单+人名：", cur.execute("SELECT ORDERS.ID, USERS.NAME FROM USERS " \
"JOIN ORDERS ON USERS.ID=ORDERS.USER_ID").fetchall())
print("每人订单数：",cur.execute("select u.name, count(*) from users u " \
"join orders o on u.id=o.user_id group by u.name").fetchall())
print("总金额>100的用户:", cur.execute("select u.name, sum(o.amount) from users u " \
"join orders o on u.id=o.user_id group by u.name having sum(o.amount)>100").fetchall())
conn.close()
