from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========== 请求模型 ==========

class InterviewEvalRequest(BaseModel):
    """面试一致性评估请求"""
    candidate_name: str = Field(..., min_length=1, max_length=64, description="候选人姓名")
    job_title: str = Field(..., min_length=1, max_length=128, description="岗位名称")
    competency_model_text: str = Field(..., min_length=1, description="岗位能力模型文本")
    interview_records_text: str = Field(..., min_length=1, description="多轮面试记录文本（合并）")


# ========== 响应模型 ==========

class DeviationItem(BaseModel):
    """评分偏差项"""
    dimension: str
    weight: float
    scores: dict  # {"初面": 4, "复面": 3, "终面": None}
    max_gap: float
    deviation_level: str  # 一致/轻微偏差/严重偏差
    analysis: str


class EvidenceItem(BaseModel):
    """证据充分性项（字段名与 Dify 输出对齐）"""
    interviewer: str
    dimension_checks: list[dict] = []
    overall_evidence_quality: str = ""  # 充分/一般/不足
    weak_evidence_count: int = 0


class MissedFollowupItem(BaseModel):
    """追问遗漏项（字段名与 Dify 输出对齐）"""
    interview_round: str
    context: str
    what_should_ask: str
    why_important: str = ""
    severity: str


class InterviewReportResponse(BaseModel):
    """面试一致性评估响应"""
    id: int
    candidate_name: str
    job_title: str
    status: str
    deviation: Optional[list[DeviationItem]] = None
    evidence: Optional[list[EvidenceItem]] = None
    missed_followups: Optional[list[MissedFollowupItem]] = None
    consensus_level: Optional[str] = None
    full_report: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class InterviewReportListItem(BaseModel):
    """面试评估列表项"""
    id: int
    candidate_name: str
    job_title: str
    status: str
    consensus_level: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
