# HR智能招聘平台 - 后端配置
import os

# ========== 数据库配置 ==========
# 默认使用 MySQL，可通过环境变量覆盖
DATABASE_URL = os.getenv(
    "DB_URL",
    "mysql+pymysql://root:123456@localhost:3306/hr_platform?charset=utf8mb4"
)

# ========== Dify API 配置 ==========
DIFY_BASE_URL = os.getenv("DIFY_BASE_URL", "https://api.dify.ai/v1")

# 两个工作流是独立应用，各自拥有独立的 API Key
DIFY_API_KEY_MATCH = os.getenv("DIFY_API_KEY_MATCH")          # 候选人匹配筛查应用的 Key
DIFY_API_KEY_INTERVIEW = os.getenv("DIFY_API_KEY_INTERVIEW")  # 面试一致性评估应用的 Key

# 兼容旧配置：如果只配了一个 Key，两个工作流共用
_DEFAULT_KEY = os.getenv("DIFY_API_KEY")
if not DIFY_API_KEY_MATCH and _DEFAULT_KEY:
    DIFY_API_KEY_MATCH = _DEFAULT_KEY
if not DIFY_API_KEY_INTERVIEW and _DEFAULT_KEY:
    DIFY_API_KEY_INTERVIEW = _DEFAULT_KEY

# ========== Dify 工作流端点 ==========
DIFY_WORKFLOW_CANDIDATE_MATCH = os.getenv("DIFY_WORKFLOW_MATCH")      # 必须在 .env 中配置
DIFY_WORKFLOW_INTERVIEW_EVAL = os.getenv("DIFY_WORKFLOW_INTERVIEW")   # 必须在 .env 中配置

# ========== 文件上传配置 ==========
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ========== 服务配置 ==========
API_PREFIX = "/api/v1"
PROJECT_NAME = "HR智能招聘平台"
VERSION = "1.0.0"
