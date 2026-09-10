# 1. 使用你指定的 Ctyun 镜像作为基础镜像
FROM su3817807/ctyun:latest

# 2. 切换到 root 用户以安装系统级依赖
USER root

# 3. 设置时区为亚洲/上海，确保 Cron 定时任务按北京时间执行
ENV TZ=Asia/Shanghai
ENV RUNNING_IN_DOCKER=true
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 替换为阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list 2>/dev/null || true && \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true

# 4. 安装 Python3、包管理器、Chromium、中文字体、Cron 以及图像处理底层库。
# 国内镜像偶尔会出现索引与软件包不同步；首次安装失败时自动切回 Debian 官方源。
RUN set -eux; \
    install_packages() { \
        apt-get -o Acquire::Retries=5 update; \
        DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y --no-install-recommends \
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
        echo "[!] 阿里云 Debian 镜像安装失败，切换到官方源重试。"; \
        sed -i 's|mirrors.aliyun.com|deb.debian.org|g' /etc/apt/sources.list 2>/dev/null || true; \
        sed -i 's|mirrors.aliyun.com|deb.debian.org|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true; \
        rm -rf /var/lib/apt/lists/*; \
        install_packages; \
    fi; \
    rm -rf /var/lib/apt/lists/*

# 5. 安装 Python 依赖（Debian 12 默认开启 PEP 668，需要 break-system-packages）
RUN pip3 install --no-cache-dir DrissionPage==4.0.4.19 ddddocr --break-system-packages

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
