"""Day1 第 1 个 LangGraph：状态沿着图的节点流动，被逐步改写。

看不懂时的阅读顺序：先看 State（数据长什么样）→ 再看两个 step_ 函数（每步怎么改数据）
→ 最后看 builder 那几行（按什么顺序执行）。这三块是互相独立的。
"""

# TypedDict 用来"声明"一个 dict 有哪些键、各是什么类型。
# 它在运行时就是普通 dict，**不做校验**：类型传错不会在这里报错，而是等到某个节点
# 对它做运算时才炸 —— 实测把 count 传成字符串，TypeError 出现在下面 step_add_ten 的 +10 那一行。
# 想让状态在入口就被校验，得换成 pydantic BaseModel（大纲 U1-2 练这个）。
from typing import TypedDict

# StateGraph = 搭图用的构造器；START / END 是两个哨兵，代表图的入口和出口。
from langgraph.graph import END, START, StateGraph


# 状态（state）就是在整张图里流动的那一份数据：每个节点读它、改它、传给下一个节点。
class State(TypedDict):
    count: int          # 一个数字，被节点逐步计算
    log: list[str]      # 一串字符串，记录走过的节点名


# 节点就是一个普通 Python 函数：入参是当前状态，返回值是"我想改动哪些键"。
def step_double(state: State) -> State:
    # 只返回要改的键，不必返回整个 state —— LangGraph 会把它合并进状态。
    # 为什么写 state["log"] + ["double"]（造新 list）而不是 state["log"].append(...)（就地改）？
    # 实测：简单图里两者结果一样（并行 append 也不丢数据），但 append 是绕过图的更新机制在改对象：
    # 它会把你传给 invoke() 的那个 dict 也一并改脏，而 return {} 等于没向图提交任何更新。
    # 返回新 list 才是 LangGraph 期望的写法：改动通过返回值提交，才轮得到 reducer 去合并。
    return {"count": state["count"] * 2, "log": state["log"] + ["double"]}


def step_add_ten(state: State) -> State:
    # 和上面同理：+10，并往 log 里追加自己的名字。
    return {"count": state["count"] + 10, "log": state["log"] + ["add_ten"]}


# ---- 以下开始"搭图"。这几行的先后顺序不影响结果，搭完才 compile ----

builder = StateGraph(State)              # 告诉构造器：这张图的状态长 State 这个样子
builder.add_node("double", step_double)  # 注册节点；第一个参数是节点名，边靠这个名字指路
builder.add_node("add_ten", step_add_ten)
builder.add_edge(START, "double")        # 入口 → double
builder.add_edge("double", "add_ten")    # double → add_ten（add_edge 是固定顺序，没有条件）
builder.add_edge("add_ten", END)         # add_ten → 出口

# compile() 把"图纸"变成"可执行的图"。compile 之前 builder 上没有 invoke 方法，跑不起来。
graph = builder.compile()


# 只有直接运行本文件时才执行下面这段；被测试 import 时不会自动跑。
if __name__ == "__main__":
    # invoke = 从 START 一路跑到 END，返回最终状态。初始状态由你传进去。
    result = graph.invoke({"count": 3, "log": []})
    print("结果:", result)               # 预期 {'count': 16, 'log': ['double', 'add_ten']}
    # 3 →（double）× 2 = 6 →（add_ten）+ 10 = 16。执行顺序错了这个断言就会失败。
    assert result["count"] == 3 * 2 + 10, "图的执行顺序不符合预期"
    print("OK: langgraph 已跑通")        # tests/test_day1_graph.py 靠这行字判断脚本跑通了
