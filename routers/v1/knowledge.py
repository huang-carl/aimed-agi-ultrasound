"""
AIMED Hermes - 统一知识库 API
知识中心：统一知识库 + 分类管理 + 权限控制
"""
import os
import json
import hashlib
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from routers.v1.auth import verify_token, require_role, ROLE_PERMISSIONS

router = APIRouter(prefix="/kb", tags=["统一知识库"])

# ============================================
# 知识库分类体系
# ============================================
KNOWLEDGE_CATEGORIES = {
    "medical": {
        "name": "医疗诊断",
        "icon": "🏥",
        "subcategories": [
            {"id": "stomach", "name": "胃部诊断"},
            {"id": "pancreas", "name": "胰腺诊断"},
            {"id": "biliary", "name": "胆管诊断"},
            {"id": "esophagus", "name": "食道诊断"},
        ]
    },
    "product": {
        "name": "产品知识",
        "icon": "📦",
        "subcategories": [
            {"id": "contrast", "name": "口服造影剂"},
            {"id": "longnao", "name": "龙脑抑菌液"},
            {"id": "tianxia", "name": "天下牌系列"},
            {"id": "aius", "name": "AI 诊断系统"},
        ]
    },
    "technology": {
        "name": "技术文档",
        "icon": "🔧",
        "subcategories": [
            {"id": "api", "name": "API 文档"},
            {"id": "architecture", "name": "系统架构"},
            {"id": "algorithm", "name": "算法模型"},
            {"id": "blockchain", "name": "区块链"},
        ]
    },
    "compliance": {
        "name": "合规认证",
        "icon": "📋",
        "subcategories": [
            {"id": "nmpa", "name": "NMPA 申报"},
            {"id": "ethics", "name": "伦理审批"},
            {"id": "quality", "name": "质量控制"},
            {"id": "certification", "name": "产品认证"},
        ]
    },
    "sales": {
        "name": "销售支持",
        "icon": "💼",
        "subcategories": [
            {"id": "training", "name": "培训资料"},
            {"id": "marketing", "name": "营销素材"},
            {"id": "cases", "name": "成功案例"},
            {"id": "faq", "name": "常见问题"},
        ]
    },
    "research": {
        "name": "科研合作",
        "icon": "🎓",
        "subcategories": [
            {"id": "papers", "name": "学术论文"},
            {"id": "clinical", "name": "临床试验"},
            {"id": "partners", "name": "合作伙伴"},
            {"id": "data", "name": "数据集"},
        ]
    },
}

# ============================================
# 知识库文档模型
# ============================================
class KnowledgeDoc(BaseModel):
    id: str
    title: str
    category: str
    subcategory: str
    tags: List[str] = []
    content: str = ""
    summary: str = ""
    author: str = ""
    company: str = ""
    status: str = "published"  # draft/published/archived
    views: int = 0
    created_at: str = ""
    updated_at: str = ""
    attachments: List[Dict[str, str]] = []

class KnowledgeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str
    subcategory: str
    tags: List[str] = []
    content: str = ""
    summary: str = ""
    status: str = "published"

class KnowledgeUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None

class KnowledgeSearch(BaseModel):
    query: str = Field(..., min_length=1)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)

# ============================================
# 知识库存储（生产环境使用 PostgreSQL）
# ============================================
KB_DIR = os.path.join(os.path.dirname(__file__), "../../data/knowledge")
os.makedirs(KB_DIR, exist_ok=True)

def get_kb_path():
    return os.path.join(KB_DIR, "knowledge_base.json")

def load_kb():
    path = get_kb_path()
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"documents": [], "version": "1.0"}

