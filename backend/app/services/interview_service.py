import json
from app.models.interview_report import InterviewReport, ReportStatus
from app.services.dify_client import dify_client


def _to_json_str(value):
    """将 Dify 返回的值统一转为 JSON 字符串存库"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def parse_interview_result(raw_data: dict, duration_ms: int) -> dict:
    """
    解析 Dify 返回的面试一致性评估结果
    """
    full_report = _to_json_str(raw_data.get("final_report", ""))
    deviation = _to_json_str(raw_data.get("deviation", {}))
    evidence = _to_json_str(raw_data.get("evidence", {}))
    conflict = _to_json_str(raw_data.get("conflict", {}))
    missed_followup = _to_json_str(raw_data.get("missed_followup", {}))
    consensus_level = raw_data.get("consensus_level", None)

    return {
        "deviation_json": deviation,
        "evidence_json": evidence,
        "conflict_json": conflict,
        "missed_followup_json": missed_followup,
        "full_report": full_report,
        "consensus_level": consensus_level,
        "duration_ms": duration_ms,
        "status": ReportStatus.DONE,
    }


def run_interview_task(report_id: int, competency_model_text: str, interview_records_text: str):
    """
    后台任务：调用 Dify 面试一致性评估工作流并更新数据库
    """
    from app.models.database import SessionLocal
    db = SessionLocal()
    try:
        report = db.query(InterviewReport).filter(InterviewReport.id == report_id).first()
        if not report:
            return

        result = dify_client.run_interview_eval(competency_model_text, interview_records_text)

        if result["success"]:
            update_data = parse_interview_result(result["data"], result["duration_ms"])
            for key, value in update_data.items():
                setattr(report, key, value)
        else:
            report.status = ReportStatus.FAILED
            report.error_message = result["error"]

        db.commit()
    except Exception as e:
        db.rollback()
        report = db.query(InterviewReport).filter(InterviewReport.id == report_id).first()
        if report:
            report.status = ReportStatus.FAILED
            report.error_message = f"后台任务异常: {str(e)}"
            db.commit()
    finally:
        db.close()
