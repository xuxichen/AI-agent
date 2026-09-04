# AI-agent

[`doc/AI_Agent_Outline.md`](<doc/AI_Agent_Outline.md>) 这份学习计划所用的工作环境 ——
一份为期约 6 个月、分 4 个阶段的前端转型 AI Agent 开发路线。

[English](README.md) | **简体中文**

## 大纲四句话

1. **第 1–2 月** —— Python 异步、FastAPI、Pydantic · LLM 与 Prompt 基础 · RAG → 一个流式对话服务
2. **第 3–4 月** —— 规划器、工具、记忆、ReAct 循环 · LangChain / LangGraph / LlamaIndex → 一个多工具助手
3. **第 5 月** —— 多 Agent 协作模式 · API 服务化、SSE、可观测、评估、审批 → 一个针对自己笔记的知识问答 Agent
4. **第 6 月** —— Node 产品层 + Python AI 层、部署上线 → 一个完整的 Agent 产品

> **当前环境处在哪一步：**这里只钉了 `langgraph`（一个阶段二的依赖），其它什么都没有。
> 阶段一要用的包（FastAPI、Pydantic、向量库、模型客户端）**尚未安装**，走到那一步再 `uv add`。

## 前置条件

- [uv](https://docs.astral.sh/uv/)
- Python 3.13（`>=3.13,<3.14`，写在 `pyproject.toml` 里；本机没有时 uv 会自己下载一个托管版）

## 启动

```bash
git clone https://github.com/xuxichen/AI-agent.git
cd AI-agent
uv sync                          # 创建 .venv，并按 uv.lock 安装依赖
source .venv/bin/activate        # Windows：.venv\Scripts\activate
```

## 验证

```bash
python -c "import sys, langgraph; print(sys.version.split()[0])"
```

预期输出 `3.13.x`。当前锁定的版本是 **langgraph 1.2.11**。

> 这个 venv 里**有 `pip`** —— pip 自己被钉在 `dev` 组里，所以 `uv sync` 不会清它。
> 装包推荐 `uv add <pkg>`；直接 `pip install <pkg>` 也能用，
> 只是 `pyproject.toml` 和 `uv.lock` 不会知道你装了东西。

## 重来一遍

```bash
rm -rf .venv && uv sync
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `doc/AI_Agent_ Outline.md` | 学习计划本身 —— 4 个阶段，月粒度，附资源链接 |
| `pyproject.toml` | 项目元信息与依赖范围 |
| `uv.lock` | 精确锁定的解析结果 —— 可复现性的唯一来源 |
| `requirements.txt` | 从 lock 导出的清单，给没有 `uv` 的人和 CI 用 |
| `.gitignore` | 把 `.venv/`、`.env*`、模型权重、各类缓存挡在 git 之外 |

## `requirements.txt`

它是从 lock 导出出来的，不是手写的：

```bash
uv export --no-hashes --all-groups -o requirements.txt
```

每次 `uv add` 或 `uv remove` 之后重新生成一次。两点需要知道：

- 手改 `requirements.txt` 对 `uv sync` **完全无效** —— 它只读 `pyproject.toml` 和 `uv.lock`，
  也不会提醒你对不上。
- 在没有 `uv` 的机器上，`pip install -r requirements.txt` 能复现出同一套版本
  （已验证：对一个空的 Python 3.13 venv 做 dry-run，43 个包全部解析成功）。

采用 MIT 许可证，详见 `LICENSE`。
