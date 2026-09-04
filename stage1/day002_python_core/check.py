"""Day 2 自动验收。跑法：

    uv run python stage1/day002_python_core/check.py

先按 01_作业.md 第 1 题抄一份「故意错的」calculator.py —— 那时这里应该报 3 个 ✗。
"""

import ast
import inspect
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "calculator.py"
METHODS = ("add", "sub", "mul")

results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）" if detail else label))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))
    except Exception as e:
        results.append((False, f"{label} —— 出了意外：{type(e).__name__}: {e}"))


def load_module():
    if not TARGET.exists():
        raise AssertionError(
            f"没找到 {TARGET.relative_to(HERE.parent.parent)}。"
            "先按 01_作业.md 第 1 题抄一份「故意错的」，让这里红起来。"
        )
    source = TARGET.read_text(encoding="utf-8")
    # 不用 importlib：它会命中 __pycache__ 里的陈旧字节码。
    # 同大小、同一秒内改写的文件会让 timestamp 校验通过，
    # 结果就是 check.py 验的是上一版代码。直接编译源码文本最稳。
    mod = types.ModuleType("day2_calculator")
    mod.__file__ = str(TARGET)
    try:
        exec(compile(source, str(TARGET), "exec"), mod.__dict__)
    except Exception as e:
        raise AssertionError(f"calculator.py 导入就炸了：{type(e).__name__}: {e}")
    if not hasattr(mod, "Calculator"):
        raise AssertionError("calculator.py 里必须有 class Calculator")
    return mod


try:
    mod = load_module()
except AssertionError as e:
    print(f"✗ {e}\n\nDay 2 未过关：还没有可查的 calculator.py")
    sys.exit(1)

C = mod.Calculator
SRC = TARGET.read_text(encoding="utf-8")
TREE = ast.parse(SRC)


# ---- 1. 三个方法算得对，且各记一条 history ----
def t_methods():
    try:
        c = C("probe")
    except TypeError as e:
        raise AssertionError(f"构造器要能接一个 name：Calculator('probe') —— {e}")
    for m, args, want in (("add", (2, 3), 5), ("sub", (9, 4), 5), ("mul", (6, 7), 42)):
        fn = getattr(c, m, None)
        assert callable(fn), f"缺方法 {m}(a, b)"
        got = fn(*args)
        assert got == want, f"{m}{args} 应返回 {want}，实际 {got!r}"
    assert len(c.history) == 3, f"三次调用应记 3 条 history，实际 {len(c.history)} 条"
    for text, nums in zip(c.history, (("2", "3"), ("9", "4"), ("6", "7"))):
        assert all(n in str(text) for n in nums), (
            f"history 记录 {text!r} 里看不出操作数 {nums}，"
            '写成 f"add({a}, {b}) = {r}" 这样'
        )
    return "add/sub/mul 正确，各记 1 条"


# ---- 2. 全文件没有可变默认参数 ----
def t_no_mutable_defaults():
    bad = []
    for node in ast.walk(TREE):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d]
        for d in defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                bad.append(f"{node.name}() 第 {d.lineno} 行")
    assert not bad, (
        "用了可变默认值：" + "、".join(bad) + "。改成 x=None，函数体内 if x is None: x = []"
    )
    return "AST 扫描：0 处"


# ---- 3. history 不是类属性 ----
def t_history_not_class_attr():
    assert "history" not in C.__dict__, (
        "history 写在了类体里（class Calculator: history = []），"
        "所有实例共享同一个列表。挪进 __init__：self.history = []"
    )
    shared = [k for k, v in vars(C).items() if isinstance(v, (list, dict, set))]
    assert not shared, f"类体里还有可变对象 {shared}，同样会被所有实例共享"
    return "类体干净"


# ---- 4. 两个实例互不污染 ----
def t_isolated():
    c1, c2 = C("a"), C("b")
    c1.add(1, 1)
    c1.add(2, 2)
    assert len(c1.history) == 2, f"c1 应有 2 条，实际 {len(c1.history)}"
    assert c2.history == [], (
        f"c2 被 c1 污染了：{c2.history}。"
        "这就是第 3 项那个类属性 bug 的后果"
    )
    assert c1.history is not c2.history, "两个实例指向同一个 list 对象"
    return "c1 记 2 条，c2 仍是 []"


# ---- 5. total 用 None 哨兵 ----
def t_total():
    assert hasattr(mod, "total"), "缺模块级函数 total(nums=None)"
    sig = inspect.signature(mod.total)
    p = sig.parameters.get("nums")
    assert p is not None, "total 的参数名应为 nums"
    assert p.default is None, (
        f"total 的默认值应为 None（哨兵），实际是 {p.default!r}"
    )
    assert mod.total([1, 2, 3]) == 6, "total([1,2,3]) 应为 6"
    for _ in range(3):
        assert mod.total() == 0, "total() 反复调用结果变了 —— 哨兵没生效"
    return "None 哨兵 + 三次空调用不累积"


# ---- 6. 装饰器：至少用一个，且不吃掉 __name__ ----
def t_decorator():
    cls = next((n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == "Calculator"), None)
    assert cls, "找不到 class Calculator"
    deco = [m.name for m in cls.body if isinstance(m, ast.FunctionDef) and m.decorator_list]
    assert deco, (
        "Calculator 里没有任何方法被套上装饰器。"
        "第 2 题要求：自己写一个 logged，至少套一个方法"
    )
    for name in METHODS:
        fn = getattr(C, name, None)
        if fn is None:
            continue
        assert fn.__name__ == name, (
            f"{name}.__name__ 是 {fn.__name__!r}，你的装饰器吃掉了名字。"
            "在内层函数上加 @functools.wraps(fn)"
        )
    return f"已装饰 {deco}，__name__ 全部保留"


check("1. add/sub/mul 与 history", t_methods)
check("2. 没有可变默认参数", t_no_mutable_defaults)
check("3. history 不是类属性", t_history_not_class_attr)
check("4. 两个实例互不污染", t_isolated)
check("5. total 用 None 哨兵", t_total)
check("6. 装饰器没吃掉名字", t_decorator)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 1 项机器判不了，你自己批 ──")
print("  □ 第 5 题：4 句话讲清「Python 类体 ≈ JS static」，含实例字段的写法")

print(f"\nDay 2 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，1 项需你自批")
sys.exit(0 if passed == len(results) else 1)
