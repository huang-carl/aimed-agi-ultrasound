# Hermes + 多 Agent 最佳实践

_来源：腾讯新闻 - 万字保姆级教程：Hermes+Kimi K2.6 打造 7x24h Agent 军团_
_整理时间：2026-04-22_
_整理人：小超同学_

---

## 🎯 核心架构

### 多 Agent 协同模式
```
用户 (飞书) → 总管 Agent → 各专科 Agent → 共享上下文 (Honcho) → 交付结果
```

### 六角色 Profile 结构
```
profiles/
├── commander/           # 总管：调度协调，不直接产出
├── market-director/     # 市场总监：调研分析
├── product-director/    # 产品总监：PRD 输出
├── architect-director/  # 架构总监：技术评审
├── dev-director/        # 开发总监：代码实现
└── test-director/       # 测试总监：测试验收
```

### 工作流
1. **市场调研** → 输出竞品分析报告
2. **产品设计** → 输出 PRD 文档
3. **架构设计** → 评审 PRD 可实现性
4. **开发实现** → 调用工具完成开发
5. **测试验收** → 输出测试报告并修复

---

## 🔧 技术配置

### Hermes 安装
```bash
# WSL 2 环境
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 启动
source ~/.bashrc
hermes
```

### 模型选择建议
**推荐：Kimi K2.6-code-preview**
- 超长上下文窗口（适合长任务）
- 长任务链路稳定（不失忆）
- 多工具协同能力强

**配置示例：**
```yaml
# profiles/commander/config.yaml
model: kimi-for-coding
model_version: k2.6-code-preview
api_key: ${KIMI_API_KEY}
```

### 飞书 Gateway 配置
```bash
hermes gateway setup
# 选择飞书 → 自动创建机器人 → 私聊配对授权
# 安装为 systemd 服务
```

**WSL 提权操作：**
```bash
which hermes
sudo <hermes 路径> gateway install --system --run-as-user <username>
sudo <hermes 路径> gateway start --system

# 验证
systemctl status hermes-gateway
journalctl -u hermes-gateway -f
```

---

## 🧠 核心原理

### 四组件架构
| 组件 | 职责 | 类比 |
|------|------|------|
| **Profiles** | 独立 Agent 组织方式 | 公司不同部门 |
| **Gateway** | 对外消息通道 | 前台/客服 |
| **Honcho** | 共享长期记忆 | 共享知识库 |
| **tmux** | 进程保活 | 保持办公室灯亮 |

### Agent 间通信流程
1. 通过 **Honcho** 写入共享上下文
2. 通过 **Gateway** 发送通知（飞书@）
3. 目标 Agent 读取共享上下文
4. 完成后回写结果并通知总管

### 关键公式
```
角色化分工 (Profiles) + 共享上下文 (Honcho) + 明确任务交接 (Gateway) = 多 Agent 协同
```

---

## 📁 文件结构

| 文件/目录 | 作用 |
|----------|------|
| `config.yaml` | Agent 人设配置（模型、角色、工具） |
| `.env` | 敏感信息（API Keys、网关令牌） |
| `profiles/` | 多 Agent 独立配置 |
| `skills/` | 可调用的工具（Python 脚本） |
| `memory/` | 记忆存储（每日 + 长期 + Honcho） |
| `sessions/` | 会话历史 |
| `gateway/` | 消息平台连接配置 |

---

## ⚠️ 常见问题排查

| 错误类型 | 典型报错 | 解决方案 |
|----------|----------|----------|
| 命令找不到 | `hermes: command not found` | `source ~/.bashrc` |
| Python 版本低 | `requires Python >=3.10` | 升级 Python 到 3.10+ |
| API Key 错误 | `Invalid API key` | 检查 `.env` 配置 |
| 速率限制 | `Too many requests` | 降低频率或升级套餐 |
| Docker 未启动 | `Cannot connect to Docker` | 启动 Docker 服务 |
| Docker 权限 | `permission denied` | 用户加入 docker 组 |
| MCP 连接失败 | `MCP server timeout` | 检查 MCP 服务器配置 |
| OAuth 过期 | `OAuth token expired` | 重新授权 |
| 上下文溢出 | `context length exceeded` | 清理历史或换大模型 |
| Subagent 超时 | `RPC timeout after 30s` | 增加超时时间 |

**排查三步走：**
1. 看报错信息，对照上表确定类型
2. 用 `hermes --verbose` 查看详细日志
3. 从环境配置→API 配置→服务状态逐项检查

---

## 💡 对 AIMED 项目的借鉴

### 立即应用（高优先级）
- ✅ 飞书 Gateway 配置流程 → 完善小菲同学渠道
- ✅ Profile 结构设计 → 优化专科 Agent 配置
- ✅ Honcho 共享记忆 → 实现 Agent 上下文同步
- ✅ 常见问题排查清单 → 节省调试时间

### 中期评估（中优先级）
- ⏳ Kimi K2.6 API Key 申请 → 与 Qwen-Plus 对比测试
- ⏳ MCP 工具链配置 → 参考 OAuth 和连接配置
- ⏳ 错误处理优化 → 借鉴排查清单

### 选择性参考（低优先级）
- ⏸️ Claude Code 集成 → 医疗场景无需代码生成
- ⏸️ 7x24h 持续运行 → 按需诊断即可
- ⏸️ 多群聊路由 → 当前单渠道足够

---

## 🎓 关键洞察

> **「框架负责协调，模型负责执行」**

这正是 AIMED 项目的核心设计原则：
- **Hermes 后端** → 多 Agent 调度和流程管理
- **底层模型**（阿里云百炼/Kimi）→ 具体诊断推理

---

## 📚 相关链接

- Hermes Agent GitHub: https://github.com/NousResearch/hermes-agent
- Kimi K2.6 发布：https://www.moonshot.cn/
- 原文：https://view.inews.qq.com/a/20260421A05E9Z00

---

_此文档作为 AIMED 项目 Hermes 配置的参考手册，定期更新优化。_
