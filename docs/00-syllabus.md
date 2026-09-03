# LangGraph / AI Agent 学习大纲（任务驱动版）

配套：[`01-capstone.md`](01-capstone.md)（结业项目需求：多来源研究 Agent）· [`atguigu-env.md`](atguigu-env.md)（环境与依赖）
教材：尚硅谷 LangGraph 教程，第 00–05 章，视频 P1–P132，78 个 notebook。

## 怎么用这份大纲

**编号读法**：每个任务单元写成 `U{章号}-{章内序号}`。`U0-4` = 第 00 章第 4 个单元（装依赖），
`U1-5` = 第 01 章第 5 个单元（第一个调模型的节点）。全文共定义 **35 个单元**（U0-1、U0-2 已完成，剩 **33 个待做**）。其他文档（如结业需求）引用时也用这套编号。

每个**任务单元**四件事，按顺序做，不许跳：

1. **先读"今日问题"** —— 不要先看代码。拿张纸写下你现在的答案（错的也行）。
2. **实现"你要写出来的东西"** —— 写在 `dayN/NN_name.py`，**不要打开教程 notebook 抄**。
3. **跑验收** —— `uv run pytest tests/test_dayN.py -k <单元名>` 必须绿。
4. **费曼回写** —— 把开头那张纸上的答案改对，用 3 句话讲给一个不懂 LangGraph 的人（或写进代码注释）。讲不顺就回到第 2 步。

作业规则沿用你既有的偏好：**每单元 5–6 道，难度高于本单元，附答案要点供自批**。
本文件把第 01 章的作业完整写出来作为样板；02–05 章的作业模板相同，开学时逐章生成。

前提假设（若不符请告诉我，我重排行程）：

- 每天可投入 **2 小时**（1 小时实现 + 1 小时作业与费曼回写）
- 已有 `DEEPSEEK_API_KEY`（第 01 章 U1-5 起需要，约 5 分钟申请，新用户送的额度足够全程）
- Python 语法不是障碍（你有 10 年编程经验），**卡点会集中在"状态合并语义"和"控制流"上**

## 目录与命名约定

```
day1/  01_graph.py … 10_message_llm.py     ← 第 01 章，每个 notebook 对应一个你的 .py
day2/  …                                   ← 第 02 章
tests/ test_day1.py …                      ← 每章一个测试文件，按单元名断言
```

教程载体是 `.ipynb`（章节内 78 本，共 143 个 code cell、**0 个 markdown cell**，平均每本 1.83 格），本大纲一律要求你产出 `.py`。

看图的拓扑用下面三种，优先级从高到低（都已在 langgraph 1.2.11 实测）：

| 做法 | 依赖 | 联网 | 说明 |
|---|---|---|---|
| `get_graph().draw_mermaid()` | 无 | 否 | 返回 mermaid 文本，存成 `.mmd` 本地预览。**默认用这个** |
| `get_graph().draw_ascii()` | 需 `uv add grandalf` | 否 | 终端直接看；节点一多会挤，且不装会 `ImportError` |
| `get_graph().draw_mermaid_png()` | `requests`（环境里已有） | **是** | `graph_mermaid.py:423` 默认端点 `https://mermaid.ink`，会把你的图定义发出去。学习期别用 |

---

# 第 00 章 · 环境配置（P1–P7）

> 你已经做完了，而且做得比教程要求的多（uv 替代 conda）。跳过视频，只做 U0-3。

- **U0-1 环境隔离**：✅ 已完成（Python 3.13 + uv + `.venv`）
- **U0-2 conda → uv 迁移**：✅ 已完成，见 `atguigu-env.md`
- **U0-3 密钥通路**（15 分钟）
  - 今日问题：为什么 `load_dotenv(override=True)` 里的 `override=True` 不是多余的？
  - 你要写出：`cp .env.example .env` 填入 key；`day0/00_check_key.py` 打印 `DEEPSEEK_API_KEY` 是否已加载（**打印是否存在，绝不打印值**）
  - 验收：删掉 `.env` 后脚本给出可读的错误提示而不是 `NoneType` 崩溃
