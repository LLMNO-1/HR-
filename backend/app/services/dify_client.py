import time
import json
import requests
from app.config import DIFY_BASE_URL, DIFY_API_KEY_MATCH, DIFY_API_KEY_INTERVIEW, DIFY_WORKFLOW_CANDIDATE_MATCH, DIFY_WORKFLOW_INTERVIEW_EVAL


class DifyClient:
    """Dify 工作流 API 封装"""

    def __init__(self):
        self.base_url = DIFY_BASE_URL.rstrip("/")

    def _headers(self, api_key: str) -> dict:
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _run_workflow_blocking(self, workflow_id: str, api_key: str, inputs: dict, user: str = "hr-platform") -> dict:
        """阻塞模式：适合快速工作流"""
        url = f"{self.base_url}/workflows/run"
        payload = {"inputs": inputs, "response_mode": "blocking", "user": user}
        try:
            response = requests.post(
                url, headers=self._headers(api_key), json=payload, timeout=300
            )
            response.raise_for_status()
            result = response.json()
            if "data" in result and "outputs" in result["data"]:
                return {"success": True, "data": result["data"]["outputs"]}
            return {"success": False, "error": f"Unexpected response format: {result}"}
        except requests.Timeout:
            return {"success": False, "error": "Dify 工作流执行超时（超过300秒）"}
        except requests.ConnectionError:
            return {"success": False, "error": f"无法连接到 Dify 服务: {self.base_url}"}
        except requests.HTTPError as e:
            return {"success": False, "error": f"Dify API 错误: {e.response.status_code} - {e.response.text[:200]}"}
        except Exception as e:
            return {"success": False, "error": f"调用 Dify 异常: {str(e)}"}

    def _run_workflow_streaming(self, workflow_id: str, api_key: str, inputs: dict, user: str = "hr-platform") -> dict:
        """流式模式：适合长耗时工作流，不受网关100秒超时限制"""
        url = f"{self.base_url}/workflows/run"
        payload = {"inputs": inputs, "response_mode": "streaming", "user": user}
        try:
            response = requests.post(
                url, headers=self._headers(api_key), json=payload,
                timeout=600, stream=True  # 10分钟超时，流式读取
            )
            response.raise_for_status()

            final_outputs = None
            for line in response.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                try:
                    event = json.loads(line[6:])  # 去掉 "data: " 前缀
                except json.JSONDecodeError:
                    continue
                # workflow_finished 事件包含最终 outputs
                if event.get("event") == "workflow_finished":
                    final_outputs = event.get("data", {}).get("outputs", {})

            if final_outputs is not None:
                return {"success": True, "data": final_outputs}
            return {"success": False, "error": "流式响应未收到 workflow_finished 事件"}
        except requests.Timeout:
            return {"success": False, "error": "Dify 工作流执行超时（超过600秒）"}
        except requests.ConnectionError:
            return {"success": False, "error": f"无法连接到 Dify 服务: {self.base_url}"}
        except requests.HTTPError as e:
            return {"success": False, "error": f"Dify API 错误: {e.response.status_code} - {e.response.text[:200]}"}
        except Exception as e:
            return {"success": False, "error": f"调用 Dify 异常: {str(e)}"}

    def run_candidate_match(self, resume_text: str, jd_text: str) -> dict:
        """
        执行候选人匹配筛查工作流

        注意：Dify 工作流的输入变量名需要与这里一致。
        如果 Dify 中变量名为 resume_text 和 jd_text，则无需修改。
        如果不同，请修改 inputs 中的 key。

        修改：从 blocking 改为 streaming 模式，避免 Cloudflare 100 秒网关超时（504）
        blocking 模式下，Cloudflare 代理会在 ~100s 切断长连接，返回 HTML 错误页；
        streaming 模式逐块推送 SSE 事件，不受网关超时限制，适合多 LLM 节点工作流。
        """
        start = time.time()
        result = self._run_workflow_streaming(  # 改用 streaming，避免 Cloudflare 504 超时
            workflow_id=DIFY_WORKFLOW_CANDIDATE_MATCH,
            api_key=DIFY_API_KEY_MATCH,
            inputs={
                "resume_text": resume_text,
                "jd_text": jd_text,
            },
        )
        elapsed_ms = int((time.time() - start) * 1000)
        result["duration_ms"] = elapsed_ms
        return result

    def run_interview_eval(self, competency_model_text: str, interview_records_text: str) -> dict:
        """
        执行面试一致性评估工作流
        """
        start = time.time()
        result = self._run_workflow_streaming(
            workflow_id=DIFY_WORKFLOW_INTERVIEW_EVAL,
            api_key=DIFY_API_KEY_INTERVIEW,
            inputs={
                "competency_model_text": competency_model_text,
                "interview_records_text": interview_records_text,
            },
        )
        elapsed_ms = int((time.time() - start) * 1000)
        result["duration_ms"] = elapsed_ms
        return result


# 全局单例
dify_client = DifyClient()
