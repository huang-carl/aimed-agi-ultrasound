# API 使用示例 (API Examples)

本文档提供 AIMED Agent Swarm API 的实际使用示例。

---

## 📡 基础信息

**Base URL:** `http://localhost:8000`

**API 文档：** `http://localhost:8000/docs` (Swagger UI)

**认证：** 当前版本无需认证（生产环境将启用 JWT）

---

## 🔍 健康检查

### 请求

```bash
curl -X GET "http://localhost:8000/health"
```

### 响应

```json
{
  "status": "ok",
  "service": "AIMED Agent Swarm",
  "version": "0.1.0"
}
```

---

## 🫀 胃诊断接口

### 请求

```bash
curl -X POST "http://localhost:8000/api/stomach/diagnose" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@stomach_ultrasound.png"
```

### Python 示例

```python
import requests

url = "http://localhost:8000/api/stomach/diagnose"
files = {"file": open("stomach_ultrasound.png", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"诊断结果：{result['disease']}")
print(f"置信度：{result['probability']:.2%}")
print(f"建议：{result['suggestion']}")
```

### 响应

```json
{
  "organ": "胃",
  "disease": "慢性胃炎",
  "probability": 0.85,
  "suggestion": "建议结合临床症状，必要时行胃镜检查",
  "image_quality": "good",
  "timestamp": "2026-04-18T05:30:00"
}
```

---

## 🧠 胰腺诊断接口

### 请求

```bash
curl -X POST "http://localhost:8000/api/pancreas/diagnose" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@pancreas_ultrasound.png"
```

### Python 示例

```python
import requests

url = "http://localhost:8000/api/pancreas/diagnose"
files = {"file": open("pancreas_ultrasound.png", "rb")}

response = requests.post(url, files=files)
result = response.json()

print(f"诊断结果：{result['disease']}")
print(f"置信度：{result['probability']:.2%}")
```

### 响应

```json
{
  "organ": "胰腺",
  "disease": "胰腺回声均匀",
  "probability": 0.92,
  "suggestion": "未见明显异常，建议定期体检",
  "image_quality": "good",
  "timestamp": "2026-04-18T05:30:00"
}
```

---

## 🎯 任务分发接口（总指挥）

### 请求

```bash
curl -X POST "http://localhost:8000/api/conductor/dispatch" \
  -H "Content-Type: application/json" \
  -d '{
    "organs": ["stomach", "pancreas"],
    "image_paths": ["/path/to/image1.png", "/path/to/image2.png"],
    "patient_id": "PAT001"
  }'
```

### Python 示例

```python
import requests

url = "http://localhost:8000/api/conductor/dispatch"
payload = {
    "organs": ["stomach", "pancreas"],
    "image_paths": ["/path/to/image1.png", "/path/to/image2.png"],
    "patient_id": "PAT001"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"任务 ID: {result['task_id']}")
print(f"状态：{result['status']}")
```

### 响应

```json
{
  "task_id": "task_20260418053000_abc123",
  "status": "processing",
  "created_at": "2026-04-18T05:30:00"
}
```

---

## 📄 报告生成接口

### 请求

```bash
curl -X POST "http://localhost:8000/api/report/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "PAT001",
    "patient_name": "张三",
    "diagnosis_results": [
      {
        "organ": "胃",
        "disease": "慢性胃炎",
        "probability": 0.85,
        "suggestion": "建议结合临床症状"
      }
    ],
    "doctor_id": "DR001",
    "doctor_name": "李医生"
  }'
```

### Python 示例

```python
import requests

url = "http://localhost:8000/api/report/generate"
payload = {
    "patient_id": "PAT001",
    "patient_name": "张三",
    "diagnosis_results": [
        {
            "organ": "胃",
            "disease": "慢性胃炎",
            "probability": 0.85,
            "suggestion": "建议结合临床症状"
        }
    ],
    "doctor_id": "DR001",
    "doctor_name": "李医生"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"报告 ID: {result['report_id']}")
print(f"状态：{result['status']}")
```

### 响应

```json
{
  "report_id": "RPT_20260418053000_PAT001",
  "patient_id": "PAT001",
  "status": "generated",
  "pdf_url": null,
  "created_at": "2026-04-18T05:30:00"
}
```

---

## 🌐 API v1 示例

### 胃诊断 v1

```bash
curl -X POST "http://localhost:8000/api/v1/stomach/diagnose" \
  -F "file=@stomach_ultrasound.png"
```

### 任务分发 v1

```bash
curl -X POST "http://localhost:8000/api/v1/conductor/dispatch" \
  -H "Content-Type: application/json" \
  -d '{
    "organs": ["stomach", "pancreas"],
    "image_paths": ["/path/to/image1.png"],
    "patient_id": "PAT001",
    "patient_name": "张三"
  }'
```

### 查询任务状态 v1

```bash
curl -X GET "http://localhost:8000/api/v1/conductor/task/task_20260418053000_abc123"
```

---

## 🔧 错误处理

### 400 Bad Request

```json
{
  "error": "value_error",
  "message": "不支持的器官类型：liver"
}
```

### 404 Not Found

```json
{
  "error": "file_not_found",
  "message": "请求的文件不存在"
}
```

### 422 Validation Error

```json
{
  "error": "validation_error",
  "message": "请求参数验证失败",
  "details": [
    {
      "loc": ["body", "patient_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error

```json
{
  "error": "internal_error",
  "message": "服务器内部错误",
  "tip": "请稍后重试或联系管理员"
}
```

---

## 📊 批量处理示例

### 批量诊断多个患者

```python
import requests
import concurrent.futures

def diagnose_patient(patient_id, image_path):
    url = "http://localhost:8000/api/stomach/diagnose"
    files = {"file": open(image_path, "rb")}
    response = requests.post(url, files=files)
    return {
        "patient_id": patient_id,
        "result": response.json()
    }

# 批量处理
patients = [
    ("PAT001", "patient1_stomach.png"),
    ("PAT002", "patient2_stomach.png"),
    ("PAT003", "patient3_stomach.png"),
]

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(diagnose_patient, pid, img)
        for pid, img in patients
    ]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

for result in results:
    print(f"{result['patient_id']}: {result['result']['disease']}")
```

---

## 💡 最佳实践

### 1. 错误重试

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(
    total=3,
    backoff_factor=0.3,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount("http://", adapter)

response = session.post(url, files=files)
```

### 2. 超时设置

```python
response = requests.post(url, files=files, timeout=30)
```

### 3. 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    response = requests.post(url, files=files)
    logger.info(f"诊断成功：{response.json()}")
except Exception as e:
    logger.error(f"诊断失败：{e}")
```

---

**最后更新：** 2026-04-18
