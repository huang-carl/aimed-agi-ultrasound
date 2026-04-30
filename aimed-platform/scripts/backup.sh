#!/bin/bash
# AIMED 平台自动备份脚本
# 执行时间：每日 02:00

BACKUP_DIR="/root/.openclaw/workspace/aimed-platform/backups"
DATA_DIR="/root/.openclaw/workspace/aimed-platform/static"
DATE=$(date +%Y%m%d_%H%M%S)

echo "[$(date)] 开始备份 AIMED 平台数据..."

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份平台数据
tar -czf "$BACKUP_DIR/platform_$DATE.tar.gz" -C /root/.openclaw/workspace/aimed-platform static/
echo "[$(date)] 平台数据备份完成"

# 清理 7 天前的备份
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete
echo "[$(date)] 清理完成，保留最近 7 天备份"

echo "[$(date)] 备份完成！"
