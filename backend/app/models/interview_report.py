from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from app.models.database import Base
from app.models.match_report import ReportStatus


class InterviewReport(Base):
    """面试一致性评估报告表"""
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_name = Column(String(64), nullable=False, comment="候选人姓名")
    job_title = Column(String(128), nullable=False, comment="岗位名称")
    interview_records_text = Column(Text, nullable=False, comment="多轮面试记录原文（合并）")
    competency_model_text = Column(Text, nullable=False, comment="能力模型原文")
    status = Column(SAEnum(ReportStatus), default=ReportStatus.PENDING, comment="处理状态")
    deviation_json = Column(Text, nullable=True, comment="评分偏差分析JSON")
    evidence_json = Column(Text, nullable=True, comment="证据充分性JSON")
    conflict_json = Column(Text, nullable=True, comment="结论冲突JSON")
    missed_followup_json = Column(Text, nullable=True, comment="追问遗漏JSON")
    full_report = Column(Text, nullable=True, comment="完整报告Markdown")
    consensus_level = Column(String(32), nullable=True, comment="结论一致/基本一致/存在分歧/严重分歧")
    error_message = Column(Text, nullable=True, comment="失败原因")
    duration_ms = Column(Integer, nullable=True, comment="处理耗时(毫秒)")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
