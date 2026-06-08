# Dify 工作流搭建指南（配套 combat_HR 后端代码）

> **重要**：本文档中的所有变量名与 `backend/` 代码严格对应。按本文档搭建，无需修改任何代码。

---

# 前置准备

1. 打开 Dify 平台（云版 `cloud.dify.ai` 或私有部署地址）
2. 确认已配置 LLM 模型（推荐 DeepSeek-V3 或通义千问-Max）
3. 顶部导航 → **"工作室"** → **"创建空白应用"** → 选择 **"工作流"**

---

# 一、候选人匹配筛查工作流

## 1.0 代码期望的输入输出（搭建前必读）

| 方向 | 变量名 | 类型 | 说明 |
|------|--------|------|------|
| **输入** | `resume_text` | Text | 简历全文 |
| **输入** | `jd_text` | Text | 岗位JD全文 |
| 输出 | `hard_check_result` | JSON | 硬性条件校验结果 |
| 输出 | `match_score` | JSON | 技能匹配详情 |
| 输出 | `risk_analysis` | JSON | 风险分析结果 |
| 输出 | `overall_score` | Number | 综合匹配度（0-5） |
| 输出 | `final_report` | Text | 完整报告Markdown |

## 1.1 开始节点配置

点击"开始"节点，添加两个输入变量：

| 变量名 | 类型 | 必填 |
|--------|------|------|
| `resume_text` | 文本 | 是 |
| `jd_text` | 文本 | 是 |

## 1.2 节点1：简历结构化提取

- **节点类型**：LLM
- **节点名称**：简历结构化提取

**System Prompt**：

```
你是一位专业的HR招聘解析助手。从候选人简历中提取结构化信息。

严格输出以下JSON，不要输出其他内容：

{
  "name": "姓名",
  "education": {
    "highest_degree": "大专/本科/硕士/博士",
    "major": "专业名称",
    "school": "毕业院校",
    "major_match": "是否计算机相关专业 true/false"
  },
  "work_years": 工作年限数字,
  "current_level": "初级/中级/高级/资深/专家",
  "skills": ["技能1", "技能2"],
  "work_history": [
    {
      "company": "公司名",
      "period": "起止时间",
      "duration_months": 在职月数,
      "position": "职位",
      "responsibilities": "主要职责（50字内）",
      "highlights": "亮点成果（50字内）"
    }
  ],
  "project_experience": [
    {
      "name": "项目名",
      "role": "角色",
      "description": "描述（30字内）",
      "highlights": "成果（30字内）"
    }
  ],
  "job_hopping": {
    "total_jobs": 公司数量,
    "avg_tenure_months": 平均每段月数,
    "risk_flag": "是否频繁跳槽 true/false（平均<12个月或3段以上为true）"
  },
  "career_gaps": [
    {
      "period": "空白期",
      "duration_months": 月数,
      "possible_reason": "可能原因"
    }
  ],
  "industry_experience": ["行业列表"]
}
```

**User Prompt**：

```
请解析以下候选人简历，提取结构化信息：

{{#开始.resume_text#}}
```

**输出变量**：`resume_json`（类型：文本）

## 1.3 节点2：JD结构化提取

- **节点类型**：LLM
- **节点名称**：JD结构化提取

**System Prompt**：

```
你是一位专业的HR招聘解析助手。从岗位JD中提取结构化信息。

严格输出以下JSON，不要输出其他内容：

{
  "position": "岗位名称",
  "department": "所属部门",
  "location": "工作地点",
  "hard_requirements": {
    "min_degree": "最低学历要求",
    "degree_major_required": "是否要求专业对口 true/false",
    "min_work_years": 最低年限数字,
    "must_skills": ["必备技能1", "必备技能2"],
    "other_requirements": ["其他硬性要求"]
  },
  "responsibilities": ["职责1", "职责2"],
  "preferred": {
    "skills": ["加分技能"],
    "experience": ["加分经验"],
    "other": ["其他加分项"]
  },
  "soft_skills": ["软技能要求"],
  "level_required": "职级要求"
}
```

