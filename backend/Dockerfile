FROM python:3.12.4

WORKDIR /

COPY requirements.txt .
RUN apt-get update && apt-get install -y cmake libgl1-mesa-glx libglib2.0-0
RUN pip install -r requirements.txt
RUN pip install gunicorn gevent

# 复制整个应用程序到 app 目录中
COPY lib/ /lib
COPY models /models
COPY gunconf.py /
COPY app.py /

# 设置 Flask 环境变量
ENV FLASK_APP=app.py

EXPOSE 5000

# 启动 Flask 应用
CMD ["gunicorn", "-c", "gunconf.py", "app:app"]