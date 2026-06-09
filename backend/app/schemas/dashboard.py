# ==== 新增：Dashboard 统计 API 的响应模型 ====
# 为前端 Dashboard 首页提供聚合统计数据
from pydantic import BaseModel
from typing import Optional


class MatchStats(BaseModel):
    """候选人匹配筛查的统计数据"""
    total: int = 0              # 评估总份数
    done: int = 0               # 已完成
    processing: int = 0         # 处理中
    failed: int = 0             # 失败
    avg_score: Optional[float] = None  # 已完成报告的平均匹配分（0-5）


class InterviewStats(BaseModel):
    """面试一致性评估的统计数据"""
    total: int = 0              # 评估总份数
    done: int = 0               # 已完成
    processing: int = 0         # 处理中
    failed: int = 0             # 失败
    # 一致性等级分布（四档）
    consensus_一致: int = 0
    consensus_基本一致: int = 0
    consensus_存在分歧: int = 0
    consensus_严重分歧: int = 0


class MonthlyTrend(BaseModel):
    """单月趋势数据点，用于折线图"""
    month: str          # 月份标签，如 "2026-05"
    match_count: int    # 当月匹配评估数
    interview_count: int  # 当月面试评估数


class DashboardStats(BaseModel):
    """Dashboard 首页完整统计数据"""
    match: MatchStats
    interview: InterviewStats
    monthly_trend: list[MonthlyTrend] = []  # 近6个月趋势
