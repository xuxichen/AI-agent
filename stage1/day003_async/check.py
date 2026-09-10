"""Day 3 自动验收。跑法：

    uv run python stage1/day003_async/check.py

它**真的去跑**你写的 code/python/batch_slow.py，再从 stdout 里解析耗时和顺序。
所以那几行 print 的格式必须和 01_作业.md 第 4 题给的一致。

它不联网、不需要 FastAPI、也不需要 httpx。
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "code" / "python" / "batch_slow.py"

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
    print(f"✗ 找不到 {TARGET.relative_to(ROOT)}")
    print("  先做作业第 4 题：在 stage1/day003_async/code/python/ 下建 batch_slow.py")
    print("\nDay 3 未过关：0/6")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
TREE = ast.parse(SRC)
try:
    PROC = subprocess.run(
        [sys.executable, str(TARGET)], cwd=ROOT, capture_output=True, text=True, timeout=60
    )
except subprocess.TimeoutExpired:
    print("✗ batch_slow.py 跑了 60 秒还没完 —— 八成是哪里在等一个永远不会来的东西")
    print("\nDay 3 未过关：0/6")
    sys.exit(1)
OUT = PROC.stdout + PROC.stderr

TIMING = re.search(r"串行\s*([\d.]+)s\s*\|\s*并发\s*([\d.]+)s\s*\|\s*比值\s*([\d.]+)", OUT)
ORDER = re.search(r"返回顺序:\s*(\[[^\]]*\])", OUT)
THREAD = re.search(r"to_thread 花掉\s*([\d.]+)s", OUT)

ASYNC_DEFS = [n for n in ast.walk(TREE) if isinstance(n, ast.AsyncFunctionDef)]
PLAIN_DEFS = [n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef)]


# ---- 1. 脚本跑得通 ----
def t_runs():
    assert PROC.returncode == 0, (
        f"退出码 {PROC.returncode}，输出最后一行："
        f"{(OUT.strip().splitlines() or ['（一行都没印）'])[-1]}"
    )
    return "退出码 0"


# ---- 2. 三行输出格式可解析 ----
def t_output_shape():
    missing = []
    if not TIMING:
        missing.append('串行/并发/比值那行。要印成 print(f"串行 {s:.2f}s | 并发 {c:.2f}s | 比值 {c / s:.2f}")')
    if not ORDER:
        missing.append('顺序那行。要印成 print("返回顺序:", res)')
    if not THREAD:
        missing.append('to_thread 那行。要印成 print(f"两个 to_thread 花掉 {...:.2f}s")')
    assert not missing, "缺：" + "；".join(missing)
    return "三行都在"


# ---- 3. 并发真的生效 ----
def t_speedup():
    assert TIMING, "那行耗时没印出来，第 2 项就没能解析——先看第 1、2 项的报错"
    serial, concurrent, ratio = (float(g) for g in TIMING.groups())
    assert serial >= 0.85, (
        f"串行只花了 {serial:.2f}s。三次各 0.3s 排着等，应该在 0.90s 上下。"
        "你是不是在 serial() 里偷偷用了 gather"
    )
    assert concurrent <= 0.55, (
        f"并发那趟花了 {concurrent:.2f}s，没并起来。三个 0.3s 同时睡应该是 0.30s 上下。"
        "两种可能：`concurrent()` 里根本没用 gather（教案第二节），"
        "或者用了 gather 但函数体里有 time.sleep 把唯一的线程按住了（教案第六节）"
    )
    assert ratio <= 0.6, (
        f"比值 {ratio:.2f} —— 并发没生效。"
        "九成是 make_coffee 里用了 time.sleep（教案第六节那个坑），"
        "或者你的比值算反了（要 并发 ÷ 串行）"
    )
    return f"串行 {serial:.2f}s → 并发 {concurrent:.2f}s，比值 {ratio:.2f}"


# ---- 4. gather 的返回顺序 = 传入顺序 ----
def t_order():
    assert ORDER, "「返回顺序」那一行没印出来——先看第 1、2 项的报错"
    got = [int(x) for x in re.findall(r"-?\d+", ORDER.group(1))]
    assert got == [2, 0, 1], (
        f"返回顺序应为 [2, 0, 1]，实际 {got}。"
        "gather 返回的是「传入顺序」，不是「完成顺序」——"
        "如果你自己按谁先跑完去收集，就会得到 [0, 1, 2]（教案第四节）"
    )
    return "[2, 0, 1]"


# ---- 5. async 函数体里没有阻塞调用，且 to_thread 真的在用 ----
def t_no_blocking_inside_async():
    bad = [n.name for n in ASYNC_DEFS if "time.sleep" in ast.unparse(n)]
    assert not bad, (
        f"这些 async def 里面有 time.sleep：{bad}。"
        "它会按住唯一的那个线程，你的 gather 立刻退化成串行（教案第六节）。"
        "async 函数里等时间要用 await asyncio.sleep"
    )
    assert "asyncio.to_thread" in SRC, (
        "全文没有 asyncio.to_thread —— 要求 6 要你把那个普通 def 里的阻塞"
        "丢到别的线程去跑"
    )
    blockers = [n.name for n in PLAIN_DEFS if "time.sleep" in ast.unparse(n)]
    assert blockers, (
        "没有任何**普通 def**（不是 async def）里面用了 time.sleep。"
        "要求 6 要的就是一个你改不动的阻塞函数，把它调给 to_thread"
    )
    th = [n.name for n in ASYNC_DEFS if "to_thread" in ast.unparse(n)]
    assert th, f"to_thread 只出现在 async def 之外的话就不成立（找到的是：{th}）"
    return f"async 内无 time.sleep；{blockers[0]}() 是阻塞函数，被 {th[0]}() 交给线程"


# ---- 6. asyncio.run 只在最外层，且主程序被开关包住 ----
def t_run_at_top_level():
    inside = [n.name for n in ASYNC_DEFS if re.search(r"asyncio\.run\s*\(", ast.unparse(n))]
    assert not inside, (
        f"这些 async def 里面调了 asyncio.run：{inside}。"
        "会报 RuntimeError: asyncio.run() cannot be called from a running event loop（教案第八节）"
    )
    guarded = [
        st for st in TREE.body
        if isinstance(st, ast.If) and "__main__" in ast.unparse(st.test)
    ]
    assert guarded, (
        "顶层没有 if __name__ == \"__main__\": 这一段（昨天第七节教的那个开关）。"
        "把驱动整个脚本的那几行搬进去"
    )
    calls_run_in_guard = any("asyncio.run" in ast.unparse(st) for st in guarded)
    assert calls_run_in_guard, (
        "开关里面没有 asyncio.run —— 整个脚本的入口应该长这样："
        'if __name__ == "__main__":\n    asyncio.run(main())'
    )
    return "asyncio.run 只在最外层的开关里"


check("1. 脚本跑得通", t_runs)
check("2. 输出三行可解析", t_output_shape)
check("3. 行为 · 并发生效", t_speedup)
check("4. 行为 · gather 返回传入顺序", t_order)
check("5. 写法 · async 里没有阻塞调用", t_no_blocking_inside_async)
check("6. 写法 · asyncio.run 只在最外层", t_run_at_top_level)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 3 项机器判不了，你自己批 ──")
print("  □ 第 1 题：五个形状你都是先写下猜测再跑的；猜错的那几个，你能说出错在哪")
print("  □ 第 2 题：你的 wake_two 是关着教案写的，而且你亲手把它改回串行跑过一次")
print("  □ 第 3 题：三段耗时你都是先算再跑的；只改一行之后那版的新耗时你写下来了")

print(f"\nDay 3 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，3 项需你自批")
sys.exit(0 if passed == len(results) else 1)