**User Prompt**：

```
请解析以下岗位JD，提取结构化信息：

{{#开始.jd_text#}}
```

**输出变量**：`jd_json`（类型：文本）

## 1.4 节点3：硬性条件校验

- **节点类型**：LLM
- **节点名称**：硬性条件校验

**System Prompt**：

```
你是一位严谨的HR简历筛选专家。对比候选人和JD的硬性条件，逐项判断是否达标。

校验规则：
1. 学历：大专<本科<硕士<博士，候选人学历>=JD最低要求即为达标
2. 专业：如果JD要求专业对口，检查候选人专业是否相关
3. 工作年限：候选人年限>=JD最低年限即为达标
4. 必备技能：JD列出的必备技能，候选人必须全部覆盖
5. 结果只能是"达标"、"不达标"或"存疑"

严格输出以下JSON，不要输出其他内容：

{
  "checks": [
    {
      "item": "校验项名称",
      "requirement": "JD要求",
      "candidate_status": "候选人情况",
      "result": "达标/不达标/存疑",
      "detail": "详细说明（20字内）"
    }
  ],
  "total_result": "全部达标/部分不达标/严重不达标",
  "fatal_items": ["致命缺陷项"],
  "suggest_continue": true/false
}
```

**User Prompt**：

```
请校验候选人与JD的硬性条件匹配情况：

【JD要求】
{{#JD结构化提取.jd_json#}}

【候选人信息】
{{#简历结构化提取.resume_json#}}
```

**输出变量**：`hard_check_result`（类型：文本）

## 1.5 节点4：技能匹配打分

- **节点类型**：LLM
- **节点名称**：技能匹配打分

**System Prompt**：

```
你是一位HR技能评估专家。对候选人与JD的匹配度进行逐项打分。

打分维度：
1. 必备技能匹配度（0-5）：JD必备技能，候选人掌握程度
2. 加分项匹配度（0-5）：候选人覆盖了多少加分项
3. 行业经验匹配度（0-5）：是否有JD所处行业经验
4. 项目复杂度匹配度（0-5）：项目经验复杂度是否匹配
5. 职级匹配度（0-5）：当前职级与JD要求是否匹配
6. 综合匹配度（0-5）：综合以上维度

严格输出以下JSON：

{
  "scores": [
    {
      "dimension": "维度名称",
      "score": 分数,
      "reason": "打分依据（50字内）",
      "evidence": "简历中的证据"
    }
  ],
  "overall_score": 综合分数,
  "summary": "一句话总结（30字内）",
  "strengths": ["突出优势"],
  "gaps": ["主要差距"]
}
```

**User Prompt**：

```
请对候选人与JD进行技能匹配度打分：

【JD要求】
{{#JD结构化提取.jd_json#}}

【候选人信息】
{{#简历结构化提取.resume_json#}}
```

**输出变量**：`match_score`（类型：文本）

## 1.6 节点5：风险点识别

- **节点类型**：LLM
- **节点名称**：风险点识别

**System Prompt**：

```
你是HR风险识别专家。识别候选人简历中的潜在风险。

检查维度：
1. 跳槽频率：平均每段<12个月，或近2年换了2家以上→稳定性风险
2. 经验断层：两段工作之间有>6个月空白→能力存疑
3. 行业不匹配：候选人行业与JD行业差异大→适应成本高
4. 职级倒挂：当前级别明显低于JD要求→能否胜任
5. 技能退化：有技能但最近一段工作未使用→熟练度存疑
6. 项目注水：项目描述空泛或无法验证→真实性存疑
7. 大厂依赖：只在成熟体系下工作，缺0到1经验

严格输出以下JSON：

{
  "risks": [
    {
      "type": "风险类型",
      "level": "高/中/低",
      "description": "风险描述（30字内）",
      "evidence": "简历中的证据",
      "suggestion": "建议HR进一步确认什么"
    }
  ],
  "risk_level": "高风险/中等风险/低风险",
  "suggested_questions": ["建议面试追问的问题"],
  "recommend_next_step": "建议进入面试/建议电话沟通/建议淘汰"
}
```

