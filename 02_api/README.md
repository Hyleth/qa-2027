# 02_api · 接口自动化项目（W2–W4 主教材）

一个能跑、能改、能讲的接口自动化项目。被测服务是本目录的 `mock_server.py`，
纯标准库实现，不联网、不装依赖、2 秒跑完 19 条用例。

## 怎么跑

```bash
cd 02_api
..\.venv\Scripts\python.exe -m pytest -q
```

预期结果：**17 passed, 2 xfailed**。那 2 条 xfailed 是服务端真埋的 bug，不是你的脚本写错。

想看某一条：
```bash
..\.venv\Scripts\python.exe -m pytest tests\test_orders.py -v
..\.venv\Scripts\python.exe -m pytest -k "越权" -v
```

单独启动 mock 服务（想用 Postman / Apifox 手动点一点的时候）：
```bash
..\.venv\Scripts\python.exe mock_server.py
# 然后用 Postman 调 http://127.0.0.1:8000/api/health
```

## 目录在讲什么

| 文件 | 作用 | 什么时候读 |
|---|---|---|
| `mock_server.py` | 被测服务。里面埋了 2 个 bug | W2 第一天 |
| `core/http_client.py` | 把 requests 包一层：统一 base_url、自动带 token | W3 |
| `core/schema_check.py` | 用 JSON Schema 校验"返回结构还在不在" | W2 后半周 |
| `data/cases.yaml` | 用例数据。加用例改这里，不用改代码 | W2 必做 3 |
| `conftest.py` | pytest 的"装配车间"：起服务、发 token | W2 第三天 |
| `tests/test_login.py` | 登录：数据驱动 + 响应结构校验 | W2 |
| `tests/test_orders.py` | 订单：权限与越权（重点） | W2 |
| `tests/test_refund.py` | 退款：金额精度 + 已知缺陷管理 | W3 |
| **`my_cases/`** | **你自己写的 5 条用例**（骨架已给，W3 填完） | W3 · 11/19 起 |

## 埋的两个 bug（W3 的任务）

| 编号 | 位置 | 现象 | 怎么验 |
|---|---|---|---|
| **BUG-01** | `mock_server.py` 退款接口 | 退款金额传负数也能"成功"，等于给用户倒打钱 | `pytest -k 负数` |
| **BUG-02** | `mock_server.py` 订单查询 | 用 alice 的 token 能查到 bob 的订单（越权） | `pytest -k 越权` |

修好之后记得**删掉对应的 `xfail` 标记**，否则 `strict=True` 会让它变成 XPASS 然后报错。
这个"报错"是故意的——它在提醒你：bug 修了，标记该摘了。

## 三个练手任务

1. **加 3 条用例，只改 `data/cases.yaml`，不改任何 `.py`** —— 做出来说明你理解了数据驱动。
2. **给 `schema_check.py` 加一个 `REFUND_LIST` 结构**，用于校验"退款列表"接口（需自己先在 mock 里加这个接口）。
3. **修掉两个 bug，让 `pytest -q` 变成 19 passed** —— 做出来说明你能定位到代码。

## 自己写的用例：`my_cases/`

`tests/` 是教材，**`my_cases/` 是你自己写的**。两个目录的用例分开跑，故意的：

```bash
# 教材基线 —— 永远是 17 passed, 2 xfailed，用来判断"我有没有搞坏东西"
..\.venv\Scripts\python.exe -m pytest -q

# 自己写的 —— 现在是 5 skipped，W3 填完应该是 5 passed
..\.venv\Scripts\python.exe -m pytest my_cases -v
```

分不开跑会怎样：红了以后你分不清是"我写错了"还是"教材里那个已知 bug 又冒出来了"，
于是就开始瞎改，改到最后两边都看不懂。**基线和自己的用例必须能独立判定。**

细节（怎么填、什么算抄、验收四条、四个常见坑）全在 **`my_cases/README.md`**，别在这里猜。

## CI 在哪

`.github/workflows/ci.yml`（在仓库根，不在本目录）。push 到 main 就自动跑一次 `pytest -q`，
红了 PR 合不进去。

它是门禁，不是"顺便跑跑"：**pytest 有 1 条 failed → 退出码非 0 → 这一步红 → 合不进去**，
不需要另写任何判断逻辑。这就是"质量门禁"最朴素的实现，面试问"你怎么卡发版"可以直接讲这个。

两件事这份配置故意没做，理由写在文件末尾的注释里，值得读一遍：

- **CI 里不跑 UI 测试**（浏览器太重、UI 用例天生不稳，做成门禁会天天红 → 真实做法是 nightly）
- **不跑真实模型评测**（结果每次不同，门禁会天天红 → 真实做法是提交跑 mock、每日跑真模型）

## 五个概念，能用人话说清才算学会

- **`assert`**：断言。写"我认为这里应该是什么"，不符合就红。
- **`fixture`**：pytest 的"预备动作"。测试前准备好数据/服务/登录态，测完自动清理。
- **`conftest.py`**：放 fixture 的地方，pytest 会自动读，不用 import。
- **`parametrize`**：一份代码跑多组数据。5 条用例只写 1 个函数。
- **`xfail`**：预期失败。已知 bug 的用例挂这个标记，不算红，但会一直提醒你它还在。

## 面试会追问的三件事

1. **为什么断言不能只写 `status_code == 200`？**
   → 很多系统出错也返 200，靠 body 里的 `code` 区分。只断 HTTP 码等于没断业务。
2. **为什么 `client` 用函数级 fixture，`base_url` 用会话级？**
   → 起服务贵、且要复用；客户端必须每条用例一个，否则 token 互相覆盖，单跑绿、一起跑红。
3. **为什么金额用字符串不用 float？**
   → `0.1 + 0.2 != 0.3`。金额用 float 会在特定数值上出现一分钱误差，且极难复现。
