# my_cases · 自己写的接口用例

这个目录是**整份计划里唯一没有样板可抄的地方**。`02_api/tests/` 里那 19 条是教材，
这里的 5 条必须是你自己打出来的。

---

## 一、什么时候用

| 时间 | 做什么 | 对应逐日表 |
|---|---|---|
| **W3 · 11/19（周四）** | 写第 1 条：正常查询自己的订单 | `01_逐日表_W1-W4.md` → 11/19 |
| **W3 · 11/20（周五）** | 写第 2、3 条：参数化鉴权失败 + Schema 契约断言 | 同上 → 11/20 |
| **W4 · 11/23（周一）** | 开分支 `feat/my-cases` 提交，再合回 `main` | 同上 → 11/23 |
| **W4 · 11/28（周六）** | 截图 `my_cases` 的运行结果，写进 README | 同上 → 11/28 |
| **W4 · 11/29（周日）** | Gate 1 新建空目录时，这里是你**唯一可以参照**的样板 | 同上 → 11/29 |

**W5 之后不再动它。** 它会一直躺在仓库里，作为简历第二段「自己从零写 5 条接口用例」的实物证据。

---

## 二、干什么用

三层用途，从近到远：

1. **验证你真的会写**。W2 你做的所有事（读代码、改 YAML、修 bug）都还是"在别人的结构里改"。
   这里是从空白文件开始，结构和命名自己定。这一步过不去，面试官问「fixture 为什么 session 级」
   你只能背，答不了。
2. **Gate 1 的参照物**。11/29 那天要你新建空目录重搭一遍，允许回头看这里，但不许粘贴。
3. **简历那句话的实物**。计划里写的是「从零搭建 pytest 分层框架」——这句话现在不能写，
   等这个目录里有 5 条全绿的用例，才能写。**没有实物的简历条目，被追问三层就塌。**

---

## 三、怎么用

### 命令

在 `02_api/` 目录下执行（不是在本目录）：

```bash
# 只跑你自己写的（推荐，天天用这条）
..\.venv\Scripts\python.exe -m pytest my_cases -v

# 跑一条看看细节
..\.venv\Scripts\python.exe -m pytest my_cases -v -k "第1条"
```

**现在跑应该看到 `5 skipped`** —— 骨架里每个函数第一行都是 `pytest.skip("TODO ...")`，
表示"还没写"。这是故意的：让你一眼就知道还剩几条没动手。

5 条是这么来的：3 个测试函数，其中参数化那个展开成 3 条 → **1 + 3 + 1 = 5**。
写完之后应该是 **5 passed**，一条 skipped 都不剩。

> **一个会让人误以为出问题的现象**：用例名里的中文会显示成
> `[\u4e0d\u5e26Authorization\u5934]` 这种。这是 pytest 默认把非 ASCII 字符转义的，
> **教材里的 `tests/` 也一样**，不是环境坏了、不是编码坏了。结果照样是 passed。
> （真想让中文正常显示要加一个很长的 `-o` 参数，不值得，忽略它。）

### 为什么直接 `pytest` 跑不到这里

`02_api/pytest.ini` 里有这一行：

```ini
testpaths = tests
```

意思是"不带参数时，只扫 `tests` 目录"。所以：

- `pytest -q` → 只跑教材那 19 条（基线永远是 17 passed / 2 xfailed，方便你判断"我有没有搞坏东西"）
- `pytest my_cases` → 只跑你自己写的

**这两套必须分开跑。** 混在一起，你就分不清"红了是我写错了"还是"教材里那个 bug 又冒出来了"。

---

## 四、三条规则

**规则一：参照不算抄，粘贴算抄。**

判断标准很简单：**关掉参照文件，能不能把这几行重新打出来。**
能 → 你会了。不能 → 你刚才只是在搬运。

`tests/test_orders.py` 就在旁边 40 行外，允许打开看结构、看断言写法、看 `alice.pretty()` 怎么用。
但不允许选中复制。

**规则二：不碰 `tests/` 和 `core/`。**

这两个目录是教材基线。你改了它，`pytest -q` 从 17 passed 变成别的数字，
后面就失去了"我有没有搞坏东西"的参照。**要改，等 W4 收口之后再改。**

**规则三：每条用例必须能单独跑。**

```bash
..\.venv\Scripts\python.exe -m pytest "my_cases/test_my_first.py::test_my_1_query_own_order" -v
```

