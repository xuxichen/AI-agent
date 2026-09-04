"""Day 2 自动验收。跑法（仓库根目录）：

    uv run python stage1/day002_python_core/check.py

它读你的 calculator.py：先用 AST 查写法，再 exec 进来查运行时行为。
calculator.py 不存在时 6 项全红——你不写文件它是过不了的。

注意：这里不用 importlib，直接编译源码文本。importlib 会命中 __pycache__ 里
的陈旧字节码，让你改错了却看到绿灯（我踩过，两版文件大小相同、同一秒写入，
timestamp 校验直接放过）。
"""

import ast
import dataclasses
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "calculator.py"

results: list[tuple[bool, str]] = []


def check(label: str, fn) -> None:
    try:
        detail = fn()
        results.append((True, f"{label}（{detail}）" if detail else label))
    except AssertionError as e:
        results.append((False, f"{label} —— {e}"))
    except Exception as e:
        results.append((False, f"{label} —— 检查器撞到了异常：{type(e).__name__}: {e}"))


if not TARGET.exists():
    print(f"✗ 找不到 {TARGET.relative_to(ROOT)}")
    print("  先做作业第 6 题：在 stage1/day002_python_core/ 下建 calculator.py")
    print("\nDay 2 未过关：0/6")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
try:
    TREE = ast.parse(SRC)
except SyntaxError as e:
    print(f"✗ calculator.py 有语法错误：第 {e.lineno} 行 {e.msg}")
    print("\nDay 2 未过关")
    sys.exit(1)

mod = types.ModuleType("day2_calculator")
mod.__file__ = str(TARGET)
try:
    exec(compile(SRC, str(TARGET), "exec"), mod.__dict__)
except Exception as e:
    print(f"✗ calculator.py 导入阶段就炸了：{type(e).__name__}: {e}")
    print("  注意 `if __name__ == '__main__'` 里的代码不会执行，所以炸的一定是顶层语句")
    print("\nDay 2 未过关")
    sys.exit(1)

