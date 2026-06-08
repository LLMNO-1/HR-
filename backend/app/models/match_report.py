from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from app.models.database import Base
import enum


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class MatchReport(Base):
    """候选人匹配评估报告表"""
    __tablename__ = "match_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_name = Column(String(64), nullable=False, comment="候选人姓名")
    job_title = Column(String(128), nullable=False, comment="岗位名称")
    resume_text = Column(Text, nullable=False, comment="简历原文")
    jd_text = Column(Text, nullable=False, comment="JD原文")
    status = Column(SAEnum(ReportStatus), default=ReportStatus.PENDING, comment="处理状态")
    match_score = Column(Float, nullable=True, comment="综合匹配度 0-5")
    hard_check_json = Column(Text, nullable=True, comment="硬性条件校验结果JSON")
    match_detail_json = Column(Text, nullable=True, comment="技能匹配详情JSON")
    risk_json = Column(Text, nullable=True, comment="风险分析JSON")
    full_report = Column(Text, nullable=True, comment="完整报告Markdown")
    error_message = Column(Text, nullable=True, comment="失败原因")
    duration_ms = Column(Integer, nullable=True, comment="处理耗时(毫秒)")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
