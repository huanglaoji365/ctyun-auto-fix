# 1. 使用你指定的 Ctyun 镜像作为基础镜像
FROM su3817807/ctyun:latest

# 2. 切换到 root 用户以安装系统级依赖
USER root

# 3. 设置时区为亚洲/上海，确保 Cron 定时任务按北京时间执行
ENV TZ=Asia/Shanghai
ENV RUNNING_IN_DOCKER=true
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 当前部分网络会重置 APT 的 HTTP 大文件连接，统一改用 HTTPS。
RUN sed -i 's|http://|https://|g' /etc/apt/sources.list 2>/dev/null || true && \
    sed -i 's|http://|https://|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true

# 4. 安装 Python3、包管理器、Chromium、中文字体、Cron 以及图像处理底层库。
# 默认使用基础镜像自带的 Debian 官方源；失败时再切换阿里云源。
# 较短的无响应超时可避免镜像不可达时每次卡住一分钟以上。
RUN set -eux; \
    install_packages() { \
        apt-get \
            -o Acquire::Retries=2 \
            -o Acquire::http::Timeout=20 \
            -o Acquire::https::Timeout=20 \
            update; \
        DEBIAN_FRONTEND=noninteractive apt-get \
            -o Acquire::Retries=2 \
            -o Acquire::http::Timeout=20 \
            -o Acquire::https::Timeout=20 \
            install -y --no-install-recommends \
            python3 \
            python3-pip \
            chromium \
            chromium-driver \
            fonts-wqy-zenhei \
            cron \
            libgl1 \
            libglib2.0-0 \
            dos2unix; \
    }; \
    if ! install_packages; then \
        echo "[!] Debian 官方源安装失败，切换到阿里云源重试。"; \
        sed -i 's|deb.debian.org|mirrors.aliyun.com|g; s|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
        sed -i 's|deb.debian.org|mirrors.aliyun.com|g; s|security.debian.org|mirrors.aliyun.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true; \
        rm -rf /var/lib/apt/lists/*; \
        install_packages; \
    fi; \
    rm -rf /var/lib/apt/lists/*

# 5. 安装 Python 依赖（Debian 12 默认开启 PEP 668，需要 break-system-packages）。
# 某些网络到默认 PyPI 路由不稳定，依次尝试三个 HTTPS 源。
RUN set -eux; \
    install_python_packages() { \
        pip3 install \
            --no-cache-dir \
            --disable-pip-version-check \
            --timeout 30 \
            --retries 2 \
            --index-url "$1" \
            --break-system-packages \
            DrissionPage==4.0.4.19 \
            ddddocr; \
    }; \
    install_python_packages https://mirrors.aliyun.com/pypi/simple \
        || install_python_packages https://pypi.tuna.tsinghua.edu.cn/simple \
        || install_python_packages https://pypi.org/simple

# 6. 将 Python 脚本和启动脚本复制到工作目录
COPY login_script.py /app/login_script.py
COPY pc_login.py /app/pc_login.py
COPY task_lock.py /app/task_lock.py
COPY entrypoint.sh /app/entrypoint.sh
COPY run_python_task.sh /app/run_python_task.sh

# 7. 修复 Windows 环境下可能产生的 CRLF 换行符问题，并赋予执行权限
RUN dos2unix /app/entrypoint.sh /app/run_python_task.sh \
    && chmod +x /app/entrypoint.sh /app/run_python_task.sh

# 8. 配置 Cron 定时任务
RUN { \
    echo "0 3,20 * * * root /app/run_python_task.sh /app/login_script.py > /proc/1/fd/1 2>&1"; \
    echo "0 4,6 * * * root /app/run_python_task.sh /app/pc_login.py > /proc/1/fd/1 2>&1"; \
    } > /etc/cron.d/ctyun-cron \
    && chmod 0644 /etc/cron.d/ctyun-cron

# 9. 覆盖原镜像的 ENTRYPOINT，使用我们的双进程启动脚本
ENTRYPOINT ["/app/entrypoint.sh"]
