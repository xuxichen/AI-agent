"""Day 4 自动验收。跑法：

    uv run python stage1/day004_fastapi_basics/check.py

它会 import 你的 app，用 TestClient 打 7 组请求。全部离线，不占端口。
"""

import ast
import re
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "api_basics.py"

results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）" if detail else label))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))
    except Exception as e:
        # TestClient 默认会把服务端未处理的异常重新抛出来，
        # 不能让它把整个 check.py 带崩。
        results.append((False, f"{label} —— 服务端抛了未处理的异常：{type(e).__name__}: {e}"))


if not TARGET.exists():
    print(f"✗ 没找到 {TARGET.relative_to(ROOT)}。契约见 01_作业.md 第 2 题。")
    print("\nDay 4 未过关：还没有可查的 api_basics.py")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
TREE = ast.parse(SRC)

# 不用 importlib：它会命中 __pycache__ 里的陈旧字节码。
# 同大小、同一秒内改写的文件会让 timestamp 校验通过，
# 结果就是 check.py 验的是上一版代码。直接编译源码文本最稳。
mod = types.ModuleType("day4_api_basics")
mod.__file__ = str(TARGET)
try:
    exec(compile(SRC, str(TARGET), "exec"), mod.__dict__)
except Exception as e:
    print(f"✗ api_basics.py 导入就炸了：{type(e).__name__}: {e}")
    print("\nDay 4 未过关：先把 import 错误修掉")
    sys.exit(1)

if not hasattr(mod, "app"):
    print("✗ 模块级必须有 app = FastAPI()，check.py 要 import 它")
    sys.exit(1)

from fastapi import FastAPI
from fastapi.testclient import TestClient

assert isinstance(mod.app, FastAPI), "app 不是 FastAPI 实例"
client = TestClient(mod.app)


def detail_of(resp):
    """422 的 detail 是列表，404 的 detail 是字符串。"""
    return resp.json().get("detail")


# ---- 1. /notes/mine 命中自己的处理函数（注册顺序对了）----
def t_mine():
    r = client.get("/notes/mine")
    assert r.status_code == 200, (
        f"/notes/mine 返回 {r.status_code}，不是 200。"
        "如果是 422，说明它被 /notes/{note_id} 截住了——"
        "把 /notes/mine 的定义挪到 {note_id} 之前"
    )
    assert r.json() == {"note": "mine"}, f"响应体应为 {{'note': 'mine'}}，实际 {r.json()}"
    return "200 {'note': 'mine'}"


# ---- 2. 路径参数按注解转成 int ----
def t_path_param():
    r = client.get("/notes/7?q=hello")
    assert r.status_code == 200, f"/notes/7?q=hello 返回 {r.status_code}"
    body = r.json()
    got = body.get("note_id")
    assert got == 7 and isinstance(got, int), (
        f"note_id 应为 int 7，实际 {got!r}（类型 {type(got).__name__}）。"
        "注解漏了 : int 的话 FastAPI 不会转换"
    )
    assert body.get("q") == "hello", f"q 应为 'hello'，实际 {body.get('q')!r}"
    r2 = client.get("/notes/7")
    assert r2.json().get("q") is None, "q 有默认值 None，不传时应为 null"
    return "note_id 是 int 7，q 可选"


# ---- 3. 类型不符 → 422，且 loc/type 指得准 ----
def t_bad_path():
    r = client.get("/notes/abc")
    assert r.status_code == 422, f"/notes/abc 应为 422，实际 {r.status_code}"
    d = detail_of(r)
    assert isinstance(d, list) and d, "422 的 detail 应是非空列表"
    assert d[0]["loc"] == ["path", "note_id"], f"loc 应为 ['path','note_id']，实际 {d[0]['loc']}"
    assert d[0]["type"] == "int_parsing", f"type 应为 int_parsing，实际 {d[0]['type']}"
    assert d[0]["input"] == "abc", f"input 应保留原始字符串 'abc'，实际 {d[0]['input']!r}"
    return "422 / loc=['path','note_id'] / type=int_parsing"


# ---- 4. 必填查询参数：不传 422，传了 200 ----
def t_required_query():
    ok = client.get("/search?keyword=x")
    assert ok.status_code == 200, f"/search?keyword=x 应为 200，实际 {ok.status_code}"
    assert ok.json() == {"keyword": "x"}, f"响应体应为 {{'keyword': 'x'}}，实际 {ok.json()}"
    miss = client.get("/search")
    assert miss.status_code == 422, (
        f"/search 缺 keyword 应为 422，实际 {miss.status_code}。"
        "你大概给 keyword 加了默认值，它就变可选了"
    )
    d = detail_of(miss)[0]
    assert d["loc"] == ["query", "keyword"], f"loc 应为 ['query','keyword']，实际 {d['loc']}"
    assert d["type"] == "missing", f"type 应为 missing，实际 {d['type']}"
    return "必填生效，loc 指向 query"


# ---- 5. 404 与 422 的形状差异 ----
def t_404_shape():
    r = client.get("/nope")
    assert r.status_code == 404, f"/nope 应为 404，实际 {r.status_code}"
    d = detail_of(r)
    assert isinstance(d, str), (
        f"404 的 detail 应为字符串，实际是 {type(d).__name__}：{d!r}"
    )
    assert d == "Not Found", f"应为 'Not Found'，实际 {d!r}"
    return "detail 是字符串 'Not Found'（422 那边是列表）"


# ---- 6. 注册顺序（静态）+ 自测入口 ----
def t_registration_order():
    lines = {}
    for node in TREE.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in node.decorator_list:
            m = re.search(r'app\.(?:get|post|put|delete|api_route)\(\s*["\']([^"\']+)', ast.unparse(d))
            if m:
                lines[m.group(1)] = node.lineno
    for path in ("/notes/mine", "/notes/{note_id}", "/search"):
        assert path in lines, f"缺路由 {path}，已注册的有：{sorted(lines)}"
    assert lines["/notes/mine"] < lines["/notes/{note_id}"], (
        f"/notes/mine 在第 {lines['/notes/mine']} 行，"
        f"/notes/{{note_id}} 在第 {lines['/notes/{note_id}']} 行 —— "
        "字面量路径必须注册在通配路径之前"
    )
    assert "__main__" in SRC, "缺 if __name__ == \"__main__\": 自测块"
    assert "TestClient" in SRC, "自测块要用 TestClient，不要起 uvicorn"
    return f"mine@{lines['/notes/mine']} < {{note_id}}@{lines['/notes/{note_id}']}，含 TestClient 自测块"


check("1. /notes/mine 未被截住", t_mine)
check("2. 路径参数转成 int", t_path_param)
check("3. 类型不符报 422", t_bad_path)
check("4. 必填查询参数", t_required_query)
check("5. 404 的形状", t_404_shape)
check("6. 注册顺序与自测块", t_registration_order)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 1 项机器判不了，你自己批 ──")
print("  □ 第 5 题：3 句话讲清 404 与 422 分别先查什么，含 detail 的形状差异")

print(f"\nDay 4 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，1 项需你自批")
sys.exit(0 if passed == len(results) else 1)
