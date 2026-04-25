"""
AIMED Hermes 后端 - 主入口
胃胰腺超声造影 AI 诊断平台
端口：18790
"""

import os
import sys
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入服务
from services.diagnosis_service import DiagnosisService
from services.vector_search_service import VectorSearchService, CHROMADB_AVAILABLE
from services.image_segmentation_service import ImageSegmentationService, SAM_AVAILABLE

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title="AIMED Hermes - 胃胰腺超声造影 AI 诊断",
    description="基于口服超声造影剂 + AI 多智能体诊断的胃胰疾病早筛平台",
    version="2.0.0",
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


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global diagnosis_service, vector_search, segmentation_service
    
    print("=" * 60)
    print("AIMED Hermes 后端启动")
    print("=" * 60)
    
    # 初始化诊断服务
    try:
        diagnosis_service = DiagnosisService()
        print("✅ 诊断服务已初始化")
    except Exception as e:
        print(f"⚠️ 诊断服务初始化失败: {e}")
    
    # 初始化向量检索服务
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
    
    # 初始化图像分割服务
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
    
    # 挂载静态文件
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"✅ 静态文件目录已挂载：{static_dir}")
    
    print("=" * 60)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "AIMED Hermes",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "diagnosis": diagnosis_service is not None,
            "vector_search": vector_search is not None,
            "segmentation": segmentation_service is not None
        }
    }


@app.get("/api/v1/status")
async def get_status():
    """获取系统状态"""
    status = {
        "service": "AIMED Hermes",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "models": {
            "primary": os.getenv('DASHSCOPE_MODEL', 'qwen-plus'),
            "nvidia": os.getenv('NVIDIA_MODEL', 'meta/llama-3.3-70b-instruct') if os.getenv('NVIDIA_API_KEY') else None
        },
        "features": {
            "diagnosis": diagnosis_service is not None,
            "vector_search": vector_search is not None,
            "segmentation": segmentation_service is not None,
            "mock_mode": os.getenv('MOCK_MODE', 'true').lower() == 'true'
        }
    }
    
    if vector_search:
        status["vector_search"] = vector_search.get_stats()
    
    if segmentation_service:
        status["segmentation"] = segmentation_service.get_model_info()
    
    return status


@app.post("/api/v1/diagnose")
async def diagnose(
    organ: str = Query(..., description="器官类型（胃/胰腺）"),
    image_description: str = Query(..., description="影像描述"),
    context: Optional[str] = Query("", description="病历信息"),
    filling_status: str = Query("已充盈", description="充盈状态")
):
    """诊断接口"""
    if not diagnosis_service:
        raise HTTPException(status_code=503, detail="诊断服务不可用")
    
    result = diagnosis_service.diagnose(
        organ=organ,
        image_description=image_description,
        context=context,
        filling_status=filling_status
    )
    
    return result


@app.post("/api/v1/segment")
async def segment_image(file: UploadFile = File(...)):
    """图像分割接口"""
    if not segmentation_service:
        raise HTTPException(status_code=503, detail="图像分割服务不可用")
    
    # 保存上传的文件
    upload_dir = "./data/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 执行自动分割
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
    return {
        "primary": {
            "name": os.getenv('DASHSCOPE_MODEL', 'qwen-plus'),
            "provider": "aliyun"
        },
        "fallback": {
            "name": os.getenv('NVIDIA_MODEL', 'meta/llama-3.3-70b-instruct'),
            "provider": "nvidia"
        } if os.getenv('NVIDIA_API_KEY') else None,
        "routing": os.getenv('MODEL_ROUTING', 'smart')
    }


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
