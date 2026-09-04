"""Day 5 自动验收。跑法：

    uv run python stage1/day005_pydantic/check.py

它会 import 你的 models.py，检查三个模型的字段边界，并真的发请求看响应体。
"""

import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
TARGET = HERE / "models.py"

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
    print("\nDay 5 未过关：还没有可查的 models.py")
    sys.exit(1)

SRC = TARGET.read_text(encoding="utf-8")
# 不用 importlib：它会命中 __pycache__ 里的陈旧字节码。
# 同大小、同一秒内改写的文件会让 timestamp 校验通过，
# 结果就是 check.py 验的是上一版代码。直接编译源码文本最稳。
mod = types.ModuleType("day5_models")
mod.__file__ = str(TARGET)
try:
    exec(compile(SRC, str(TARGET), "exec"), mod.__dict__)
except Exception as e:
    print(f"✗ models.py 导入就炸了：{type(e).__name__}: {e}")
    print("\nDay 5 未过关：先把 import 错误修掉")
    sys.exit(1)

from fastapi.testclient import TestClient
from pydantic import BaseModel

for name in ("NoteIn", "Note", "NoteOut", "app"):
    if not hasattr(mod, name):
        print(f"✗ models.py 里缺 {name}")
        sys.exit(1)

NoteIn, Note, NoteOut, app = mod.NoteIn, mod.Note, mod.NoteOut, mod.app
client = TestClient(app)
PAYLOAD = {"title": "hi", "tags": ["a"]}


def fields_of(model) -> set[str]:
    assert issubclass(model, BaseModel), f"{model.__name__} 不是 BaseModel 子类"
    return set(model.model_fields)


# ---- 1. 三个模型的字段边界 ----
def t_shapes():
    a, b, c = fields_of(NoteIn), fields_of(Note), fields_of(NoteOut)
    assert a == {"title", "tags"}, f"NoteIn 应只有 title、tags，实际 {sorted(a)}"
    assert b == {"id", "title", "tags", "owner"}, f"Note 字段不对，实际 {sorted(b)}"
    assert c == {"id", "title", "tags"}, f"NoteOut 应只有 id、title、tags，实际 {sorted(c)}"
    return f"In={sorted(a)} Note={sorted(b)} Out={sorted(c)}"


# ---- 2. NoteIn 里没有 id（否则用户能覆盖别人的记录）----
def t_no_id_in_input():
    assert "id" not in fields_of(NoteIn), (
        "NoteIn 里有 id —— 用户就能自己指定 id，"
        "PUT 时直接覆盖别人的记录。id 必须由服务端生成"
    )
    assert "id" in fields_of(NoteOut), "NoteOut 里要有 id，前端需要它来做后续请求"
    return "id 只在出口出现，不在入口"


# ---- 3. owner 是内部字段，不在出口模型里 ----
def t_owner_hidden():
    assert Note.model_fields["owner"].default == "secret-owner", (
        "Note.owner 的默认值应为 'secret-owner'，check.py 靠它认字段"
    )
    assert "owner" not in fields_of(NoteOut), (
        "NoteOut 里有 owner —— 那就过滤不掉了，出口模型不能声明它"
    )
    return "owner 在 Note 里，不在 NoteOut 里"


# ---- 4. response_model 真的把 owner 过滤掉了 ----
def t_filtered():
    r = client.post("/notes", json=PAYLOAD)
    assert r.status_code == 200, f"POST /notes 应为 200，实际 {r.status_code}：{r.text[:120]}"
    body = r.json()
    assert set(body) == {"id", "title", "tags"}, (
        f"响应体应只有 id/title/tags，实际 {sorted(body)}。"
        "response_model=NoteOut 漏写了？"
    )
    assert "owner" not in body, f"owner 泄露了：{body}"
    return f"{body}（无 owner）"


# ---- 5. 对照组：不写 response_model 就会泄露 ----
def t_leaky():
    r = client.post("/notes/leaky", json=PAYLOAD)
    assert r.status_code == 200, f"POST /notes/leaky 应为 200，实际 {r.status_code}"
    body = r.json()
    assert body.get("owner") == "secret-owner", (
        f"对照组没泄露 owner，实际响应 {sorted(body)}。"
        "这个端点是故意不加 response_model 的，加了就看不到差别了"
    )
    return f"owner={body['owner']!r} 泄露出来了"


# ---- 6. NoteIn 的 Field 约束真的生效 ----
def t_constraints():
    empty = client.post("/notes", json={"title": "", "tags": []})
    assert empty.status_code == 422, f"title='' 应为 422，实际 {empty.status_code}"
    d = empty.json()["detail"][0]
    assert d["type"] == "string_too_short", f"应为 string_too_short，实际 {d['type']}"
    assert d["loc"] == ["body", "title"], f"loc 应为 ['body','title']，实际 {d['loc']}"

    long = client.post("/notes", json={"title": "x" * 51, "tags": []})
    assert long.status_code == 422, f"51 字符的 title 应为 422，实际 {long.status_code}"
    assert long.json()["detail"][0]["type"] == "string_too_long", "应为 string_too_long"

    ok = client.post("/notes", json={"title": "x" * 50, "tags": []})
    assert ok.status_code == 200, f"50 字符应该刚好通过，实际 {ok.status_code}"
    return "min_length=1 / max_length=50 边界都对"


# ---- 7. Pydantic 的可变默认值是隔离的 ----
def t_mutable_default():
    m1 = NoteIn(title="a")
    m2 = NoteIn(title="b")
    m1.tags.append("x")
    assert m2.tags == [], (
        f"两个 NoteIn 实例共享了 tags：{m1.tags} / {m2.tags}"
    )
    assert m1.tags is not m2.tags, "指向同一个 list 对象"
    assert NoteIn.model_fields["tags"].default == [], (
        "tags 的默认值应直接写成 []，Pydantic 会替你深拷贝，"
        "不需要 field(default_factory=list)"
    )
    return "写 [] 就隔离，Pydantic 每次实例化都深拷贝"


check("1. 三个模型的字段边界", t_shapes)
check("2. NoteIn 无 id", t_no_id_in_input)
check("3. owner 不在出口模型", t_owner_hidden)
check("4. response_model 过滤生效", t_filtered)
check("5. 对照组确实泄露", t_leaky)
check("6. Field 约束边界", t_constraints)
check("7. 可变默认值隔离", t_mutable_default)

passed = sum(1 for ok, _ in results if ok)
for ok, msg in results:
    print(f"{'✓' if ok else '✗'} {msg}")

print("\n── 以下 1 项机器判不了，你自己批 ──")
print("  □ 第 5 题：4 句话讲清为什么要 NoteIn / Note / NoteOut 三个模型")

print(f"\nDay 5 {'过关' if passed == len(results) else '未过关'}："
      f"{passed}/{len(results)} 项自动检查通过，1 项需你自批")
sys.exit(0 if passed == len(results) else 1)