单跑绿、全跑红，说明**用例之间有数据污染**——这是自动化最典型的坑之一。
教材里 `test_refund.py` 开头那段注释专门讲了这件事（REF-01 改了 O1003 的状态，
所以 REF-03 只能用本来就已退款的 O1004），你写第 3 条时要注意别踩到同一个坑。

---

## 五、骨架文件里有什么

`test_my_first.py` 里三个函数，每个都是「先 skip，再给步骤注释」：

| 函数 | 条数 | 练什么 | 难点在哪 |
|---|---|---|---|
| `test_my_1_query_own_order` | 1 | 三层断言（HTTP 码 / 业务码 / 字段值） | 想不起来第三层该断哪几个字段 |
| `test_my_2_reject_bad_token` | 3 | `parametrize` + `with_auth` 参数 | 三种失败场景要用同一个函数表达 |
| `test_my_3_order_schema` | 1 | JSON Schema 契约断言 | 分不清 `SUCCESS_ENVELOPE` 和 `ORDER_DATA` 各校验哪层 |

**填法**：把 `pytest.skip(...)` 那一行删掉，然后按下面的注释补代码。
注释里给的是**步骤和提示**，不是答案——答案在 `tests/test_orders.py` 里，自己去找。

---

## 六、验收标准

做到这四条才算完成，少一条都不算：

- [ ] `pytest my_cases -v` 显示 **5 passed**，没有 skipped
- [ ] 三条函数各自能单跑通过
- [ ] `pytest -q`（跑基线）仍然显示 **17 passed, 2 xfailed** —— 说明你没改坏教材
- [ ] 能口头说清三件事：
  1. 为什么第 1 条要断 `code == 0` 而不只是 `status_code == 200`
  2. 参数化里三种失败场景的**业务码为什么不同**（4011 和 4012 不是随便编的）
  3. `assert_schema(body, SUCCESS_ENVELOPE)` 和 `assert_schema(body["data"], ORDER_DATA)` 分别在守什么

第 4 条最重要。**代码能跑不等于你会，能讲清才是。**

---

## 七、四个常见坑（提前知道，能省你一晚上）

**坑 1：`ModuleNotFoundError: No module named 'core'`**

说明你不在 `02_api/` 目录下跑，或者用了 `python` 而不是 `..\.venv\Scripts\python.exe`。
`core` 能被 import，靠的是 `02_api/conftest.py` 里那句 `sys.path.insert(0, str(ROOT))`，
而 conftest 只有在 rootdir（`02_api/`）下才会被加载。

**坑 2：报 `fixture 'alice' not found`**

`my_cases/` 自己**不需要**写 `conftest.py`。`02_api/conftest.py` 对子目录自动生效，
`alice`、`bob`、`client` 都能直接用。如果你在这里又写了一个 conftest，
反而会覆盖掉外层的，fixture 全丢。

**坑 3：改了 `client.token` 之后，后面几条用例全红了**

`client` 是**函数级** fixture，每条用例拿到的是全新的实例，正常不会串。
但如果你在参数化里把 `client.token` 设成假值之后没恢复，或者在函数外改了全局变量，
就会污染。教材里 `ApiClient.request()` 用 `saved = self.token` / `finally` 就是为了防这个——
**你自己写用例时不需要考虑它，但要知道它在防什么。**

**坑 4：跑了 `pytest` 想回滚教材的临时文件**

`data/cases.yaml` 里 REF-01 会把 O1003 置为已退款。每跑一次 pytest，mock 服务的状态就变一次——
但因为 mock 服务是**会话级 fixture 启动的、数据在内存里**，所以每次跑 pytest 都是全新的，
不受影响。**唯一会污染的是你自己手动起 `mock_server.py` 然后用 Postman 点。**
点乱了就 Ctrl+C 停掉重启，数据就复原了。

---

## 八、写完之后

1. 在 `02_api/README.md` 的「我改了什么」一节里，补一句你写了这 5 条
2. **把终端输出贴成文本块**（不要截图）：`pytest my_cases -v` 最后一行 `5 passed` 那几行粘进 README。
   原因很实际——`.gitignore` 忽略了 `screenshots/`（UI 的失败截图在里面，会越积越大），
   而且**文本可搜索、可 diff、面试官不用点开图片**，比截图更有说服力
3. `git add my_cases && git commit -m "test: 自己写的 5 条接口用例（正常/参数化鉴权/Schema 契约）"`

这一步不要省。**没有 commit，就没有证据；没有证据，面试时这句话就不能说。**
