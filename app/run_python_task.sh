#!/bin/bash
set -euo pipefail

CRON_ENV_FILE="/run/ctyun-cron.env"

if [ -r "$CRON_ENV_FILE" ]; then
    # 文件由 entrypoint 生成，仅 root 可读。
    source "$CRON_ENV_FILE"
fi

if [ "$#" -lt 1 ]; then
    echo "[!] 未指定要运行的 Python 任务。" >&2
    exit 2
fi

TASK_NAME="$(basename "$1" .py)"
LOG_DIR="/app/data"
LOG_FILE="${LOG_DIR}/cron_${TASK_NAME}.log"
mkdir -p "$LOG_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] [cron] 开始运行 ${TASK_NAME}" | tee -a "$LOG_FILE"
set +e
/usr/bin/python3 -u "$@" 2>&1 | tee -a "$LOG_FILE"
TASK_EXIT_CODE=${PIPESTATUS[0]}
set -e
echo "[$(date '+%Y-%m-%d %H:%M:%S %Z')] [cron] ${TASK_NAME} 结束，退出码 ${TASK_EXIT_CODE}" | tee -a "$LOG_FILE"
exit "$TASK_EXIT_CODE"
