# 前端工程师转型 AI Agent 开发 · 156天逐日学习计划

> 本计划基于四阶段大纲拆解为 **156 个学习日**（约 6 个月），按 **工作日每天 2-3 小时、周末每天 4-5 小时** 设计[reference:0][reference:1]。每周留出 **1 天弹性缓冲** 用于复习、补进度或休息。每 **4 周** 设置一个 **项目周**，集中完成阶段验收项目[reference:2]。

---

## 阶段一：AI 基础与后端补齐（第 1-30 天）

> **目标**：打通 LLM 调用能力，补齐 Python 后端短板，能独立搭建带流式输出的 AI 对话服务[reference:3]。

### Week 1：Python 后端快速上手（Day 1-7）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 1** | Python 环境与基础复习 | 安装 Python 3.10+、虚拟环境 venv、pip 包管理[reference:4] | 搭建开发环境，写第一个 Python 脚本 |
| **Day 2** | Python 核心语法速通 | 数据类型、函数、类与对象、装饰器 | 用类封装一个简单的计算器 |
| **Day 3** | 异步编程入门 | `async/await` 语法、事件循环、`asyncio.gather`[reference:5] | 写一个并发请求多个 API 的脚本 |
| **Day 4** | FastAPI 基础 | 安装 FastAPI + Uvicorn，路由、路径参数、查询参数[reference:6] | 搭建第一个 GET/POST 接口 |
| **Day 5** | Pydantic 数据校验 | 请求体校验、响应模型、嵌套模型[reference:7] | 用 Pydantic 实现用户注册接口 |
| **Day 6** | FastAPI 进阶 | 依赖注入 `Depends()`、异常处理、中间件[reference:8] | 给接口加上日志中间件和全局异常处理 |
| **Day 7** | 复习与整合 | 回顾本周内容，整理代码模板 | 用 FastAPI 搭建一个完整的 RESTful CRUD 服务 |

### Week 2：LLM 基础与 Prompt 工程（Day 8-14）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 8** | LLM 核心概念 | Token、Temperature、Top-p、Context Window[reference:9] | 注册 OpenAI/DeepSeek API，获取 API Key |
| **Day 9** | 第一次 API 调用 | Chat Completion API 基础用法 | 用 Python 调用 API，实现一个简单的问答 |
| **Day 10** | 流式输出 | SSE 流式响应、`stream=True` 参数 | 实现打字机效果的流式输出 |
| **Day 11** | System Prompt 设计 | 角色定义、行为边界、输出格式控制[reference:10] | 设计一个“前端技术顾问”的 System Prompt |
| **Day 12** | Few-shot 与 CoT | Few-shot 示例、Chain of Thought 思维链[reference:11] | 用 Few-shot 让模型做数学推理 |
| **Day 13** | ReAct 模式入门 | ReAct（推理+行动）模式原理[reference:12] | 手写一个极简的 ReAct 循环（无框架） |
| **Day 14** | 复习与整合 | 整理 Prompt 模板库 | 用 FastAPI 封装一个可配置 System Prompt 的对话接口 |

### Week 3：RAG 检索增强生成（Day 15-21）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 15** | Embedding 基础 | 文本向量化原理、常用 Embedding 模型[reference:13] | 用 `sentence-transformers` 生成文本向量 |
| **Day 16** | 向量数据库入门 | Chroma 安装与基础操作（增删改查）[reference:14] | 向 Chroma 中存入 10 条文档向量 |
| **Day 17** | 相似度检索 | 余弦相似度、Top-K 检索[reference:15] | 实现“输入问题 → 检索最相似文档” |
| **Day 18** | Chunking 策略 | 文本分片策略、重叠窗口、按语义分块[reference:16] | 对一篇长文档实施不同的分片策略并比较效果 |
| **Day 19** | RAG 完整链路 | 检索 + 生成 全流程串联[reference:17] | 基于私有文档做 RAG 问答 |
| **Day 20** | RAG 优化技巧 | HyDE（假设性文档嵌入）、重排序（Rerank） | 对比有无 HyDE 的检索效果差异 |
| **Day 21** | 复习与整合 | 整理 RAG 代码模板 | 将 RAG 能力封装为 FastAPI 接口 |

