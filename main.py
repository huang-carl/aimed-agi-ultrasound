"""
AIMED Hermes 后端 - 主入口
胃胰腺超声造影 AI 诊断平台
端口：18790

架构：
┌─────────────────────────────────────────┐
│          FastAPI Gateway (main.py)       │
│  - CORS / 静态文件 / 健康检查            │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   routers/v1/           services/
   (路由层)              (服务层)
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   agents/              model_router.py
   (智能体层)            (模型路由)
        │
   Conductor → Stomach/Pancreas/Report
"""

import os
import sys
from fastapi import FastAPI, UploadFile, File, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# ===== 导入服务层 =====
try:
    from services.diagnosis_service_v2 import DiagnosisServiceV2
    diagnosis_service_cls = DiagnosisServiceV2
    print("✅ 使用诊断服务 V2（智能降级）")
except ImportError:
    from services.diagnosis_service import DiagnosisService
    diagnosis_service_cls = DiagnosisService
    print("✅ 使用诊断服务 V1（标准模式）")

from services.vector_search_service import VectorSearchService, CHROMADB_AVAILABLE
from services.image_segmentation_service import ImageSegmentationService, SAM_AVAILABLE
from services.model_router import get_router, ModelRouter
from services.api_key_pool import get_key_pool

# ===== 导入智能体层 =====
from agents.conductor_agent import conductor_agent
from agents.stomach_agent import stomach_agent
from agents.pancreas_agent import pancreas_agent
from agents.report_agent import report_agent

# ===== 导入路由层 =====
from routers.v1 import diagnosis, conductor, cases, stomach, pancreas, report, blockchain

# 创建 FastAPI 应用
app = FastAPI(
    title="AIMED Hermes - 胃胰腺超声造影 AI 诊断",
    description="基于口服超声造影剂 + AI 多智能体诊断的胃胰疾病早筛平台",
    version="2.1.0",
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

# 全局服务实例
diagnosis_service = None
vector_search = None
segmentation_service = None
model_router = None
key_pool = None


@app.on_event("startup")
async def startup_event():
    """应用启动事件 - 分层初始化"""
    global diagnosis_service, vector_search, segmentation_service, model_router, key_pool
    
    print("=" * 60)
    print("AIMED Hermes 后端启动 v2.1.0")
    print("=" * 60)
    
    # 1. 初始化模型路由层
    try:
        model_router = get_router()
        print(f"✅ 模型路由已初始化 - 提供商: {list(model_router.providers.keys())}")
    except Exception as e:
        print(f"⚠️ 模型路由初始化失败: {e}")
    
    # 2. 初始化 Key 池
    try:
        key_pool = get_key_pool()
        print(f"✅ Key 池已初始化")
    except Exception as e:
        print(f"⚠️ Key 池初始化失败: {e}")
    
    # 3. 初始化诊断服务
    try:
        diagnosis_service = diagnosis_service_cls()
        print("✅ 诊断服务已初始化")
    except Exception as e:
        print(f"⚠️ 诊断服务初始化失败: {e}")
    
    # 4. 初始化向量检索服务
    if CHROMADB_AVAILABLE:
        try:
            vector_search = VectorSearchService(
                provider="chromadb",
                persist_dir="./data/vectors/medical"
            )
            print(f"✅ 向量检索服务已初始化 - 文档数: {vector_search.get_stats().get('document_count', 0)}")
        except Exception as e:
            print(f"⚠️ 向量检索服务初始化失败: {e}")
    else:
        print("⚠️ ChromaDB 未安装，跳过向量检索服务")
    
    # 5. 初始化图像分割服务
    if SAM_AVAILABLE:
        try:
            segmentation_service = ImageSegmentationService(model_type="vit_b")
            info = segmentation_service.get_model_info()
            if info['model_loaded']:
                print(f"✅ 图像分割服务已初始化 - 模型: {info['model_type']}")
            else:
                print("⚠️ SAM 模型未加载（需要下载权重）")
        except Exception as e:
            print(f"⚠️ 图像分割服务初始化失败: {e}")
    else:
        print("⚠️ SAM 未安装，跳过图像分割服务")
    
    # 6. 注册智能体到 Conductor
    try:
        conductor_agent.register_agent("stomach", stomach_agent)
        conductor_agent.register_agent("pancreas", pancreas_agent)
        conductor_agent.register_agent("report", report_agent)
        print(f"✅ 智能体注册完成 - {len(conductor_agent.agent_registry)} 个 Agent")
    except Exception as e:
        print(f"⚠️ 智能体注册失败: {e}")
    
    # 7. 挂载路由层
    try:
        app.include_router(diagnosis.router, prefix="/api/v1/diagnosis", tags=["v1-诊断服务"])
        app.include_router(conductor.router, prefix="/api/v1/conductor", tags=["v1-总指挥"])
        app.include_router(cases.router, prefix="/api/v1/cases", tags=["v1-病例管理"])
        app.include_router(stomach.router, prefix="/api/v1/stomach", tags=["v1-胃部诊断"])
        app.include_router(pancreas.router, prefix="/api/v1/pancreas", tags=["v1-胰腺诊断"])
        app.include_router(report.router, prefix="/api/v1/report", tags=["v1-报告生成"])
        app.include_router(blockchain.router, prefix="/api/v1", tags=["v1-区块链服务"])
        print("✅ API 路由层已挂载 (6 个路由组)")
    except Exception as e:
        print(f"⚠️ 路由挂载失败: {e}")
    
    # 8. 挂载静态文件
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"✅ 静态文件目录已挂载：{static_dir}")
    
    # 9. 挂载 AI 平台入口
    portal_dir = os.path.join(os.path.dirname(__file__), "static", "portal")
    if os.path.exists(portal_dir):
        # 不挂载整个目录，改为显式路由
        print(f"✅ AI 平台入口目录已就绪：{portal_dir}")
    
    print("=" * 60)