- **U0-4 装齐第 01 章的包**（20 分钟）
  - 今日问题：为什么 `uv add` 之前要先跑一次 `--dry-run`？解析结果里你最该盯住的是哪个包？
  - 你要写出：
    ```bash
    uv add --dry-run langchain langchain-core langchain-deepseek python-dotenv loguru
    # 人工确认 langgraph 仍是 1.2.11（没被降级），再去掉 --dry-run 真装
    uv add langchain langchain-core langchain-deepseek python-dotenv loguru
    ```
  - 验收：`uv run pytest -q` 仍为 3 passed；`uv pip show langgraph` 版本仍是 **1.2.11**
  - 坑：不要在这一步跑 `uv sync`，它会把不在 lock 里的包（包括 pip）卸掉；需要时用 `uv sync --inexact`
  - 不装 jupyter：理由与实测数字见 [`atguigu-env.md`](atguigu-env.md) 第 3 节

---

# 第 01 章 · LangGraph 基础入门（P8–P27）

**一级知识**：图 = 状态 + 节点 + 边。**二级知识**：状态容器选型、reducer 合并语义、节点输入输出契约、消息类型、首次接 LLM。
本章是整个课程的地基，**后面所有 bug 的 60% 根源在这里**（状态没合并对）。

### U1-1 图的骨架（对应 `01_graph`、`09_state`）

- 今日问题：`builder.compile()` 之前和之后，你手上分别是什么东西？为什么少了 compile 就不能 invoke？
- 你要写出：一个三节点线性图 `START → a → b → END`，状态为 `TypedDict`，两个节点各写一个键
- 验收：`graph.invoke({...})` 返回结果含两个节点写入的键；`draw_mermaid()` 输出里能看到 3 个节点

### U1-2 状态的三种容器（对应 `02_dataclass`、`03_pydantic`）

- 今日问题：`TypedDict` / `dataclass` / `pydantic BaseModel` 做状态，行为差异出现在**校验**还是**合并**上？
- 你要写出：同一个图，分别用三种容器实现，然后**故意传一个错字段**，记录三者各自的报错文字
- 验收：你能用 3 句话说出「什么时候必须用 pydantic」

### U1-3 reducer：本章最重要（对应 `04_reducer`、`05_addmessage`、`07_node_overwrite`）

- 今日问题：两个节点都写 `state["log"]`，为什么默认结果是覆盖而不是追加？`operator.add` 解决了什么、又制造了什么新问题？
- 你要写出：同一个图两版，A 版无 reducer（观察覆盖），B 版 `Annotated[list, operator.add]`（观察追加）
- 验收：A 版 `log` 长度 = 1，B 版 = 2，且你能解释为什么

### U1-4 节点的输入输出契约（对应 `06_node_state`、`08_node_state`）

- 今日问题：节点函数 `return` 整个 state 和只 `return` 改动的键，效果一样吗？如果节点不 return 会怎样？
- 你要写出：三个节点分别用「返回全量」「返回增量」「返回 `{}`」三种写法，比较最终状态
- 验收：你能说出「返回部分状态」为什么是 LangGraph 而不是普通函数调用的关键差异

### U1-5 消息与第一个 LLM 节点（对应 `10_message_llm`）

- 今日问题：`HumanMessage` / `AIMessage` / `SystemMessage` 的区别在**内容**还是**角色字段**？为什么 LangGraph 里聊天历史必须用 message 而不是 str？
- 你要写出：第一个真调模型的节点 —— `ChatDeepSeek(model="deepseek-v4-flash")`，把回答以 `AIMessage` 追加进状态
- 验收：连续两次 invoke，第二次能"看到"第一轮的对话（这一步还没真记忆，你要在报告里写清楚你观察到了什么、为什么）

### 第 01 章作业（样板：完整写出，含答案要点）

1. `graph.invoke({"count": 3})` 与 `graph.invoke({"count": 3}, config={"configurable": {}})` 结果相同吗？空 config 会改变什么？
   *要点：相同；config 影响运行期行为（thread_id、可中断点），本章尚未使用。*
2. 一个节点返回 `{"log": ["x"]}`，另一个节点返回 `{"log": ["y"]}`，无 reducer 时最终 `log` 是什么？如果执行顺序不确定，你会看到什么现象？
   *要点：只剩后写入的那个；顺序不定时结果不可复现 —— 这正是并行分支必须配 reducer 的原因。*
