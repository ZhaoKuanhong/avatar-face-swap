<div align="center">
  <h1><b> 团建合影大头自动覆盖 </b></h1>
</div>


## 项目简介

本人有点脸盲，偶尔见上一两面完全认不清群友哪个是哪个，尤其是某些群友喜欢头像和昵称一块换，p大头的时候更找不到！因此一怒之下搓了这个项目

本项目是一个基于 Vue 3 前端和 Flask 后端的 Web 应用程序，旨在提供用户友好的界面，用于选择预先切割的人脸图片，上传个人头像，并为后续的人脸替换和编辑功能做准备。

* **口令验证：** 线下分发口令，群友通过口令进入特定活动。
* **人脸选择：** 用户可以浏览并选择之前通过人脸识别程序生成的人脸图片。
* **头像上传：** 通过 QQ 号获取头像。
* **图片编辑：** 在后台可以进行活动创建、收集管理和最终的图片导出。在导出前可以对大头进行删除、调整大小、旋转等操作。

## 技术栈

**前端**
* Vue 3 + Vite
* Element Plus
* Konva.js (图片编辑)

**后端**
* Flask + Gunicorn
* OpenCV + dlib
* InsightFace (RetinaFace、YuNet、MediaPipe 多模型融合检测)
* SQLite

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 后端部署

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置项

# 下载人脸检测模型（首次运行时也会自动下载）
python download_models.py

# 启动开发服务器
python app.py
```

### 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.development
# 编辑 .env.development，设置 VITE_API_BASE_URL

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### Docker 部署

```bash
cd backend
docker build -t avatar-face-swap .
docker run -p 5000:5000 --env-file .env avatar-face-swap
```

## 环境变量

### 后端 (.env)

| 变量名 | 说明 | 必填 |
|--------|------|------|
| SECRET_KEY | Flask 会话密钥 | 是 |
| ADMIN_PASSWORD | 管理员登录密码 | 是 |
| JWT_SECRET | JWT 签名密钥 | 是 |
| JWT_EXPIRES_IN | JWT 过期时间（秒），默认 3600 | 否 |
| KEYCLOAK_* | Keycloak SSO 配置 | 否 |

### 前端 (.env.*)

| 变量名 | 说明 |
|--------|------|
| VITE_API_BASE_URL | 后端 API 地址 |

## 使用方法

1. 使用 `ADMIN_PASSWORD` 进入后台，创建活动
2. 在活动列表选择"上传图片"，等待后端自动识别切分
3. 对于识别错误的人脸，可以进入"查看活动"中删除
4. 将活动口令分发给参与者
5. 参与者通过口令进入活动，选择自己的人脸并上传头像
6. 管理员在编辑器中调整头像位置，导出最终图片

## 项目结构

```
 backend/
    app.py              # 应用入口
    blueprints/         # API 路由
    lib/                # 核心库
       face_detection/ # 人脸检测模块
    models/             # 模型文件目录
    event/              # 活动数据目录
 frontend/
    src/
       views/          # 页面组件
       components/     # 通用组件
    public/
 README.md
```

## 演示

登录页面

![Login.png](IMAGE_URL_LOGIN)

选择页面

![Main.png](IMAGE_URL_MAIN)

管理页面

![EventList.png](IMAGE_URL_ADMIN)

## License

[MIT](LICENSE)
