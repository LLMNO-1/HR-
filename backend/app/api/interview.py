import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.models.interview_report import InterviewReport, ReportStatus
from app.schemas.interview import (
    InterviewEvalRequest, InterviewReportResponse, InterviewReportListItem,
    DeviationItem, EvidenceItem, MissedFollowupItem,
)
from app.schemas.common import TaskResponse
from app.services.file_service import save_upload_file, read_text_file
from app.services.interview_service import run_interview_task

router = APIRouter(prefix="/interview", tags=["面试一致性评估"])


@router.post("/evaluate", response_model=TaskResponse, summary="提交面试一致性评估任务")
def evaluate_interview(req: InterviewEvalRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    report = InterviewReport(
        candidate_name=req.candidate_name,
        job_title=req.job_title,
        competency_model_text=req.competency_model_text,
        interview_records_text=req.interview_records_text,
        status=ReportStatus.PROCESSING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    background_tasks.add_task(run_interview_task, report.id, req.competency_model_text, req.interview_records_text)
    return TaskResponse(task_id=report.id)


@router.post("/evaluate/upload", response_model=TaskResponse, summary="上传文件并提交面试评估任务")
async def evaluate_interview_upload(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    candidate_name: str = Form(..., description="候选人姓名"),
    job_title: str = Form(..., description="岗位名称"),
    competency_file: UploadFile = File(..., description="能力模型文件（txt/md）"),
    interview_files: list[UploadFile] = File(..., description="面试记录文件（可多轮，每轮一个文件）"),
):
    comp_path = await save_upload_file(competency_file)
    competency_text = read_text_file(comp_path)

    records_parts = []
    for i, file in enumerate(interview_files):
        path = await save_upload_file(file)
        text = read_text_file(path)
        records_parts.append(f"【第{i+1}轮面试记录】\n{text}")

    interview_text = "\n\n".join(records_parts)

    report = InterviewReport(
        candidate_name=candidate_name,
        job_title=job_title,
        competency_model_text=competency_text,
        interview_records_text=interview_text,
        status=ReportStatus.PROCESSING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    background_tasks.add_task(run_interview_task, report.id, competency_text, interview_text)
    return TaskResponse(task_id=report.id)


@router.get("/reports", response_model=list[InterviewReportListItem], summary="查询面试评估历史列表")
def list_reports(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    reports = (
        db.query(InterviewReport)
        .order_by(InterviewReport.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return reports


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


@router.get("/reports/{report_id}", response_model=InterviewReportResponse, summary="查询单份面试评估报告详情")
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(InterviewReport).filter(InterviewReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报告不存在")

    deviation_raw = json.loads(report.deviation_json) if report.deviation_json else {}
    evidence_raw = json.loads(report.evidence_json) if report.evidence_json else {}
    missed_raw = json.loads(report.missed_followup_json) if report.missed_followup_json else {}

    # Dify 返回 {"dimension_comparison": [...]}，提取内层数组
    deviation_list = deviation_raw.get("dimension_comparison", []) if isinstance(deviation_raw, dict) else []
    # Dify 返回 {"evidence_checks": [...]}
    evidence_list = evidence_raw.get("evidence_checks", []) if isinstance(evidence_raw, dict) else []
    # Dify 返回 {"missed_followups": [...]}
    missed_list = missed_raw.get("missed_followups", []) if isinstance(missed_raw, dict) else []

    return InterviewReportResponse(
        id=report.id,
        candidate_name=report.candidate_name,
        job_title=report.job_title,
        status=report.status.value if report.status else None,
        deviation=[DeviationItem(**item) for item in deviation_list] if deviation_list else None,
        evidence=[EvidenceItem(**item) for item in evidence_list] if evidence_list else None,
        missed_followups=[MissedFollowupItem(**item) for item in missed_list] if missed_list else None,
        consensus_level=report.consensus_level,
        full_report=_unwrap_report(report.full_report),
        error_message=report.error_message,
        duration_ms=report.duration_ms,
        created_at=report.created_at,
    )
