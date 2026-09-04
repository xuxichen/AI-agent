"""Day 7 自动验收（也是 Week 1 验收）。跑法：

    uv run python stage1/day007_crud_integration/check.py

它 exec 你的 crud_api.py，然后模拟一个完整用户旅程：
建 → 列 → 读 → 改 → 删 → 读不到。全部离线，不起服务器进程。
"""

import ast
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "crud_api.py"

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
    print("\nDay 7 未过关：还没有可查的 crud_api.py")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
TREE = ast.parse(SRC)
# 不用 importlib：它会命中 __pycache__ 里的陈旧字节码。
# 同大小、同一秒内改写的文件会让 timestamp 校验通过，
# 结果 check.py 验的是上一版代码（Day 6 我就是这样拿到过假绿灯）。
mod = types.ModuleType("day7_crud")
mod.__file__ = str(TARGET)
try:
    exec(compile(SRC, str(TARGET), "exec"), mod.__dict__)
except Exception as e:
    print(f"✗ crud_api.py 导入就炸了：{type(e).__name__}: {e}")
    print("  如果是 'Status code 204 must not have a response body'，")
    print("  说明 DELETE 端点声明了 response_model —— 204 不能有响应体")
    print("\nDay 7 未过关：先把 import 错误修掉")
    sys.exit(1)

for name in ("app", "store", "NoteIn", "Note", "NoteOut"):
    if not hasattr(mod, name):
        print(f"✗ crud_api.py 里缺模块级的 {name}")
        print("\nDay 7 未过关：契约见 01_作业.md 第 2 题")
        sys.exit(1)

from fastapi import FastAPI
from fastapi.testclient import TestClient

assert isinstance(mod.app, FastAPI), "app 不是 FastAPI 实例"
assert isinstance(mod.store, dict), f"store 必须是模块级的 dict，实际 {type(mod.store).__name__}"

client = TestClient(mod.app)


def reset() -> None:
    """每项检查都从空库开始，避免前一项留下的数据影响判断。"""
    mod.store.clear()


def new(title: str = "t", **kw) -> int:
    r = client.post("/notes", json={"title": title, **kw})
    assert r.status_code == 201, f"POST 建不出数据：{r.status_code} {r.text[:120]}"
    return r.json()["id"]


# ---- 1. 完整用户旅程：建 → 列 → 读 → 改 ----
def t_journey():
    reset()
    r = client.get("/notes")
    assert r.status_code == 200, f"空库的 GET 列表应为 200，实际 {r.status_code}"
    assert r.json() == [], f"空库应返回 []，实际 {r.json()}（空集合是 200 []，不是 404）"

    r = client.post("/notes", json={"title": "a"})
    assert r.status_code == 201, (
        f"POST 新建应为 201，实际 {r.status_code}。status_code=201 漏写了的话会是 200"
    )
    nid = r.json()["id"]
    assert r.json() == {"id": nid, "title": "a", "tags": []}, f"新建的响应体不对：{r.json()}"

    r = client.get("/notes")
    assert r.status_code == 200 and len(r.json()) == 1, (
        f"建完一条之后列表里应有 1 条，实际 {len(r.json())} 条：{r.json()}。"
        "如果是 0 条：store 建在依赖函数里了（每请求一个新字典），"
        "POST 照样返回 201 但数据随请求结束被丢掉 —— 见教案 3.3"
    )

    r = client.get(f"/notes/{nid}")
    assert r.status_code == 200 and r.json()["title"] == "a", f"单项读取不对：{r.status_code} {r.text[:80]}"

    r = client.put(f"/notes/{nid}", json={"title": "b", "tags": ["x"]})
    assert r.status_code == 200, f"PUT 应为 200，实际 {r.status_code}"
    assert r.json() == {"id": nid, "title": "b", "tags": ["x"]}, f"PUT 后响应体不对：{r.json()}"

    r = client.get(f"/notes/{nid}")
    assert r.json()["title"] == "b", f"PUT 没真的改到存储：{r.json()}"

    r = client.get("/notes/999999")
    assert r.status_code == 404, f"读不存在的应为 404，实际 {r.status_code}"
    assert r.json() == {"detail": "note 999999 not found"}, f"404 的 detail 不对：{r.json()}"

    r = client.put("/notes/999999", json={"title": "z"})
    assert r.status_code == 404, f"改不存在的应为 404，实际 {r.status_code}"

    return f"建(id={nid}) → 列 → 读 → 改 → 读，状态码与响应体全对"


