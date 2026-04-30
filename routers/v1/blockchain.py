"""
区块链 API v1 路由
- DID 注册/验证/查询
- 数据存证/验证
- 链状态查询
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from services.blockchain_service import blockchain_service

router = APIRouter(prefix="/blockchain", tags=["区块链服务"])


# ===== 请求/响应模型 =====

class DIDRegisterRequest(BaseModel):
    """DID 注册请求"""
    user_id: str = Field(..., description="用户 ID")
    user_type: str = Field(..., description="用户类型：patient/doctor/developer/admin")
    chain: Optional[str] = Field(None, description="指定链（默认使用配置链）")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外元数据")


class DIDVerifyRequest(BaseModel):
    """DID 验证请求"""
    did: str = Field(..., description="数字身份标识")
    chain: Optional[str] = Field(None, description="指定链")


class EvidenceStoreRequest(BaseModel):
    """存证请求"""
    data: Any = Field(..., description="要存证的数据（字符串或 JSON）")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    chain: Optional[str] = Field(None, description="指定链")


class EvidenceVerifyRequest(BaseModel):
    """存证验证请求"""
    evidence_id: str = Field(..., description="存证 ID")
    chain: Optional[str] = Field(None, description="指定链")


# ===== DID 接口 =====

@router.post("/did/register", summary="注册链上数字身份")
async def register_did(req: DIDRegisterRequest):
    """
    注册链上数字身份（DID）
    
    - **user_id**: 用户唯一标识
    - **user_type**: 用户类型（patient/doctor/developer/admin）
    - **chain**: 指定链（可选，默认使用配置的链）
    - **metadata**: 额外元数据（可选）
    
    返回 DID 标识和交易哈希。
    """
    try:
        result = await blockchain_service.register_did(
            user_id=req.user_id,
            user_type=req.user_type,
            chain=req.chain,
            metadata=req.metadata
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DID 注册失败: {str(e)}")


@router.post("/did/verify", summary="验证链上身份")
async def verify_did(req: DIDVerifyRequest):
    """
    验证链上数字身份是否有效
    
    - **did**: 数字身份标识
    - **chain**: 指定链（可选）
    
    返回验证结果。
    """
    try:
        result = await blockchain_service.verify_did(did=req.did, chain=req.chain)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DID 验证失败: {str(e)}")


@router.get("/did/{did}", summary="查询身份详情")
async def query_did(did: str, chain: Optional[str] = None):
    """
    查询链上身份详情
    
    - **did**: 数字身份标识
    - **chain**: 指定链（可选）
    
    返回身份详情。
    """
    try:
        result = await blockchain_service.query_did(did=did, chain=chain)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DID 查询失败: {str(e)}")


# ===== 存证接口 =====

@router.post("/evidence/store", summary="数据上链存证")
async def store_evidence(req: EvidenceStoreRequest):
    """
    将数据哈希上链存证
    
    - **data**: 要存证的数据（字符串或 JSON 对象）
    - **metadata**: 元数据（可选）
    - **chain**: 指定链（可选）
    
    系统会自动计算数据哈希并上链，返回存证 ID 和交易哈希。
    """
    try:
        result = await blockchain_service.store_evidence(
            data=req.data,
            metadata=req.metadata,
            chain=req.chain
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"存证失败: {str(e)}")


@router.post("/evidence/verify", summary="验证存证")
async def verify_evidence(req: EvidenceVerifyRequest):
    """
    验证链上存证是否有效
    
    - **evidence_id**: 存证 ID
    - **chain**: 指定链（可选）
    
    返回验证结果。
    """
    try:
        result = await blockchain_service.verify_evidence(
            evidence_id=req.evidence_id,
            chain=req.chain
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"存证验证失败: {str(e)}")


@router.get("/evidence/{evidence_id}", summary="查询存证详情")
async def query_evidence(evidence_id: str, chain: Optional[str] = None):
    """
    查询存证详情
    
    - **evidence_id**: 存证 ID
    - **chain**: 指定链（可选）
    
    返回存证详情。
    """
    try:
        result = await blockchain_service.verify_evidence(
            evidence_id=evidence_id,
            chain=chain
        )
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"存证查询失败: {str(e)}")


# ===== 状态接口 =====

@router.get("/status", summary="获取链状态")
async def get_chain_status(chain: Optional[str] = None):
    """
    获取区块链状态
    
    - **chain**: 指定链（可选，不传则返回所有链状态）
    
    返回链的启用状态、配置信息等。
    """
    try:
        result = await blockchain_service.get_status(chain=chain)
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"状态查询失败: {str(e)}")


@router.get("/chains", summary="获取所有可用链")
async def get_all_chains():
    """获取所有可用区块链列表和状态"""
    try:
        result = await blockchain_service.get_all_chains_status()
        return {
            "success": True,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"链列表查询失败: {str(e)}")