# ===== 全局端点（健康检查 + 系统状态） =====

@app.get("/portal")
@app.get("/portal/")
async def portal_index():
    """AI 平台入口页"""
    from fastapi.responses import FileResponse
    portal_dir = os.path.join(os.path.dirname(__file__), "static", "portal")
    return FileResponse(os.path.join(portal_dir, "index.html"))


@app.get("/portal/{page}.html")
async def portal_page(page: str):
    """AI 平台页面"""
    from fastapi.responses import FileResponse
    portal_dir = os.path.join(os.path.dirname(__file__), "static", "portal")
    page_file = os.path.join(portal_dir, f"{page}.html")
    
    # 安全检查：防止路径遍历
    if not os.path.abspath(page_file).startswith(os.path.abspath(portal_dir)):
        raise HTTPException(status_code=404, detail="页面不存在")
    
    if os.path.exists(page_file):
        return FileResponse(page_file)
    raise HTTPException(status_code=404, detail="页面不存在")


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "AIMED Hermes",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "diagnosis": diagnosis_service is not None,
            "vector_search": vector_search is not None,
            "segmentation": segmentation_service is not None,
            "model_router": model_router is not None,
            "key_pool": key_pool is not None,
            "conductor": len(conductor_agent.agent_registry)
        }
    }


@app.get("/api/v1/status")
async def get_status():
    """获取系统状态"""
    status = {
        "service": "AIMED Hermes",
        "version": "2.1.0",
        "timestamp": datetime.now().isoformat(),
        "architecture": {
            "gateway": "FastAPI (main.py)",
            "router_layer": "routers/v1/ (7 组)",
            "service_layer": "services/ (12 个服务)",
            "agent_layer": "agents/ (4 个 Agent)"
        },
        "models": {
            "primary": os.getenv('DASHSCOPE_MODEL', 'qwen-plus'),
            "nvidia": os.getenv('NVIDIA_MODEL', 'meta/llama-3.3-70b-instruct') if os.getenv('NVIDIA_API_KEY') else None
        },
        "features": {
            "diagnosis": diagnosis_service is not None,
            "vector_search": vector_search is not None,
            "segmentation": segmentation_service is not None,
            "model_router": model_router is not None,
            "mock_mode": os.getenv('MOCK_MODE', 'true').lower() == 'true'
        },
        "agents": {
            "registered": list(conductor_agent.agent_registry.keys()),
            "statistics": conductor_agent.get_statistics()
        }
    }
    
    if vector_search:
        status["vector_search"] = vector_search.get_stats()
    
    if segmentation_service:
        status["segmentation"] = segmentation_service.get_model_info()
    
    if model_router:
        status["model_router"] = model_router.get_stats()
    
    if key_pool:
        status["key_pool"] = key_pool.get_stats()
    
    return status


