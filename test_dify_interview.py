import requests
import json

# 模块二的 API Key
API_KEY = "app-RCQb9U7tH0WzYcYp9P8IEuv8"

r = requests.post(
    "https://api.dify.ai/v1/workflows/run",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "inputs": {
            "competency_model_text": "测试",
            "interview_records_text": "测试",
        },
        "response_mode": "blocking",
        "user": "test",
    },
    timeout=60,
)

print(f"状态码: {r.status_code}")
print(f"响应内容:")
print(json.dumps(r.json(), ensure_ascii=False, indent=2)[:1000])