FUNCS = {n.name: n for n in ast.walk(TREE) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
CLASSES = {n.name: n for n in ast.walk(TREE) if isinstance(n, ast.ClassDef)}
MUTABLE = (ast.List, ast.Dict, ast.Set)


# ---- 1. 没有任何函数用可变对象当默认值 ----
def t_no_mutable_default():
    bad = []
    for f in FUNCS.values():
        for d in list(f.args.defaults) + [x for x in f.args.kw_defaults if x]:
            if isinstance(d, MUTABLE):
                bad.append(f"{f.name}() 第 {d.lineno} 行")
            if isinstance(d, ast.Call) and getattr(d.func, "id", "") in {"list", "dict", "set"}:
                bad.append(f"{f.name}() 第 {d.lineno} 行")
    assert not bad, (
        f"可变默认值 {bad}。默认值只在 def 那一行求值一次，"
        "改成 None 哨兵：def f(x, acc=None) 然后 if acc is None: acc = []"
    )
    assert "running_total" in FUNCS, "还没写 running_total（作业第 6 题要求 1）"
    defaults = [ast.unparse(d) for d in FUNCS["running_total"].args.defaults]
    return f"零个可变默认值；running_total 的默认值是 {defaults}"


# ---- 2. Calculator 的历史记录不能是类属性 ----
def t_no_mutable_class_attr():
    assert "Calculator" in CLASSES, "还没写 class Calculator（作业第 6 题要求 2）"
    bad = []
    for st in CLASSES["Calculator"].body:
        if isinstance(st, ast.Assign) and isinstance(st.value, MUTABLE):
            names = ",".join(ast.unparse(t) for t in st.targets)
            bad.append(f"第 {st.lineno} 行 {names} = {ast.unparse(st.value)}")
        if isinstance(st, ast.AnnAssign) and isinstance(st.value, MUTABLE):
            bad.append(f"第 {st.lineno} 行 {ast.unparse(st.target)}: ... = {ast.unparse(st.value)}")
    assert not bad, (
        f"Calculator 类体里有裸的可变类属性：{bad}。"
        "类体只执行一次，那个列表会被所有实例共享。搬到 __init__ 里 self.history = []"
    )
    return "类体里没有 = [] 这种写法"


# ---- 3. 两个计算器真的隔离 ----
def t_instances_isolated():
    assert hasattr(mod, "Calculator"), "Calculator 没定义"
    c1, c2 = mod.Calculator(), mod.Calculator()
    assert hasattr(c1, "history"), "Calculator 实例上找不到 history 属性"
    c1.add(5)
    assert c2.history == [], (
        f"只给 c1 加了一次数，c2.history 就成了 {c2.history}。"
        "别人的数据出现在你的对象里 —— 这是类属性共享，见教案第四节"
    )
    assert c1.history is not c2.history, "c1.history 和 c2.history 是同一个列表对象"
    return f"c1.history={c1.history} 而 c2.history={c2.history}"


# ---- 4. 端到端算式与契约一致 ----
def t_arithmetic():
    c = mod.Calculator()
    r1, r2 = c.add(5), c.sub(2)
    assert (r1, r2) == (5, 3), (
        f"add(5) 应返回 5、sub(2) 应返回 3，实际 ({r1}, {r2})。"
        "方法要把「算完之后的当前值」return 出来"
    )
    assert c.history == [5, 3], (
        f"history 应是 [5, 3]（每次操作后的当前值），实际 {c.history}"
    )
    assert mod.running_total([1, 2, 3]) == [1, 3, 6], "running_total 要返回累计和"
    again = mod.running_total([9])
    assert again == [9], (
        f"running_total([9]) 应返回 [9]，实际 {again}。"
        "如果它是 [1,3,6,15]，说明你上一次的列表还活着 —— 就是第 1 项那个坑"
    )
    return "add/sub 与 history、running_total 两次调用都独立"


# ---- 5. 装饰器存在，而且没吃掉名字 ----
def t_decorator_keeps_name():
    c = mod.Calculator()
    assert c.add.__name__ == "add", (
        f"Calculator.add 的名字变成了 {c.add.__name__!r} —— 你的装饰器把它吃了。"
        "在内层函数上面加一行 @functools.wraps(fn)"
    )
    used = set()
    for f in FUNCS.values():
        for d in f.decorator_list:
            used.add(ast.unparse(d))
    mine = {n for n in used if n in FUNCS}
    assert mine, (
        f"没有你自己的装饰器被用上（现有装饰器：{sorted(used) or '无'}）。"
        "作业第 6 题要求 3：写一个 log_call 并 @ 在 add 或 sub 上"
    )
    body = ast.unparse(FUNCS[next(iter(mine))])
    assert "wraps" in body, f"装饰器 {sorted(mine)} 里没有 functools.wraps"
    return f"装饰器 {sorted(mine)} 存在，且 __name__ 保住了"


# ---- 6. dataclass 的可变字段用 default_factory ----
def t_dataclass_factory():
    candidates = [
        name
        for name, cls in vars(mod).items()
        if isinstance(cls, type) and hasattr(cls, "__dataclass_fields__")
    ]
    assert candidates, "文件里没有任何 @dataclass（作业第 6 题要求 4）"
    checked = []
    for name in candidates:
        cls = getattr(mod, name)
        # default_factory 没设时是 dataclasses.MISSING，不是 None——这是最常写错的地方
        factories = [
            f for f, m in cls.__dataclass_fields__.items()
            if m.default_factory is not dataclasses.MISSING
        ]
        if not factories:
            continue
        try:
            a, b = cls(), cls()
        except TypeError as e:
            raise AssertionError(f"{name}() 构造不出来：{e}。有默认值的字段要放在没默认值的后面") from None
        for f in factories:
            va = getattr(a, f)
            if not isinstance(va, list):
                continue
            va.append("x")
            assert getattr(b, f) == [], (
                f"{name}.{f} 被两个实例共享了：{getattr(b, f)}。"
                "要用 field(default_factory=list)，不是 = []"
            )
            checked.append(f"{name}.{f}")
    assert checked, f"有 dataclass {candidates}，但没有一个用 default_factory 的可变字段"
    return f"隔离正常：{checked}"


check("1. 写法 · 没有可变默认参数", t_no_mutable_default)
check("2. 写法 · 没有可变类属性", t_no_mutable_class_attr)
check("3. 行为 · 两个计算器互不污染", t_instances_isolated)
check("4. 行为 · 端到端算式与契约一致", t_arithmetic)
check("5. 行为 · 装饰器没吃掉函数名", t_decorator_keeps_name)
check("6. 行为 · dataclass 用 default_factory", t_dataclass_factory)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 3 项机器判不了，你自己批 ──")
print("  □ 第 2 题：你真的先猜了再看输出，而且猜错了至少一次")
print("  □ 第 3 题：一句话能说清「Python 和 JS 的默认值分别在哪一刻求值」")
print("  □ 第 5 题：写出了 __name__ 变成 inner 的那一行，并且用 wraps 修回去了")

print(f"\nDay 2 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，3 项需你自批")
sys.exit(0 if passed == len(results) else 1)
