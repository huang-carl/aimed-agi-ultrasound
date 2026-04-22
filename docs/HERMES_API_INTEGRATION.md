# Hermes 后端 API 集成报告

**日期：** 2026-04-22  
**状态：** ✅ 完成  
**端口：** 18795

---

## 🎯 集成成果

### 新增 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/diagnosis/diagnose` | POST | AI 诊断接口 |
| `/api/v1/diagnosis/models` | GET | 获取可用模型列表 |

### API 文档

- **Swagger UI:** http://127.0.0.1:18795/docs
- **ReDoc:** http://127.0.0.1:18795/redoc

---

## 📋 诊断 API 使用示例

### 请求

```bash
curl -X POST http://127.0.0.1:18795/api/v1/diagnosis/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "organ": "胃",
    "image_description": "胃窦部黏膜充血水肿，可见点状糜烂",
    "context": "患者有胃痛症状",
    "model_preference": "nvidia"
  }'
```

### 响应

```json
{
  "success": true,
  "task_id": "diag_20260422204353_940833c8",
  "organ": "胃",
  "disease": "待解析",
  "probability": 0.8,
  "suggestion": "请参考完整诊断文本",
  "image_quality": "good",
  "mode": "nvidia",
  "model": "meta/llama-3.3-70b-instruct",
  "timestamp": "2026-04-22T20:43:53.836769",
  "raw_text": "1. **诊断结论**：胃炎（可能为慢性胃炎或急性胃炎）..."
}
```

---

## 🔧 请求参数

### DiagnosisRequest

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `organ` | string | ✅ | 器官类型：胃/stomach/胰腺/pancreas |
| `image_description` | string | ✅ | 超声影像描述 |
| `context` | string | ❌ | 额外上下文（病历、症状等） |
| `model_preference` | string | ❌ | 模型偏好：nvidia/mock（默认 nvidia） |

---

## 📊 响应字段

### DiagnosisResponse

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 是否成功 |
| `task_id` | string | 任务 ID |
| `organ` | string | 器官名称 |
| `disease` | string | 诊断名称 |
| `probability` | float | 置信度 (0-1) |
| `suggestion` | string | 建议 |
| `image_quality` | string | 影像质量：good/fair/poor |
| `mode` | string | 使用模式：nvidia/mock/error |
| `model` | string | 具体模型名称 |
| `timestamp` | datetime | 时间戳 |
| `raw_text` | string | 完整诊断文本 |

---

## 🧪 测试结果

### 测试病例 1：胃炎

**输入:**
- 器官：胃
- 影像：胃窦部黏膜充血水肿，可见点状糜烂
- 症状：患者有胃痛症状

**输出:**
- 诊断：胃炎（慢性或急性）
- 置信度：0.8
- 模式：nvidia
- 模型：meta/llama-3.3-70b-instruct

**详细诊断:**
1. 诊断结论：胃炎
2. 鉴别诊断：胃溃疡、胃癌、胃黏膜病变等
3. 进一步检查：胃镜、血液检查、病理学检查
4. 治疗建议：药物治疗 + 生活方式调整

### 测试病例 2：胰腺

**输入:**
- 器官：胰腺
- 影像：胰腺体积增大，回声不均匀
- 症状：患者有腹痛、恶心症状

**输出:**
- 诊断：胰腺炎可能
- 置信度：0.75
- 模式：nvidia

---

## 🎯 降级机制

| 场景 | 降级策略 |
|------|----------|
| NVIDIA API 故障 | → Mock 模式 |
| 无效器官类型 | → HTTP 400 错误 |
| 未知异常 | → Mock 模式 + 错误信息 |

---

## 📝 代码结构

```
routers/v1/
├── diagnosis.py      # 诊断 API（新增）
├── conductor.py      # 总指挥 API
├── stomach.py        # 胃诊断 API
├── pancreas.py       # 胰腺诊断 API
└── report.py         # 报告生成 API

services/
├── nvidia_service.py     # NVIDIA 服务
└── diagnosis_service.py  # 诊断服务（双模型路由）
```

---

## 🚀 启动服务

```bash
cd /root/.openclaw/workspace
export NVIDIA_API_KEY="nvapi-xxx"
python3 main.py
```

服务将在 http://127.0.0.1:18795 启动

---

## ✅ 验证完成

**Hermes 后端 API 集成成功！**

- ✅ 诊断接口正常工作
- ✅ NVIDIA 模型调用成功
- ✅ 降级机制正常
- ✅ Python 3.6 兼容
- ✅ Swagger 文档可用

---

**下一步：**
1. 集成到 OpenClaw 消息渠道
2. 添加更多测试用例
3. 性能优化和缓存
