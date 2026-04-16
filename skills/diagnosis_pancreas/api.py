from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import io

app = FastAPI(title="胰腺AI诊断Skill")

class DiagnoseResult(BaseModel):
    organ: str
    disease: str
    probability: float
    suggestion: str

@app.post("/diagnose", response_model=DiagnoseResult, summary="胰腺B超图片智能AI诊断")
async def diagnose(file: UploadFile = File(...)):
    # 读取图片数据
    img_bytes = await file.read()
    # TODO: 替换下方为你实际的AI推理逻辑，比如API调用/本地模型
    # 这里用假数据演示
    result = DiagnoseResult(
        organ="胰腺",
        disease="胰腺炎",
        probability=0.88,
        suggestion="建议进一步检查"
    )
    return result
