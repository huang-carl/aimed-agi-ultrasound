from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import conductor, stomach, pancreas, report
from middleware.exceptions import global_exception_handler
from loguru import logger
import uvicorn

app = FastAPI(
    title="AIMED Agent Swarm - 胃胰超声造影 AI 诊断",
    description="聚焦胃 + 胰腺 2 器官的充盈超声造影 AI 辅助诊断系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 全局异常处理
app.middleware("http")(global_exception_handler)

# CORS 配置（生产环境应限制具体域名）
allowed_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else ["*"]
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
    from routers.v1 import conductor as conductor_v1, stomach as stomach_v1, pancreas as pancreas_v1, report as report_v1
    app.include_router(conductor_v1.router, prefix="/api/v1/conductor", tags=["v1-总指挥"])
    app.include_router(stomach_v1.router, prefix="/api/v1/stomach", tags=["v1-胃诊断"])
    app.include_router(pancreas_v1.router, prefix="/api/v1/pancreas", tags=["v1-胰腺诊断"])
    app.include_router(report_v1.router, prefix="/api/v1/report", tags=["v1-报告生成"])
    logger.info("API v1 路由已注册")
except ImportError as e:
    logger.warning(f"API v1 路由未完全加载：{e}")

@app.on_event("startup")
async def startup_event():
    logger.info(f"AIMED Agent Swarm 启动 - 端口：{settings.port}")
    logger.info(f"调试模式：{settings.debug}")

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "service": "AIMED Agent Swarm", "version": "0.1.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