### Week 4：阶段一项目冲刺（Day 22-30）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 22** | 项目架构设计 | 设计“流式 AI 对话应用”的技术架构 | 画架构图，确定技术选型 |
| **Day 23** | 后端核心开发 | FastAPI + 大模型 API 流式接口 | 实现 SSE 流式对话接口 |
| **Day 24** | RAG 模块集成 | 将 Week 3 的 RAG 能力接入对话接口 | 实现“文档上传 → 向量化 → RAG 问答” |
| **Day 25** | 前端接入 | 用 React/Vue 接入 SSE 流式接口[reference:18] | 实现前端打字机效果 + 对话界面 |
| **Day 26** | 联调与优化 | 前后端联调，处理边界情况 | 解决流式中断、超时等问题 |
| **Day 27** | 项目复盘与文档 | 写项目 README、整理踩坑记录 | 完成项目文档 |
| **Day 28** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 29** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 30** | 阶段总结 | 回顾阶段一所有知识点 | 输出学习笔记汇总 |

---

## 阶段二：Agent 核心能力（第 31-70 天）

> **目标**：掌握 Agent 的规划、工具调用、记忆等核心能力，能独立开发单 Agent 应用[reference:19]。

### Week 5-6：Agent 核心组件（Day 31-44）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 31** | Agent 架构总览 | Agent 四要素：大脑+工具+记忆+循环[reference:20] | 画出 Agent 架构图 |
| **Day 32** | Planner 规划器 | 任务拆解、Plan-and-Execute 模式[reference:21] | 手写一个任务分解器 |
| **Day 33** | Tools 工具系统（上） | 工具的定义、参数描述、注册机制[reference:22] | 封装一个“获取当前时间”的工具 |
| **Day 34** | Tools 工具系统（下） | 多工具注册、工具选择策略 | 封装“天气查询 + 汇率换算”两个工具 |
| **Day 35** | Memory 记忆系统 | 短期记忆（对话上下文）vs 长期记忆（向量库）[reference:23] | 实现带对话历史的 Agent |
| **Day 36** | ReAct 循环实现 | “思考→行动→观察”完整循环[reference:24] | 手写一个完整的 ReAct Agent（无框架） |
| **Day 37** | Agent 错误处理 | 工具调用失败、超时、重试机制 | 给 Agent 加上容错逻辑 |
| **Day 38** | LangChain 入门 | LangChain 核心概念：Model、Chain、Tool[reference:25] | 用 LangChain 实现第一个 LLM 调用 |
| **Day 39** | LangChain Chain | LCEL（LangChain 表达式语言）、串联多个组件[reference:26] | 用 LCEL 构建一个“问答+翻译”链 |
| **Day 40** | LangChain Tool | `@tool` 装饰器、Tool 注册与调用[reference:27] | 用 LangChain 封装 3 个工具并注册 |
| **Day 41** | LangChain Agent | `create_react_agent`、AgentExecutor[reference:28] | 用 LangChain 构建第一个 ReAct Agent |
| **Day 42** | LangGraph 入门 | 状态图（StateGraph）、节点与边[reference:29] | 用 LangGraph 实现一个两节点的简单流程 |
| **Day 43** | LangGraph Agent | 用 LangGraph 实现 ReAct Agent[reference:30] | 对比 LangChain Agent 和 LangGraph Agent |
| **Day 44** | 复习与整合 | 对比三种实现方式：手写 vs LangChain vs LangGraph | 整理 Agent 代码模板库 |

### Week 7-8：框架深入与实战（Day 45-58）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 45** | LlamaIndex 入门 | LlamaIndex 核心概念：Document、Index、Query Engine[reference:31] | 用 LlamaIndex 实现 RAG 问答 |
| **Day 46** | LlamaIndex Agent | LlamaIndex 的 Agent 实现方式 | 用 LlamaIndex 构建一个简单 Agent |
| **Day 47** | Dify 工作流 | Dify 低代码平台的基本使用[reference:32] | 在 Dify 上搭建一个 Agent 工作流 |
| **Day 48** | Coze 快速验证 | Coze  Bot 创建与发布[reference:33] | 在 Coze 上快速验证 Agent 想法 |
| **Day 49** | 工具设计最佳实践 | 工具描述怎么写模型才懂、参数设计原则 | 优化已有工具的描述 |
| **Day 50** | 多工具协同 | 一个任务调用多个工具的组合模式 | 实现“查询天气+推荐穿衣+记录待办”的组合 |
| **Day 51** | Agent 对话管理 | 多轮对话中的状态管理 | 实现带状态的对话 Agent |
| **Day 52** | 记忆持久化 | 用向量数据库实现长期记忆[reference:34] | Agent 重启后能记住之前的对话 |
| **Day 53** | 项目：多功能助手（上） | 需求分析、工具清单设计 | 确定“多功能助手”要集成的工具列表 |
| **Day 54** | 项目：多功能助手（中） | 各工具开发与注册 | 实现天气、汇率、待办等工具 |
| **Day 55** | 项目：多功能助手（下） | Agent 集成与测试 | 完成多功能助手 Agent |
| **Day 56** | 项目优化 | 意图识别准确率优化、响应速度优化 | 提升 Agent 的用户体验 |
| **Day 57** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 58** | 阶段总结 | 回顾 Agent 核心知识点 | 输出学习笔记汇总 |