# ---- 2. DELETE：204 空响应体，且重复删是 404 ----
def t_delete():
    reset()
    nid = new("d")

    r = client.delete(f"/notes/{nid}")
    assert r.status_code == 204, (
        f"DELETE 成功应为 204，实际 {r.status_code}。两种可能："
        "① 404 = store 没存住数据（第 3 项会同时红，见教案 3.3）；"
        "② 200 = status_code=204 漏写了，响应体会变成 'null'"
    )
    assert r.content == b"", (
        f"204 的响应体必须是空的，实际 {r.content!r}。"
        "别在 DELETE 里 return 东西（注意 r.json() 在 204 上会抛异常，所以这里比的是 r.content）"
    )

    r = client.get(f"/notes/{nid}")
    assert r.status_code == 404, f"删完还能读到：{r.status_code} {r.text[:80]}"

    r = client.delete(f"/notes/{nid}")
    assert r.status_code == 404, (
        f"重复 DELETE 应为 404，实际 {r.status_code}。"
        "让它返回 204 是另一种合理设计（面向重试的客户端），"
        "但今天的契约是「找不到就 404」，和 GET/PUT 保持一致 —— 见第 5 题"
    )
    assert isinstance(r.json().get("detail"), str), (
        f"404 的 detail 应是字符串，实际 {r.json()}（列表是 422 的形状）"
    )
    return "204 空响应体；删后读不到；重复 DELETE 是 404 且 detail 是字符串"


# ---- 3. store 的生命周期：跨请求存得住，id 不撞 ----
def t_store_survives():
    reset()
    a = client.post("/notes", json={"title": "第一次"})
    b = client.post("/notes", json={"title": "第二次"})
    assert a.status_code == 201 and b.status_code == 201, f"两次 POST：{a.status_code} {b.status_code}"
    assert a.json()["id"] != b.json()["id"], (
        f"两次 POST 拿到同一个 id {a.json()['id']} —— 计数器没有真的自增。"
        "在函数里写 next_id = next_id + 1 会 UnboundLocalError；"
        "用 itertools.count(1) 或模块级 counter = [0] 改 counter[0]"
    )

    lst = client.get("/notes").json()
    assert len(lst) == 2, (
        f"两次 POST 之后列表里应有 2 条，实际 {len(lst)} 条 {lst}。"
        "0 条 = store 建在依赖函数里了；1 条 = 第二次 POST 覆盖了第一次（id 撞了）"
    )
    titles = [n["title"] for n in lst]
    assert titles == ["第一次", "第二次"], f"列表内容/顺序不对：{titles}"
    return "两次 POST 的 id 不撞，且下一个请求还读得到两条"


# ---- 4. 422 的两个来源：body 与 path ----
def t_422():
    reset()
    r = client.post("/notes", json={"title": ""})
    assert r.status_code == 422, f"空 title 应为 422，实际 {r.status_code}"
    d = r.json()["detail"]
    assert isinstance(d, list), "422 的 detail 是列表（404 的才是字符串）—— Day 4 的秒判依据"
    assert d[0]["type"] == "string_too_short", f"错误类型不对：{d[0]['type']}"
    assert d[0]["loc"] == ["body", "title"], f"loc 应指向 body 的 title，实际 {d[0]['loc']}"

    r = client.get("/notes/abc")
    assert r.status_code == 422, (
        f"/notes/abc 应为 422，实际 {r.status_code}。"
        "404 说明路径参数没标 int（note_id: int），"
        "200 说明你把它当字符串收下了"
    )
    d = r.json()["detail"]
    assert d[0]["type"] == "int_parsing", f"错误类型不对：{d[0]['type']}"
    assert d[0]["loc"] == ["path", "note_id"], f"loc 应指向 path 的 note_id，实际 {d[0]['loc']}"
    assert d[0]["input"] == "abc", f"input 应是原始的 'abc'，实际 {d[0]['input']!r}"
    return "body 与 path 两个来源的 422，loc 各自指对了位置"


