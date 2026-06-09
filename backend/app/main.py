from dotenv import load_dotenv
load_dotenv()  # 必须在 import config 之前执行，加载 .env 到环境变量

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import API_PREFIX, PROJECT_NAME, VERSION
from app.models.database import init_db
from app.api import match, interview, dashboard  # dashboard 为新增的统计 API


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时初始化数据库表"""
    init_db()
    yield


app = FastAPI(
    title=PROJECT_NAME,
    version=VERSION,
    description="基于 Dify + FastAPI 的 HR 智能招聘平台 — 候选人匹配筛查 & 面试一致性评估",
    lifespan=lifespan,
)

# 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 生产环境改为前端具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(match.router, prefix=API_PREFIX)
app.include_router(interview.router, prefix=API_PREFIX)
app.include_router(dashboard.router, prefix=API_PREFIX)  # 新增：Dashboard 统计页 API


@app.get("/")
def root():
    return {
        "service": PROJECT_NAME,
        "version": VERSION,
        "docs": f"{API_PREFIX}/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
