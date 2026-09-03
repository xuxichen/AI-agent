# AI-agent — LangGraph 学习项目

[English](README.md) | **简体中文**

动手写的 [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) 最小可运行示例，
用于学习 Agent 的基础机制。

---

## 环境要求

| 依赖 | 版本 | 检查命令 |
|---|---|---|
| Python | `>=3.13,<3.14`（实测 3.13.15） | `python --version` |
| [uv](https://docs.astral.sh/uv/) | 较新版本均可（实测 0.12.5） | `uv --version` |

锁定 Python 3.13 是有意为之。这些示例在 3.14.4 上同样验证过可以运行，但 LangGraph 生态对 3.14
的支持比本项目所需更新，锁死版本能让环境保持无聊、可预测。想试 3.14 的话，改 `pyproject.toml`
里的 `requires-python` 即可。

## 快速开始

### 方式 A —— 用 uv（推荐）

```bash
git clone https://github.com/xuxichen/AI-agent.git
cd AI-agent
uv sync                              # 创建 .venv，装上运行依赖和开发依赖
uv run python day1/01_first_graph.py # 运行示例
uv run pytest                        # 跑测试
```

`uv sync` 读取 `uv.lock`，因此装出来的版本是精确一致的。如果你的机器上没有匹配的 Python，
uv 会自己下载一个 —— 你不需要手动安装 Python 3.13。

### 方式 B —— 用普通 pip

```bash
git clone https://github.com/xuxichen/AI-agent.git
cd AI-agent
python3.13 -m venv .venv
source .venv/bin/activate            # Windows 用 .venv\Scripts\activate
pip install -r requirements-dev.txt
python day1/01_first_graph.py
pytest
```

注意：这条路径要求你的 PATH 里已经有一个真正的 CPython 3.13，pip 不会替你下载解释器。

## 运行示例

```bash
uv run python day1/01_first_graph.py
```

预期输出：

```text
结果: {'count': 16, 'log': ['double', 'add_ten']}
OK: langgraph 已跑通
```

脚本内部自带断言，所以退出码非 0 就说明有问题。

## 测试

```bash
uv run pytest            # 或者：uv run pytest -v
```

预期结果：`3 passed`。测试覆盖：

| 测试 | 守住什么 |
|---|---|
| `test_graph_doubles_then_adds_ten` | 编译出的图能算出预期状态 |
| `test_nodes_run_in_declared_order` | 边确实让 `double` 先于 `add_ten` 执行 |
| `test_example_runs_as_documented_script` | 上面那条 Quickstart 命令依然可用 |

第三个测试故意用子进程去跑示例：一旦本文档里写的命令失效，它就会失败。

补充：`day1/01_first_graph.py` 以数字开头，不是合法的 Python 模块名，无法被 `import`。
`tests/test_day1_graph.py` 通过 `importlib.util.spec_from_file_location` 按文件路径加载它。
以后新增 `dayN/0Y_*.py` 时会遇到同样的情况，这里先记一笔。

## 目录结构

```text
.
├── day1/
│   └── 01_first_graph.py     # 最小 StateGraph：两个节点，状态依次流过
├── tests/
│   └── test_day1_graph.py    # 3 个测试，按文件路径加载示例
├── docs/
│   ├── 00-syllabus.md        # 任务驱动学习大纲：每个单元一个问题、一段要写的代码、一条验收
│   ├── 01-capstone.md        # 结业项目需求：多来源研究 Agent，含入门判定表
│   └── atguigu-env.md        # 教程章节 → 环境 → 依赖对照表、conda→uv 命令翻译
├── pyproject.toml            # 项目元信息、requires-python、dev 依赖组
├── uv.lock                   # 精确锁定的依赖解析 —— 应当提交，它是可复现性的唯一来源
├── requirements.txt          # 全量 pin 的运行依赖，供纯 pip 路径使用
├── requirements-dev.txt      # 运行依赖 + pytest
├── .env.example              # API Key 模板 —— 复制成 .env 使用，.env 已被 gitignore
├── README.md                 # 英文版文档
├── LICENSE                   # MIT
└── .gitignore                # .venv/、各类缓存、模型权重、向量库、密钥
```

## `day1` 演示了什么

`StateGraph` 是一个编译出来的状态机，运行在一份共享的类型化字典之上：

- **`State`** —— 一个 `TypedDict`，声明在图中流动的通道（channel）。
- **节点（Node）** —— 形如 `State -> 部分 State` 的函数。它的返回值会被合并进状态，
  节点拿到的不是整个对象，也不去原地修改它。
- **边（Edge）** —— `add_edge(A, B)` 固定执行顺序；`START` 和 `END` 是入口与出口的哨兵值。
- **`compile()`** —— 把 builder 变成可运行的图，暴露 `.invoke()`。

因为每个节点都返回 `log` 这个键的完整替代值，列表按 `[] -> ["double"] -> ["double", "add_ten"]`
增长。后续的天数会加入 reducer、条件边、checkpoint 持久化，以及由真实 LLM 驱动的节点。

## 常见问题排查

| 症状 | 原因 | 解决 |
|---|---|---|
| `source .venv/bin/activate` 之后立刻 `python: command not found` | venv 被移动过，或项目目录被改名 —— venv 里写死了绝对路径 | `uv venv --clear`（缓存命中时约 1 秒），然后 `uv sync` |
| `bad interpreter: /旧的/路径/.venv/bin/python3.x` | 同一个根因，体现在脚本的 shebang 上 | 同上。没有打补丁的余地，venv 不可搬迁 |
| 激活后 `pip: command not found` | `uv venv` 默认不安装 pip | 改用 `uv pip install <pkg>`，或建时加 `uv venv --seed`，或 `uv pip install pip` |
| `uv sync` 把你刚装的 pip 删了 | 是预期行为：不加参数的 `uv sync` 会清理 lock 里没有的包 | 用 `uv sync --inexact` 保留额外包 |
| `ModuleNotFoundError: langgraph` | 你用的解释器不是项目 venv 里那个 | `which python` 确认，或者命令统一加 `uv run` 前缀 |
| 示例跑通过，之后再跑用的是旧代码 | IDE 选了自己的解释器 | 把编辑器指到 `.venv/bin/python`（`Python: Select Interpreter`） |

## 说明

- `.venv/` 已被 gitignore —— 永远不要提交它。环境应由 `uv.lock` / `requirements.txt` 重建。
- `requirements.txt` 是某一次解析结果的全量 pin（macOS arm64）。要精确复现请优先用 `uv sync`；
  改完依赖后用 `uv pip freeze | grep -v '^pip==' > requirements.txt` 重新生成该文件。
- 关于 API Key：`day1/01_first_graph.py` 不需要任何 key，它是纯状态图代码，不调用模型。教程的 LLM
  章节（[`docs/00-syllabus.md`](docs/00-syllabus.md) 的 U1-5 单元起）会通过网络调用 DeepSeek，并从
  `.env` 读 `DEEPSEEK_API_KEY`；把 `.env.example` 复制成 `.env` 填入即可。`.env` 连同 `.env.*`、
  `*.pem`、`service-account*.json` 已被 `.gitignore` 拦住；`.env.example` 会被提交，里面不包含真实密钥。
- 想系统学 AI Agent 开发：看 [`docs/00-syllabus.md`](docs/00-syllabus.md)，它把教程的 78 个 notebook 拆成了任务单元，
  每个单元都写明“先回答什么问题、要写出什么功能、怎么算验收”，每章末尾有闭卷检验；
  结业项目需求与“算不算真入门”的判定表在 [`docs/01-capstone.md`](docs/01-capstone.md)。
- 如果跟的是尚硅谷 LangGraph 教程，先看 [`docs/atguigu-env.md`](docs/atguigu-env.md)：
  它把每一章对应真正需要装的包列了出来，并把教程里的 `conda` 命令翻译成了 `uv`。
- 本项目采用 MIT 许可证，详见 `LICENSE`。