def save_kb(data):
    path = get_kb_path()
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================
# 初始化示例数据
# ============================================
def init_sample_data():
    kb = load_kb()
    if len(kb["documents"]) > 0:
        return kb
    
    now = datetime.now(timezone.utc).isoformat()
    kb["documents"] = [
        {
            "id": "kb_001",
            "title": "口服超声造影剂产品手册",
            "category": "product",
            "subcategory": "contrast",
            "tags": ["造影剂", "产品手册", "口服"],
            "content": "AIMED 口服超声造影剂系列包含三款产品：胰腺型、胃肠型、胆管型。每款产品针对特定器官优化配方，安全无创，显著提升超声成像质量。",
            "summary": "三款口服超声造影剂产品详细介绍",
            "author": "AIMED 产品部",
            "company": "阿尔麦德",
            "status": "published",
            "views": 156,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "kb_002",
            "title": "龙脑抑菌液产品手册",
            "category": "product",
            "subcategory": "longnao",
            "tags": ["龙脑", "抑菌液", "天然植物"],
            "content": "龙脑抑菌液精选天然龙脑叶提取精华，纯植物配方，对人体温和无刺激。经权威机构检测，2 分钟抑菌率达 97.86%，20 分钟抑菌率超 99.98%。适用于慢性鼻炎辅助治疗、痔疮护理、医院感染控制、皮肤病防治等场景。",
            "summary": "龙脑抑菌液产品详细介绍和应用场景",
            "author": "天下牌产品部",
            "company": "东亚医药",
            "status": "published",
            "views": 89,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "kb_003",
            "title": "天下牌系列产品介绍",
            "category": "product",
            "subcategory": "tianxia",
            "tags": ["天下牌", "系列", "消毒产品"],
            "content": "天下牌系列包含龙脑抑菌液、消毒产品等。拥有多项发明专利及软件著作权，通过严格的质量标准认证。浙卫消证字 (2024) 第 0010 号，符合国家消毒产品卫生标准。",
            "summary": "天下牌系列产品线和合规认证",
            "author": "天下牌产品部",
            "company": "东亚医药",
            "status": "published",
            "views": 67,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "kb_004",
            "title": "AI 诊断系统 API 快速入门",
            "category": "technology",
            "subcategory": "api",
            "tags": ["API", "诊断", "快速入门"],
            "content": "AIMED 诊断 API 提供完整的 AI 辅助诊断能力。支持胃部、胰腺、胆管、食道四个器官的诊断。调用方式：POST /api/v1/diagnosis/diagnose，需要携带 JWT Token。",
            "summary": "3 分钟快速调用诊断 API",
            "author": "AIMED 技术部",
            "company": "阿尔麦德",
            "status": "published",
            "views": 234,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "kb_005",
            "title": "销售培训：产品知识手册",
            "category": "sales",
            "subcategory": "training",
            "tags": ["销售", "培训", "产品"],
            "content": "销售团队产品知识培训手册。包含：1）口服造影剂产品线和竞争优势；2）龙脑抑菌液应用场景和目标客户；3）天下牌系列合规资质；4）常见客户问题解答。",
            "summary": "销售团队必备产品知识",
            "author": "AIMED 销售部",
            "company": "阿尔麦德",
            "status": "published",
            "views": 45,
            "created_at": now,
            "updated_at": now,
        },
        {
            "id": "kb_006",
            "title": "合规认证：NMPA 三类证申报指南",
            "category": "compliance",
            "subcategory": "nmpa",
            "tags": ["NMPA", "三类证", "合规"],
            "content": "NMPA 三类医疗器械注册证申报指南。Phase 3（2027 Q4+）启动申报，需要准备：1）临床试验数据；2）质量管理体系文件；3）产品技术要求；4）注册检验报告。",
            "summary": "NMPA 三类证申报全流程指南",
            "author": "AIMED 合规部",
            "company": "阿尔麦德",
            "status": "published",
            "views": 32,
            "created_at": now,
            "updated_at": now,
        },
    ]
    save_kb(kb)
    return kb

# ============================================
# API 路由
# ============================================
@router.get("/categories")
async def get_categories():
    """获取知识库分类体系"""
    return {
        "categories": KNOWLEDGE_CATEGORIES,
        "total_categories": len(KNOWLEDGE_CATEGORIES),
        "total_subcategories": sum(len(c["subcategories"]) for c in KNOWLEDGE_CATEGORIES.values()),
    }

@router.get("/list")
async def list_documents(
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    status: Optional[str] = "published",
    token_data: dict = Depends(verify_token),
):
    """获取知识库文档列表"""
    kb = init_sample_data()
    docs = kb["documents"]
    
    if category:
        docs = [d for d in docs if d.get("category") == category]
    if subcategory:
        docs = [d for d in docs if d.get("subcategory") == subcategory]
    if status:
        docs = [d for d in docs if d.get("status") == status]
    
    return {
        "documents": docs,
        "total": len(docs),
    }

