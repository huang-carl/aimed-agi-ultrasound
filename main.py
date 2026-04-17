from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import conductor, stomach, pancreas, report
from loguru import logger
import uvicorn

app = FastAPI(
    title="AIMED Agent Swarm - 胃胰超声造影 AI 诊断",
    description="聚焦胃 + 胰腺 2 器官的充盈超声造影 AI 辅助诊断系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(conductor.router, prefix="/api/conductor", tags=["总指挥"])
app.include_router(stomach.router, prefix="/api/stomach", tags=["胃诊断"])
app.include_router(pancreas.router, prefix="/api/pancreas", tags=["胰腺诊断"])
app.include_router(report.router, prefix="/api/report", tags=["报告生成"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"AIMED Agent Swarm 启动 - 端口：{settings.port}")
    logger.info(f"调试模式：{settings.debug}")

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "service": "AIMED Agent Swarm", "version": "0.1.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