3. 把 `Annotated[int, operator.add]` 用在初值为 `0` 的键上，两个节点各返回 `{"n": 1}`，最终 `n` = ?如果忘了给初值会怎样？
   *要点：2；无初值时首次合并会拿 `None + 1` 报错。*
4. 为什么 `StateGraph(State)` 传的是类型而不是实例？如果传实例会发生什么？
   *要点：图需要 schema 来建 channel；实例会被当成初始值或被拒 —— 观察实际报错。*
5. 【难度↑】用 pydantic `BaseModel` 做状态，写一个字段校验（`ge=0`），让某个节点返回负数。报错发生在**节点内**还是**合并进 state 时**？
   *要点：合并/校验阶段，不在节点函数体内 —— 因此 traceback 里会看到 langgraph 的帧。*
6. 【难度↑】把本章你的三容器版本各跑 50 次，量一下 invoke 耗时差异。pydantic 版的开销来自哪里？
   *要点：字段校验开销；结论应是"状态字段多、变更频繁时用 TypedDict，需要边界防御时用 pydantic"。*

**闭卷检验**：合上所有资料，20 分钟内从零写出「两个节点并行写同一个 list 键、结果必须保留两条」的图。写不出来就不要进第 02 章。

---

# 第 02 章 · 控制流与节点执行（P28–P55，17 个 notebook）

**一级知识**：边决定执行顺序，分四类：固定边 / 条件边 / 动态派生 / 循环。**二级知识**：`Command`、`Send`、fan-in 汇聚语义、循环退出、retry 与 cache。

| 单元 | 覆盖 notebook | 今日问题 | 你要写出的功能 | 验收 |
|---|---|---|---|---|
| U2-1 边与路由 | `01_edge` `03_route` `05_route2` | 条件边函数返回的是**节点名**还是**布尔**？返回 `END` 意味着什么？ | 一个"数字>0 走正分支、否则走 END"的图 | 两条路径各跑通一次，`draw_mermaid()` 能看到分支 |
| U2-2 path_map | `04_path_map` `06_path_map2` | 既然路由函数能直接返回名字，为什么还要 `path_map`？ | 把 U2-1 改成字典映射版 | 传一个不在映射表里的返回值，报错信息你能看懂 |
| U2-3 并行与 fan-in | `02_parallel` `10_fan_in_and` | 两个并行节点都写同一个键、没有 reducer，是报错还是静默覆盖？ | 三节点扇出、一个节点汇聚 | 汇聚节点拿到全部三份结果 |
| U2-4 动态扇出 map-reduce | `07_defer` `08_Dynamic_send` `11_mapreduce` | `Send` 和固定边在执行图上有什么区别？子任务数量运行期才知道怎么办？ | 输入一个列表，动态为每个元素派一个节点实例，再汇总 | 输入长度 3 和长度 7 都能正确处理，无手写 if |
| U2-5 Command 与控制转移 | `09_command` `13_loop_goto` `14_remaining_steps` | `Command(goto=..., update=...)` 一条语句干了几件事？节点返回 Command 后还需要边吗？ | 用 Command 实现 U2-1 的同一逻辑 | 图里没有任何 `add_conditional_edges` |
| U2-6 循环与退出 | `12_static_loop` `15_end_loop` | 循环怎么终止？没有退出条件会发生什么（不是死循环，具体报错）？ | 一个"反复改写直到结果含关键词"的重试环，上限 3 次 | 上限触发时能拿到部分结果而不是异常 |
| U2-7 韧性：retry / cache | `16_retry` `17_cache` | retry 配在节点上还是边上？缓存键由什么决定？ | 一个会随机失败的节点，配 `RetryPolicy`；另一版配缓存 | 关掉随机失败源后仍观察到重试；同输入第二次调用不发请求 |

**⚠️ 教程已知坑**：`13_loop_goto.ipynb` 里有 `from sympy.codegen.cnodes import goto`、`09_fork.ipynb` 里有 `from pikepdf._core import Annotation`，都是 IDE 自动补全事故。**抄到这两行直接删**，不要装 sympy / pikepdf。

