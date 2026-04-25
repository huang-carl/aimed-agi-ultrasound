"""
向量检索服务 - 医疗知识库 RAG
支持：ChromaDB + Faiss + Qdrant
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


class VectorSearchService:
    """向量检索服务（医疗知识库 RAG）"""
    
    def __init__(self, provider: str = "chromadb", persist_dir: str = "./data/vectors"):
        """
        初始化向量检索服务
        
        Args:
            provider: 向量数据库提供商（chromadb/faiss/qdrant）
            persist_dir: 数据持久化目录
        """
        self.provider = provider
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        
        # 初始化向量数据库
        self.client = None
        self.collection = None
        self._init_provider()
        
        print(f"[向量检索] 初始化完成 - Provider: {provider}")
    
    def _init_provider(self):
        """初始化指定的向量数据库"""
        if self.provider == "chromadb" and CHROMADB_AVAILABLE:
            self._init_chromadb()
        elif self.provider == "faiss" and FAISS_AVAILABLE:
            self._init_faiss()
        elif self.provider == "qdrant" and QDRANT_AVAILABLE:
            self._init_qdrant()
        else:
            raise ValueError(f"向量数据库不可用: {provider}")
    
    def _init_chromadb(self):
        """初始化 ChromaDB"""
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="medical_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        print(f"[ChromaDB] 集合已加载 - 文档数: {self.collection.count()}")
    
    def _init_faiss(self):
        """初始化 Faiss"""
        self.dimension = 768  # 默认向量维度
        self.index = faiss.IndexFlatIP(self.dimension)  # 内积相似度
        self.metadata_file = os.path.join(self.persist_dir, "faiss_metadata.json")
        self.metadata = self._load_faiss_metadata()
        print(f"[Faiss] 索引已初始化 - 向量数: {self.index.ntotal}")
    
    def _init_qdrant(self):
        """初始化 Qdrant"""
        self.client = QdrantClient(path=os.path.join(self.persist_dir, "qdrant"))
        # 创建集合
        try:
            self.client.create_collection(
                collection_name="medical_knowledge",
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
            print("[Qdrant] 集合已创建")
        except Exception:
            print("[Qdrant] 集合已存在")
    
    def _load_faiss_metadata(self) -> List[Dict]:
        """加载 Faiss 元数据"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_faiss_metadata(self):
        """保存 Faiss 元数据"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
    
    def add_document(self, text: str, metadata: Optional[Dict] = None, doc_id: Optional[str] = None) -> str:
        """
        添加文档到向量库
        
        Args:
            text: 文档内容
            metadata: 元数据（器官、疾病类型等）
            doc_id: 文档 ID（可选）
            
        Returns:
            文档 ID
        """
        if not doc_id:
            doc_id = hashlib.md5(text.encode()).hexdigest()[:12]
        
        if self.provider == "chromadb":
            return self._add_chromadb(text, metadata, doc_id)
        elif self.provider == "faiss":
            return self._add_faiss(text, metadata, doc_id)
        elif self.provider == "qdrant":
            return self._add_qdrant(text, metadata, doc_id)
    
    def _add_chromadb(self, text: str, metadata: Dict, doc_id: str) -> str:
        """ChromaDB 添加文档"""
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {}],
            ids=[doc_id]
        )
        return doc_id
    
    def _add_faiss(self, text: str, metadata: Dict, doc_id: str) -> str:
        """Faiss 添加文档（需要外部提供向量）"""
        # Faiss 需要预计算的向量，这里记录元数据
        self.metadata.append({
            "id": doc_id,
            "text": text,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        self._save_faiss_metadata()
        return doc_id
    
    def _add_qdrant(self, text: str, metadata: Dict, doc_id: str) -> str:
        """Qdrant 添加文档（需要外部提供向量）"""
        # Qdrant 需要预计算的向量，这里记录元数据
        print(f"[Qdrant] 文档已记录: {doc_id}（需要向量嵌入）")
        return doc_id
    
    def search(self, query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            filter_metadata: 元数据过滤
            
        Returns:
            搜索结果列表
        """
        if self.provider == "chromadb":
            return self._search_chromadb(query, top_k, filter_metadata)
        else:
            return self._search_fallback(query, top_k, filter_metadata)
    
    def _search_chromadb(self, query: str, top_k: int, filter_metadata: Optional[Dict]) -> List[Dict]:
        """ChromaDB 搜索"""
        where_filter = None
        if filter_metadata:
            where_filter = filter_metadata
        
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )
        
        # 格式化结果
        formatted = []
        for i in range(len(results['ids'][0])):
            formatted.append({
                'id': results['ids'][0][i],
                'document': results['documents'][0][i] if results['documents'] else '',
                'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                'distance': results['distances'][0][i] if 'distances' in results else 0
            })
        return formatted
    
    def _search_fallback(self, query: str, top_k: int, filter_metadata: Optional[Dict]) -> List[Dict]:
        """简单文本搜索（无向量库时）"""
        # 基于关键词的简单搜索
        results = []
        if self.provider == "faiss" and hasattr(self, 'metadata'):
            for item in self.metadata:
                if query in item.get('text', ''):
                    if not filter_metadata or all(
                        item.get('metadata', {}).get(k) == v 
                        for k, v in filter_metadata.items()
                    ):
                        results.append(item)
                        if len(results) >= top_k:
                            break
        return results
    
    def delete_document(self, doc_id: str) -> bool:
        """删除文档"""
        if self.provider == "chromadb":
            self.collection.delete(ids=[doc_id])
            return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {
            'provider': self.provider,
            'persist_dir': self.persist_dir
        }
        
        if self.provider == "chromadb":
            stats['document_count'] = self.collection.count()
        elif self.provider == "faiss":
            stats['document_count'] = len(self.metadata)
        
        return stats


# 便捷函数
def create_vector_search(provider: str = "chromadb", persist_dir: str = "./data/vectors") -> VectorSearchService:
    """创建向量检索服务实例"""
    return VectorSearchService(provider=provider, persist_dir=persist_dir)


# 测试
if __name__ == '__main__':
    print("=" * 60)
    print("向量检索服务测试")
    print("=" * 60)
    
    # 测试 ChromaDB
    if CHROMADB_AVAILABLE:
        print("\n【测试 ChromaDB】")
        service = VectorSearchService(provider="chromadb", persist_dir="./data/vectors/test")
        
        # 添加文档
        service.add_document(
            text="胃窦部黏膜充血水肿，可见点状糜烂，考虑慢性胃炎",
            metadata={"organ": "胃", "disease": "慢性胃炎", "type": "诊断"},
            doc_id="case_001"
        )
        service.add_document(
            text="胰腺回声均匀，胰管无扩张，未见明显异常",
            metadata={"organ": "胰腺", "disease": "正常", "type": "诊断"},
            doc_id="case_002"
        )
        
        print(f"文档数: {service.collection.count()}")
        
        # 搜索
        results = service.search("胃窦部炎症", top_k=2)
        print(f"搜索结果: {len(results)} 条")
        for r in results:
            print(f"  - {r['id']}: {r['document'][:30]}...")
        
        # 统计
        print(f"统计: {service.get_stats()}")
        
    print("\n" + "=" * 60)
