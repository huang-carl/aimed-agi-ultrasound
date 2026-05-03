"""
AIMED Hermes - 文件上传 API
功能：文件上传、文档管理、知识库集成
"""
import os
import json
import hashlib
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from routers.v1.auth import verify_token, require_role

router = APIRouter(tags=["文件上传"])

# ============================================
# 配置
# ============================================
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../data/uploads")
DOC_DIR = os.path.join(os.path.dirname(__file__), "../../data/documents")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_TYPES = {
    "document": [".pdf", ".doc", ".docx", ".txt", ".md", ".xlsx", ".xls", ".ppt", ".pptx"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg"],
    "data": [".json", ".csv", ".xml"],
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# ============================================
# 文档数据库
# ============================================
def get_docs_db_path():
    return os.path.join(DOC_DIR, "documents.json")

def load_docs_db():
    path = get_docs_db_path()
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"documents": [], "version": "1.0"}

def save_docs_db(data):
    path = get_docs_db_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================
# 请求模型
# ============================================
class UploadResponse(BaseModel):
    success: bool
    file_id: str
    filename: str
    file_size: int
    file_type: str
    category: str
    uploaded_at: str
    url: str

class DocumentInfo(BaseModel):
    id: str
    filename: str
    file_size: int
    file_type: str
    category: str
    company: str
    uploader: str
    tags: List[str] = []
    status: str = "active"
    created_at: str
    updated_at: str

# ============================================
# 工具函数
# ============================================
def get_file_category(filename: str) -> str:
    """根据文件扩展名判断文件类型"""
    ext = os.path.splitext(filename)[1].lower()
    for cat, extensions in ALLOWED_TYPES.items():
        if ext in extensions:
            return cat
    return "other"

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return os.path.splitext(filename)[1].lower()

def generate_file_id(filename: str, content: bytes) -> str:
    """生成唯一文件 ID"""
    hash_val = hashlib.md5(content + filename.encode() + datetime.now(timezone.utc).isoformat().encode()).hexdigest()[:12]
    return f"doc_{hash_val}"

# ============================================
# API 路由
# ============================================
@router.post("/", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    company: Optional[str] = Form(None),
    token_data: dict = Depends(verify_token),
):
    """
    上传文件
    
    - **file**: 上传的文件（最大 50MB）
    - **category**: 文件分类（document/image/data）
    - **tags**: 标签（逗号分隔）
    - **company**: 所属公司
    """
    # 读取文件内容
    content = await file.read()
    
    # 检查文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"文件过大，最大允许 {MAX_FILE_SIZE // 1024 // 1024}MB")
    
    # 检查文件类型
    ext = get_file_extension(file.filename)
    all_allowed = []
    for exts in ALLOWED_TYPES.values():
        all_allowed.extend(exts)
    if ext not in all_allowed:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型：{ext}")
    
    # 生成文件 ID
    file_id = generate_file_id(file.filename, content)
    
    # 确定文件分类
    file_category = category or get_file_category(file.filename)
    
    # 保存文件
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")
    with open(file_path, 'wb') as f:
        f.write(content)
    
    # 更新文档数据库
    db = load_docs_db()
    now = datetime.now(timezone.utc).isoformat()
    
    doc = {
        "id": file_id,
        "filename": file.filename,
        "file_size": len(content),
        "file_type": ext,
        "category": file_category,
        "company": company or token_data.get("company", ""),
        "uploader": token_data.get("username", ""),
        "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    
    db["documents"].append(doc)
    save_docs_db(db)
    
    return UploadResponse(
        success=True,
        file_id=file_id,
        filename=file.filename,
        file_size=len(content),
        file_type=ext,
        category=file_category,
        uploaded_at=now,
        url=f"/api/v1/upload/{file_id}",
    )

@router.get("/list")
async def list_documents(
    category: Optional[str] = None,
    company: Optional[str] = None,
    include_stats: bool = False,
    token_data: dict = Depends(verify_token),
):
    """获取文档列表"""
    db = load_docs_db()
    docs = db["documents"]
    
    if category:
        docs = [d for d in docs if d.get("category") == category]
    if company:
        docs = [d for d in docs if d.get("company") == company]
    
    # 只返回基本信息（不包含文件内容）
    result = []
    for doc in docs:
        result.append({
            "id": doc["id"],
            "filename": doc["filename"],
            "file_size": doc["file_size"],
            "file_type": doc["file_type"],
            "category": doc["category"],
            "company": doc.get("company", ""),
            "uploader": doc.get("uploader", ""),
            "tags": doc.get("tags", []),
            "status": doc.get("status", "active"),
            "created_at": doc.get("created_at", ""),
        })
    
    response = {
        "documents": result,
        "total": len(result),
    }
    
    # 如果需要统计信息
    if include_stats:
        stats = {
            "total_files": len(db["documents"]),
            "total_size": sum(d.get("file_size", 0) for d in db["documents"]),
            "by_category": {},
            "by_company": {},
        }
        
        for doc in db["documents"]:
            cat = doc.get("category", "other")
            company = doc.get("company", "unknown")
            
            if cat not in stats["by_category"]:
                stats["by_category"][cat] = {"count": 0, "size": 0}
            stats["by_category"][cat]["count"] += 1
            stats["by_category"][cat]["size"] += doc.get("file_size", 0)
            
            if company not in stats["by_company"]:
                stats["by_company"][company] = {"count": 0, "size": 0}
            stats["by_company"][company]["count"] += 1
            stats["by_company"][company]["size"] += doc.get("file_size", 0)
        
        response["stats"] = stats
    
    return response

@router.post("/to-knowledge")
async def upload_to_knowledge(
    file_id: str = Form(...),
    title: str = Form(...),
    category: str = Form(...),
    subcategory: str = Form(...),
    summary: str = Form(""),
    token_data: dict = Depends(require_role(50)),  # editor 以上
):
    """将上传的文件添加到知识库"""
    # 获取文件信息
    db = load_docs_db()
    doc = next((d for d in db["documents"] if d["id"] == file_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 添加到知识库
    from routers.v1.knowledge import load_kb, save_kb
    kb = load_kb()
    
    now = datetime.now(timezone.utc).isoformat()
    kb_doc = {
        "id": f"kb_{doc['id']}",
        "title": title,
        "category": category,
        "subcategory": subcategory,
        "tags": doc.get("tags", []),
        "content": f"附件：{doc['filename']} ({doc['file_size']} bytes)",
        "summary": summary,
        "author": token_data.get("username", ""),
        "company": token_data.get("company", ""),
        "status": "published",
        "views": 0,
        "created_at": now,
        "updated_at": now,
        "attachments": [{"id": file_id, "filename": doc["filename"], "size": doc["file_size"]}],
    }
    
    kb["documents"].append(kb_doc)
    save_kb(kb)
    
    return {"success": True, "knowledge_id": kb_doc["id"]}

@router.get("/{file_id}")
async def get_document(
    file_id: str,
    token_data: dict = Depends(verify_token),
):
    """下载文件"""
    db = load_docs_db()
    doc = next((d for d in db["documents"] if d["id"] == file_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{doc['file_type']}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件已丢失")
    
    # 返回文件
    return FileResponse(
        file_path,
        filename=doc["filename"],
        media_type="application/octet-stream",
    )

@router.delete("/{file_id}")
async def delete_document(
    file_id: str,
    token_data: dict = Depends(require_role(80)),  # admin 以上
):
    """删除文件"""
    db = load_docs_db()
    doc = next((d for d in db["documents"] if d["id"] == file_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 删除物理文件
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{doc['file_type']}")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 更新数据库
    db["documents"] = [d for d in db["documents"] if d["id"] != file_id]
    save_docs_db(db)
    
    return {"success": True, "deleted": file_id}