**闭卷检验**：给一个"批量抓 5 个 URL、每个失败重试 2 次、最后汇总"的需求，30 分钟从零写出来，必须用到动态扇出 + retry。

---

# 第 03 章 · 持久化与记忆管理（P56–P83，11 个 notebook）

**一级知识**：checkpoint 让图可暂停、可回放、可分叉；`thread_id` 是记忆的边界。**二级知识**：后端选型（内存/SQLite/Postgres）、state 历史、store 与 checkpoint 的区别、上下文窗口裁剪。

| 单元 | 覆盖 notebook | 今日问题 | 你要写出的功能 | 验收 |
|---|---|---|---|---|
| U3-1 三级后端 | `01_in_memory` `02_in_SQL` `03_in_pgSQL` | 换后端要改几行代码？内存版重启后丢的是什么、SQLite 版留在磁盘上的是什么文件？ | 同一个对话图分别用三种 checkpointer 跑通 | `ls` 能看到 `.sqlite` 文件；pg 版若无本地库，写出你跳过的理由 |
| U3-2 thread 边界 | `04_history_state` | 换 `thread_id` 会看到什么？同 id 第三次 invoke 时 `state.values` 有几条历史？ | 两个 thread 交叉对话，各自打印历史 | 两条历史的消息互不污染 |
| U3-3 调试与回放 | `05_error` `06_find_error` `07_fix_error` `08_replay` | 图跑到第 3 个节点炸了，怎么在不重跑前 2 个节点的前提下复现？ | 制造一个坏节点，用 checkpoint 定位并回放 | 复现时**没有**重复消耗 LLM 调用（用日志证明） |
| U3-4 分叉 fork | `09_fork` | 从历史某一步重新走另一条路，原历史会被改吗？ | 在同一 thread 上 fork 出两个不同分支 | 两个分支并存，`get_state_history` 都能看到 |
| U3-5 store vs checkpoint | `10_store` | 跨 thread 也要记住的东西（用户偏好）该放 checkpoint 还是 store？ | 用 store 存一个偏好，第二个 thread 读出来 | 换一个全新 `thread_id` 仍能读到 |
| U3-6 上下文裁剪 | `11_context` | 20 轮对话后 token 爆了，删消息还是总结？两种做法各自丢什么？ | 加一个"只保留最近 N 条 + 一条摘要"的处理 | 第 30 轮仍能答对第 2 轮的事实（或明确说明丢了什么） |

**闭卷检验**：不看资料，写出"同一个用户第二个 thread 记得第一个 thread 的偏好"的最小实现。这题同时考 U3-2 和 U3-5。

---

# 第 04 章 · 中断、人工介入与工具（P84–P106，17 个 notebook）

**一级知识**：Agent 的可靠性来自**工具契约**和**人工闸门**，不来自模型更聪明。**二级知识**：`interrupt`、HITL 审批/编辑/拒绝、tool calling、ToolNode、中断后的恢复。

| 单元 | 覆盖 notebook | 今日问题 | 你要写出的功能 | 验收 |
|---|---|---|---|---|
| U4-1 静态中断 | `10_static_interrupt` `11_static_parallel` `12_error_static` | 中断点能放在边中间吗？并行节点里中断会发生什么？ | 在某个节点前 interrupt，恢复后继续 | 中断时进程能退出，重启后凭 thread_id 续跑 |
| U4-2 HITL 三态 | `01_HITL` `03_approve` `04_approve_edit` | approve / edit / reject 三种人工响应，分别要改状态的哪一部分？ | 一个"草稿 → 人工审批 → 可编辑 → 定稿"的环 | 三条分支各跑通；edit 分支能证明原文被替换 |
| U4-3 工具调用底层 | `13_tool_call` `16_wrap_tool_call` `17_warp_tool_call_cache` | 模型是"执行了工具"还是"输出了想调工具的意图"？ | 手写一次 tool schema → 模型返回 tool_calls → 你自己执行 → 回填 | 你能打印出 `tool_calls` 原始结构并解释每个字段 |
| U4-4 ToolNode | `14_tool_node` `15_tool_node_runtime` | `ToolNode` 帮你省掉了哪三步？运行时注入依赖怎么做？ | 用 `ToolNode` 重写 U4-3，功能等价 | 代码行数减少且测试仍绿 |
| U4-5 工具级审批 | `05_tool_approve` `06_single_node` | 为什么"每次调工具都要人确认"在生产上是错的？怎么只卡危险工具？ | 3 个工具里只给"写操作"那个加审批 | 只读工具不中断，写工具中断 |
| U4-6 中断 + checkpoint | `07_HITL_checkpoint` `08_parallel_checkpoint` `09_half_checkpoint` | 中断后为什么必须能持久化？内存 checkpointer 够吗？ | U4-2 配 SQLite checkpointer，跨进程完成一次审批 | 杀掉进程重启后仍能 approve 并跑完 |