### Week 9-10：阶段二项目冲刺（Day 59-70）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 59** | 项目选题与架构 | 确定“多功能助手 Agent”的完整架构 | 画架构图，技术选型 |
| **Day 60** | 后端服务搭建 | FastAPI + LangChain Agent 服务 | 搭建 Agent 后端服务骨架 |
| **Day 61** | 工具开发 | 至少 5 个实用工具（天气、汇率、待办、搜索、计算等） | 完成所有工具开发与测试 |
| **Day 62** | Agent 核心实现 | LangGraph/LangChain Agent 实现 | Agent 能正确选择并调用工具 |
| **Day 63** | 记忆系统集成 | 短期记忆 + 长期记忆 | Agent 支持多轮对话和跨会话记忆 |
| **Day 64** | 前端界面开发 | 对话界面 + 工具调用可视化 | 前端展示 Agent 的思考过程 |
| **Day 65** | 流式输出优化 | SSE 流式 + 前端打字机效果 | 完整体验流畅的流式对话 |
| **Day 66** | 联调与测试 | 端到端测试、边界情况处理 | 修复 Bug，优化体验 |
| **Day 67** | 项目文档 | README、架构说明、使用指南 | 完成项目文档 |
| **Day 68** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 69** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 70** | 阶段总结 | 回顾阶段二所有知识点 | 输出学习笔记汇总 |

---

## 阶段三：多 Agent 与工程化（第 71-110 天）

> **目标**：掌握多 Agent 协作模式和 AI 工程化能力，能交付生产级 Agent 应用[reference:35]。

### Week 11-12：多 Agent 系统（Day 71-84）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 71** | 多 Agent 架构概述 | 为什么需要多 Agent、常见协作模式[reference:36] | 画出多 Agent 架构图 |
| **Day 72** | Manager-Worker 模式 | 管理者分配任务、工作者执行[reference:37] | 实现“管理者分配 + 工作者执行”的简单demo |
| **Day 73** | 专家小组模式 | 多个专家 Agent 并行工作、汇总结果[reference:38] | 实现“三个专家分别分析再汇总” |
| **Day 74** | Self-Refine 模式 | Agent 自我反思与迭代改进[reference:39] | 实现“写代码 → 审查 → 修改”的循环 |
| **Day 75** | CrewAI 入门 | CrewAI 的核心概念：Agent、Task、Crew[reference:40] | 用 CrewAI 搭建第一个多 Agent 系统 |
| **Day 76** | CrewAI 实战 | 角色化多 Agent 协作 | 实现“研究员+写作者+审阅者”的文档协作 |
| **Day 77** | LangGraph 多 Agent | 用 LangGraph 实现多 Agent 状态机[reference:41] | 用 LangGraph 实现多 Agent 协作 |
| **Day 78** | 多 Agent 通信 | Agent 间的消息传递与同步 | 实现 Agent 间的信息共享 |
| **Day 79** | 多 Agent 任务分配 | 动态任务分配策略 | 实现根据任务复杂度动态分配 |
| **Day 80** | 多 Agent 冲突处理 | 结果冲突时的裁决机制 | 实现“投票”或“仲裁者”模式 |
| **Day 81** | 多 Agent 可观测性 | 多 Agent 执行过程的可视化追踪 | 记录每个 Agent 的思考与行动 |
| **Day 82** | 多 Agent 性能优化 | 并行执行、资源调度 | 优化多 Agent 系统的响应时间 |
| **Day 83** | 复习与整合 | 对比不同多 Agent 框架 | 整理多 Agent 代码模板 |
| **Day 84** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |

