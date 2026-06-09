# HR 智能招聘平台

> 基于 Dify + FastAPI + Vue3 的智能招聘辅助平台，覆盖「招人 → 面人」全链路。

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4-4FC08D?logo=vue.js)](https://vuejs.org/)
[![Dify](https://img.shields.io/badge/AI%E5%BC%95%E6%93%8E-Dify-6366F1)](https://dify.ai/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql)](https://www.mysql.com/)

---

## 项目定位与薪资参考

### 项目级别

| 维度 | 评级 | 说明 |
|------|------|------|
| 工程完整度 | ⭐⭐⭐⭐ | 前后端 + AI 引擎 + DB 全链路，有测试用例 |
| 技术深度 | ⭐⭐⭐ | LLM 应用层深度足够，未涉及 RAG/Agent/微调 |
| 业务复杂度 | ⭐⭐⭐⭐ | 四个检测维度设计合理，场景覆盖全面 |
| 独立完成难度 | 中高级（P5-P6） | 需具备全栈能力 + LLM 应用设计思维 |

> **定位**：一份有工程厚度的中级项目，适合放在简历第 2-3 位，不适合作为唯一亮点。

### 薪资基准（2025 年中国市场）

以下为**能独立设计并完成本项目的工程师**的市场薪资参考：

| 城市等级 | 月薪范围（税前） | 说明 |
|----------|:---------------:|------|
| 一线（北上广深） | 18K - 30K | 3-5 年经验，全栈 + LLM 应用方向 |
| 新一线（杭州/成都/武汉等） | 15K - 25K | 同上 |
| 二线 | 12K - 20K | — |

> **注意**：
> - 如果只实现了 Dify 工作流（无前后端），属于 LLM 应用开发方向，参考 15K-22K
> - 如果只实现了前后端（不碰 Dify/Prompt），属于常规全栈，参考 12K-18K
> - **本项目是全链路（前端 + 后端 + Dify AI），应走全栈 + LLM 应用复合方向，溢价 20-30%**

### 面试定位建议

| 面试重点 | 怎么讲 |
|----------|--------|
| **问题定义** | "多轮面试评分口径不统一，我拆了四个检测维度：偏差、证据、追问、冲突" |
| **设计决策** | "偏差阈值用 1.5 分而非'差 1 级'，因为 3→4 和 4→5 含义不同" |
| **工程落地** | "不是 Dify Demo——前端 Vue3 提交 → FastAPI 异步调 Dify → streaming 防超时 → 入库 → 轮询展示" |
| **避免说的** | 不要说"课程项目"——说"调研业界方案后用 Dify 实现" |

---

## 目录

- [项目背景](#项目背景)
- [功能概览](#功能概览)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [Dify 工作流搭建](#dify-工作流搭建)
- [API 文档](#api-文档)
- [测试](#测试)
- [常见问题](#常见问题)
- [后续计划](#后续计划)

---

## 项目背景

在企业招聘中，HR 和面试官面临两个核心痛点：

| 环节 | 痛点 | 解决方案 |
|------|------|----------|
| **筛选简历** | 海量简历人工筛选耗时、标准不统一、容易遗漏风险信号 | 候选人匹配筛查 — 自动校验硬性条件、技能匹配度打分、风险识别 |
| **多轮面试** | 不同面试官评分口径不统一，评价主观，难以横向比较 | 面试一致性评估 — 检测评分偏差、证据充分性、追问遗漏、结论冲突 |

本平台通过 LLM 对 JD/简历/面试记录进行结构化解析和多维度分析，辅助 HR 做出更客观、可追溯的招聘决策。

---

## 功能概览

### 模块一：候选人匹配筛查

```
简历 + JD → 硬性条件校验 → 技能匹配打分 → 风险识别 → 综合报告
```

- **硬性条件校验**：学历、专业、工作年限、必备技能逐项对比，输出达标/不达标/存疑
- **技能匹配打分**：必备技能、加分项、行业经验、项目复杂度、职级 5 维度 0-5 评分
- **风险识别**：跳槽频率、经验断层、行业不匹配、职级倒挂、技能退化、项目注水、大厂依赖 7 类风险
- **综合报告**：呈现实力的 Markdown 报告，含行动建议和面试追问方向

### 模块二：面试一致性评估

```
能力模型 + 多轮面试记录 → 偏差检测 → 证据检查 → 追问遗漏 → 冲突分析 → 综合报告
```

- **评分偏差检测**：同维度跨轮对比，分差 ≥1.5 标记严重偏差，1.0~1.5 标记轻微偏差
- **证据充分性检查**：逐项检查评分是否有具体事例/数据支撑，空洞评分标记不足
- **追问遗漏检测**：识别候选人回答模糊/回避时面试官未追问的情况
- **结论冲突检测**：A 说录用 B 说淘汰、结论一致但理由相反、初终面评分级差过大
- **综合报告**：含评分矩阵、分差标注、证据质量评级、补充面试建议

### 模块三：数据概览 Dashboard（新增）

```
首页 Dashboard → GET /api/v1/dashboard/stats → 聚合统计 → ECharts 可视化
```

- **统计卡片**：匹配筛查总数、面试评估总数、平均匹配分、累计评估量
- **状态分布**：匹配评估和面试评估的状态分布（已完成 / 处理中 / 失败）环形饼图
- **一致性分布**：面试结论一致性等级（一致 / 基本一致 / 存在分歧 / 严重分歧）饼图
- **月度趋势**：近 6 个月匹配筛查和面试评估的月度增量折线图
- 数据来源自 MySQL 聚合查询，无需调用 Dify，页面秒开

---

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    前端 (Vue3 + Element Plus)         │
│  localhost:3000                                      │
│  Dashboard / CandidateMatch / InterviewEval /         │
│  History / Report                                     │
│  输入模式：文本粘贴 / 文件上传                          │
│  结果获取：提交 → 轮询状态 → 展示报告                   │
└──────────────┬──────────────────────────────────────┘
               │ REST API (axios, /api/v1/*)
┌──────────────▼──────────────────────────────────────┐
│                 后端 (FastAPI, localhost:18000)        │
│  /match/evaluate       /interview/evaluate           │
│  /match/evaluate/upload /interview/evaluate/upload   │
│  /match/reports         /interview/reports            │
│  /match/reports/{id}    /interview/reports/{id}       │
│  /dashboard/stats  ← 统计 API（新增）                  │
│                                                       │
│  BackgroundTasks → 异步调用 Dify → 结果解析 → 入库     │
└──────────────┬──────────────────────────────────────┘
               │ HTTP (Dify Workflow API)
┌──────────────▼──────────────────────────────────────┐
│                Dify 工作流（AI 引擎）                  │
│  ┌──────────────────┐  ┌──────────────────────┐      │
│  │ 候选人匹配筛查      │  │ 面试一致性评估          │      │
│  │ blocking mode     │  │ streaming mode        │      │
│  │ 7 个 LLM/代码节点  │  │ 8 个 LLM/代码节点      │      │
│  └──────────────────┘  └──────────────────────┘      │
└──────────────┬──────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────┐
│                   MySQL (hr_platform)                 │
│  match_reports  /  interview_reports                  │
│  ──────────────────────────────────                  │
│  评估历史可追溯，报告可回溯                             │
└─────────────────────────────────────────────────────┘
```

**设计决策**：

- 候选人匹配用 **blocking mode**（节点少、耗时可控），面试评估用 **streaming mode**（节点多、上下文长、防网关超时）
- 两层结构化：第一层 LLM 解析自然语言 → JSON，第二层 LLM 分析 JSON → 检测结果，第三层 LLM 汇总 → Markdown 报告
- 不依赖预定义题库——能力模型和追问检测均由 LLM 根据内容动态判断

---

## 技术栈

| 层 | 技术 | 说明 |
|------|------|------|
| AI 引擎 | [Dify](https://dify.ai/) | 工作流编排、Prompt 管理、API 发布 |
| 后端 | Python 3.12 + FastAPI | REST API、BackgroundTasks、SQLAlchemy ORM |
| 前端 | Vue 3.4 + Element Plus 2.8 | SPA、ECharts 可视化、marked 渲染 Markdown |
| 数据库 | MySQL 8.0 + PyMySQL | 评估报告持久化、历史回溯 |
| 构建工具 | Vite 5.4 | 前端构建与开发代理 |

---

## 项目结构

```
combat_HR/
├── backend/                         # 后端
│   ├── app/
│   │   ├── main.py                  # FastAPI 入口，路由注册
│   │   ├── config.py                # 配置（DB、Dify、文件上传）
│   │   ├── api/
│   │   │   ├── match.py             # 候选人匹配 REST API
│   │   │   ├── interview.py         # 面试评估 REST API
│   │   │   └── dashboard.py         # 数据概览统计 API（新增）
│   │   ├── models/
│   │   │   ├── database.py          # SQLAlchemy 引擎、会话、基类
│   │   │   ├── match_report.py      # 候选人匹配报告 ORM
│   │   │   └── interview_report.py  # 面试评估报告 ORM
│   │   ├── schemas/
│   │   │   ├── common.py            # 通用 Schema（TaskResponse）
│   │   │   ├── match.py             # 匹配请求/响应 Schema
│   │   │   ├── interview.py         # 面试请求/响应 Schema
│   │   │   └── dashboard.py         # Dashboard 统计 Schema（新增）
│   │   └── services/
│   │       ├── dify_client.py       # Dify API 封装（blocking + streaming）
│   │       ├── match_service.py     # 匹配结果解析 + 后台任务
│   │       ├── interview_service.py # 面试结果解析 + 后台任务
│   │       └── file_service.py      # 文件上传/读取
│   ├── .env                         # 环境变量（需自行创建）
│   ├── requirements.txt
│   └── uploads/                     # 上传文件存储
├── frontend/                        # 前端
│   ├── src/
│   │   ├── main.js                  # Vue 入口
│   │   ├── App.vue                  # 根组件
│   │   ├── router/index.js          # 路由配置
│   │   ├── api/
│   │   │   ├── index.js             # axios 实例
│   │   │   ├── match.js             # 匹配 API 封装
│   │   │   ├── interview.js         # 面试 API 封装
│   │   │   └── dashboard.js         # 数据概览 API（新增）
│   │   └── views/
│   │       ├── CandidateMatch.vue   # 候选人匹配页
│   │       ├── MatchReportDetail.vue # 匹配报告详情页
│   │       ├── InterviewEval.vue    # 面试评估页
│   │       ├── InterviewReportDetail.vue # 评估报告详情页
│   │       ├── History.vue          # 历史记录页
│   │       └── Dashboard.vue        # 数据概览首页（新增）
│   ├── vite.config.js
│   └── package.json
├── testdata/                        # 测试数据
│   ├── ability.txt                  # 能力模型示例
│   ├── JDtest1.txt                  # JD 示例
│   ├── CVtest1.txt / CVtest2.txt    # 简历示例
│   ├── interview.txt                # 一致性面试示例
│   ├── interview2.txt / interview3.txt  # 偏差/证据不足面试示例
│   └── 面试一致性评估_测试用例.md      # 4 组完整测试用例 + 预期结果
├── Dify工作流搭建指南.md              # Dify 工作流详细搭建文档
├── 项目进度报告.md                    # 开发进度说明
└── test_dify_interview.py           # Dify 直连测试脚本
```

---

## 快速开始

### 前置条件

- Python 3.12+
- Node.js 18+
- MySQL 8.0+
- Dify 账号（云版 [cloud.dify.ai](https://cloud.dify.ai) 或私有部署）

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd combat_HR
```

### 2. 搭建 Dify 工作流

在 Dify 平台创建两个应用（详细配置见 [Dify工作流搭建指南.md](Dify工作流搭建指南.md)）：

| 工作流 | 类型 | 模式 |
|--------|------|------|
| 候选人匹配筛查 | 工作流 | blocking |
| 面试一致性评估 | 工作流 | streaming |

发布后在「API 访问」页获取 `workflow_id` 和 `api_key`。

### 3. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cp .env.example .env  # 如无 .env.example，手动创建
```

**backend/.env** 配置示例：

```env
# 数据库
DB_URL=mysql+pymysql://atguigu:***@localhost:3306/hr_platform?charset=utf8mb4

# Dify API（两个工作流各自独立 Key）
DIFY_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY_MATCH=app-xxxxxxxxxxxxx
DIFY_API_KEY_INTERVIEW=app-xxxxxxxxxxxxx
DIFY_WORKFLOW_MATCH=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
DIFY_WORKFLOW_INTERVIEW=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

### 4. 创建数据库

> **Windows 用户**：如果 MySQL80 服务未启动，先用管理员权限打开终端，执行 `net start MySQL80`。

```sql
CREATE DATABASE hr_platform DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

服务启动后会自动建表（`init_db()` 通过 `Base.metadata.create_all`）。

### 5. 启动后端

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 18000 --reload
```

> **Windows 用户注意**：如果报错 `[WinError 10013]`（端口被占用/保留），说明该端口在 Windows 动态端口范围内。换一个高端口（如 18000、19000），并同步修改 `frontend/vite.config.js` 里的 proxy target。

访问 http://localhost:18000/docs 查看 Swagger API 文档。

### 6. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000。前端通过 Vite 代理将 `/api` 转发到 `localhost:18000`。

### 7. 服务端口与启动方式速查

| 服务 | 端口 | 启动方式 | 验证 |
|------|:----:|----------|------|
| MySQL | 3306 | `net start MySQL80`（管理员终端） | `mysql -u atguigu -p` |
| 后端 (FastAPI) | 18000 | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 18000 --reload` | http://localhost:18000/health |
| 前端 (Vue3) | 3000 | `cd frontend && npm run dev` | http://localhost:3000 |

> **启动顺序**：MySQL → 后端 → 前端。后端依赖 MySQL（启动时自动建表），前端通过 Vite 代理依赖后端。

---

## Dify 工作流搭建

详见 [Dify工作流搭建指南.md](Dify工作流搭建指南.md)，包含：

- 每个节点的完整 System Prompt + User Prompt
- 所有 JSON 输出 Schema
- 节点连线图
- 代码节点 Python 脚本
- 变量名对照速查表（确保与后端代码严格对应）
- `curl` 测试命令
- 常见问题 FAQ

**工作流1 — 候选人匹配筛查**（7 节点）：

```
开始 → 简历结构化提取 → JD结构化提取 ──→ 硬性条件校验
                                    ├──→ 技能匹配打分 → 提取分数
                                    └──→ 风险点识别
                                              └──→ 综合报告生成 → 结束
```

**工作流2 — 面试一致性评估**（8 节点）：

```
开始 → 能力模型解析 → 面试记录解析 ──→ 评分偏差检测
                                    ├──→ 证据充分性检查
                                    ├──→ 追问遗漏检测
                                    └──→ 结论冲突检测 → 提取一致性等级
                                              └──→ 一致性报告生成 → 结束
```

---

## API 文档

启动后端后访问 http://localhost:18000/docs 查看交互式 Swagger 文档。

### 数据概览 Dashboard（新增）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/dashboard/stats` | 获取首页聚合统计数据 |

**响应示例**：

```json
{
  "match": {
    "total": 32, "done": 28, "processing": 2, "failed": 2,
    "avg_score": 3.8
  },
  "interview": {
    "total": 18, "done": 15, "processing": 1, "failed": 2,
    "consensus_一致": 10, "consensus_基本一致": 3, "consensus_存在分歧": 1, "consensus_严重分歧": 1
  },
  "monthly_trend": [
    {"month": "2026-04", "match_count": 8, "interview_count": 4},
    {"month": "2026-05", "match_count": 12, "interview_count": 6},
    {"month": "2026-06", "match_count": 10, "interview_count": 5}
  ]
}
```

> 该接口直接从 MySQL 聚合查询（`GROUP BY` + `COUNT` / `AVG`），不经过 Dify，响应毫秒级。

### 候选人匹配筛查

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/match/evaluate` | 提交匹配评估（JSON 模式） |
| POST | `/api/v1/match/evaluate/upload` | 提交匹配评估（文件上传） |
| GET | `/api/v1/match/reports` | 查询历史列表（分页） |
| GET | `/api/v1/match/reports/{id}` | 查询单份报告详情 |

**提交匹配评估（JSON）**：

```json
{
  "candidate_name": "张三",
  "job_title": "高级Java开发工程师",
  "resume_text": "张三，本科计算机科学，5年Java开发经验...",
  "jd_text": "高级Java开发，要求本科以上，5年经验..."
}
```

**响应**：

```json
{
  "task_id": 42,
  "status": "PROCESSING"
}
```

前端轮询 `/match/reports/{task_id}` 直到 `status != "PROCESSING"`。

### 面试一致性评估

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/interview/evaluate` | 提交面试评估（JSON 模式） |
| POST | `/api/v1/interview/evaluate/upload` | 提交面试评估（文件上传） |
| GET | `/api/v1/interview/reports` | 查询历史列表（分页） |
| GET | `/api/v1/interview/reports/{id}` | 查询单份报告详情 |

**提交面试评估（JSON）**：

```json
{
  "candidate_name": "张三",
  "job_title": "高级Java开发工程师",
  "competency_model_text": "岗位：高级Java开发工程师\n\n维度1：技术架构能力（权重35%）...",
  "interview_records_text": "【第1轮面试记录】\n面试轮次：初面...\n---\n【第2轮面试记录】..."
}
```

> **注意**：多轮面试记录用 `【第N轮面试记录】` 分隔，文件上传模式下自动拼接。

**报告响应示例**：

```json
{
  "id": 42,
  "candidate_name": "张三",
  "job_title": "高级Java开发工程师",
  "status": "DONE",
  "deviation": [
    {
      "dimension": "技术架构能力",
      "weight": 0.35,
      "scores": {"初面": 4, "复面": 4, "终面": 4},
      "max_gap": 0,
      "deviation_level": "一致",
      "trend": "平稳",
      "analysis": "三轮面试评分一致，候选人技术架构能力评估一致性好"
    }
  ],
  "consensus_level": "一致",
  "full_report": "# 面试一致性评估报告\n\n...",
  "duration_ms": 45230,
  "created_at": "2026-05-28T14:30:00"
}
```

---

## 测试

### 测试数据

`testdata/` 目录包含：

| 文件 | 说明 |
|------|------|
| `ability.txt` | 高级Java开发岗位能力模型（5 维度 + 1-5 分锚点） |
| `JDtest1.txt` | 高级Java JD 示例 |
| `CVtest1.txt` / `CVtest2.txt` | 候选人简历示例 |
| `interview.txt` | 三轮面试记录（用例1：评分一致） |
| `interview2.txt` | 用例2：评分严重偏差（含前同事关系） |
| `interview3.txt` | 用例3：证据严重不足 |
| `面试一致性评估_测试用例.md` | 4 组完整测试用例 + 预期结果 |

### 测试用例矩阵

| 用例 | 场景 | 偏差 | 证据 | 追问 | 冲突 | 预期结论 |
|------|------|------|------|------|------|----------|
| 1 | 三轮一致 | ✅ 一致 | ✅ 充分 | ✅ 无遗漏 | ✅ 一致 | 一致 |
| 2 | 初面5分 vs 复面2分 | 🔴 严重 | ⚠️ 不足 | ⚠️ 偏少 | 🔴 严重分歧 | 严重分歧 |
| 3 | 评分空泛无事例 | N/A | 🔴 严重不足 | 🔴 严重 | N/A | 建议重面 |
| 4 | 综合异常+注水 | 🔴 严重 | 🔴 不足 | 🔴 严重 | 🔴 严重分歧 | 严重分歧 |

### 直接测试 Dify 工作流

```bash
# 测试候选人匹配
curl -X POST https://api.dify.ai/v1/workflows/run \
  -H "Authorization: Bearer app-xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "resume_text": "...",
      "jd_text": "..."
    },
    "response_mode": "blocking",
    "user": "test"
  }'

# 测试面试评估
curl -X POST https://api.dify.ai/v1/workflows/run \
  -H "Authorization: Bearer app-xxxxx" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "competency_model_text": "...",
      "interview_records_text": "..."
    },
    "response_mode": "streaming",
    "user": "test"
  }'
```

或运行项目自带的测试脚本：

```bash
cd combat_HR
python test_dify_interview.py
```

---

## 常见问题

### Q1：Dify 工作流返回的 JSON 嵌套层级不对？

Dify 的 `outputs` 只包含结束节点直接输出的变量。如果某个字段嵌套在其他 JSON 中（如 `consensus_level` 嵌套在 `conflict` JSON 里），需要加「代码节点」提取后再作为独立变量输出。详见 Dify工作流搭建指南.md 1.8 和 2.10 节。

### Q2：LLM 输出不是纯 JSON 怎么办？

- 在 LLM 节点开启「结构化输出」（Dify 1.0+ 支持）
- 设置 Temperature = 0 降低随机性
- 在 Prompt 中强调「严格输出以下 JSON，不要输出其他内容」

### Q3：工作流执行超时？

- 候选人匹配默认 300 秒超时（blocking），面试评估默认 600 秒超时（streaming）
- 可修改 `dify_client.py` 中的 `timeout` 参数
- 如果文本特别大（如 10 轮面试记录），建议拆分为多次评估

### Q4：前端提交后一直显示"处理中"？

1. 确认后端控制台无报错
2. 检查 Dify API Key 和 Workflow ID 是否正确
3. 确认 MySQL 服务运行中
4. 查看 `interview_reports` 表的 `status` 和 `error_message` 字段

### Q5：能力模型格式有要求吗？

没有硬性格式要求。推荐的格式（见 `testdata/ability.txt`）：

```
岗位：XXX
维度1：XXX（权重XX%）
- 1分：XXX
- 2分：XXX
...
```

第一层 LLM 节点会自动解析，但越结构化 LLM 解析越准确。

---

## 后续计划

- [ ] 在 Dify 平台搭建两个工作流并完成联调
- [ ] 端到端测试 + 效果验证截图
- [ ] 第三模块：绩效事实校验助手（基于 LangGraph）
- [ ] Docker 容器化打包
- [ ] CI/CD 流水线

---

## License

MIT
