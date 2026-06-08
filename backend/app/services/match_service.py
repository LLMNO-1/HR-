import json
import traceback
from sqlalchemy.orm import Session
from app.models.match_report import MatchReport, ReportStatus
from app.services.dify_client import dify_client


def _to_json_str(value):
    """将 Dify 返回的值统一转为 JSON 字符串存库。
    Dify 中 LLM 节点输出是文本类型，API 返回的是字符串；
    如果 Dify 侧做了自动解析也可能是 dict，这里兼容两种。
    """
    if value is None:
        return None
    if isinstance(value, str):
        return value  # Dify 返回的已是 JSON 字符串，直接存
    return json.dumps(value, ensure_ascii=False)  # 如果是 dict，序列化


def parse_match_result(raw_data: dict, duration_ms: int) -> dict:
    """
    解析 Dify 返回的工作流输出，适配到数据库字段。
    """
    full_report = _to_json_str(raw_data.get("final_report", ""))
    hard_check = _to_json_str(raw_data.get("hard_check_result", {}))
    match_detail = _to_json_str(raw_data.get("match_score", {}))
    risks = _to_json_str(raw_data.get("risk_analysis", {}))
    match_score = raw_data.get("overall_score", None)

    return {
        "match_score": float(match_score) if match_score else None,
        "hard_check_json": hard_check,
        "match_detail_json": match_detail,
        "risk_json": risks,
        "full_report": full_report,
        "duration_ms": duration_ms,
        "status": ReportStatus.DONE,
    }


def run_match_task(report_id: int, resume_text: str, jd_text: str):
    """
    后台任务：调用 Dify 并更新数据库。
    这个函数在 FastAPI BackgroundTasks 中异步执行。
    """
    from app.models.database import SessionLocal
    db = SessionLocal()
    try:
        report = db.query(MatchReport).filter(MatchReport.id == report_id).first()
        if not report:
            return

        # 调用 Dify
        result = dify_client.run_candidate_match(resume_text, jd_text)

        if result["success"]:
            update_data = parse_match_result(result["data"], result["duration_ms"])
            for key, value in update_data.items():
                setattr(report, key, value)
        else:
            report.status = ReportStatus.FAILED
            report.error_message = result["error"]

        db.commit()
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        report = db.query(MatchReport).filter(MatchReport.id == report_id).first()
        if report:
            report.status = ReportStatus.FAILED
            report.error_message = f"后台任务异常: {str(e)}"
            db.commit()
    finally:
        db.close()
