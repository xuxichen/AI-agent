"""Day1 第 1 个 LangGraph：状态沿着图的节点流动，被逐步改写。"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    count: int
    log: list[str]


def step_double(state: State) -> State:
    return {"count": state["count"] * 2, "log": state["log"] + ["double"]}


def step_add_ten(state: State) -> State:
    return {"count": state["count"] + 10, "log": state["log"] + ["add_ten"]}


builder = StateGraph(State)
builder.add_node("double", step_double)
builder.add_node("add_ten", step_add_ten)
builder.add_edge(START, "double")
builder.add_edge("double", "add_ten")
builder.add_edge("add_ten", END)

graph = builder.compile()

if __name__ == "__main__":
    result = graph.invoke({"count": 3, "log": []})
    print("结果:", result)
    assert result["count"] == 3 * 2 + 10, "图的执行顺序不符合预期"
    print("OK: langgraph 已跑通")