**User Prompt**：

```
请识别以下候选人的潜在风险：

【候选人信息】
{{#简历结构化提取.resume_json#}}

【JD要求】
{{#JD结构化提取.jd_json#}}
```

**输出变量**：`risk_analysis`（类型：文本）

## 1.7 节点6：综合报告生成

- **节点类型**：LLM
- **节点名称**：综合报告生成

**System Prompt**：

```
你是一位专业HR招聘顾问。根据前面的分析结果，生成一份简洁的候选人评估报告。

报告格式如下（用Markdown）：

# 候选人评估报告

## 基本信息
| 项目 | 内容 |
|------|------|
| 候选人 | [姓名] |
| 应聘岗位 | [岗位名] |
| 当前职级 | [职级] |
| 工作年限 | [年限] |

## 硬性条件校验
| 校验项 | 要求 | 实际情况 | 结果 |
|--------|------|----------|------|
| ... | ... | ... | ✅/❌/⚠️ |

## 匹配度评分
| 维度 | 分数 | 说明 |
|------|------|------|
| 必备技能 | ★★★★☆ 4/5 | ... |

**综合匹配度：X.X/5**

## 优势
- ...

## 差距
- ...

## 风险提示
| 风险类型 | 等级 | 说明 |
|----------|------|------|
| ... | 🔴/🟡/🟢 | ... |

## HR行动建议
- **建议结论**：[进入面试/电话沟通后决定/淘汰]
- **建议追问**：
  1. ...
```

**User Prompt**：

```
请生成候选人综合评估报告：

【综合匹配度】
{{#提取分数.overall_score#}}

【硬性条件校验结果】
{{#硬性条件校验.hard_check_result#}}

【技能匹配打分】
{{#技能匹配打分.match_score#}}

【风险分析】
{{#风险点识别.risk_analysis#}}

【候选人原始简历】
{{#开始.resume_text#}}
```

**输出变量**：`final_report`（类型：文本）

## 1.8 节点7：提取综合分数（代码节点）

- **节点类型**：代码（Python）
- **节点名称**：提取分数

**代码内容**：

```python
import json

def main(match_score_text: str) -> dict:
    """从技能匹配打分的JSON文本中提取 overall_score 和 hard_check_result"""
    try:
        data = json.loads(match_score_text) if isinstance(match_score_text, str) else match_score_text
        return {
            "overall_score": data.get("overall_score", 0)
        }
    except:
        return {"overall_score": 0}
```

**输入变量**：`match_score_text` ← 选择 `{{#技能匹配打分.match_score#}}`

**输出变量**：`overall_score`（类型：数字）

## 1.9 结束节点配置

点击"结束"节点，设置输出变量（这些变量就是 Python 代码中 `parse_match_result` 读取的字段）：

| 输出变量名 | 来源 |
|------------|------|
| `hard_check_result` | `{{#硬性条件校验.hard_check_result#}}` |
| `match_score` | `{{#技能匹配打分.match_score#}}` |
| `risk_analysis` | `{{#风险点识别.risk_analysis#}}` |
| `overall_score` | `{{#提取分数.overall_score#}}` |
| `final_report` | `{{#综合报告生成.final_report#}}` |

## 1.10 工作流连线总览

```
开始(start)
  ├── resume_text ──→ 简历结构化提取 ──→ resume_json ──┐
  │                                                      ├──→ 硬性条件校验 ──→ hard_check_result ──┐
  └── jd_text ──────→ JD结构化提取 ────→ jd_json ───────┘                                        │
                                                         ├──→ 技能匹配打分 ────→ match_score ──────┤
                                                         │         │                              │
                                                         │         └──→ 提取分数 ──→ overall_score│
                                                         │                                        ├──→ 综合报告生成 ──→ final_report ──→ 结束
                                                         └──→ 风险点识别 ──────→ risk_analysis ───┘
```

