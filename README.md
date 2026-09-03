# AI-agent — LangGraph Learning Project

Minimal, runnable [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) examples
built while learning agent fundamentals.

**English** | [简体中文](README.zh.md)

---

## Requirements

| Requirement | Version | Verify with |
|---|---|---|
| Python | `>=3.13,<3.14` (tested 3.13.15) | `python --version` |
| [uv](https://docs.astral.sh/uv/) | any recent (tested 0.12.5) | `uv --version` |

Python 3.13 is pinned deliberately. The examples were also verified to run on 3.14.4, but the
LangGraph ecosystem's support for 3.14 is newer than this project needs, so the pin keeps the
environment boring. Relax `requires-python` in `pyproject.toml` if you want to experiment.

## Quickstart

### Option A — uv (recommended)

```bash
git clone https://github.com/xuxichen/AI-agent.git
cd AI-agent
uv sync                              # creates .venv, installs runtime + dev deps
uv run python day1/01_first_graph.py # run an example
uv run pytest                        # run the tests
```

`uv sync` reads `uv.lock`, so the resolution is exact. If no matching Python is on your machine,
uv downloads one — you do not need to install Python 3.13 yourself.

### Option B — plain pip

```bash
git clone https://github.com/xuxichen/AI-agent.git
cd AI-agent
python3.13 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python day1/01_first_graph.py
pytest
```

This route needs a real CPython 3.13 on your PATH; pip will not fetch one for you.

## Run the examples

```bash
uv run python day1/01_first_graph.py
```

Expected output:

```text
结果: {'count': 16, 'log': ['double', 'add_ten']}
OK: langgraph 已跑通
```

The script asserts its own result, so a non-zero exit code means something is wrong.

## Test

```bash
uv run pytest            # or: uv run pytest -v
```

Expected: `3 passed`. The suite covers:

| Test | What it guards |
|---|---|
| `test_graph_doubles_then_adds_ten` | compiled graph produces the expected state |
| `test_nodes_run_in_declared_order` | edges actually execute `double` before `add_ten` |
| `test_example_runs_as_documented_script` | the Quickstart command above still works |

The third test spawns the example as a subprocess on purpose: it fails if the command in this
README ever stops working.

Note: `day1/01_first_graph.py` starts with digits and therefore cannot be `import`ed as a module.
`tests/test_day1_graph.py` loads it by file path via `importlib.util.spec_from_file_location`.
Keep that in mind when adding `dayN/0Y_*.py` files.

## Project layout

```text
.
├── day1/
│   └── 01_first_graph.py     # minimal StateGraph: two nodes, state flows through them
├── tests/
│   └── test_day1_graph.py    # 3 tests, loads the example by file path
├── docs/
│   ├── 00-syllabus.md        # task-driven learning outline: one question per unit, closed-book checks (中文)
│   ├── 01-capstone.md        # capstone spec — a multi-source research agent with an entry-level rubric (中文)
│   └── atguigu-env.md        # tutorial chapter → environment → package map (中文)
├── pyproject.toml            # project metadata, requires-python, dev dependency group
├── uv.lock                   # exact pinned resolution — commit it, it is the source of truth
├── requirements.txt          # pinned runtime deps, for the plain-pip route
├── requirements-dev.txt      # runtime deps + pytest
├── .env.example              # API key template — copy to .env, which is gitignored
├── README.zh.md              # Simplified Chinese version of this document
├── LICENSE                   # MIT
└── .gitignore                # .venv/, caches, model weights, vector stores, secrets
```

## What `day1` demonstrates

A `StateGraph` is a compiled state machine over a shared typed dict:

- **`State`** — a `TypedDict` declaring the channels that flow through the graph.
- **Node** — a function `State -> partial State`. Its return value is merged into the state;
  it does not receive or mutate the whole object.
- **Edge** — `add_edge(A, B)` fixes the order; `START` and `END` are the entry and exit sentinels.
- **`compile()`** — turns the builder into a runnable graph exposing `.invoke()`.

Because each node returns a full replacement for the `log` key, the list grows as
`[] -> ["double"] -> ["double", "add_ten"]`. A later day adds reducers, conditional edges,
checkpointing, and an LLM-backed node.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `python: command not found` right after `source .venv/bin/activate` | The venv was moved or the project folder renamed — venvs hard-code absolute paths | `uv venv --clear` (1 s, cache-warm), then `uv sync` |
| `bad interpreter: /some/old/path/.venv/bin/python3.x` | Same root cause, visible in the script shebang | Same fix. There is no patch-around; venvs are not relocatable |
| `pip: command not found` inside an activated venv | `uv venv` does not install pip by default | Use `uv pip install <pkg>`, or `uv venv --seed`, or `uv pip install pip` |
| `uv sync` deleted the pip you just installed | Expected: plain `uv sync` prunes packages not in the lock | `uv sync --inexact` keeps extra packages |
| `ModuleNotFoundError: langgraph` | You are on a different interpreter than the project venv | Check `which python`, or prefix commands with `uv run` |
| Example ran, then a later run uses stale code | IDE selected its own interpreter | Point the editor at `.venv/bin/python` (`Python: Select Interpreter`) |

## Notes

- `.venv/` is gitignored — never commit it. The environment is rebuilt from `uv.lock` /
  `requirements.txt`.
- `requirements.txt` is a full pin of one specific resolution (macOS arm64). Prefer `uv sync`
  for exact reproduction; regenerate the file with
  `uv pip freeze | grep -v '^pip==' > requirements.txt` after changing dependencies.
- API keys: `day1/01_first_graph.py` needs none — it is pure state-graph code with no model call.
  The tutorial's LLM chapters (unit U1-5 onward in [`docs/00-syllabus.md`](docs/00-syllabus.md)) call
  DeepSeek over the network and read `DEEPSEEK_API_KEY` from `.env`; copy `.env.example` to `.env`
  to supply it. `.env` and `.env.*` are gitignored (along with `*.pem` and `service-account*.json`);
  `.env.example` is committed and holds no real key.
- Learning AI Agent development? [`docs/00-syllabus.md`](docs/00-syllabus.md) turns the tutorial's 78
  notebooks into task units — each one states the question you must answer, the feature you must write,
  and how it is verified. The final project and the pass/fail rubric live in
  [`docs/01-capstone.md`](docs/01-capstone.md). Both are in Chinese.
- Following the 尚硅谷 LangGraph tutorial? [`docs/atguigu-env.md`](docs/atguigu-env.md) maps each
  course chapter to the packages it actually needs, and translates `conda` commands to `uv`.
- Licensed under the MIT License; see `LICENSE`.
