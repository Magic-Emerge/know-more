# 使用官方的Python基础镜像
FROM python:3.9

# 设置工作目录
WORKDIR /know-more

# 复制依赖文件到容器内
COPY requirements.txt .

# 升级pip
RUN /usr/local/bin/python -m pip install --upgrade pip
# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制配置文件
COPY .env .
# 复制template文件夹
COPY templates/ templates/

# 复制app目录中的所有内容到容器内
COPY app/ app/

# 暴露端口，确保与FastAPI应用中的端口一致
EXPOSE 9000

# 设置容器启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