---

# 二、面试一致性评估工作流

## 2.0 代码期望的输入输出

| 方向 | 变量名 | 类型 | 说明 |
|------|--------|------|------|
| **输入** | `competency_model_text` | Text | 岗位能力模型 |
| **输入** | `interview_records_text` | Text | 多轮面试记录（合并） |
| 输出 | `deviation` | JSON | 评分偏差分析 |
| 输出 | `evidence` | JSON | 证据充分性 |
| 输出 | `conflict` | JSON | 结论冲突 |
| 输出 | `missed_followup` | JSON | 追问遗漏 |
| 输出 | `consensus_level` | Text | 结论一致性等级 |
| 输出 | `final_report` | Text | 完整报告Markdown |

## 2.1 开始节点配置

| 变量名 | 类型 | 必填 |
|--------|------|------|
| `competency_model_text` | 文本 | 是 |
| `interview_records_text` | 文本 | 是 |

## 2.2 节点1：能力模型解析

- **节点类型**：LLM
- **节点名称**：能力模型解析

**System Prompt**：

```
从岗位能力模型中提取结构化信息。

严格输出以下JSON：

{
  "position": "岗位名称",
  "dimensions": [
    {
      "name": "维度名称",
      "weight": 权重百分比数字,
      "description": "描述（20字内）",
      "scoring_guide": {
        "1": "1分描述",
        "2": "2分描述",
        "3": "3分描述",
        "4": "4分描述",
        "5": "5分描述"
      }
    }
  ],
  "total_weight": 100
}
```

**User Prompt**：

```
请解析以下能力模型：

{{#开始.competency_model_text#}}
```

**输出变量**：`competency_json`（类型：文本）

## 2.3 节点2：面试记录解析

- **节点类型**：LLM
- **节点名称**：面试记录解析

**System Prompt**：

```
从面试记录中提取结构化信息。interview_records_text 中可能包含多轮面试记录（用【第N轮】分隔），请分别解析每一轮。

严格输出以下JSON（records数组每轮一个元素）：

{
  "records": [
    {
      "round": "初面/复面/终面",
      "interviewer": {
        "name": "面试官姓名",
        "role": "面试官角色",
        "years": 年限数字
      },
      "date": "面试日期",
      "duration_minutes": 时长,
      "format": "视频/现场/电话",
      "scores": [
        {
          "dimension": "维度名称",
          "score": 1-5的评分,
          "notes": "面试官备注"
        }
      ],
      "overall_comment": "面试官整体评语",
      "questions_asked": ["问题1", "问题2"],
      "follow_up_questions": [
        {
          "original": "原始问题",
          "follow_up": "追问内容",
          "response_summary": "候选人回答摘要"
        }
      ],
      "key_observations": ["关键观察"],
      "recommendation": "录用/淘汰/进入下一轮/有条件录用",
      "tone": "正面/中性/负面/混合"
    }
  ]
}
```

**User Prompt**：

```
请解析以下面试记录：

{{#开始.interview_records_text#}}
```

**输出变量**：`interview_json`（类型：文本）

## 2.4 节点3：评分偏差检测

- **节点类型**：LLM
- **节点名称**：评分偏差检测

**System Prompt**：

```
比较多轮面试中同一维度的评分，检测异常偏差。

检测规则：
1. 同一维度不同面试官评分差距>=1.5分→"严重偏差"
2. 差距>=1.0且<1.5→"轻微偏差"
3. 差距<1.0→"一致"
4. 某维度只在部分轮次被评→"数据不完整"

严格输出以下JSON：

{
  "dimension_comparison": [
    {
      "dimension": "维度名称",
      "weight": 权重,
      "scores": {"初面": 4, "复面": 3},
      "max_gap": 最大分差,
      "deviation_level": "一致/轻微偏差/严重偏差/数据不完整",
      "trend": "平稳/下滑/上升/波动",
      "analysis": "偏差原因分析（50字内）"
    }
  ],
  "overall_deviation": {
    "level": "一致/轻微偏差/严重偏差",
    "summary": "整体偏差情况（50字内）",
    "problematic_dimensions": ["问题维度"]
  },
  "score_trend": {
    "pattern": "先高后低/先低后高/平稳/波动",
    "possible_meaning": "可能含义（30字内）"
  }
}
```

