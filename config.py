from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """应用配置（使用 Pydantic Settings）"""
    
    # 服务配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "18795"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    # 阿里云百炼 API
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    dashscope_model: str = os.getenv("DASHSCOPE_MODEL", "qwen-plus")
    
    # Mock 模式开关
    mock_mode: bool = os.getenv("MOCK_MODE", "true").lower() == "true"
    diagnosis_timeout: int = int(os.getenv("DIAGNOSIS_TIMEOUT", "30"))
    
    # 数据库
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///../data/aimed-demo.db")
    cases_db_path: str = os.getenv("CASES_DB_PATH", "../data/cases.db")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "demo-secret-key-change-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_hours: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    
    # 知识库
    knowledge_base_path: str = os.getenv("KNOWLEDGE_BASE_PATH", "../knowledge/medical_guidelines.md")
    rag_enabled: bool = os.getenv("RAG_ENABLED", "true").lower() == "true"
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "3"))
    
    # 诊断配置
    stomach_model_path: str = os.getenv("STOMACH_MODEL_PATH", "../data/models/stomach_v1.pt")
    pancreas_model_path: str = os.getenv("PANCREAS_MODEL_PATH", "../data/models/pancreas_v1.pt")
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    
    # 日志
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "../logs/aimed-demo.log")
    
    # 数据安全
    data_mode: str = os.getenv("DATA_MODE", "demo")
    data_scope: str = os.getenv("DATA_SCOPE", "small")
    real_data_enabled: bool = os.getenv("REAL_DATA_ENABLED", "true").lower() == "true"
    real_data_max_samples: int = int(os.getenv("REAL_DATA_MAX_SAMPLES", "50"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