# ---- 5. 入口边界与出口过滤（Day 5 的结论在这里变成断言）----
def t_models():
    reset()
    r = client.post("/notes", json={"title": "t"})
    assert "owner" not in r.json(), f"响应里泄露了 owner：{r.json()}（response_model=NoteOut 漏写）"

    # 强行塞 id 和 owner，看服务端收不收
    r = client.post("/notes", json={"title": "t", "id": 999, "owner": "hacker"})
    assert r.status_code == 201, f"多传字段应该被忽略而不是报错，实际 {r.status_code} {r.text[:120]}"
    assert r.json()["id"] != 999, (
        f"服务端接受了用户指定的 id={r.json()['id']} —— NoteIn 里不该有 id，"
        "否则用户 PUT 时能直接覆盖别人的记录"
    )
    assert "owner" not in r.json(), f"用户能自己指定 owner：{r.json()}"

    f_in = set(mod.NoteIn.model_fields)
    assert "id" not in f_in, f"NoteIn 有 id：{sorted(f_in)}"
    assert "owner" not in f_in, f"NoteIn 有 owner：{sorted(f_in)}"
    f_out = set(mod.NoteOut.model_fields)
    assert "owner" not in f_out, f"NoteOut 有 owner：{sorted(f_out)}"
    assert "id" in f_out, f"NoteOut 缺 id：{sorted(f_out)}（前端需要它来做后续请求）"
    return f"NoteIn={sorted(f_in)} NoteOut={sorted(f_out)}；多传的 id/owner 被 Pydantic 忽略"


# ---- 6. 路由组织：paths 干净 + 用了 APIRouter + 204 没声明 response_model ----
def t_router_shape():
    paths = set(mod.app.openapi()["paths"])
    assert "/notes" in paths and "/notes/{note_id}" in paths, (
        f"应有 /notes 和 /notes/{{note_id}}，实际 {sorted(paths)}"
    )
    trailing = sorted(p for p in paths if p.endswith("/") and p != "/")
    assert not trailing, (
        f"有以斜杠结尾的路径 {trailing} —— 集合端点该写 \"\" 而不是 \"/\"。"
        "写 \"/\" 会把集合劈成两个 URL，POST /notes 直接 405（第 4 题的实验）"
    )
    assert "APIRouter" in SRC and "prefix=" in SRC, (
        "契约要求用 APIRouter(prefix=...) 组织路由，不要把所有端点都挂在 app 上"
    )
    assert "include_router" in SRC, "router 建了但没挂到 app 上"

    for node in ast.walk(TREE):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            s = ast.unparse(dec)
            if "204" in s:
                assert "response_model" not in s, (
                    f"{node.name} 声明了 status_code=204 又写了 response_model —— "
                    "FastAPI 启动就 AssertionError: Status code 204 must not have a response body"
                )
                break

    assert "__main__" in SRC, "缺 if __name__ == \"__main__\": 自测块"
    return f"paths={sorted(paths)}，用了 APIRouter+prefix，204 端点没有 response_model"


check("1. 完整用户旅程", t_journey)
check("2. DELETE 的 204 与重复删", t_delete)
check("3. store 跨请求存活", t_store_survives)
check("4. 422 的两个来源", t_422)
check("5. 入口边界与出口过滤", t_models)
check("6. 路由组织的形状", t_router_shape)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 2 项机器判不了，你自己批 ──")
print("  □ 第 5 题：4 句话讲清「重复 DELETE 返回 404 为什么不违反幂等性」")
print("  □ 第 6 题：测试隔离的解法，以及它在多进程下为什么不成立")

print(f"\nDay 7 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，2 项需你自批")
sys.exit(0 if passed == len(results) else 1)
