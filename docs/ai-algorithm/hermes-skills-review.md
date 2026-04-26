# Hermes 技能库核查报告

**日期：** 2026-04-25  
**核查人：** 小超同学  
**目的：** 识别 Hermes 官方技能库中与 AIMED 项目适配的技能  
**状态：** ✅ 核心库已安装

---

## ✅ 已安装库（2026-04-25）

| 库 | 版本 | 状态 | 说明 |
|------|------|------|------|
| **chromadb** | 1.5.8 | ✅ 已安装 | 开源向量数据库，语义搜索 + 全文检索 |
| **faiss-cpu** | 1.13.2 | ✅ 已安装 | Facebook 向量检索，十亿级向量 |
| **segment-anything** | 1.0 | ✅ 已安装 | SAM 零样本图像分割 |
| **qdrant-client** | 1.17.1 | ✅ 已安装 | 高性能向量搜索引擎 |
| **torch** | 2.11.0+cpu | ✅ 已安装 | PyTorch 深度学习框架 |
| **torchvision** | 0.26.0+cpu | ✅ 已安装 | 计算机视觉库 |

**安装位置：** `/root/.openclaw/workspace/.venv/` (Python 3.11 虚拟环境)

**测试结果：** 全部通过 ✅

---

## 📊 Hermes 技能库概览

| 类别 | 内置技能 | 可选技能 | 合计 |
|------|----------|----------|------|
| autonomous-ai-agents | 4 | 2 | 6 |
| creative | 13 | 4 | 17 |
| data-science | 1 | 0 | 1 |
| devops | 1 | 2 | 3 |
| dogfood | 1 | 1 | 2 |
| email | 1 | 1 | 2 |
| gaming | 2 | 0 | 2 |
| github | 6 | 0 | 6 |
| mcp | 1 | 2 | 3 |
| media | 5 | 0 | 5 |
| mlops | 15 | 20 | 35 |
| note-taking | 1 | 0 | 1 |
| productivity | 6 | 4 | 10 |
| red-teaming | 1 | 0 | 1 |
| research | 3 | 8 | 11 |
| security | 0 | 3 | 3 |
| web-development | 0 | 1 | 1 |
| **合计** | **61** | **48** | **109** |

---

## 🎯 AIMED 项目适配技能（高优先级）

### 1. MCP 集成（已配置）
| 技能 | 状态 | 说明 |
|------|------|------|
| **native-mcp** | ✅ 内置 | 连接外部 MCP 服务器，发现工具并注册为本地工具 |
| **fastmcp** | ⏸️ 可选 | 用 FastMCP 构建/测试/部署 MCP 服务器 |
| **mcporter** | ⏸️ 可选 | CLI 工具，管理 MCP 服务器连接 |

**建议：** native-mcp 已满足需求，fastmcp 可用于自定义 MCP 服务器开发

### 2. RAG & 向量检索（医疗知识库核心）
| 技能 | 状态 | 说明 |
|------|------|------|
| **chroma** | ⏸️ 可选 | 开源向量数据库，支持语义搜索 + 全文检索 |
| **faiss** | ⏸️ 可选 | Facebook 向量检索库，支持十亿级向量 |
| **qdrant-vector-search** | ⏸️ 可选 | 高性能向量搜索引擎，支持混合搜索 |
| **pinecone** | ⏸️ 可选 | 托管向量数据库，生产级 RAG |

**建议：** Chroma（开源）或 Qdrant（高性能）适合医疗知识库

### 3. 图像分割（超声图像分析）
| 技能 | 状态 | 说明 |
|------|------|------|
| **segment-anything-model** | ✅ 内置 | SAM 零样本图像分割，支持点/框/掩码提示 |

**建议：** 极高适配度，可用于胃镜/超声图像分割

### 4. 视觉 - 语言模型
| 技能 | 状态 | 说明 |
|------|------|------|
| **clip** | ⏸️ 可选 | OpenAI CLIP，零样本图像分类 + 跨模态检索 |
| **llava** | ⏸️ 可选 | 视觉指令微调，支持图像对话 + 视觉问答 |

**建议：** CLIP 适合医学图像分类，LLaVA 适合图像 + 文本对话

### 5. 结构化输出
| 技能 | 状态 | 说明 |
|------|------|------|
| **outlines** | ✅ 内置 | 保证 JSON/XML/代码结构，支持 Pydantic 类型安全 |
| **guidance** | ⏸️ 可选 | 微软约束生成框架，正则/语法控制 |
| **instructor** | ⏸️ 可选 | Pydantic 验证 + 自动重试 + 流式输出 |

**建议：** outlines（内置）已满足诊断结果结构化需求

### 6. 模型训练 & 微调
| 技能 | 状态 | 说明 |
|------|------|------|
| **axolotl** | ✅ 内置 | 100+ 模型微调，LoRA/QLoRA/DPO |
| **unsloth** | ✅ 内置 | 2-5x 快速微调，50-80% 内存节省 |
| **trl-fine-tuning** | ✅ 内置 | RLHF 训练，SFT/DPO/PPO/GRPO |
| **peft-fine-tuning** | ⏸️ 可选 | 参数高效微调，LoRA/QLoRA + 25 种方法 |