@router.get("/search")
async def search_documents(
    q: str,
    category: Optional[str] = None,
    limit: int = 20,
    token_data: dict = Depends(verify_token),
):
    """搜索知识库文档"""
    kb = init_sample_data()
    docs = kb["documents"]
    
    results = []
    q_lower = q.lower()
    for doc in docs:
        if doc.get("status") != "published":
            continue
        if category and doc.get("category") != category:
            continue
        
        # 简单文本搜索
        score = 0
        if q_lower in doc.get("title", "").lower():
            score += 10
        if q_lower in doc.get("content", "").lower():
            score += 5
        if q_lower in doc.get("summary", "").lower():
            score += 3
        if any(q_lower in tag.lower() for tag in doc.get("tags", [])):
            score += 2
        
        if score > 0:
            doc_copy = doc.copy()
            doc_copy["_score"] = score
            results.append(doc_copy)
    
    results.sort(key=lambda x: x["_score"], reverse=True)
    return {
        "query": q,
        "documents": results[:limit],
        "total": len(results),
    }

@router.get("/{doc_id}")
async def get_document(
    doc_id: str,
    token_data: dict = Depends(verify_token),
):
    """获取单个文档详情"""
    kb = init_sample_data()
    doc = next((d for d in kb["documents"] if d["id"] == doc_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 增加浏览量
    doc["views"] = doc.get("views", 0) + 1
    save_kb(kb)
    
    return doc

@router.post("/")
async def create_document(
    req: KnowledgeCreate,
    token_data: dict = Depends(require_role(50)),  # editor 以上
):
    """创建知识库文档"""
    kb = load_kb()
    
    now = datetime.now(timezone.utc).isoformat()
    doc_id = f"kb_{hashlib.md5((req.title + now).encode()).hexdigest()[:8]}"
    
    doc = {
        "id": doc_id,
        "title": req.title,
        "category": req.category,
        "subcategory": req.subcategory,
        "tags": req.tags,
        "content": req.content,
        "summary": req.summary,
        "author": token_data.get("username", ""),
        "company": token_data.get("company", ""),
        "status": req.status,
        "views": 0,
        "created_at": now,
        "updated_at": now,
        "attachments": [],
    }
    
    kb["documents"].append(doc)
    save_kb(kb)
    
    return doc

@router.put("/{doc_id}")
async def update_document(
    doc_id: str,
    req: KnowledgeUpdate,
    token_data: dict = Depends(require_role(50)),  # editor 以上
):
    """更新知识库文档"""
    kb = load_kb()
    doc = next((d for d in kb["documents"] if d["id"] == doc_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 更新字段
    update_data = req.dict(exclude_unset=True)
    for key, value in update_data.items():
        doc[key] = value
    
    doc["updated_at"] = datetime.now(timezone.utc).isoformat()
    save_kb(kb)
    
    return doc

@router.delete("/{doc_id}")
async def delete_document(
    doc_id: str,
    token_data: dict = Depends(require_role(80)),  # admin 以上
):
    """删除知识库文档"""
    kb = load_kb()
    doc = next((d for d in kb["documents"] if d["id"] == doc_id), None)
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    kb["documents"] = [d for d in kb["documents"] if d["id"] != doc_id]
    save_kb(kb)
    
    return {"success": True, "deleted": doc_id}

@router.get("/stats")
async def get_stats(token_data: dict = Depends(verify_token)):
    """获取知识库统计"""
    kb = init_sample_data()
    docs = kb["documents"]
    
    stats = {
        "total_documents": len(docs),
        "by_category": {},
        "total_views": sum(d.get("views", 0) for d in docs),
    }
    
    for cat_id, cat_info in KNOWLEDGE_CATEGORIES.items():
        cat_docs = [d for d in docs if d.get("category") == cat_id]
        stats["by_category"][cat_id] = {
            "name": cat_info["name"],
            "count": len(cat_docs),
            "views": sum(d.get("views", 0) for d in cat_docs),
        }
    
    return stats
