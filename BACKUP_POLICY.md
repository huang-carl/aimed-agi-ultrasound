# BACKUP_POLICY.md - 重大修改前备份机制

**生效时间：** 2026-05-04
**决策人：** Skytop 总

---

## 📋 触发条件

以下操作**必须**先执行备份流程，再获得用户确认：

### 重大修改（必须备份）
- 网站结构重组（新增/删除页面、目录变更）
- 导航栏/路由变更
- 身份体系/登录逻辑修改
- 数据库/智能合约结构变更
- 配置文件大规模修改
- API 接口变更（影响前端调用）
- 跨文件重构（修改 3 个以上文件）

### 常规修改（可不备份）
- 单个文件内容微调（文字、颜色、间距）
- 修复 typo
- 日志清理、临时文件删除

---

## 🔄 标准流程

```
1. 识别修改类型 → 判断是否"重大修改"
2. 重大修改 → 主动询问用户：
   "本次修改属于 [修改类型]，建议先备份当前版本。
    是否执行备份？[Y/N]"
3. 用户确认后 → 执行备份（改造前快照）
4. 备份完成 → 告知用户备份路径 + 撤回方法
5. 用户确认"开始修改" → 执行修改
6. 修改完成后 → 主动询问用户：
   "修改已完成，是否需要保存当前版本为备份点？
    方便后续随时回退。[Y/N]"
7. 用户确认后 → 创建改造后备份 tag
```

---

## 💾 备份方式

### 方式一：Git Tag（推荐）
```bash
# 备份
cd /root/.openclaw/workspace
git add -A
git commit -m "backup: [修改描述] - [日期]"
git tag -a backup-[YYYY-MM-DD]-[序号] -m "[修改描述]"
git push origin backup-[YYYY-MM-DD]-[序号]

# 撤回
git checkout backup-[YYYY-MM-DD]-[序号]
# 或创建恢复分支
git checkout -b restore-from-[backup-tag]
```

### 方式二：文件快照
```bash
# 备份
tar -czf /root/backups/static-backup-[YYYY-MM-DD]-[序号].tar.gz /root/.openclaw/workspace/static/
tar -czf /root/backups/portal-backup-[YYYY-MM-DD]-[序号].tar.gz /root/.openclaw/workspace/static/portal/

# 撤回
tar -xzf /root/backups/static-backup-[YYYY-MM-DD]-[序号].tar.gz -C /
```

### 方式三：版本目录
```bash
# 备份
cp -r /root/.openclaw/workspace/static /root/.openclaw/workspace/static.backup.[YYYY-MM-DD].[序号]

# 撤回
rm -rf /root/.openclaw/workspace/static
mv /root/.openclaw/workspace/static.backup.[YYYY-MM-DD].[序号] /root/.openclaw/workspace/static
```
```

---

## 📝 备份日志

| 日期 | 备份标签 | 修改内容 | 备份方式 | 状态 |
|------|----------|----------|----------|------|
| 2026-05-04 | backup-base-20260504 | 基础备份：官网 + 双平台架构 | git tag | ✅ 基础版本 |

---

## ⚠️ 注意事项

1. **备份后必须告知用户：**
   - 备份路径/标签
   - 撤回命令（复制即用）
   - 备份大小

2. **用户未确认备份时：**
   - 不执行任何重大修改
   - 即使用户说"直接改"，也要再确认一次

3. **备份保留策略：**
   - 保留最近 5 个备份
   - 超过 5 个时自动清理最旧的
   - 重要节点备份永久保留（如 V1.0 正式版）

---

_此机制由 Skytop 总提出，小菲同学执行。_