### Week 13-14：AI 工程化（Day 85-98）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 85** | API 服务化设计 | RESTful API 设计、版本管理[reference:42] | 设计 Agent 服务的 API 规范 |
| **Day 86** | WebSocket 集成 | WebSocket 双向通信、实时交互[reference:43] | 用 WebSocket 实现 Agent 实时交互 |
| **Day 87** | 流式输出深入 | SSE 高级用法、流式中断与恢复[reference:44] | 实现可中断的流式输出 |
| **Day 88** | 可观测性：日志 | 结构化日志、日志分级、日志聚合[reference:45] | 给 Agent 服务加上完善的日志 |
| **Day 89** | 可观测性：链路追踪 | 分布式追踪、Agent 执行链路[reference:46] | 用 OpenTelemetry 追踪 Agent 调用链 |
| **Day 90** | Agent 执行可视化 | 用前端展示 Agent 的思考过程[reference:47] | 实现“思考过程可视化”面板 |
| **Day 91** | LLM-as-Judge 评测 | 用 LLM 评估 Agent 输出质量[reference:48] | 构建自动化评测数据集 |
| **Day 92** | Agent 自动化测试 | 单元测试、集成测试、端到端测试[reference:49] | 为 Agent 服务编写测试用例 |
| **Day 93** | API 安全与鉴权 | API Key 认证、JWT、权限控制[reference:50] | 给 Agent API 加上认证 |
| **Day 94** | 敏感操作审批 | 高风险工具调用的人工审批流程[reference:51] | 实现“删除/修改”等操作的审批机制 |
| **Day 95** | 提示词版本管理 | Prompt 版本控制、A/B 测试[reference:52] | 搭建 Prompt 管理后台 |
| **Day 96** | 成本监控 | Token 用量统计、费用预警[reference:53] | 实现 Token 用量 Dashboard |
| **Day 97** | 复习与整合 | 整理工程化最佳实践 | 输出工程化 Checklist |
| **Day 98** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |

### Week 15-16：阶段三项目冲刺（Day 99-110）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 99** | 项目选题 | 确定“个人知识问答 Agent”的需求与范围 | 准备个人文档数据集（笔记/博客/代码） |
| **Day 100** | 数据预处理 | 文档清洗、Chunking、Embedding | 完成知识库的向量化 |
| **Day 101** | RAG 检索优化 | 多路召回、重排序、HyDE[reference:54] | 优化检索准确率 |
| **Day 102** | Agent 核心实现 | 基于 RAG 的问答 Agent | Agent 能基于知识库回答问题 |
| **Day 103** | 引用溯源 | 答案标注信息来源[reference:55] | 每个回答都附上引用来源 |
| **Day 104** | 多轮对话 | 上下文理解与追问能力 | 支持多轮对话和追问 |
| **Day 105** | 知识库管理 | 文档增删改、增量更新 | 实现知识库的 CRUD |
| **Day 106** | 前端界面 | 问答界面 + 引用展示 | 完成前端交互 |
| **Day 107** | 工程化完善 | 日志、监控、测试 | 完善生产级能力 |
| **Day 108** | 联调与部署 | 端到端测试、部署上线 | 将服务部署到云端 |
| **Day 109** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 110** | 阶段总结 | 回顾阶段三所有知识点 | 输出学习笔记汇总 |

---

## 阶段四：综合实战与交付（第 111-156 天）

> **目标**：独立完成一个完整的 AI Agent 产品，从前端界面到后端 Agent 到部署上线[reference:56]。

### Week 17-18：架构设计与核心开发（Day 111-124）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 111** | 产品选题与需求 | 确定最终项目选题（周报生成器/智能客服/代码助手等） | 撰写产品需求文档 |
| **Day 112** | 技术架构设计 | Node.js + Python 混合架构设计[reference:57] | 画完整架构图 |
| **Day 113** | 前端框架搭建 | Next.js/React + Vercel AI SDK[reference:58] | 搭建前端项目骨架 |
| **Day 114** | 前端 AI 能力接入 | Vercel AI SDK 流式接入[reference:59] | 实现前端流式对话组件 |
| **Day 115** | 后端服务搭建 | FastAPI + Agent 核心服务[reference:60] | 搭建 Python 后端服务骨架 |
| **Day 116** | Node.js 产品层 | BFF（Backend for Frontend）层 | Node.js 服务对接 Python Agent |
| **Day 117** | Agent 核心开发（上） | 根据项目需求设计 Agent 逻辑 | 完成 Agent 核心规划器 |
| **Day 118** | Agent 核心开发（下） | 工具集成与测试 | 完成所有工具开发 |
| **Day 119** | 记忆系统 | 短期+长期记忆完整实现 | Agent 支持个性化记忆 |
| **Day 120** | 多 Agent 协作（如需要） | 复杂任务的多 Agent 分工[reference:61] | 实现多 Agent 协作 |
| **Day 121** | 前端深度开发 | 界面完善、交互优化 | 完成前端所有页面 |
| **Day 122** | 前后端联调 | 端到端流程打通 | 完整体验产品流程 |
| **Day 123** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 124** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |

