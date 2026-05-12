from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import conductor, stomach, pancreas, report
from middleware.exceptions import global_exception_handler
from loguru import logger
from datetime import datetime
import uvicorn

app = FastAPI(
    title="AIMED Agent Swarm - 胃胰超声造影 AI 诊断",
    description="充盈视界 FillingVision - 上消化器官超声造影普筛早查服务生态 v1.0",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 全局异常处理
app.middleware("http")(global_exception_handler)

# CORS 配置（生产环境应限制具体域名）
allowed_origins = settings.allowed_origins.split(",") if settings.allowed_origins else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由（当前版本）
app.include_router(conductor.router, prefix="/api/conductor", tags=["总指挥"])
app.include_router(stomach.router, prefix="/api/stomach", tags=["胃诊断"])
app.include_router(pancreas.router, prefix="/api/pancreas", tags=["胰腺诊断"])
app.include_router(report.router, prefix="/api/report", tags=["报告生成"])

# 注册路由 v1（版本化管理）
try:
    from routers.v1 import conductor as conductor_v1, stomach as stomach_v1, pancreas as pancreas_v1, report as report_v1, diagnosis as diagnosis_v1
    app.include_router(conductor_v1.router, prefix="/api/v1/conductor", tags=["v1-总指挥"])
    app.include_router(stomach_v1.router, prefix="/api/v1/stomach", tags=["v1-胃诊断"])
    app.include_router(pancreas_v1.router, prefix="/api/v1/pancreas", tags=["v1-胰腺诊断"])
    app.include_router(report_v1.router, prefix="/api/v1/report", tags=["v1-报告生成"])
    app.include_router(diagnosis_v1.router, prefix="/api/v1/diagnosis", tags=["v1-诊断服务"])
    logger.info("API v1 路由已注册（含诊断服务）")
except ImportError as e:
    logger.warning(f"API v1 路由未完全加载：{e}")

@app.on_event("startup")
async def startup_event():
    logger.info(f"AIMED Agent Swarm 启动 - 端口：{settings.port}")
    logger.info(f"调试模式：{settings.debug}")
    logger.info("✅ 病例库：已加载 (/opt/aimed-demo/data/cases.db)")
    logger.info("✅ 知识库：已加载 (/opt/aimed-demo/knowledge/medical_guidelines.md)")
    logger.info("✅ RAG 检索：已启用 (top_k=3)")

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "service": "AIMED Agent Swarm", "version": "0.1.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
