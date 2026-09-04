# AI-agent

The working environment for [`doc/AI_Agent_Outline.md`](<doc/AI_Agent_Outline.md>) — a 4-stage,
~6-month plan for moving from front-end engineering to AI Agent development.

[**English**](README.md) | [简体中文](README.zh.md)

## The plan, in four lines

1. **Months 1–2** — Python async, FastAPI, Pydantic · LLM and prompt fundamentals · RAG → a streaming chat service
2. **Months 3–4** — planner, tools, memory, ReAct loop · LangChain / LangGraph / LlamaIndex → a multi-tool assistant
3. **Month 5** — multi-agent patterns · API serving, SSE, observability, evaluation, approval gates → a RAG Q&A agent over your own notes
4. **Month 6** — Node product layer + Python AI layer, deployment → one complete agent product

> **Where this environment sits in the plan:** it pins `langgraph` — a stage-2 dependency — and nothing
> else. Stage-1 packages (FastAPI, Pydantic, a vector store, an LLM client) are **not installed yet**;
> add them with `uv add` as you reach them.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- Python 3.13 (`>=3.13,<3.14`, declared in `pyproject.toml`; uv provisions a managed build if you lack one)

## Start

```bash
git clone https://github.com/xuxichen/AI-agent.git
cd AI-agent
uv sync                          # creates .venv and installs from uv.lock
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## Verify

```bash
python -c "import sys, langgraph; print(sys.version.split()[0])"
```

Expected: `3.13.x`. Current lock resolves to **langgraph 1.2.11**.

> `pip` is available inside this venv — it is pinned in the `dev` group, so `uv sync` keeps it.
> Add packages with `uv add <pkg>`. Plain `pip install <pkg>` also works, but it leaves
> `pyproject.toml` and `uv.lock` unaware of what you just did.

## Reset

```bash
rm -rf .venv && uv sync
```

## Files

| File | Role |
|---|---|
| `doc/AI_Agent_ Outline.md` | The study plan itself — 4 stages at monthly granularity, plus resource links |
| `pyproject.toml` | Project metadata and dependency ranges |
| `uv.lock` | Exact pinned resolution — the source of truth for reproducibility |
| `requirements.txt` | Generated export of the lock, for people and CI without `uv` |
| `.gitignore` | Keeps `.venv/`, `.env*`, model weights and caches out of git |

## `requirements.txt`

It is generated from the lock, never hand-edited:

```bash
uv export --no-hashes --all-groups -o requirements.txt
```

Regenerate it whenever you `uv add` or `uv remove`. Two things worth knowing:

- Editing `requirements.txt` changes **nothing** for `uv sync` — it reads only
  `pyproject.toml` and `uv.lock`, and will not warn you about the mismatch.
- On a machine without `uv`, `pip install -r requirements.txt` reproduces this exact set
  (verified: a dry run against an empty Python 3.13 venv resolves all 43 packages).

Licensed under the MIT License; see `LICENSE`.
