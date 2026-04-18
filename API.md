# AIMED Agent Swarm API 文档

## 基础信息

- **Base URL:** `http://localhost:8000`
- **API 文档:** `http://localhost:8000/docs` (Swagger UI)
- **版本:** v0.1.0

---

## 健康检查

### GET /health

服务健康检查接口。

**请求：**
```bash
curl http://localhost:8000/health
```

**响应：**
```json
{
  "status": "ok",
  "service": "AIMED Agent Swarm",
  "version": "0.1.0"
}
```

---

## 胃诊断 API

### POST /api/stomach/diagnose

胃超声影像 AI 诊断。

**请求：**
```bash
curl -X POST http://localhost:8000/api/stomach/diagnose \
  -F "file=@stomach_ultrasound.png"
```

**请求参数：**
| 参数 | 类型 | 说明 | 必填 |
|------|------|------|------|
| `file` | File | 超声影像文件（JPG/PNG/DICOM） | 是 |

**响应：**
```json
{
  "organ": "胃",
  "disease": "慢性胃炎",
  "probability": 0.85,
  "suggestion": "建议结合临床症状，必要时行胃镜检查",
  "image_quality": "good",
  "timestamp": "2026-04-17T08:00:00"
}
```

**错误响应：**
```json
{
  "detail": "不支持的文件类型：application/pdf，支持：['image/jpeg', 'image/png', 'application/dicom']"
}
```

---

### POST /api/stomach/upload

上传胃超声影像（不立即诊断）。

**请求：**
```bash
curl -X POST http://localhost:8000/api/stomach/upload \
  -F "file=@stomach_ultrasound.png"
```

**响应：**
```json
{
  "status": "success",
  "file_path": "data/samples/stomach_20260417080000_ultrasound.png",
  "size": 1024567
}
```

---

### GET /api/stomach/health

胃诊断服务健康检查。

**响应：**
```json
{
  "status": "ok",
  "service": "Stomach Diagnosis"
}
```

---

## 胰腺诊断 API

### POST /api/pancreas/diagnose

胰腺超声影像 AI 诊断。

**请求：**
```bash
curl -X POST http://localhost:8000/api/pancreas/diagnose \
  -F "file=@pancreas_ultrasound.png"
```

**响应：**
```json
{
  "organ": "胰腺",
  "disease": "胰腺回声均匀",
  "probability": 0.92,
  "suggestion": "未见明显异常，建议定期体检",
  "image_quality": "good",
  "timestamp": "2026-04-17T08:00:00"
}
```

---

### POST /api/pancreas/upload

上传胰腺超声影像（不立即诊断）。

**请求：**
```bash
curl -X POST http://localhost:8000/api/pancreas/upload \
  -F "file=@pancreas_ultrasound.png"
```

**响应：**
```json
{
  "status": "success",
  "file_path": "data/samples/pancreas_20260417080000_ultrasound.png",
  "size": 987654
}
```

---

### GET /api/pancreas/health

胰腺诊断服务健康检查。

**响应：**
```json
{
  "status": "ok",
  "service": "Pancreas Diagnosis"
}
```

---

## 总指挥 API

### POST /api/conductor/dispatch

任务分发 - 调度胃/胰腺诊断。

**请求：**
```bash
curl -X POST http://localhost:8000/api/conductor/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "organs": ["stomach", "pancreas"],
    "image_paths": ["/path/to/image1.png", "/path/to/image2.png"],
    "patient_id": "PAT001"
  }'
```

**请求参数：**
| 参数 | 类型 | 说明 | 必填 |
|------|------|------|------|
| `organs` | Array | 需要诊断的器官列表 | 是 |
| `image_paths` | Array | 影像文件路径列表 | 是 |
| `patient_id` | String | 患者 ID | 否 |

**响应：**
```json
{
  "task_id": "task_20260417080000",
  "status": "processing",
  "created_at": "2026-04-17T08:00:00"
}
```

---

### GET /api/conductor/task/{task_id}

查询任务状态。

**请求：**
```bash
curl http://localhost:8000/api/conductor/task/task_20260417080000
```

**响应：**
```json
{
  "task_id": "task_20260417080000",
  "status": "completed",
  "results": {
    "stomach": {"disease": "慢性胃炎", "probability": 0.85},
    "pancreas": {"disease": "未见明显异常", "probability": 0.92}
  },
  "created_at": "2026-04-17T08:00:00"
}
```

---

### GET /api/conductor/health

总指挥服务健康检查。

**响应：**
```json
{
  "status": "ok",
  "service": "Conductor",
  "active_tasks": 5
}
```

---

## 报告生成 API

### POST /api/report/generate

生成诊断报告。

**请求：**
```bash
curl -X POST http://localhost:8000/api/report/generate \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PAT001",
    "patient_name": "张三",
    "patient_gender": "男",
    "patient_age": 45,
    "doctor_id": "DR001",
    "doctor_name": "李医生",
    "diagnosis_results": [
      {
        "organ": "胃",
        "disease": "慢性胃炎",
        "probability": 0.85,
        "suggestion": "建议结合临床症状"
      },
      {
        "organ": "胰腺",
        "disease": "未见明显异常",
        "probability": 0.92,
        "suggestion": "建议定期体检"
      }
    ]
  }'
```

**请求参数：**
| 参数 | 类型 | 说明 | 必填 |
|------|------|------|------|
| `patient_id` | String | 患者 ID | 是 |
| `patient_name` | String | 患者姓名 | 否 |
| `patient_gender` | String | 性别 | 否 |
| `patient_age` | Integer | 年龄 | 否 |
| `doctor_id` | String | 医生 ID | 否 |
| `doctor_name` | String | 医生姓名 | 否 |
| `diagnosis_results` | Array | 诊断结果列表 | 是 |

**响应：**
```json
{
  "report_id": "RPT_20260417080000",
  "status": "success",
  "pdf_path": "data/reports/RPT_20260417080000.pdf",
  "created_at": "2026-04-17T08:00:00"
}
```

---

### GET /api/report/{report_id}

获取报告信息。

**请求：**
```bash
curl http://localhost:8000/api/report/RPT_20260417080000
```

**响应：**
```json
{
  "report_id": "RPT_20260417080000",
  "pdf_path": "data/reports/RPT_20260417080000.pdf",
  "created_at": "2026-04-17T08:00:00"
}
```

---

### GET /api/report/health

报告服务健康检查。

**响应：**
```json
{
  "status": "ok",
  "service": "Report Generation"
}
```

---

## 错误码说明

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式 |
| 404 | 资源不存在 | 确认 ID 正确 |
| 500 | 服务器内部错误 | 联系系统管理员 |

---

## 调用示例（Python）

```python
import requests

# 胃诊断
with open('stomach.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/stomach/diagnose',
        files={'file': f}
    )
    print(response.json())

# 生成报告
report_data = {
    'patient_id': 'PAT001',
    'patient_name': '张三',
    'diagnosis_results': [
        {
            'organ': '胃',
            'disease': '慢性胃炎',
            'probability': 0.85,
            'suggestion': '建议结合临床症状'
        }
    ]
}
response = requests.post(
    'http://localhost:8000/api/report/generate',
    json=report_data
)
print(response.json())
```

---

**更新日期：** 2026-04-17  
**版本：** v0.1.0
