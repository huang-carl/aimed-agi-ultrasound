# 多模型路由配置文档

**最后更新：** 2026-04-25

---

## 📊 四模型组合

| 模型 | 角色 | 费用状态 | 用途 |
|------|------|----------|------|
| **阿里云百炼** | 主力 | Coding Plan（免费额度） | 日常诊断推理 |
| **智谱 AI** | 辅助 | 永久免费 | 快速响应/简单任务 |
| **DeepSeek** | 主力 | 永久免费额度 | 诊断推理/编程 |
| **NVIDIA NIM** | 备用 | 免费一年 | 复杂推理验证 |

---

## 🔄 路由策略

### 智能路由（默认）

```python
# 优先级顺序
1. 阿里云百炼（主力）
2. DeepSeek（主力）
3. 智谱 AI（辅助）
4. NVIDIA NIM（备用）
```

### 手动路由

```bash
# 强制使用特定模型
MODEL_ROUTING=aliyun   # 阿里云百炼
MODEL_ROUTING=deepseek # DeepSeek
MODEL_ROUTING=zhipu    # 智谱 AI
MODEL_ROUTING=nvidia   # NVIDIA NIM
```

---

## 📋 配置示例

### .env 文件

```bash
# 阿里云百炼（主力 - Coding Plan）
DASHSCOPE_API_KEY=sk-xxx
DASHSCOPE_MODEL=qwen3.5-plus
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 智谱 AI（辅助 - 永久免费）
ZHIPU_API_KEY=ca0ba668eb3a48558a7f8d81e560172d.evOU5sdde1wTa7c1
ZHIPU_MODEL=glm-4-flash
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# DeepSeek（主力 - 永久免费额度）
DEEPSEEK_API_KEY=sk-27b0570804ad43d99fdf67f24a95c502
DEEPSEEK_MODEL=deepseek-v3.2
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# NVIDIA NIM（复杂推理 - 免费一年）
NVIDIA_API_KEY=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
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_TIMEOUT=60

# 路由策略
MODEL_ROUTING=smart
CONTEXT_LENGTH_THRESHOLD=30000
COMPLEXITY_THRESHOLD=0.8
```

---

## 🧪 测试命令

```bash
# 测试多模型路由服务
python3.8 scripts/test_multi_model.py

# 测试智谱 AI
python3.8 scripts/test_zhipu.py

# 测试 DeepSeek
python3.8 scripts/test_deepseek.py
```

---

## 📈 路由流程图

```
用户请求
    ↓
计算上下文长度
    ↓
智能路由选择
    ↓
┌─────────────┐
│ 阿里云百炼   │ ← 优先级 1（主力）
└─────────────┘
    ↓ (不可用)
┌─────────────┐
│ DeepSeek    │ ← 优先级 2（主力）
└─────────────┘
    ↓ (不可用)
┌─────────────┐
│ 智谱 AI     │ ← 优先级 3（辅助）
└─────────────┘
    ↓ (不可用)
┌─────────────┐
│ NVIDIA NIM  │ ← 优先级 4（备用）
└─────────────┘
    ↓
返回诊断结果
```

---

## ⚠️ 注意事项

1. **NVIDIA 免费期**：约 2026 年 4 月到期，需关注
2. **阿里云 API Key**：需配置到 `.env` 文件
3. **Mock 模式**：开发阶段启用，生产环境关闭
4. **超时设置**：NVIDIA 默认 60 秒，其他模型 30 秒

---

_文档由小菲同学维护，最后同步时间：2026-04-25_
