"""
全局异常处理中间件
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import traceback


async def global_exception_handler(request: Request, call_next):
    """全局异常拦截器"""
    try:
        return await call_next(request)
    except RequestValidationError as e:
        logger.warning(f"请求验证失败：{e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "validation_error",
                "message": "请求参数验证失败",
                "details": e.errors()
            }
        )
    except ValueError as e:
        logger.warning(f"值错误：{e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "value_error",
                "message": str(e)
            }
        )
    except FileNotFoundError as e:
        logger.warning(f"文件未找到：{e}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "file_not_found",
                "message": "请求的文件不存在"
            }
        )
    except Exception as e:
        logger.error(f"未处理的异常：{e}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "internal_error",
                "message": "服务器内部错误",
                "tip": "请稍后重试或联系管理员"
            }
        )
