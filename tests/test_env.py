"""环境验收：`uv run pytest` 跑通即代表阶段一声明的每个依赖都在真正工作。

全部离线 —— 不联网、不下模型、不需要 API Key。
它守的是两件事：新机器上 `uv sync` 出来的环境够用；以及后续 `uv add` 不会把已有依赖弄坏。
"""

import asyncio
import tempfile
from pathlib import Path

# ---------- 1. FastAPI：一条路由 + 一个 SSE 流式端点（阶段一验收项目的核心能力） ----------


def test_fastapi_route_and_sse_stream():
    from fastapi import FastAPI
    from fastapi.responses import StreamingResponse
    from fastapi.testclient import TestClient

    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/stream")
    async def stream():
        async def gen():
            for i in range(3):
                yield f"data: chunk-{i}\n\n"
                await asyncio.sleep(0)

        return StreamingResponse(gen(), media_type="text/event-stream")

    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/stream").text.count("data: chunk-") == 3


# ---------- 2. uvicorn[standard]：extras 到位（uvloop / httptools / websockets） ----------


def test_uvicorn_standard_extras():
    import httptools
    import uvicorn
    import uvloop
    import websockets

    assert callable(uvicorn.run)


# ---------- 3. Pydantic：校验失败必须报出人话 ----------


def test_pydantic_rejects_out_of_range():
    from pydantic import BaseModel, Field, ValidationError

    class ChatReq(BaseModel):
        prompt: str = Field(min_length=1)
        temperature: float = Field(default=0.7, ge=0, le=2)

    assert ChatReq(prompt="hi").temperature == 0.7
    try:
        ChatReq(prompt="hi", temperature=9)
    except ValidationError as e:
        assert "less than or equal to 2" in str(e)
    else:
        raise AssertionError("越界的 temperature 没有被拦住")


# ---------- 4. pydantic-settings：从 .env 读密钥 ----------


def test_pydantic_settings_reads_env_file():
    from pydantic_settings import BaseSettings, SettingsConfigDict

    env = Path(tempfile.mkdtemp()) / ".env"
    env.write_text("DEEPSEEK_API_KEY=sk-from-env-file\n", encoding="utf-8")

    class S(BaseSettings):
        model_config = SettingsConfigDict(env_file=str(env))
        deepseek_api_key: str

    assert S().deepseek_api_key == "sk-from-env-file"


# ---------- 5. OpenAI SDK 指向 DeepSeek 端点（构造即可，不发请求） ----------


def test_openai_client_points_at_deepseek():
    from openai import OpenAI

    client = OpenAI(api_key="sk-not-used", base_url="https://api.deepseek.com")
    assert hasattr(client.chat.completions, "create")


# ---------- 6. Chroma：持久化集合 + 显式向量写入 + 最近邻检索 ----------
# 显式传 embeddings，因此不会触发默认 embedding function 的联网下载。


def test_chroma_persist_and_query():
    import chromadb

    client = chromadb.PersistentClient(path=tempfile.mkdtemp())
    col = client.get_or_create_collection("notes")
    col.add(ids=["n1", "n2"], embeddings=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    assert col.count() == 2
    assert col.query(query_embeddings=[[0.9, 0.1, 0.0]], n_results=1)["ids"] == [["n1"]]


# ---------- 7. LangGraph：这轮安装没有动坏阶段二的地基 ----------


def test_langgraph_min_graph_still_runs():
    from typing import TypedDict

    from langgraph.graph import END, START, StateGraph

    class S(TypedDict):
        count: int
        log: list

    def double(s):
        return {"count": s["count"] * 2, "log": s["log"] + ["double"]}

    def add_ten(s):
        return {"count": s["count"] + 10, "log": s["log"] + ["add_ten"]}

    g = StateGraph(S)
    g.add_node("double", double)
    g.add_node("add_ten", add_ten)
    g.add_edge(START, "double")
    g.add_edge("double", "add_ten")
    g.add_edge("add_ten", END)
    assert g.compile().invoke({"count": 3, "log": []}) == {
        "count": 16,
        "log": ["double", "add_ten"],
    }
