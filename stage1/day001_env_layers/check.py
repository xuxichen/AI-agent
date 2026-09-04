"""Day 1 自动验收。跑法（在仓库任意位置都行）：

    uv run python stage1/day001_env_layers/check.py

只检查机器能判真伪的部分；第 4、5 题是文字题，末尾列出来让你自批。
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(*cmd: str) -> str:
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.stdout + r.stderr


results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）"))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))


# ---- 1. 三层声明完好，且第 3 题的实验残留已清理 ----
def t_pyproject():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    runtime_part = text.split("[dependency-groups]")[0]
    runtime = len(re.findall(r'^    "', runtime_part, re.M))
    assert runtime == 8, f"运行依赖应为 8 个，实际 {runtime}"
    assert "httpx>=" in runtime_part, "httpx 必须显式声明（Day 3 要用，不能靠 langsmith 拖进来）"
    dev = text.split("[dependency-groups]")[1]
    assert "pip>=" in dev and "pytest>=" in dev, "dev 组应含 pip 与 pytest"
    assert "cowsay" not in text, "第 3 题的 cowsay 没清理干净：uv remove --dev cowsay"
    return "8 运行 + 2 dev，httpx 已声明，无 cowsay 残留"


# ---- 2. lock 与实装的数字对得上（109 / 106）----
def t_numbers():
    sync = run("uv", "sync")
    resolved = re.search(r"Resolved (\d+) packages", sync)
    assert resolved, f"uv sync 输出异常：{sync[:120]}"
    assert resolved.group(1) == "109", f"Resolved 应为 109，实际 {resolved.group(1)}"
    frozen = [l for l in run("uv", "pip", "freeze").splitlines() if "==" in l]
    assert len(frozen) == 106, f"实装应为 106 个，实际 {len(frozen)}"
    assert not any("cowsay" in l for l in frozen), "cowsay 还在环境里，清理掉"
    return "Resolved 109 / 实装 106"


# ---- 3. requirements.txt 是 lock 的忠实导出（第 6 题的实验残留已恢复）----
def t_requirements():
    req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert "this-package-does-not-exist" not in req, (
        "第 6 题的实验行还在，跑：uv export --no-hashes --all-groups -o requirements.txt"
    )
    names = {m.group(1) for m in re.finditer(r"^([a-z0-9_.\-]+)==", req, re.M)}
    assert len(names) == 108, f"导出应列出 108 个包，实际 {len(names)}"
    run("uv", "export", "--no-hashes", "--all-groups", "-o", "requirements.txt")
    again = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    assert again == req, "requirements.txt 与 lock 失配，已为你重新导出"
    return "108 个包，重复导出无差异"


# ---- 4. 环境自检仍然全绿 ----
def t_env_tests():
    out = run("uv", "run", "pytest", "-q")
    m = re.search(r"(\d+) passed", out)
    assert m and m.group(1) == "7", f"tests/test_env.py 应为 7 passed，实际：{out.strip()[-80:]}"
    return "7 passed"


check("1. pyproject 三层声明", t_pyproject)
check("2. lock 与实装数字", t_numbers)
check("3. requirements.txt 同步", t_requirements)
check("4. 环境自检", t_env_tests)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 2 项机器判不了，你自己批 ──")
print("  □ 第 4 题：Node 对照 6 组齐全，且 `uv sync` 对到 `npm ci`（不是 `npm install`）")
print("  □ 第 5 题：5 个未装的包 + 各自最早需要的天数（Day 15 / 38 / 45 / 75 / 93）")

print(f"\nDay 1 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，2 项需你自批")
sys.exit(0 if passed == len(results) else 1)
