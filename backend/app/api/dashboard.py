# ==== 新增：Dashboard 统计数据 API ====
# 为前端 Dashboard 首页提供聚合统计数据（总数、状态分布、月度趋势等）
# 从 match_reports 和 interview_reports 两张表做 GROUP BY 聚合查询

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func, extract
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.match_report import MatchReport, ReportStatus
from app.models.interview_report import InterviewReport
from app.schemas.dashboard import DashboardStats, MatchStats, InterviewStats, MonthlyTrend

# 新建路由，tag 会显示在 Swagger 文档分组中
router = APIRouter(prefix="/dashboard", tags=["数据概览"])


@router.get("/stats", response_model=DashboardStats, summary="获取 Dashboard 统计数据")
def get_stats(db: Session = Depends(get_db)):
    """返回首页所需的全部聚合统计：匹配/面试概览 + 近6个月趋势"""

    # ---- 1. 匹配筛查统计 ----
    # 按 status 分组计数，同时计算已完成报告的平均分
    match_rows = (
        db.query(
            MatchReport.status,
            func.count(MatchReport.id).label("cnt"),
            func.avg(MatchReport.match_score).label("avg_score"),
        )
        .group_by(MatchReport.status)
        .all()
    )
    match_stats = MatchStats()
    for status, cnt, avg_score in match_rows:
        # status 是枚举值，取 .value 拿到 "done"/"processing" 等字符串
        if status == ReportStatus.DONE:
            match_stats.done = cnt
            match_stats.avg_score = round(avg_score, 2) if avg_score else None
        elif status == ReportStatus.PROCESSING:
            match_stats.processing = cnt
        elif status == ReportStatus.FAILED:
            match_stats.failed = cnt
        # pending 状态也计入 total
    match_stats.total = match_stats.done + match_stats.processing + match_stats.failed

    # ---- 2. 面试评估统计 ----
    interview_rows = (
        db.query(
            InterviewReport.status,
            func.count(InterviewReport.id).label("cnt"),
        )
        .group_by(InterviewReport.status)
        .all()
    )
    interview_stats = InterviewStats()
    for status, cnt in interview_rows:
        if status == ReportStatus.DONE:
            interview_stats.done = cnt
        elif status == ReportStatus.PROCESSING:
            interview_stats.processing = cnt
        elif status == ReportStatus.FAILED:
            interview_stats.failed = cnt
    interview_stats.total = interview_stats.done + interview_stats.processing + interview_stats.failed

    # 已完成报告中，按 consensus_level（一致性结论）分组统计
    consensus_rows = (
        db.query(
            InterviewReport.consensus_level,
            func.count(InterviewReport.id).label("cnt"),
        )
        .filter(InterviewReport.status == ReportStatus.DONE)
        .group_by(InterviewReport.consensus_level)
        .all()
    )
    for level, cnt in consensus_rows:
        if level == "一致":
            interview_stats.consensus_一致 = cnt
        elif level == "基本一致":
            interview_stats.consensus_基本一致 = cnt
        elif level == "存在分歧":
            interview_stats.consensus_存在分歧 = cnt
        elif level == "严重分歧":
            interview_stats.consensus_严重分歧 = cnt

    # ---- 3. 近6个月月度趋势 ----
    # 从6个月前开始，按月聚合 match + interview 的创建数量
    six_months_ago = datetime.utcnow() - timedelta(days=180)
    # 匹配月度数据：按年月分组 count
    match_monthly = (
        db.query(
            func.date_format(MatchReport.created_at, "%Y-%m").label("month"),
            func.count(MatchReport.id).label("cnt"),
        )
        .filter(MatchReport.created_at >= six_months_ago)
        .group_by("month")
        .order_by("month")
        .all()
    )
    # 面试月度数据
    interview_monthly = (
        db.query(
            func.date_format(InterviewReport.created_at, "%Y-%m").label("month"),
            func.count(InterviewReport.id).label("cnt"),
        )
        .filter(InterviewReport.created_at >= six_months_ago)
        .group_by("month")
        .order_by("month")
        .all()
    )

    # 合并为 dict: {month: {match: n, interview: n}}
    trend_map = {}
    for month, cnt in match_monthly:
        trend_map[month] = {"match_count": cnt, "interview_count": 0}
    for month, cnt in interview_monthly:
        if month in trend_map:
            trend_map[month]["interview_count"] = cnt
        else:
            trend_map[month] = {"match_count": 0, "interview_count": cnt}

    monthly_trend = [
        MonthlyTrend(month=m, match_count=v["match_count"], interview_count=v["interview_count"])
        for m, v in trend_map.items()
    ]

    return DashboardStats(
        match=match_stats,
        interview=interview_stats,
        monthly_trend=monthly_trend,
    )