**User Prompt**：

```
请比较多轮面试的评分偏差：

【能力模型】
{{#能力模型解析.competency_json#}}

【面试记录】
{{#面试记录解析.interview_json#}}
```

**输出变量**：`deviation`（类型：文本）

## 2.5 节点4：证据充分性检查

- **节点类型**：LLM
- **节点名称**：证据充分性检查

**System Prompt**：

```
检查每位面试官的评分是否有充分的事实证据支撑。

规则：
- 有具体场景、行为、数据→"充分"
- 有笼统评价但部分具体→"一般"
- 只有结论无事例→"不足"
- 评价与分数矛盾也标记为"不足"

严格输出以下JSON：

{
  "evidence_checks": [
    {
      "interviewer": "面试官",
      "dimension_checks": [
        {
          "dimension": "维度",
          "score": 评分,
          "evidence_in_record": "记录中的证据",
          "evidence_level": "充分/一般/不足",
          "issue": "问题描述或null"
        }
      ],
      "overall_evidence_quality": "充分/一般/不足",
      "weak_evidence_count": 不足项数量
    }
  ],
  "summary": {
    "total_weak_items": 总不足项数,
    "main_concern": "主要担忧（30字内）",
    "suggest_rescore": ["建议重评的维度"]
  }
}
```

**User Prompt**：

```
请检查各轮面试评分的证据充分性：

【能力模型】
{{#能力模型解析.competency_json#}}

【面试记录】
{{#面试记录解析.interview_json#}}
```

**输出变量**：`evidence`（类型：文本）

## 2.6 节点5：追问遗漏检测

- **节点类型**：LLM
- **节点名称**：追问遗漏检测

**System Prompt**：

```
检查面试中是否应该追问但没有追问的情况。

检查规则：
1. 候选人回答笼统模糊，面试官直接跳过→标记
2. 候选人回答有疑点（数据不清、理由不明），未追问→标记
3. 候选人回答过于简短或回避，面试官未追问→标记
4. 面试官自己写了"感觉"、"不太确定"但没追问→标记

严格输出以下JSON：

{
  "missed_followups": [
    {
      "interview_round": "哪一轮",
      "context": "当时问答上下文（50字内）",
      "what_should_ask": "应该追问什么（30字内）",
      "why_important": "为什么重要（30字内）",
      "severity": "严重/中等/轻微"
    }
  ],
  "total_missed": 遗漏数,
  "most_problematic_round": "问题最严重的轮次",
  "suggestions": ["面试官改进建议"]
}
```

**User Prompt**：

```
请检查面试中的追问遗漏：

{{#开始.interview_records_text#}}
```

**输出变量**：`missed_followup`（类型：文本）

## 2.7 节点6：结论冲突检测

- **节点类型**：LLM
- **节点名称**：结论冲突检测

**System Prompt**：

```
比较各轮面试官的最终结论是否存在冲突。

冲突类型：
1. 明确冲突：A建议"录用"，B建议"淘汰"
2. 条件冲突：建议"有条件录用"，但条件互相矛盾
3. 隐含冲突：结论一致但理由完全相反
4. 级差过大：初面极高但终面极低（或反之），且无合理解释

严格输出以下JSON：

{
  "conclusions": [
    {"round": "轮次", "interviewer": "面试官", "conclusion": "结论", "reasoning": "理由（30字内）"}
  ],
  "conflicts": [
    {
      "type": "冲突类型",
      "parties": ["面试官A", "面试官B"],
      "description": "冲突描述（50字内）",
      "resolution_suggestion": "解决建议（30字内）"
    }
  ],
  "has_conflict": true/false,
  "consensus_level": "一致/基本一致/存在分歧/严重分歧",
  "final_recommendation": "录用/有条件录用/加面一轮/淘汰",
  "final_reasoning": "推荐理由（50字内）"
}
```

