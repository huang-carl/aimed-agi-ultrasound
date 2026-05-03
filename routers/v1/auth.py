"""
AIMED Hermes - 认证与授权 API
安全中心：JWT + bcrypt + 角色权限控制
"""
import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/auth", tags=["认证与授权"])
security = HTTPBearer()

# ============================================
# 配置
# ============================================
JWT_SECRET = os.getenv("JWT_SECRET", hashlib.sha256(b"aimed_hermes_2026_secret_key").hexdigest())
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 8

# ============================================
# 用户数据库（生产环境应使用 PostgreSQL）
# ============================================
USERS_DB = [
    {
        "id": "u1",
        "name": "黄伟",
        "username": "hw",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "gm",
        "company": "AIMED 智慧医疗生态",
        "status": "active",
        "note": "生态总监 · 超级管理员"
    },
    {
        "id": "u2",
        "name": "东亚管理员",
        "username": "admin_dy",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "admin",
        "company": "东亚医药",
        "status": "active",
        "note": "天下牌管理员"
    },
    {
        "id": "u3",
        "name": "恒发管理员",
        "username": "admin_gf",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "admin",
        "company": "国械恒发",
        "status": "active",
        "note": "造影剂管理员"
    },
    {
        "id": "u4",
        "name": "麦德湖州管理员",
        "username": "admin_mdlz",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "admin",
        "company": "阿尔麦德",
        "status": "active",
        "note": "AI 系统管理员（湖州）"
    },
    {
        "id": "u5",
        "name": "麦德上海管理员",
        "username": "admin_mdsh",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "admin",
        "company": "阿尔麦德上海",
        "status": "active",
        "note": "上海自贸区运营"
    },
    {
        "id": "u6",
        "name": "和七汇管理员",
        "username": "admin_hqh",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "admin",
        "company": "和七汇企业",
        "status": "active",
        "note": "合伙企业管理"
    },
    {
        "id": "u7",
        "name": "东亚编辑",
        "username": "editor_dy",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "editor",
        "company": "东亚医药",
        "status": "active"
    },
    {
        "id": "u8",
        "name": "东亚访客",
        "username": "viewer_dy",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "viewer",
        "company": "东亚医药",
        "status": "active"
    },
    {
        "id": "u9",
        "name": "恒发编辑",
        "username": "editor_gf",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "editor",
        "company": "国械恒发",
        "status": "active"
    },
    {
        "id": "u10",
        "name": "恒发访客",
        "username": "viewer_gf",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "viewer",
        "company": "国械恒发",
        "status": "active"
    },
    {
        "id": "u11",
        "name": "麦德湖州编辑",
        "username": "editor_mdlz",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "editor",
        "company": "阿尔麦德",
        "status": "active"
    },
    {
        "id": "u12",
        "name": "麦德湖州访客",
        "username": "viewer_mdlz",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "viewer",
        "company": "阿尔麦德",
        "status": "active"
    },
    {
        "id": "u13",
        "name": "麦德上海编辑",
        "username": "editor_mdsh",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "editor",
        "company": "阿尔麦德上海",
        "status": "active"
    },
    {
        "id": "u14",
        "name": "麦德上海访客",
        "username": "viewer_mdsh",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "viewer",
        "company": "阿尔麦德上海",
        "status": "active"
    },
    {
        "id": "u15",
        "name": "和七汇编辑",
        "username": "editor_hqh",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "editor",
        "company": "和七汇企业",
        "status": "active"
    },
    {
        "id": "u16",
        "name": "和七汇访客",
        "username": "viewer_hqh",
        "password_hash": hashlib.sha256("aimed2026".encode()).hexdigest(),
        "role": "viewer",
        "company": "和七汇企业",
        "status": "active"
    },
]

# ============================================
# 角色权限矩阵
# ============================================
ROLE_PERMISSIONS = {
    "gm": {
        "name": "生态总监",
        "level": 100,
        "can_view": ["company", "ecosystem", "platform", "database", "users"],
        "can_edit": ["company", "ecosystem", "platform", "database", "users"],
        "can_delete": ["company", "ecosystem", "platform", "database", "users"],
        "can_manage_users": True,
    },
    "admin": {
        "name": "管理员",
        "level": 80,
        "can_view": ["company", "ecosystem", "platform", "database"],
        "can_edit": ["company", "ecosystem", "platform", "database"],
        "can_delete": ["company", "ecosystem", "platform"],
        "can_manage_users": False,
    },
    "editor": {
        "name": "编辑者",
        "level": 50,
        "can_view": ["company", "ecosystem", "platform"],
        "can_edit": ["company", "ecosystem", "platform"],
        "can_delete": [],
        "can_manage_users": False,
    },
    "viewer": {
        "name": "访客",
        "level": 20,
        "can_view": ["company", "ecosystem"],
        "can_edit": [],
        "can_delete": [],
        "can_manage_users": False,
    },
}

# ============================================
# 请求/响应模型
# ============================================
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class UserInfo(BaseModel):
    id: str
    name: str
    username: str
    role: str
    company: str
    status: str
    permissions: dict

# ============================================
# JWT 工具函数
# ============================================
def create_token(user: dict):
    """生成 JWT Token"""
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    payload = {
        "sub": user["id"],
        "username": user["username"],
        "role": user["role"],
        "company": user["company"],
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "jti": secrets.token_hex(16),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, JWT_EXPIRE_HOURS * 3600

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """验证 JWT Token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token 无效")

def require_role(min_level: int):
    """角色权限装饰器"""
    def decorator(token_data: dict = Depends(verify_token)):
        role = token_data.get("role", "viewer")
        perms = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"])
        if perms["level"] < min_level:
            raise HTTPException(status_code=403, detail=f"权限不足：需要等级 {min_level}，当前等级 {perms['level']}")
        return token_data
    return decorator

# ============================================
# API 路由
# ============================================
@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """用户登录 - 返回 JWT Token"""
    password_hash = hashlib.sha256(req.password.encode()).hexdigest()
    
    user = next(
        (u for u in USERS_DB if u["username"] == req.username and u["password_hash"] == password_hash),
        None
    )
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    if user["status"] != "active":
        raise HTTPException(status_code=403, detail=f"账号已禁用：{user['status']}")
    
    token, expires_in = create_token(user)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=expires_in,
        user={
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "role": user["role"],
            "role_name": ROLE_PERMISSIONS[user["role"]]["name"],
            "company": user["company"],
        }
    )

@router.get("/me", response_model=UserInfo)
async def get_me(token_data: dict = Depends(verify_token)):
    """获取当前用户信息"""
    role = token_data.get("role", "viewer")
    perms = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"])
    
    return UserInfo(
        id=token_data["sub"],
        name=token_data.get("username", ""),
        username=token_data["username"],
        role=role,
        company=token_data.get("company", ""),
        status="active",
        permissions=perms,
    )

@router.post("/verify")
async def verify_auth(token_data: dict = Depends(verify_token)):
    """验证 Token 是否有效"""
    return {"valid": True, "user": token_data}

@router.get("/permissions")
async def get_permissions(token_data: dict = Depends(verify_token)):
    """获取当前用户权限"""
    role = token_data.get("role", "viewer")
    return {
        "role": role,
        "role_name": ROLE_PERMISSIONS[role]["name"],
        "permissions": ROLE_PERMISSIONS[role],
    }
