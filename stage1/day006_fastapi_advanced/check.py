"""Day 6 自动验收。跑法：

    uv run python stage1/day006_fastapi_advanced/check.py

它会 import 你的 app 和 TRACE，发四次请求，逐个元素比对执行顺序。
"""

import ast
import re
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "pipeline.py"

results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）" if detail else label))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))
    except Exception as e:
        results.append((False, f"{label} —— 服务端抛了未处理的异常：{type(e).__name__}: {e}"))


if not TARGET.exists():
    print(f"✗ 没找到 {TARGET.relative_to(ROOT)}。契约见 01_作业.md 第 2 题。")
    print("\nDay 6 未过关：还没有可查的 pipeline.py")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
TREE = ast.parse(SRC)
# 不用 importlib：它会命中 __pycache__ 里的陈旧字节码。
# 同大小、同一秒内改写的文件会让 timestamp 校验通过，
# 结果就是 check.py 验的是上一版代码（我第一版就因为这个
# 在中间件调换的实验里得到了假绿灯）。直接编译源码文本最稳。
mod = types.ModuleType("day6_pipeline")
mod.__file__ = str(TARGET)
try:
    exec(compile(SRC, str(TARGET), "exec"), mod.__dict__)
except Exception as e:
    print(f"✗ pipeline.py 导入就炸了：{type(e).__name__}: {e}")
    print("\nDay 6 未过关：先把 import 错误修掉")
    sys.exit(1)

for name in ("app", "TRACE"):
    if not hasattr(mod, name):
        print(f"✗ pipeline.py 里缺模块级的 {name}")
        sys.exit(1)

from fastapi import FastAPI
from fastapi.testclient import TestClient

assert isinstance(mod.app, FastAPI), "app 不是 FastAPI 实例"
assert isinstance(mod.TRACE, list), "TRACE 必须是模块级的 list"

client = TestClient(mod.app)

EXPECTED = {
    "/ok": ["mw2-in", "mw1-in", "dep_a", "dep_b", "acquire", "handler",
            "mw1-out", "mw2-out", "release"],
    "/boom": ["mw2-in", "mw1-in", "dep_a", "dep_b", "acquire", "boom",
              "release", "handler-for-oops", "mw1-out", "mw2-out"],
    "/http404": ["mw2-in", "mw1-in", "mw1-out", "mw2-out"],
    "/bg": ["mw2-in", "mw1-in", "bg", "mw1-out", "mw2-out", "后台任务"],
}


def diff(want: list[str], got: list[str]) -> str:
    for i, (w, g) in enumerate(zip(want, got)):
        if w != g:
            return f"第 {i} 位应是 {w!r}，实际是 {g!r}｜完整实际={got}"
    if len(want) != len(got):
        return f"应有 {len(want)} 条，实际 {len(got)} 条｜完整实际={got}"
    return "顺序完全一致"


def hit(url: str) -> list[str]:
    mod.TRACE.clear()
    return client.get(url)


# ---- 1. /ok：中间件倒序 + 依赖拓扑序 + release 在最后 ----
def t_ok():
    r = hit("/ok")
    assert r.status_code == 200, f"/ok 应为 200，实际 {r.status_code}：{r.text[:120]}"
    assert r.json() == {"b": "b", "res": "res"}, f"响应体不对：{r.json()}"
    got = list(mod.TRACE)
    assert got == EXPECTED["/ok"], diff(EXPECTED["/ok"], got)
    return "9 步顺序全对，release 在 mw2-out 之后"


# ---- 2. /boom：异常路径下 release 在 exception_handler 之前 ----
def t_boom():
    r = hit("/boom")
    assert r.status_code == 418, (
        f"/boom 应为 418，实际 {r.status_code}。"
        "exception_handler 没注册，或者返回的 status_code 写错了"
    )
    assert r.json() == {"caught": "炸了"}, f"响应体应为 {{'caught': '炸了'}}，实际 {r.json()}"
    got = list(mod.TRACE)
    assert got == EXPECTED["/boom"], diff(EXPECTED["/boom"], got)
    return "release 排在 handler-for-oops 之前（与 /ok 不对称）"


# ---- 3. /http404：HTTPException 走内置处理器，不碰依赖 ----
def t_http404():
    r = hit("/http404")
    assert r.status_code == 404, f"/http404 应为 404，实际 {r.status_code}"
    assert r.json() == {"detail": "自己抛的"}, f"detail 不对：{r.json()}"
    got = list(mod.TRACE)
    assert got == EXPECTED["/http404"], (
        diff(EXPECTED["/http404"], got)
        + "｜这个端点不该声明任何依赖，所以 TRACE 里只有 4 条中间件记录"
    )
    return "只有 4 条中间件记录，说明异常没跳过中间件链"


# ---- 4. /bg：后台任务在整条链的最后 ----
def t_bg():
    r = hit("/bg")
    assert r.status_code == 200, f"/bg 应为 200，实际 {r.status_code}"
    assert r.json() == {"ok": True}, f"响应体应为 {{'ok': True}}，实际 {r.json()}"
    got = list(mod.TRACE)
    assert got == EXPECTED["/bg"], diff(EXPECTED["/bg"], got)
    assert got[-1] == "后台任务", "后台任务必须排在所有中间件 out 之后"
    return "后台任务在 mw2-out 之后，是最后一步"


# ---- 5. 静态：mw1 定义在 mw2 之前 ----
def t_middleware_order():
    lines = {}
    for node in TREE.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in node.decorator_list:
            if "middleware" in ast.unparse(d):
                lines[node.name] = node.lineno
    assert "mw1" in lines and "mw2" in lines, (
        f"两个中间件必须分别叫 mw1、mw2，实际找到：{sorted(lines)}"
    )
    assert lines["mw1"] < lines["mw2"], (
        f"mw1 在第 {lines['mw1']} 行、mw2 在第 {lines['mw2']} 行 —— "
        "契约要求 mw1 先定义（这样 mw2 才在外层）"
    )
    return f"mw1@{lines['mw1']} < mw2@{lines['mw2']}，所以 mw2 在外层"


# ---- 6. 静态：dep_b 真的依赖 dep_a，dep_resource 用了 try/finally ----
def t_dependency_shape():
    funcs = {n.name: n for n in TREE.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert "dep_b" in funcs, "缺 dep_b"
    body = ast.unparse(funcs["dep_b"])
    assert re.search(r"Depends\(\s*dep_a\s*\)", body), (
        "dep_b 必须通过 Depends(dep_a) 声明依赖，"
        "而不是在函数体里直接调用 dep_a()——那样就绕过了 FastAPI 的缓存"
    )
    assert "dep_resource" in funcs, "缺 dep_resource"
    res = ast.unparse(funcs["dep_resource"])
    assert "yield" in res, "dep_resource 必须是生成器（用 yield）"
    assert "finally" in res, "release 要放在 finally 里，否则异常路径下不会执行"
    assert "__main__" in SRC, "缺 if __name__ == \"__main__\": 自测块"
    return "dep_b→Depends(dep_a)，dep_resource 用 try/finally 包住 yield"


check("1. /ok 的 9 步顺序", t_ok)
check("2. /boom 的异常路径", t_boom)
check("3. /http404 的内置处理", t_http404)
check("4. /bg 的后台任务时机", t_bg)
check("5. 中间件定义顺序", t_middleware_order)
check("6. 依赖声明的形状", t_dependency_shape)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 1 项机器判不了，你自己批 ──")
print("  □ 第 5 题：4 句话讲清 release 在两条路径下的时机差与应对")

print(f"\nDay 6 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，1 项需你自批")
sys.exit(0 if passed == len(results) else 1)
