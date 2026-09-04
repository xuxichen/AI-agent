"""Day 1 自动验收。跑法（仓库任意位置都行）：

    uv run python stage1/day001_env_layers/check.py

只检查「你做完第 2 题之后才会出现的东西」。
仓库的初始状态是故意不够格的：你不做事，5 项全红。

它不会替你修文件——旧版曾经悄悄跑过一次 uv export 帮你把
requirements.txt 同步好，那等于把你的遗漏掩盖掉了。现在只查不改。
"""

import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE_DEV = {"pip", "pytest"}
BASELINE_FROZEN = 106
JUNK = ("cowsay", "this-package-does-not-exist")


def run(*cmd: str) -> str:
    r = subprocess.run(list(cmd), cwd=ROOT, capture_output=True, text=True)
    return r.stdout + r.stderr


# 注意：这里绝不使用 `uv run <cmd>`。
# check.py 自己就是被 `uv run python check.py` 启动的，而 `uv run`
# 会为了子进程的整个生命周期持有虚拟环境锁——嵌套的 `uv run`
# 永远等不到它，会死锁（我实测到 9 个 `uv run pytest` 堆在那儿）。
# `uv sync` / `uv pip freeze` 是短命锁，嵌套没问题；run 不行。
# 要跑子进程就用 sys.executable（它已经是 .venv 里的 python）。


def norm(spec: str) -> str:
    """'uvicorn[standard]>=0.52.4' -> 'uvicorn'；'ruff==0.16.6' -> 'ruff'"""
    return re.split(r"[\[<>=!~; ]", spec)[0].strip().lower().replace("_", "-")


results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）" if detail else label))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))
    except Exception as e:
        results.append((False, f"{label} —— 检查器自己撞到了异常：{type(e).__name__}: {e}"))


try:
    DATA = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
except Exception as e:
    print(f"✗ 读不了 pyproject.toml：{type(e).__name__}: {e}")
    print("\nDay 1 未过关")
    sys.exit(1)

DEV = {norm(s) for s in DATA.get("dependency-groups", {}).get("dev", [])}
EXTRA = sorted(DEV - BASELINE_DEV)


def need_q2() -> None:
    if not EXTRA:
        raise AssertionError(
            "dev 组还是原来的 pip + pytest，你没加任何东西。"
            "先做第 2 题：uv add --dev <你挑的包>"
        )


# ---- 1. 第 2 题：他自己声明了一个 dev 包 ----
def t_declared():
    need_q2()
    hit = [p for p in EXTRA if p in JUNK]
    assert not hit, f"你加的是实验残留 {hit}，换一个你真的会用的工具（第 2 题有三个候选）"
    assert len(EXTRA) <= 2, (
        f"dev 组多出来 {len(EXTRA)} 个包 {EXTRA}，契约只要求 1 个。"
        "多余的用 uv remove --dev <包> 清掉，不然你说不清每个包为什么在那儿"
    )
    return f"你自己声明的 dev 包：{EXTRA}"


# ---- 2. 它在 uv.lock 里：证明跑过 uv add，而不是手改 pyproject ----
def t_in_lock():
    need_q2()
    lock = (ROOT / "uv.lock").read_text(encoding="utf-8")
    missing = [p for p in EXTRA if f'name = "{p}"' not in lock]
    assert not missing, (
        f"{missing} 不在 uv.lock 里 —— 你手改了 pyproject.toml 而没跑 uv add。"
        f"改 lock 的是 uv add / uv lock，不是编辑器：uv add --dev {' '.join(EXTRA)}"
    )
    return f"{EXTRA} 都在 uv.lock 里"


# ---- 3. 它已导出到 requirements.txt：查的是你漏没漏这一步 ----
def t_exported():
    need_q2()
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    names = {norm(m.group(1)) for m in re.finditer(r"^([A-Za-z0-9_.\-]+)==", req, re.M)}
    missing = [p for p in EXTRA if p not in names]
    assert not missing, (
        f"{missing} 没进 requirements.txt —— 忘了重新导出："
        "uv export --no-hashes --all-groups -o requirements.txt"
    )
    return f"{EXTRA} 已导出（requirements.txt 共 {len(names)} 个包）"


# ---- 4. uv sync 不删它，而且它真的在 .venv 里 ----
def t_survives_sync():
    need_q2()
    out = run("uv", "sync")
    gone = [p for p in EXTRA if re.search(rf"\n\s+- {re.escape(p)}==", out, re.I)]
    assert not gone, (
        f"`uv sync` 把 {gone} 删了：说明它没进 lock。"
        f"看第 2 项为什么红，然后 uv add --dev {' '.join(EXTRA)}"
    )
    frozen = {norm(l) for l in run("uv", "pip", "freeze").splitlines() if "==" in l}
    absent = [p for p in EXTRA if p not in frozen]
    assert not absent, f"{absent} 不在 .venv 里（uv pip freeze 数不到它）"
    delta = len(frozen) - BASELINE_FROZEN
    note = (
        f"实装 {BASELINE_FROZEN} → {len(frozen)}，涨了 {delta} 个"
        if delta > 0
        else f"实装仍是 {len(frozen)} 个——它本来就是传递依赖，"
        "数字不变但责任变了，就是教案第六节那件事"
    )
    return f"sync 后 {EXTRA} 仍在；{note}"


# ---- 5. 卫生：没有实验残留，且环境自检仍全绿 ----
def t_clean():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    frozen = run("uv", "pip", "freeze").lower()

    problems = []
    for j in JUNK:
        if j in text:
            problems.append(f"{j} 还写在 pyproject.toml 里")
        if j in req:
            problems.append(f"{j} 还在 requirements.txt 里（重新 uv export 会冲掉）")
        if f"{j}==" in frozen:
            problems.append(f"{j} 还在 .venv 里：uv remove --dev {j}")
    assert not problems, "；".join(problems)

    out = run(sys.executable, "-m", "pytest", "-q")
    m = re.search(r"(\d+) passed", out)
    assert m and m.group(1) == "7", (
        f"tests/test_env.py 应为 7 passed，实际：{out.strip()[-160:]}。"
        "如果你 uv add 的包触发了一次重解析、升级了别的包，这就是教案第 4 题 B 说的那件事"
    )
    return "无实验残留，pytest 7 passed"


check("1. 第 2 题 · 你自己声明的 dev 包", t_declared)
check("2. 第 2 题 · 它在 uv.lock 里", t_in_lock)
check("3. 第 2 题 · 它已导出到 requirements.txt", t_exported)
check("4. 第 2 题 · uv sync 不删它", t_survives_sync)
check("5. 卫生 · 无残留且环境自检全绿", t_clean)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 4 项机器判不了，你自己批 ──")
print("  □ 第 1 题：说清了 109→108→106 是**两个原因**，不是三个数字")
print("  □ 第 3 题：说出「比数字只能证明没看出差别，比集合才能证明没差别」，")
print("           且 uvloop（你独有）和 colorama（他独有）方向没搞反")
print("  □ 第 4 题：三个事故各自先看第几层说对了；事故 C 的残留已清掉（第 5 项会替你盯）")
print("  □ 第 5 题：5 句话正面回答了他「我没动过任何东西」的疑惑，并且用上了那三个 npm 词")

print(f"\nDay 1 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，4 项需你自批")
sys.exit(0 if passed == len(results) else 1)
