FROM python:3.12.4

RUN mkdir /app
WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y cmake libgl1-mesa-glx libglib2.0-0
RUN pip install -r requirements.txt
RUN pip install gunicorn gevent

# 复制应用程序代码
COPY blueprints /app/blueprints
COPY lib/ /app/lib
COPY gunconf.py /app/
COPY app.py /app/
COPY download_models.py /app/

# 设置 Flask 环境变量
ENV FLASK_APP=app.py

EXPOSE 5000

# 启动 Flask 应用
CMD ["gunicorn", "-c", "gunconf.py", "app:create_app()"]