**User Prompt**：

```
请检查各轮面试结论是否存在冲突：

【面试记录解析结果】
{{#面试记录解析.interview_json#}}

【评分偏差分析】
{{#评分偏差检测.deviation#}}

【证据充分性】
{{#证据充分性检查.evidence#}}
```

**输出变量**：`conflict`（类型：文本）

## 2.8 节点7：一致性报告生成

- **节点类型**：LLM
- **节点名称**：一致性报告生成

**System Prompt**：

```
你是一位资深HR质量保障专家。根据所有分析结果，生成一份面试一致性评估报告。

报告格式（Markdown）：

# 面试一致性评估报告

## 候选人信息
- 候选人：[从面试记录中提取]
- 岗位：[岗位名]
- 面试轮次：X轮
- 面试官：[列出]

## 评分一致性总览
| 维度 | 权重 | 各轮评分 | 最大分差 | 一致性 |
|------|------|----------|----------|--------|
| ... | ... | ... | ... | ✅/⚠️/🔴 |

**整体一致性：[结论]**

## 偏差详情
### 严重偏差项
（如有）
### 轻微偏差项
（如有）

## 证据充分性
| 面试轮次 | 证据质量 | 不足项 |
|----------|----------|--------|

## 追问遗漏
| 轮次 | 应追问项 | 重要性 |
|------|----------|--------|

## 结论一致性
| 面试官 | 结论 | 核心理由 |
|--------|------|----------|

**结论一致性：[等级]**

## 改进建议
1. ...
2. ...

## 是否建议加面
- **结论**：[是/否]
- **理由**：[...]
```

**User Prompt**：

```
请生成面试一致性评估报告：

【能力模型】
{{#能力模型解析.competency_json#}}

【面试记录】
{{#面试记录解析.interview_json#}}

【评分偏差】
{{#评分偏差检测.deviation#}}

【证据充分性】
{{#证据充分性检查.evidence#}}

【追问遗漏】
{{#追问遗漏检测.missed_followup#}}

【结论冲突】
{{#结论冲突检测.conflict#}}
```

**输出变量**：`final_report`（类型：文本）

## 2.9 结束节点配置

| 输出变量名 | 来源 |
|------------|------|
| `deviation` | `{{#评分偏差检测.deviation#}}` |
| `evidence` | `{{#证据充分性检查.evidence#}}` |
| `missed_followup` | `{{#追问遗漏检测.missed_followup#}}` |
| `conflict` | `{{#结论冲突检测.conflict#}}` |
| `consensus_level` | `{{#结论冲突检测.conflict#}}`（取其中的 consensus_level 字段） |
| `final_report` | `{{#一致性报告生成.final_report#}}` |

> **注意**：`consensus_level` 嵌套在 `conflict` JSON 中，建议加一个**代码节点**提取它。

## 2.10 节点8：提取一致性等级（代码节点）

- **节点类型**：代码（Python）
- **节点名称**：提取一致性

**代码内容**：

```python
import json

def main(conflict_text: str) -> dict:
    try:
        data = json.loads(conflict_text) if isinstance(conflict_text, str) else conflict_text
        return {
            "consensus_level": data.get("consensus_level", "未知")
        }
    except:
        return {"consensus_level": "未知"}
```

**输入变量**：`conflict_text` ← `{{#结论冲突检测.conflict#}}`

**输出变量**：`consensus_level`（类型：文本）

更新结束节点 `consensus_level` 的来源为 `{{#提取一致性.consensus_level#}}`。

## 2.11 工作流连线总览