# ===== 全局端点（保留兼容） =====

@app.post("/api/v1/segment")
async def segment_image(file: UploadFile = File(...)):
    """图像分割接口（全局保留）"""
    if not segmentation_service:
        raise HTTPException(status_code=503, detail="图像分割服务不可用")
    
    upload_dir = "./data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    result = segmentation_service.auto_segment(file_path)
    result['filename'] = file.filename
    result['file_size'] = len(content)
    
    return result


@app.post("/api/v1/knowledge/add")
async def add_knowledge(
    text: str = Query(..., description="知识文本"),
    organ: str = Query(..., description="器官类型"),
    disease: str = Query("", description="疾病类型"),
    doc_id: Optional[str] = Query(None, description="文档 ID")
):
    """添加知识库文档"""
    if not vector_search:
        raise HTTPException(status_code=503, detail="向量检索服务不可用")
    
    metadata = {
        "organ": organ,
        "disease": disease,
        "type": "knowledge",
        "timestamp": datetime.now().isoformat()
    }
    
    doc_id = vector_search.add_document(text, metadata, doc_id)
    
    return {
        "success": True,
        "doc_id": doc_id,
        "total_documents": vector_search.get_stats().get('document_count', 0)
    }


@app.get("/api/v1/knowledge/search")
async def search_knowledge(
    query: str = Query(..., description="搜索查询"),
    top_k: int = Query(5, description="返回结果数"),
    organ: Optional[str] = Query(None, description="器官过滤")
):
    """搜索知识库"""
    if not vector_search:
        raise HTTPException(status_code=503, detail="向量检索服务不可用")
    
    filter_metadata = {"organ": organ} if organ else None
    results = vector_search.search(query, top_k, filter_metadata)
    
    return {
        "query": query,
        "result_count": len(results),
        "results": results
    }


@app.get("/api/v1/models")
async def list_models():
    """列出可用模型"""
    models_info = {
        "primary": {
            "name": os.getenv('DASHSCOPE_MODEL', 'qwen-plus'),
            "provider": "aliyun"
        },
        "fallback": {
            "name": os.getenv('NVIDIA_MODEL', 'meta/llama-3.3-70b-instruct'),
            "provider": "nvidia"
        } if os.getenv('NVIDIA_API_KEY') else None,
        "routing": "smart (智能降级)"
    }
    
    # 如果 model_router 可用，补充详细信息
    if model_router:
        models_info["providers"] = model_router.get_stats()
    
    return models_info


# ===== 公开诊断 API（无需认证，限流） =====

_public_diagnose_count = {}  # IP -> count

@app.post("/api/v1/public/diagnose")
async def public_diagnose(
    organ: str = Query(..., description="器官类型（胃/胰腺）"),
    image_description: str = Query(..., description="影像描述"),
    context: Optional[str] = Query("", description="病历信息"),
    filling_status: str = Query("已充盈", description="充盈状态"),
    request: Request = None
):
    """公开诊断 API（无需认证，限流 100 次/天/IP）"""
    client_ip = request.client.host if request else "unknown"
    today = datetime.now().strftime('%Y-%m-%d')
    key = f"{client_ip}:{today}"
    
    if key not in _public_diagnose_count:
        _public_diagnose_count[key] = 0
    
    if _public_diagnose_count[key] >= 100:
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    
    _public_diagnose_count[key] += 1
    
    if not diagnosis_service:
        raise HTTPException(status_code=503, detail="诊断服务不可用")
    
    result = diagnosis_service.diagnose(
        organ=organ,
        image_description=image_description,
        context=context,
        filling_status=filling_status
    )
    
    result['api'] = 'public'
    result['remaining'] = 100 - _public_diagnose_count[key]
    
    return result


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', '18790'))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    print(f"启动 AIMED Hermes 后端 - 端口：{port}")
    print(f"调试模式：{debug}")
    print(f"API 文档：http://localhost:{port}/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info" if debug else "warning"
    )
