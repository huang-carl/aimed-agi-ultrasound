from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from routers import conductor, stomach, pancreas, report
from middleware.exceptions import global_exception_handler
from loguru import logger
import uvicorn
import os

app = FastAPI(
    title="AIMED Agent Swarm - 胃胰超声造影 AI 诊断",
    description="聚焦胃 + 胰腺 2 器官的充盈超声造影 AI 辅助诊断系统",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 挂载静态文件目录（Demo 演示页面）
static_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    logger.info(f"✅ 静态文件目录已挂载：{static_path}")

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
    from routers.v1 import conductor as conductor_v1, stomach as stomach_v1, pancreas as pancreas_v1, report as report_v1, diagnosis as diagnosis_v1, cases as cases_v1
    app.include_router(conductor_v1.router, prefix="/api/v1/conductor", tags=["v1-总指挥"])
    app.include_router(stomach_v1.router, prefix="/api/v1/stomach", tags=["v1-胃诊断"])
    app.include_router(pancreas_v1.router, prefix="/api/v1/pancreas", tags=["v1-胰腺诊断"])
    app.include_router(report_v1.router, prefix="/api/v1/report", tags=["v1-报告生成"])
    app.include_router(diagnosis_v1.router, prefix="/api/v1/diagnosis", tags=["v1-诊断服务"])
    app.include_router(cases_v1.router, prefix="/api/v1/cases", tags=["v1-病例管理"])
    logger.info("API v1 路由已注册（含双模型诊断服务 + 病例管理）")
except ImportError as e:
    logger.warning(f"API v1 路由未完全加载：{e}")

@app.on_event("startup")
async def startup_event():
    logger.info(f"AIMED Agent Swarm 启动 - 端口：{settings.port}")
    logger.info(f"调试模式：{settings.debug}")
    logger.info("✅ 病例库：已加载 (/opt/aimed-demo/data/cases.db)")
    logger.info("✅ 知识库：已加载 (/opt/aimed-demo/knowledge/medical_guidelines.md)")
    logger.info("✅ RAG 检索：已启用 (top_k=3)")

@app.get("/", tags=["首页"])
async def root():
    """重定向到 Demo 演示页面"""
    from fastapi.responses import FileResponse
    demo_path = os.path.join(static_path, "demo.html")
    if os.path.exists(demo_path):
        return FileResponse(demo_path)
    return {"message": "AIMED Agent Swarm", "docs": "/docs", "demo": "/static/demo.html"}

@app.get("/health", tags=["健康检查"])
async def health_check():
    return {"status": "ok", "service": "AIMED Agent Swarm", "version": "0.1.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