**闭卷检验**：设计"AI 生成的 SQL 必须人工确认才执行"的图，说出中断点、状态里存什么、拒绝后走哪。

---

# 第 05 章 · 高级特性：流式与子图（P107–P132，23 个 notebook）

**一级知识**：多 Agent 协作 = 图套图 + 编排模式；流式是体验问题不是功能问题。**二级知识**：stream mode、子图状态共享、五种 Agent 设计模式。

| 单元 | 覆盖 notebook | 今日问题 | 你要写出的功能 | 验收 |
|---|---|---|---|---|
| U5-1 流式四种 | `01_values` `02_messages` `03_checkpoints` `04_custom` | `values` / `messages` / `updates` / `custom` 各自适合给谁看（终端用户？调试台？） | 同一个图分别用四种 mode 流式输出 | 你能指出哪种适合打字机效果、哪种适合进度条 |
| U5-2 事件流 | `05_asteam_events` | `astream_events` 比 `astream` 多了什么？为什么前端要它？ | 一个 async 版，打印节点开始/结束/LLM token 三类事件 | 事件类型和出现时机你能对上号 |
| U5-3 子图三种接法 | `06`–`11` `12_more_subgraph` `13_more_subgraph_nodes` | 子图当"函数调用"、当"节点"、当"带自己 checkpointer 的图"，状态怎么传？ | 把一个 U2-4 的 map-reduce 改造成子图 | 父子图共享键 / 私有键行为差异被你在测试里钉住 |
| U5-4 无状态子图与流穿透 | `14_subgraph_stateless` `15_subgraph_stream` `16_subgraph_llm_stream` | 子图的 token 能不能直接流到最外层？ | 外层能看到内层 LLM 的逐字输出 | 不靠 hack 事件遍历实现 |
| U5-5 子图间控制转移 | `17_subgraph_goto` | 子图里能不能 `goto` 到父图的节点？边界在哪？ | 一个子图跳回父图某节点的例子 | 你能画出完整拓扑 |
| U5-6 **五种 Agent 模式** | `18_prompt_chaining` `19_Parallelization` `20_router` `21_Orchestrator_worker` `22_evaluator_optimizer` | 这五种模式分别解决什么**模型能力不足**的问题？ | 每种模式各写一个最小可跑实现（不许合并成一个） | 5 个测试；能说清 router 与 orchestrator 的区别 |
| U5-7 Agent 收口 | `23_agent` | `create_react_agent` 帮你搭的是上面哪一种？拆开看还剩什么？ | 先用 prebuilt 版，再手写一个等价版 | 两版在同一输入上行为一致，且你能指出差异 |

**闭卷检验（第 05 章即结业）**：完成 `01-capstone.md`。

---

# 进度与节奏建议

| 阶段 | 内容 | 建议时长 | 完成标志 |
|---|---|---|---|
| 地基 | 第 00 章 U0-3 + 第 01 章 | 4 天 | U1 闭卷通过 |
| 控制流 | 第 02 章 | 5 天 | U2 闭卷通过 |
| 记忆 | 第 03 章 | 4 天 | 跨进程审批的前置能力就绪 |
| 人机与工具 | 第 04 章 | 5 天 | U4 闭卷通过（本章最贴生产） |
| 多 Agent | 第 05 章 | 6 天 | 五种模式各自实现 |
| **结业** | `01-capstone.md`（多来源研究 Agent） | 8–11 天 | 见那份文档里的入门判定表 |

合计约 **5–6 周**（每天 2 小时）。**这个节奏是可以拉的**：如果你某天只做了实现没做作业，不要欠着，砍掉单元数量而不是砍验收。
