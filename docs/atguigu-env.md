# 尚硅谷 LangGraph 教程 · 环境与依赖对照表

本仓库跟练的课程是 [尚硅谷 LangGraph 教程](https://github.com/xbsheng/atguigu-note)
（本地路径下的 `atguigu-note` 笔记仓库）。本文记录**课程要求**与**本仓库实际环境**之间的映射，
避免每次遇到报错都回去翻 193 行的 `requirements_full.txt`。

> 结论先说：**不要整体迁移 `requirements_full.txt`**，它会把本仓库 10 个包降级，
> 且其中绝大部分属于课程的其它章节或另一门 LangChain 课。按下面的分章增量装。

---

## 1. 课程结构（共 6 章，视频 P1–P132）

| 章节 | 内容 | 分 P | 代码目录 |
|---|---|---|---|
| 第 00 章 | 环境配置 | P1–P7 | — |
| 第 01 章 | LangGraph 基础入门 | P8–P27 | `chapter01/`（10 个 notebook） |
| 第 02 章 | 控制流与节点执行 | P28–P55 | `chapter02/` |
| 第 03 章 | 持久化与记忆管理 | P56–P83 | `chapter03/` |
| 第 04 章 | 中断与工具与**部署** | P84–P106 | `chapter04/` |
| 第 05 章 | 高级特性（流式 / 子图 / 图设计） | P107–P132 | `chapter05/` |

载体是 **79 个 `.ipynb`**，不是 `.py`。`代码/langgraph/main.py` 是 PyCharm 自动生成的
`print_hi('PyCharm')` 模板，无任何实质内容。所以跟练的第一步是配好 Jupyter kernel，
而不是配 `.py` 的运行配置。

**注意**：课件 `00-环境配置.md` 里两处写「Ch 9 及之后 / Ch 9 项目部署章节」，但课程大纲只到第 05 章
——那是过时残留。真正的部署内容在**第 04 章（P84–P106）**，`langgraph-cli` 到那里才需要。

## 2. conda → uv 命令翻译

课程 Python 版本 = **3.13**（`conda create -n langgraph python=3.13`），与本仓库
`pyproject.toml` 的 `>=3.13,<3.14` 一致，无需调整。

| 教程里（conda） | 本仓库（uv） |
|---|---|
| `conda create -n langgraph python=3.13` | `uv venv --python 3.13` |
| `conda activate langgraph` | `source .venv/bin/activate` |
| `conda deactivate` | `deactivate` |
| `pip install -r requirements.txt` | `uv pip install -r ...` 或 `uv add <包>` |
| `conda list` | `uv pip list` |
| 终端前缀 `(langgraph)` | 终端前缀 `(AI-agent)` |

⚠️ 前缀括号里的内容是**环境名**，不是"某个服务启动了"。教程里的 `(langgraph)` 只是那位讲师
给他的 conda 环境起的名字。

## 3. 分章依赖增量（按 notebook 实际 import 得出）

```bash
# 第 01 章开始前 —— 一次性
uv add langchain langchain-core langchain-deepseek python-dotenv loguru

# 第 02 章
uv add anthropic requests

# 第 03 章（持久化与记忆）
uv add langchain-experimental          # 图构造辅助
uv add langgraph-checkpoint-postgres "psycopg[binary]"   # 仅当跟到 Postgres 版；
                                                        # 该章也讲 SQLite/内存版，先用默认即可
# 第 04 章（部署 / Studio）
uv add "langgraph-cli[inmem]" fastapi uvicorn

# 第 05 章：沿用前面，无新增
```

### 关于 Jupyter（不列入默认批次）

课程用 `.ipynb` 承载代码，但章节内 78 本 notebook 共 143 个 code cell、**0 个 markdown cell**（平均每本 1.83 格），
逐格交互的价值接近 0，且无 `%魔法` / `!shell`，抽码不需 `nbconvert`。实测新增包数量：

| 选择 | 新增包 | 适用 |
|---|---|---|
| 按 [`00-syllabus.md`](00-syllabus.md) 全部产出 `.py` | **0** | 默认路线 |
| `uv add ipykernel`（只为在 Qoder 里打开 notebook） | 27 | 想照教程原样跟时 |
| `uv add jupyter`（课件推荐） | 83 | 不推荐，为一个 1.83 格的载体拖进 lab / notebook / qtconsole |

### 拓扑可视化 API 实测（langgraph 1.2.11）

- `draw_mermaid()` → 纯文本，**零依赖不联网**，首选
- `draw_ascii()` → 需要额外 `uv add grandalf`，不装则 `ImportError`
- `draw_mermaid_png()` → **默认 POST 到 `https://mermaid.ink`**（`langchain_core/runnables/graph_mermaid.py:423`）；环境里已有 `requests`，所以它不会报错而是默默联网

装之前建议先看解析结果，确认 `langgraph` 没被拖到旧版本：


```bash
uv add --dry-run <包名>     # 输出里若出现 langgraph 版本变化，先停下来
uv run pytest               # 每次装完跑一次，3 passed 才算安全
```

## 4. 明确不要装进本仓库

这些出现在 `requirements_full.txt`，但在教程的 78 本章节 notebook（另有一本 `test.ipynb`，内容只是 `print("hi")` 与环境验证）+ 4 个 `.py` 中
**一次都没有被 import**：

```
mcp / fastmcp / langchain-mcp-adapters     ← 讲义正文提 MCP，代码没用
langchain-milvus / pymilvus                ← 属于另一门 LangChain 课
langchain-tavily / langchain-community     ← 同上
langchain-openai / openai / langchain-anthropic ← 课程用 DeepSeek，这几项未被 import
unstructured 全家桶 / onnx / onnxruntime / opencv-python
transformers / tokenizers / huggingface-hub ← 出现的 graph_transformers 是 langchain-experimental 的子模块
dashscope / tencentcloud-sdk-python / sqlalchemy / pypandoc-binary / pi-heif
```

`pymilvus`、`langchain_tavily`、`langchain_community`、`langchain_openai` 确实被 import，
但**全部落在仓库的 `langchain/` 目录**（另一门 LangChain 课，46 个 notebook）。
将来学那门课时给它单独建一个环境，别和这里混。

## 5. 版本冲突表：照抄会被降级

| 包 | 本仓库（当前） | 教程 pin | 照抄后果 |
|---|---|---|---|
| langgraph | 1.2.11 | 1.1.2 | ↓ 降级 |
| langchain-core | 1.6.1 | 1.2.18 | ↓ 降级 |
| langgraph-checkpoint | 4.2.0 | 4.0.1 | ↓ 降级 |
| langgraph-sdk | 0.4.4 | 0.3.9 | ↓ 降级 |
| langgraph-prebuilt | 1.1.0 | 1.0.8 | ↓ 降级 |
| pydantic | 2.13.5 | 2.12.5 | ↓ 降级 |
| requests | 2.34.2 | 2.32.5 | ↓ 降级 |
| websockets | 16.1.1 | 16.0 | ↓ 降级 |
| pytest | 9.1.1 | 9.0.3 | ↓ 降级 |
| orjson | 3.12.0 | 3.11.7 | ↓ 降级 |

所以**只取包名，不取版本号**。真出现某 API 对不上，再单独降那一个包。

## 6. `requirements_full.txt` 为什么不能当权威清单

三条实测证据：

1. **过宽**：193 行里约 130 个包从未被 import（见第 4 节）。它是讲师开发机的环境快照，不是依赖声明。
2. **不全**：`chapter02/13_loop_goto.ipynb` 里有一行 `from sympy.codegen.cnodes import goto`，
   该 cell 有成功执行记录，但 **`sympy` 根本没出现在 `requirements_full.txt` 里**。
3. **含噪音**：同一行 `goto` 和 `chapter03/09_fork.ipynb` 里的 `from pikepdf._core import Annotation`
   是 IDE 自动补全选错包的典型事故——作者想要的是 LangGraph 的 `goto` 和 `typing.Annotated`。
   `pikepdf` 因此被记进了清单（第 166 行），`sympy` 没有。

你不需要为了跟练装这两个包。如果哪天复制那页 notebook 报 `ModuleNotFoundError`，
**正确做法是删掉那行 import**，不是装 sympy。

## 7. API Key

见根目录 `.env.example`。要点：`DEEPSEEK_API_KEY` 一项即可跟完全程；
每个 notebook 开头都有 `load_dotenv(override=True)`；课程使用的模型名是 `deepseek-v4-flash`。

真实 key 只写进 `.env`（已被 `.gitignore` 拦住），**永远不要贴进对话、提交或本文档**。

## 8. 本文的证据范围与盲区

扫描对象：`atguigu-note` 全仓库 **306 个文件**（125 个 `.ipynb` + 181 个 `.py`，
其中 LangGraph 课 83 个）。notebook 只解析 `cells[].source`，绕开 base64 输出——
早先用整文件文本搜索时，`mcp` 曾命中 33 次，全是 base64 碎片的假阳性。

这套方法**看不见**三类东西，所以本表不是完备的：

- **CLI 工具**：`langgraph-cli`、`jupyter` 不会被 import，只能从课件与 `.langgraph_api/` 目录推断
- **动态导入**：`importlib.import_module("字符串")` 抓不到
- **过期输出**：notebook 的 `outputs` 可能来自改动前的源码，据此判断"装过某个包"存在误差