**建议：** unsloth（快速微调）+ axolotl（全面支持）适合医疗模型微调

### 7. 模型推理 & 部署
| 技能 | 状态 | 说明 |
|------|------|------|
| **llama-cpp** | ✅ 内置 | 本地 GGUF 推理 + HF Hub 模型发现 |
| **vllm** | ✅ 内置 | 高吞吐推理，PagedAttention + 连续批处理 |
| **tensorrt-llm** | ⏸️ 可选 | NVIDIA TensorRT 优化，10-100x 加速 |

**建议：** vLLM 适合生产部署，TensorRT-LLM 适合 NVIDIA GPU 优化

### 8. 模型评估
| 技能 | 状态 | 说明 |
|------|------|------|
| **lm-evaluation-harness** | ✅ 内置 | 60+ 学术基准测试（MMLU/HumanEval/GSM8K） |
| **weights-and-biases** | ✅ 内置 | ML 实验跟踪 + 可视化 + 超参优化 |

**建议：** 用于医疗模型性能评估和监控

### 9. 研究 & 文献检索
| 技能 | 状态 | 说明 |
|------|------|------|
| **arxiv** | ✅ 内置 | arXiv 论文检索 + 下载 + 摘要 |
| **bioinformatics** | ⏸️ 可选 | 400+ 生物信息学技能（基因组/转录组/单细胞） |
| **drug-discovery** | ⏸️ 可选 | 药物发现工作流（ChEMBL/ADMET/药物相互作用） |
| **duckduckgo-search** | ⏸️ 可选 | 免费网页搜索（无需 API Key） |

**建议：** arXiv + bioinformatics 适合医学文献研究

### 10. 文档处理
| 技能 | 状态 | 说明 |
|------|------|------|
| **ocr-and-documents** | ✅ 内置 | PDF/扫描件 OCR + 文本提取 |
| **nano-pdf** | ✅ 内置 | 自然语言编辑 PDF |
| **powerpoint** | ✅ 内置 | PPTX 创建/解析/提取 |

**建议：** OCR 适合医疗报告数字化

---

## 📋 AIMED 项目适配技能（中优先级）

### 11. 代码审查 & GitHub 集成
| 技能 | 状态 | 说明 |
|------|------|------|
| **github-code-review** | ✅ 内置 | PR 代码审查 + 内联评论 |
| **github-issues** | ✅ 内置 | Issue 创建/管理/分类 |
| **github-pr-workflow** | ✅ 内置 | PR 完整生命周期 |
| **github-repo-management** | ✅ 内置 | 仓库管理 + 远程/发布/工作流 |

**建议：** 用于 AIMED 项目代码管理

### 12. 数据科学
| 技能 | 状态 | 说明 |
|------|------|------|
| **jupyter-live-kernel** | ✅ 内置 | 状态化 Python 执行，适合数据探索 |

**建议：** 用于医疗数据分析

### 13. 架构可视化
| 技能 | 状态 | 说明 |
|------|------|------|
| **architecture-diagram** | ✅ 内置 | 暗色 SVG 架构图（前端/后端/数据库/云） |
| **excalidraw** | ✅ 内置 | 手绘风格流程图/架构图 |
| **concept-diagrams** | ⏸️ 可选 | 扁平化教育图表，支持暗色模式 |

**建议：** 用于 AIMED 系统架构展示

---

## 🔧 推荐安装技能（按优先级）

### 立即安装（高优先级）
```bash
# 向量检索（医疗知识库）
hermes skills install official/mlops/chroma
hermes skills install official/mlops/faiss

# 图像分割（超声分析）
# segment-anything-model 已内置

# 模型微调
hermes skills install official/mlops/peft-fine-tuning

# 生物信息学
hermes skills install official/research/bioinformatics
```

### 中期安装（中优先级）
```bash
# 向量检索（生产级）
hermes skills install official/mlops/qdrant-vector-search

# 视觉 - 语言模型
hermes skills install official/mlops/clip
hermes skills install official/mlops/llava

# 药物发现
hermes skills install official/research/drug-discovery
```

### 选择性安装（低优先级）
```bash
# MCP 服务器开发
hermes skills install official/mcp/fastmcp

# 模型推理优化
hermes skills install official/mlops/tensorrt-llm

# 架构可视化
hermes skills install official/creative/concept-diagrams
```

---

## 📊 当前 Hermes 状态

| 项目 | 状态 |
|------|------|
| **Hermes 目录** | ❌ 未找到（/root/.openclaw/workspace/hermes/） |
| **18790 端口** | ❌ 未运行 |
| **日志** | ✅ 存在（logs/hermes.log） |
| **最佳实践文档** | ✅ 存在（docs/hermes-best-practices.md） |
| **NVIDIA 集成** | ✅ 已验证（API Key 有效） |

---

## 🎯 下一步建议

1. **部署 Hermes 后端**（18790 端口）
2. **安装高优先级技能**（Chroma/faiss/segment-anything）
3. **配置医疗知识库**（RAG + 向量检索）
4. **集成图像分割**（SAM 用于超声分析）
5. **测试诊断服务**（双模型路由）

---

_文档由小超同学维护，最后更新时间：2026-04-25_
