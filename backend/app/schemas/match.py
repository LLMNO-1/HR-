from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========== 请求模型 ==========

class MatchEvaluateRequest(BaseModel):
    """候选人匹配评估请求（通过JSON传文本）"""
    candidate_name: str = Field(..., min_length=1, max_length=64, description="候选人姓名")
    job_title: str = Field(..., min_length=1, max_length=128, description="岗位名称")
    resume_text: str = Field(..., min_length=1, description="简历文本内容")
    jd_text: str = Field(..., min_length=1, description="岗位JD文本内容")


# ========== 响应模型 ==========

class HardCheckItem(BaseModel):
    """硬性条件校验单项"""
    item: str
    requirement: str
    candidate_status: str
    result: str  # 达标/不达标/存疑
    detail: str


class MatchScoreItem(BaseModel):
    """技能匹配评分单项"""
    dimension: str
    score: float
    reason: str
    evidence: str


class RiskItem(BaseModel):
    """风险单项"""
    type: str
    level: str
    description: str
    evidence: str
    suggestion: str


class MatchReportResponse(BaseModel):
    """候选人匹配评估响应"""
    id: int
    candidate_name: str
    job_title: str
    status: str
    match_score: Optional[float] = None
    hard_check: Optional[list[HardCheckItem]] = None
    match_detail: Optional[list[MatchScoreItem]] = None
    risks: Optional[list[RiskItem]] = None
    full_report: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MatchReportListItem(BaseModel):
    """评估列表项（精简字段）"""
    id: int
    candidate_name: str
    job_title: str
    status: str
    match_score: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
