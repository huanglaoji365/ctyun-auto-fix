#!/bin/bash
set -euo pipefail

CRON_ENV_FILE="/run/ctyun-cron.env"

if [ -r "$CRON_ENV_FILE" ]; then
    # 文件由 entrypoint 生成，仅 root 可读。
    source "$CRON_ENV_FILE"
fi

exec /usr/bin/python3 "$@"