```
开始(start)
  ├── competency_model_text ──→ 能力模型解析 ──→ competency_json ──┐
  │                                                                  │
  └── interview_records_text ──→ 面试记录解析 ──→ interview_json ───┤
                                                                     │
        ┌────────────────────────────────────────────────────────────┤
        │                                                            │
        ├──→ 评分偏差检测 ────→ deviation ───────────────────────────┤
        │                                                            │
        ├──→ 证据充分性检查 ──→ evidence ────────────────────────────┤
        │                                                            ├──→ 一致性报告生成 ──→ final_report ──→ 结束
        ├──→ 追问遗漏检测 ────→ missed_followup ─────────────────────┤
        │                                                            │
        └──→ 结论冲突检测 ────→ conflict ──┬─────────────────────────┘
                                           └──→ 提取一致性 ──→ consensus_level ──→ 结束
```

---

# 三、发布与测试

## 3.1 发布工作流

1. 工作流搭完后，点击右上角 **"发布"** 按钮
2. 发布成功后，左侧菜单进入 **"API 访问"**
3. 复制 **工作流 ID**（一段 UUID，如 `72ef40c9-b9b8-4c2a-961f-72b616587bc5`）
4. 复制 **API Key**（以 `app-` 开头）

## 3.2 配置到后端

编辑 `backend/.env`：

```env
DIFY_API_KEY=app-你的API-Key
DIFY_WORKFLOW_MATCH=候选人匹配工作流ID
DIFY_WORKFLOW_INTERVIEW=面试一致性评估工作流ID
```

## 3.3 用 curl 测试（发布后先在终端验证）

**测试候选人匹配**：

```bash
curl -X POST https://api.dify.ai/v1/workflows/run \
  -H "Authorization: Bearer app-你的Key" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "resume_text": "张三，本科，5年Java开发经验...",
      "jd_text": "高级Java开发，要求本科以上，5年经验..."
    },
    "response_mode": "blocking",
    "user": "test"
  }'
```

**查看返回的 `data.outputs` 中是否包含**：`hard_check_result`、`match_score`、`risk_analysis`、`overall_score`、`final_report`。变量名完全一致即对接成功。

## 3.4 变量名对照速查表

### 工作流1：候选人匹配筛查

| 代码文件 | 代码位置 | 变量名 | 方向 |
|----------|----------|--------|------|
| `dify_client.py:67` | inputs | `resume_text` | 入 |
| `dify_client.py:68` | inputs | `jd_text` | 入 |
| `match_service.py:14` | .get() | `final_report` | 出 |
| `match_service.py:15` | .get() | `hard_check_result` | 出 |
| `match_service.py:16` | .get() | `match_score` | 出 |
| `match_service.py:17` | .get() | `risk_analysis` | 出 |
| `match_service.py:18` | .get() | `overall_score` | 出 |

### 工作流2：面试一致性评估

| 代码文件 | 代码位置 | 变量名 | 方向 |
|----------|----------|--------|------|
| `dify_client.py:83` | inputs | `competency_model_text` | 入 |
| `dify_client.py:84` | inputs | `interview_records_text` | 入 |
| `interview_service.py:10` | .get() | `final_report` | 出 |
| `interview_service.py:11` | .get() | `deviation` | 出 |
| `interview_service.py:12` | .get() | `evidence` | 出 |
| `interview_service.py:13` | .get() | `conflict` | 出 |
| `interview_service.py:14` | .get() | `missed_followup` | 出 |
| `interview_service.py:15` | .get() | `consensus_level` | 出 |

---

# 四、常见问题

**Q：LLM 输出不是纯 JSON 怎么办？**

A：在 LLM 节点配置中开启"结构化输出"（Dify 1.0+ 支持），或开启 Temperature=0 降低随机性。

**Q：工作流执行超时怎么办？**

A：代码默认超时 300 秒（5 分钟），如果文件特别大，可以调大 `dify_client.py` 第38行的 `timeout` 值。

**Q：返回的 JSON 嵌套层级不对？**

A：Dify 的 `outputs` 只包含结束节点直接输出的变量。如果某个变量是嵌套在其他 JSON 里的字段，需要加"代码节点"提取出来再输出（参照本文档 1.8 和 2.10 节）。
