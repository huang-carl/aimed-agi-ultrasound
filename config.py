from functools import lru_cache
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Settings:
    # 阿里云百炼 API
    dashscope_api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    
    # 服务配置
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    # 数据库
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./aimed.db")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_hours: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
    
    # 诊断配置
    stomach_model_path: str = os.getenv("STOMACH_MODEL_PATH", "models/stomach_v1.pt")
    pancreas_model_path: str = os.getenv("PANCREAS_MODEL_PATH", "models/pancreas_v1.pt")
    diagnosis_timeout: int = int(os.getenv("DIAGNOSIS_TIMEOUT", "30"))
    max_image_size_mb: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    
    # 日志
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/aimed.log")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