### Week 19-20：工程化与部署（Day 125-138）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 125** | Docker 容器化 | Dockerfile 编写、镜像构建[reference:62] | 将 Agent 服务容器化 |
| **Day 126** | Docker Compose | 多服务编排（前端+后端+向量数据库）[reference:63] | 用 Docker Compose 一键启动 |
| **Day 127** | 云端部署（上） | 云服务器选型、环境配置[reference:64] | 在云服务器上部署服务 |
| **Day 128** | 云端部署（下） | 域名、SSL、反向代理[reference:65] | 配置 Nginx + HTTPS |
| **Day 129** | CI/CD 流水线 | GitHub Actions 自动化部署[reference:66] | 实现 push 即部署 |
| **Day 130** | 监控与告警 | 服务监控、错误告警[reference:67] | 配置监控 Dashboard |
| **Day 131** | 性能压测 | 并发测试、响应时间优化[reference:68] | 优化服务性能 |
| **Day 132** | 成本优化 | Token 用量优化、缓存策略[reference:69] | 降低 API 调用成本 |
| **Day 133** | 用户测试 | 邀请真实用户试用 | 收集反馈 |
| **Day 134** | 迭代优化 | 根据反馈修复与改进 | 发布 v1.1 |
| **Day 135** | 项目文档 | 完整技术文档 + 用户手册 | 完成所有文档 |
| **Day 136** | 项目演示视频 | 录制产品演示 | 制作 3 分钟演示视频 |
| **Day 137** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 138** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |

### Week 21-22：复盘与总结（Day 139-156）

| 天数 | 学习主题 | 具体内容 | 实操任务 |
|------|---------|---------|---------|
| **Day 139** | 知识体系梳理 | 画出完整知识图谱 | 用思维导图整理所有知识点 |
| **Day 140** | 代码仓库整理 | 所有项目代码规范化 | 整理 GitHub 仓库 |
| **Day 141** | 学习笔记汇总 | 整理 140 天的学习笔记 | 输出完整的学习笔记文档 |
| **Day 142** | 博客文章撰写（上） | 写一篇转型经验分享 | 发布到技术社区 |
| **Day 143** | 博客文章撰写（下） | 写一篇技术深度文章 | 发布到技术社区 |
| **Day 144** | 简历与作品集更新 | 更新简历中的 AI Agent 项目 | 准备求职作品集 |
| **Day 145** | 面试准备（上） | AI Agent 常见面试题整理 | 准备技术面试 |
| **Day 146** | 面试准备（下） | 模拟面试 | 找朋友模拟面试 |
| **Day 147** | 开源贡献 | 给 LangChain/LangGraph 提 Issue/PR | 参与开源社区 |
| **Day 148** | 持续学习规划 | 制定后续学习方向（MCP、微调等）[reference:70] | 输出后续学习计划 |
| **Day 149** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 150** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 151** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 152** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 153** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 154** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 155** | 弹性缓冲 | 复习薄弱环节 / 休息 | — |
| **Day 156** | 🎉 毕业 | 庆祝完成 6 个月的学习旅程！ | 复盘与展望 |

---

## 学习资源速查

| 类型 | 推荐资源 |
|------|---------|
| **Python 后端** | FastAPI 官方文档、Pydantic 官方文档 |
| **LLM 基础** | OpenAI/DeepSeek API 文档、Prompt Engineering Guide |
| **RAG** | LangChain RAG 教程、LlamaIndex 文档 |
| **Agent 框架** | LangChain 文档、LangGraph 文档、CrewAI 文档 |
| **工程化** | Docker 官方文档、GitHub Actions 文档 |
| **前端 AI** | Vercel AI SDK 文档 |

---

## 每日学习时间建议

| 时间段 | 内容 | 时长 |
|--------|------|------|
| 早晨 | 复习前一天内容 | 30 分钟[reference:71] |
| 上午 | 学习新知识（看文档/教程） | 60-90 分钟[reference:72] |
| 下午 | 动手实践写代码 | 60-90 分钟[reference:73] |
| 晚上 | 记录学习笔记 | 15 分钟[reference:74] |

> **最后叮嘱**：计划是死的，人是活的。遇到卡点不要硬撑，可以调整节奏。**关键是每天都有代码产出**，而不是只看不写。你的前端背景是差异化竞争力——把 Agent 的复杂能力封装成好用的产品，就是你最大的价值。加油！🚀