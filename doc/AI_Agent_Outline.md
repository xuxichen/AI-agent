# 前端工程师转型 AI Agent 开发学习计划（4阶段 · 约6个月）

> **核心优势**：你已有的 Web 技术栈、API 调用经验和产品思维，是 AI Agent 工程化中极其稀缺的能力。AI Agent 本质上是一种**架构模式**（大脑 LLM + 工具 Tools + 记忆 Memory + 循环 Loop），与你熟悉的“前端写组件、管状态、调接口”心智模型相通。

---

## 阶段一：AI 基础与后端补齐（第 1-2 月）

> **目标**：打通 LLM 调用能力，补齐 Python 后端短板，能独立搭建带流式输出的 AI 对话服务。

### 核心学习内容

**1. Python 后端（2-3 周）**
- **异步编程**：`async/await` —— 处理 AI 流式输出的必备能力
- **Web 框架**：**FastAPI** —— 轻量级后端，对接 AI 接口首选
- **数据校验**：**Pydantic** —— 处理前端传参

**2. LLM 基础与 Prompt 工程（2-3 周）**
- 核心概念：Token、Temperature、Context Window
- Prompt Engineering：Few-shot、Chain of Thought (CoT)、ReAct 模式
- System Prompt：定义角色与行为边界
- Function Calling：让模型能调用外部工具

**3. RAG 检索增强生成（1-2 周）**
- Embedding（文本转向量）
- 向量数据库（Chroma 入门 → Pinecone/Milvus 进阶）
- Chunking（文本分片策略）
- Retrieval（检索策略优化）

### ✅ 阶段验收项目
**流式 AI 对话应用**：FastAPI + 大模型 API（OpenAI/DeepSeek）搭建支持 SSE 流式输出的服务，前端用 React/Vue 接入。

---

## 阶段二：Agent 核心能力（第 3-4 月）

> **目标**：掌握 Agent 的规划、工具调用、记忆等核心能力，能独立开发单 Agent 应用。

### 核心学习内容

**1. Agent 核心组件（2-3 周）**
- **Planner（规划器）** ：拆解复杂任务为可执行步骤
- **Tools（工具系统）** ：封装业务 API 为模型可调用的工具
- **Memory（记忆系统）** ：短期上下文 + 长期记忆（向量数据库 + RAG）
- **ReAct 循环**：“思考 → 行动 → 观察”的迭代推理模式

**2. 主流 Agent 框架（2-3 周）**
- **LangChain** —— 掌握 Chain、Tool、AgentExecutor 核心概念
- **LangGraph** —— 基于状态机的复杂任务编排
- **LlamaIndex** —— 专注 RAG 和数据索引
- **Dify / Coze** —— 低代码工作流平台，快速验证想法

### ✅ 阶段验收项目
**多功能助手 Agent**：聚合天气查询、汇率换算、待办管理等工具，Agent 能自动理解意图并调用对应工具。

---

## 阶段三：多 Agent 与工程化（第 5 月）

> **目标**：掌握多 Agent 协作模式和 AI 工程化能力，交付生产级应用。

### 核心学习内容

**1. 多 Agent 系统（2 周）**
- **协作模式**：Manager-Worker（管理者-工作者）、专家小组、Self-Refine
- **角色化协作**：如“写作者 + 审阅者”协同完成文档/代码
- **CrewAI 风格**：多角色 Agent 编排

**2. AI 工程化（2 周）**
- **API 服务化**：封装 Agent 为 REST API / WebSocket 服务
- **流式输出**：SSE / WebSocket + 前端打字机效果
- **可观测性**：日志、链路追踪、执行过程可视化
- **评估与测试**：LLM-as-Judge 评测、自动化测试
- **安全与权限**：API 鉴权、敏感操作审批

### ✅ 阶段验收项目
**个人知识问答 Agent**：基于你的笔记/文档构建 RAG 知识库，精准回答专业问题并标注信息来源。

---

## 阶段四：综合实战与交付（第 6 月）

> **目标**：独立完成完整的 AI Agent 产品，从前端到后端到部署上线。

### 核心学习内容

- **混合架构**：Node.js 构建产品层 + Python 处理 AI 核心层
- **前端 AI SDK**：Vercel AI SDK 等工具快速接入流式能力
- **部署运维**：容器化、监控、持续优化

### ✅ 最终项目
**完整 AI Agent 产品**（选题参考）：
- 自动化周报生成器
- 智能客服系统
- 代码审查助手
- 全链路：前端交互 → Agent 服务 → 工具集成 → 记忆系统 → 部署上线

---

## 推荐学习资源

| 类型 | 资源 | 说明 |
|------|------|------|
| **系统路线** | [fullstack-ai-agent-roadmap](https://github.com/Karovia/fullstack-ai-agent-roadmap) | 110 个教程、58 万字、400+ 项目 |
| **系统路线** | [ai-agent-startup](https://github.com/EldonZhao/ai-agent-startup) | 8 阶段循序渐进路线 |
| **课程示例** | [agent-study](https://github.com/Callous-0923/agent-study) | 37 章节、60+ 可运行示例 |
| **框架文档** | LangChain.js 中文文档 | 前端视角理解 LangChain 的最佳入口 |
| **API 文档** | OpenAI / DeepSeek API 文档 | 最权威的入门首选 |

---

## 学习建议

1. **每周一个小项目**：每个知识点都要动手验证，不要只看不写
2. **渐进式路径**：脚本 → 服务 → 框架 → 工程化，不跳过基础
3. **发挥前端优势**：流式交互、UI 呈现、产品化落地，是你比后端/算法同学更强的地方
4. **LangChain.js 可作为切入点**：先用熟悉的 TypeScript 理解 Agent 概念，再深入 Python 生态

> **最后叮嘱**：你的前端背景不是转型的包袱，而是**差异化的竞争力**——AI Agent 最终要落到界面上给人用，谁能把复杂的 Agent 能力封装成好用的产品，谁就掌握了话语权。加油！