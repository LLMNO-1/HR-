import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.match_report import MatchReport, ReportStatus
from app.schemas.match import (
    MatchEvaluateRequest, MatchReportResponse, MatchReportListItem,
    HardCheckItem, MatchScoreItem, RiskItem,
)
from app.schemas.common import TaskResponse
from app.services.file_service import save_upload_file, read_text_file
from app.services.match_service import run_match_task

router = APIRouter(prefix="/match", tags=["候选人匹配筛查"])


@router.post("/evaluate", response_model=TaskResponse, summary="提交候选人匹配评估任务")
def evaluate_candidate(req: MatchEvaluateRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    report = MatchReport(
        candidate_name=req.candidate_name,
        job_title=req.job_title,
        resume_text=req.resume_text,
        jd_text=req.jd_text,
        status=ReportStatus.PROCESSING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    background_tasks.add_task(run_match_task, report.id, req.resume_text, req.jd_text)
    return TaskResponse(task_id=report.id)


@router.post("/evaluate/upload", response_model=TaskResponse, summary="上传文件并提交评估任务")
async def evaluate_candidate_upload(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    candidate_name: str = Form(..., description="候选人姓名"),
    job_title: str = Form(..., description="岗位名称"),
    resume_file: UploadFile = File(..., description="简历文件（txt/md）"),
    jd_file: UploadFile = File(..., description="JD文件（txt/md）"),
):
    resume_path = await save_upload_file(resume_file)
    jd_path = await save_upload_file(jd_file)
    try:
        resume_text = read_text_file(resume_path)
        jd_text = read_text_file(jd_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件读取失败: {str(e)}")

    report = MatchReport(
        candidate_name=candidate_name,
        job_title=job_title,
        resume_text=resume_text,
        jd_text=jd_text,
        status=ReportStatus.PROCESSING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    background_tasks.add_task(run_match_task, report.id, resume_text, jd_text)
    return TaskResponse(task_id=report.id)


@router.get("/reports", response_model=list[MatchReportListItem], summary="查询评估历史列表")
def list_reports(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    reports = (
        db.query(MatchReport)
        .order_by(MatchReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reports


def _parse_nested(data, list_key):
    """从 Dify 返回的嵌套 dict 中提取列表。Dify 返回格式如 {"checks": [...]} 或直接为 [...]"""
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return data.get(list_key, [])
    return []


def _unwrap_report(text):
    """解包可能被 JSON 包裹的报告文本"""
    if not text:
        return ""
    if text.startswith("{"):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed.get("final_report", text)
        except (json.JSONDecodeError, TypeError):
            pass
    return text


@router.get("/reports/{report_id}", response_model=MatchReportResponse, summary="查询单份报告详情")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(MatchReport).filter(MatchReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    hard_check_raw = json.loads(report.hard_check_json) if report.hard_check_json else {}
    match_detail_raw = json.loads(report.match_detail_json) if report.match_detail_json else {}
    risks_raw = json.loads(report.risk_json) if report.risk_json else {}

    return MatchReportResponse(
        id=report.id,
        candidate_name=report.candidate_name,
        job_title=report.job_title,
        status=report.status.value if report.status else None,
        match_score=report.match_score,
        hard_check=[HardCheckItem(**item) for item in _parse_nested(hard_check_raw, "checks")],
        match_detail=[MatchScoreItem(**item) for item in _parse_nested(match_detail_raw, "scores")],
        risks=[RiskItem(**item) for item in _parse_nested(risks_raw, "risks")],
        full_report=_unwrap_report(report.full_report),
        error_message=report.error_message,
        duration_ms=report.duration_ms,
        created_at=report.created_at,
    )
