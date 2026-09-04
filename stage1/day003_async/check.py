"""Day 3 自动验收。跑法：

    uv run python stage1/day003_async/check.py

它会真的执行你写的 concurrent_fetch.py，并从 stdout 解析耗时。
所以那两行 print 的格式必须和 01_作业.md 第 2 题给的一致。
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "concurrent_fetch.py"

results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）" if detail else label))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))
    except Exception as e:
        results.append((False, f"{label} —— 出了意外：{type(e).__name__}: {e}"))


if not TARGET.exists():
    print(f"✗ 没找到 {TARGET.relative_to(ROOT)}。契约见 01_作业.md 第 2 题。")
    print("\nDay 3 未过关：还没有可跑的 concurrent_fetch.py")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
TREE = ast.parse(SRC)
PROC = subprocess.run([sys.executable, str(TARGET)], cwd=ROOT, capture_output=True, text=True)
OUT = PROC.stdout + PROC.stderr

TIMING = re.search(r"串行\s*([\d.]+)s\s*\|\s*并发\s*([\d.]+)s\s*\|\s*比值\s*([\d.]+)", OUT)
ORDER = re.search(r"返回顺序:\s*(\[[\d,\s]*\])", OUT)


# ---- 1. 脚本跑得通 ----
def t_runs():
    assert PROC.returncode == 0, (
        f"退出码 {PROC.returncode}，输出末尾：{OUT.strip()[-200:]}"
    )
    return "退出码 0"


# ---- 2. 输出格式可解析 ----
def t_output_shape():
    assert TIMING, (
        "解析不到耗时行。必须打印成："
        'print(f"串行 {serial:.2f}s | 并发 {concurrent:.2f}s | 比值 {concurrent / serial:.2f}")'
    )
    assert ORDER, '解析不到顺序行。必须打印成：print("返回顺序:", [...])'
    return "两行都在"


# ---- 3. 并发真的生效 ----
def t_speedup():
    serial, concurrent, ratio = (float(g) for g in TIMING.groups())
    assert serial >= 0.45, (
        f"串行只花了 {serial:.2f}s，3 次 0.2s 的等待应该有 0.6s 左右。"
        "端点里的 await asyncio.sleep(0.2) 是不是被改掉了？"
    )
    assert ratio <= 0.6, (
        f"比值 {ratio:.2f} —— 并发没生效。"
        "九成是端点里用了 time.sleep（第 6 题的实验没改回来），"
        "或者你的『并发段』其实是逐个 await"
    )
    return f"串行 {serial:.2f}s → 并发 {concurrent:.2f}s，比值 {ratio:.2f}"


# ---- 4. gather 的返回顺序 = 传入顺序 ----
def t_order():
    got = [int(x) for x in re.findall(r"\d+", ORDER.group(1))]
    assert got == [2, 0, 1], (
        f"返回顺序应为 [2, 0, 1]，实际 {got}。"
        "gather 返回的是「传入顺序」，不是「完成顺序」——"
        "如果你自己按完成先后收集，就会得到别的排列"
    )
    return "[2, 0, 1]"


# ---- 5. 静态检查：结构对，且没有阻塞调用 ----
def t_static():
    assert "ASGITransport" in SRC, (
        "要用 httpx.ASGITransport(app=app)，这样不必起 uvicorn 进程"
    )
    assert "asyncio.gather" in SRC or "create_task" in SRC, (
        "并发段必须用 gather 或 create_task，逐个 await 不算并发"
    )
    assert "time.sleep" not in SRC, (
        "源码里有 time.sleep —— 第 6 题的实验没改回来。"
        "端点里必须是 await asyncio.sleep(0.2)"
    )
    for node in ast.walk(TREE):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call) and re.search(
                r"asyncio\.run$", ast.unparse(sub.func)
            ):
                raise AssertionError(
                    f"async def {node.name}() 里调了 asyncio.run —— "
                    "会报 RuntimeError: cannot be called from a running event loop"
                )
    return "ASGITransport + gather，无 time.sleep，无嵌套 run"


# ---- 6. 慢端点是 async 的，且真的 await 了 ----
def t_endpoint():
    routes = [
        n for n in ast.walk(TREE)
        if isinstance(n, ast.AsyncFunctionDef)
        and any("slow" in ast.unparse(d) for d in n.decorator_list)
    ]
    assert routes, '找不到被 @app.get("/slow/{i}") 装饰的 async def'
    body = ast.unparse(routes[0])
    assert "asyncio.sleep" in body, "端点里要 await asyncio.sleep(0.2)"
    assert "await" in body, "端点里的 asyncio.sleep 必须 await，否则协程不会执行"
    return f"{routes[0].name}() 是 async 且 await 了 sleep"


check("1. 脚本跑得通", t_runs)
check("2. 输出格式可解析", t_output_shape)
check("3. 并发生效", t_speedup)
check("4. gather 返回顺序", t_order)
check("5. 结构与无阻塞调用", t_static)
check("6. 慢端点是 async", t_endpoint)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 1 项机器判不了，你自己批 ──")
print("  □ 第 5 题：3 句话讲清 coroutine 惰性 vs Promise 立即执行，含 create_task")

print(f"\nDay 3 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，1 项需你自批")
sys.exit(0 if passed == len(results) else 1)
