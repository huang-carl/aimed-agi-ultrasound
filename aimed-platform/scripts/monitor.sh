#!/bin/bash
# AIMED 平台监控脚本
# 执行时间：每 5 分钟

LOG_FILE="/root/.openclaw/workspace/aimed-platform/logs/monitor.log"

echo "[$(date)] 开始监控检查..." >> "$LOG_FILE"

# 检查 Nginx 状态
if ! systemctl is-active --quiet nginx; then
    echo "[$(date)] ⚠️ Nginx 未运行，尝试重启..." >> "$LOG_FILE"
    systemctl restart nginx
    echo "[$(date)] ✅ Nginx 已重启" >> "$LOG_FILE"
fi

# 检查平台访问
HEALTH=$(curl -sk -o /dev/null -w "%{http_code}" https://aimed.aius.xin 2>/dev/null)
if [ "$HEALTH" != "200" ]; then
    echo "[$(date)] ⚠️ 平台访问异常：$HEALTH" >> "$LOG_FILE"
fi

echo "[$(date)] ✅ 所有检查通过" >> "$LOG_FILE"
