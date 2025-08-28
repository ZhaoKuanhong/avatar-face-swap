import logging

from flask import Flask, send_from_directory, redirect
from flask_cors import CORS

from lib.common.constants import *
from lib.utils import *

app = Flask(__name__)
CORS(app)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/verify', methods=['POST'])
def verify_token():
    """验证口令并返回 event_id 和 description"""
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify(error='缺少 token'), 400

    token = data['token']
    if token == ADMIN_PASSWORD:
        token_data = {'role': 'admin'}

        log_activity(
            level="INFO",
            module="用户认证",
            action="管理员登录",
            user_id="admin",
            details={"ip": request.remote_addr}
        )

        return jsonify(event_id='admin', token=token_serializer.dumps(token_data))
    else:
        result = query_db(
            'SELECT event_id, description,is_open FROM event WHERE token = ?',
            [token],
            one=True
        )

        if result:
            if result['is_open']:
                token_data = {'role': 'user', 'event_id': result['event_id']}

                log_activity(
                    level="INFO",
                    module="用户认证",
                    action="用户登录",
                    event_id=result['event_id'],
                    details={"ip": request.remote_addr}
                )

                return jsonify(event_id=result['event_id'], description=result['description'],
                               token=token_serializer.dumps(token_data)), 200

            else:
                return jsonify(error='活动未开始或已结束采集'), 400
        else:
            return jsonify(error='无效的 token'), 404


@app.route('/api/events', methods=['GET'])
@requires_admin_permission
def get_events():
    return jsonify(events=load_events())


@app.route('/api/events/<int:event_id>', methods=['POST'])
@requires_event_permission
def add_or_update_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify(error="未提供任何数据"), 400

    # 从 JSON 中获取可选字段
    description = data.get('description')
    token = data.get('token')
    event_date = data.get('event_date')
    is_open = data.get('is_open')  # 可以是 bool 或 int

    try:
        # 检查事件是否已存在
        existing = query_db('SELECT * FROM event WHERE event_id = ?', [event_id], one=True)

        if existing:
            # 存在：只更新提供的字段
            fields = []
            values = []

            if description is not None:
                fields.append('description = ?')
                values.append(description)
            if token is not None:
                fields.append('token = ?')
                values.append(token)
            if event_date is not None:
                fields.append('event_date = ?')
                values.append(event_date)
            if is_open is not None:
                fields.append('is_open = ?')
                values.append(int(is_open))

            if not fields:
                return jsonify(message="未提供需要更新的字段"), 400

            update_sql = f'UPDATE event SET {", ".join(fields)} WHERE event_id = ?'
            values.append(event_id)

            execute_db(update_sql, values)

            user_data = verify_auth_token(request.headers.get('Authorization').replace('Bearer ', ''))
            user_id = user_data.get('user_id') if user_data else None

            log_activity(
                level="INFO",
                module="活动管理",
                action="更新活动" if existing else "创建活动",
                user_id=user_id,
                event_id=event_id,
                details={"description": description}
            )

            return jsonify(message="事件已更新"), 200

        else:
            # 不存在：必须有所有字段才能插入
            if not all([description, token, event_date]):
                return jsonify(error="新建事件需要 description、token、event_date"), 400

            isOpen = int(is_open) if is_open is not None else 0

            execute_db('''
                INSERT INTO event (event_id, description, token, event_date, is_open)
                VALUES (?, ?, ?, ?, ?)
            ''', [event_id, description, token, event_date, isOpen])

            return jsonify(message="事件已创建"), 201

    except Exception as e:
        return jsonify(error=f"数据库错误: {e}"), 500


@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@requires_admin_permission
def delete_event(event_id):
    try:
        # 检查事件是否存在
        existing = query_db('SELECT * FROM event WHERE event_id = ?', [event_id], one=True)

        if not existing:
            return jsonify(error=f"事件 ID '{event_id}' 不存在"), 404

        # 删除事件
        execute_db('DELETE FROM event WHERE event_id = ?', [event_id])

        log_activity(
            level="WARNING",
            module="活动管理",
            action="删除活动",
            user_id="admin",
            event_id=str(event_id)
        )

        return jsonify(message=f"事件 {event_id} 已成功删除"), 200

    except Exception as e:
        return jsonify(error=f"删除事件时发生错误: {str(e)}"), 500


@app.route('/api/events/<event_id>/faces/<face_filename>/info')
@requires_event_permission
def get_face_qq_info(event_id, face_filename):
    """获取人脸对应的QQ号码信息"""
    try:
        # 构建JSON文件路径
        base_filename = os.path.splitext(face_filename)[0]
        json_filename = f"{base_filename}.json"
        json_path = os.path.join('event', event_id, 'upload', json_filename)

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify({
                    'qq_number': data.get('qq_number'),
                    'filename': data.get('filename')
                })
        else:
            return jsonify({'qq_number': None, 'filename': face_filename})
    except Exception as e:
        return jsonify({'error': str(e), 'qq_number': None}), 500


@app.route('/api/events/<event_id>/qq-nickname/<qq_number>')
@requires_event_permission
def get_qq_nickname(event_id, qq_number):
    """获取QQ昵称的代理接口"""
    try:
        import requests
        import json

        # Tips: 先用这个，不知道啥时候失效
        url = f"https://api.ilingku.com/int/v1/qqname?qq={qq_number}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        content = response.content.decode('utf-8')
        data = json.loads(content)

        if data.get('code') == 200 and 'name' in data:
            nickname = data.get('name')

            if nickname and nickname.strip():
                return jsonify({
                    'nickname': nickname,
                    'qq_number': qq_number,
                    'success': True
                })

        return jsonify({
            'nickname': f'QQ用户{qq_number}',
            'qq_number': qq_number,
            'success': False
        })

    except Exception as e:
        print(f"获取QQ昵称失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'nickname': f'QQ用户{qq_number}',
            'qq_number': qq_number,
            'success': False,
            'error': str(e)
        })


@app.route('/api/events/<event_id>/token', methods=['GET'])
@requires_admin_permission
def get_event_qr_code(event_id):
    referer = request.headers.get('Referer') or request.headers.get('Origin')
    if not referer:
        return jsonify({'error': 'Missing Referer or Origin'}), 400

    token = load_event(event_id)['token']
    if not token:
        return jsonify({'error': 'Event not found or token missing'}), 404
    return jsonify({'token': token})


@app.route('/api/events/<event_id>/pic', methods=['GET'])
@requires_event_permission
def get_event_pic(event_id):
    event_pic_folder = os.path.join('event', event_id)
    return send_from_directory(event_pic_folder, 'input.jpg')


@app.route('/api/events/<event_id>/pic/info', methods=['GET'])
@requires_admin_permission
def get_event_pic_info(event_id):
    event_faces_folder = os.path.join('event', event_id)
    try:
        if not os.path.exists(event_faces_folder):
            return jsonify(error=f"Event ID '{event_id}' 的人脸文件夹不存在"), 404
        pic_info = json.load(open(os.path.join(event_faces_folder, 'faces_info.json'), 'r'))['image_info']
        return jsonify(pic_info=pic_info, event_id=event_id)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/api/events/<event_id>/faces')
@requires_event_permission
def get_event_faces(event_id):
    """获取特定 event_id 对应的 cropped_faces 文件夹中的所有人脸文件名。"""
    event_faces_folder = os.path.join('event', event_id, CROPPED_FACES_FOLDER)
    try:
        if not os.path.exists(event_faces_folder):
            return jsonify(error=f"Event ID '{event_id}' 的人脸文件夹不存在"), 404
        face_files = [f for f in os.listdir(event_faces_folder) if os.path.isfile(os.path.join(event_faces_folder, f))]
        return jsonify(faces=face_files, event_id=event_id)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/api/events/<event_id>/faces/info')
@requires_admin_permission
def get_event_faces_info(event_id):
    event_faces_folder = os.path.join('event', event_id)
    try:
        if not os.path.exists(event_faces_folder):
            return jsonify(error=f"Event ID '{event_id}' 的人脸文件夹不存在"), 404
        face_info = json.load(open(os.path.join(event_faces_folder, 'faces_info.json'), 'r'))['faces']
        return jsonify(faces=face_info, event_id=event_id)
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/api/events/<int:event_id>/faces/<face_filename>', methods=['DELETE'])
@requires_admin_permission
def delete_face(event_id, face_filename):
    """删除误识别的人脸"""
    try:
        import os
        import json

        event_dir = os.path.join('event', str(event_id))
        cropped_faces_dir = os.path.join(event_dir, CROPPED_FACES_FOLDER)
        upload_dir = os.path.join(event_dir, 'upload')
        faces_info_path = os.path.join(event_dir, 'faces_info.json')

        # 检查人脸文件是否存在
        face_path = os.path.join(cropped_faces_dir, face_filename)
        if not os.path.exists(face_path):
            return jsonify(error=f'人脸文件 {face_filename} 不存在'), 404

        os.remove(face_path)

        base_filename = os.path.splitext(face_filename)[0]

        # 删除用户上传的头像
        for ext in ['jpg', 'jpeg', 'png']:
            upload_file = os.path.join(upload_dir, f"{base_filename}.{ext}")
            if os.path.exists(upload_file):
                os.remove(upload_file)
                break

        # 删除对应的JSON信息文件
        json_file = os.path.join(upload_dir, f"{base_filename}.json")
        if os.path.exists(json_file):
            os.remove(json_file)

        # 更新faces_info.json，移除对应的人脸信息
        if os.path.exists(faces_info_path):
            with open(faces_info_path, 'r', encoding='utf-8') as f:
                faces_info = json.load(f)

            # 从faces数组中移除对应的人脸信息
            if 'faces' in faces_info:
                faces_info['faces'] = [
                    face for face in faces_info['faces']
                    if face.get('filename') != face_filename
                ]

            with open(faces_info_path, 'w', encoding='utf-8') as f:
                json.dump(faces_info, f, indent=4, ensure_ascii=False)

        # 记录日志
        log_activity(
            level="WARNING",
            module="活动管理",
            action="删除误识别人脸",
            user_id="admin",
            event_id=str(event_id),
            details={"deleted_face": face_filename}
        )

        return jsonify(message=f'人脸 {face_filename} 已成功删除'), 200

    except Exception as e:
        print(f"删除人脸失败: {e}")
        return jsonify(error=f'删除人脸失败: {str(e)}'), 500


@app.route('/api/events/<int:event_id>/faces/add-manual', methods=['POST'])
@requires_admin_permission
def add_manual_face(event_id):
    """手动添加人脸区域"""
    try:
        data = request.get_json()
        if not data:
            return jsonify(error="未提供数据"), 400
        
        required_fields = ['x1', 'y1', 'x2', 'y2']
        if not all(field in data for field in required_fields):
            return jsonify(error=f"缺少必需字段: {required_fields}"), 400
        
        x1, y1, x2, y2 = data['x1'], data['y1'], data['x2'], data['y2']
        import time
        face_id = data.get('face_id', f'manual_{int(time.time())}')
        
        # 基础验证
        if x1 >= x2 or y1 >= y2:
            return jsonify(error="坐标不正确：x1应小于x2，y1应小于y2"), 400
        
        if x2 - x1 < 20 or y2 - y1 < 20:
            return jsonify(error="人脸区域太小，最小尺寸为20x20像素"), 400
        
        # 读取原始图像进行验证
        event_dir = os.path.join('event', str(event_id))
        input_image_path = os.path.join(event_dir, 'input.jpg')
        
        if not os.path.exists(input_image_path):
            return jsonify(error="原始图像不存在"), 404
        
        img = cv2.imread(input_image_path)
        if img is None:
            return jsonify(error="无法读取原始图像"), 500
        
        img_h, img_w = img.shape[:2]
        
        # 确保坐标在图像范围内
        x1 = max(0, min(x1, img_w))
        y1 = max(0, min(y1, img_h))
        x2 = max(x1, min(x2, img_w))
        y2 = max(y1, min(y2, img_h))
        
        # 裁剪人脸区域
        face_roi = img[y1:y2, x1:x2]
        
        # 保存裁剪的人脸
        cropped_faces_dir = os.path.join(event_dir, CROPPED_FACES_FOLDER)
        os.makedirs(cropped_faces_dir, exist_ok=True)
        
        face_filename = f"{face_id}.jpg"
        face_path = os.path.join(cropped_faces_dir, face_filename)
        cv2.imwrite(face_path, face_roi)
        
        # 更新faces_info.json
        faces_info_path = os.path.join(event_dir, 'faces_info.json')
        
        if os.path.exists(faces_info_path):
            with open(faces_info_path, 'r', encoding='utf-8') as f:
                faces_info = json.load(f)
        else:
            # 如果不存在，创建基础结构
            faces_info = {
                "image_info": {
                    "width": img_w,
                    "height": img_h,
                    "filename": "input.jpg"
                },
                "faces": []
            }
        
        # 添加新的人脸信息
        new_face_info = {
            "filename": face_filename,
            "coordinates": {
                "x1": int(x1),
                "y1": int(y1),
                "x2": int(x2),
                "y2": int(y2)
            },
            "confidence": 1.0,
            "manual": True,
            "face_id": face_id
        }
        
        faces_info["faces"].append(new_face_info)
        
        # 保存更新后的信息
        with open(faces_info_path, 'w', encoding='utf-8') as f:
            json.dump(faces_info, f, indent=4, ensure_ascii=False)
        
        # 记录日志
        log_activity(
            level="INFO",
            module="图片处理",
            action="手动添加人脸",
            user_id="admin",
            event_id=str(event_id),
            details={
                "face_id": face_id,
                "coordinates": new_face_info["coordinates"],
                "manual": True
            }
        )
        
        return jsonify({
            'message': '人脸添加成功',
            'face_info': new_face_info
        }), 201
        
    except Exception as e:
        print(f"手动添加人脸失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify(error=f'添加人脸失败: {str(e)}'), 500


@app.route('/api/events/<event_id>/faces/<filename>')
@requires_event_permission
def get_event_face_image(event_id, filename):
    """提供特定 event_id 对应的 cropped_faces 文件夹中的人脸图片。"""
    event_faces_folder = os.path.join('event', event_id, CROPPED_FACES_FOLDER)
    return send_from_directory(event_faces_folder, filename)


@app.route('/api/events/<event_id>/faces/upload/<filename>')
@requires_event_permission
def get_upload_face_image(event_id, filename):
    """提供特定 event_id 对应的 cropped_faces 文件夹中的人脸图片。"""
    event_faces_folder = os.path.join('event', event_id, 'upload')
    return send_from_directory(event_faces_folder, filename)


@app.route('/api/upload/<event_id>/<selected_face>', methods=['POST'])
@requires_event_permission
def upload_file(event_id, selected_face):
    """接收用户上传的头像，并根据选择的人脸文件名进行命名。"""
    if 'file' not in request.files:
        return jsonify(error='No file part'), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify(error='No selected file'), 400
    if file and allowed_file(file.filename):
        # 获取上传文件的扩展名
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        # 使用选中的人脸文件名作为新的文件名 (去除扩展名，添加上传文件的扩展名)
        new_filename = f"{os.path.splitext(selected_face)[0]}.{file_extension}"
        secure_new_filename = secure_filename(new_filename)

        event_upload_folder = os.path.join('event', event_id, 'upload')
        os.makedirs(event_upload_folder, exist_ok=True)  # 确保 event_id 的上传文件夹存在
        filepath = os.path.join(event_upload_folder, secure_new_filename)
        file.save(filepath)
        return jsonify(message='头像上传成功', filename=secure_new_filename, event_id=event_id,
                       selected_face=selected_face)
    return jsonify(error='Allowed file types are png, jpg, jpeg'), 400


@app.route('/api/upload-qq-avatar/<event_id>/<selected_face>', methods=['POST'])
@requires_event_permission
def upload_qq_avatar(event_id, selected_face):
    data = request.get_json()
    qq_number = data.get('qqNumber')
    if not qq_number:
        return jsonify(error='缺少 QQ 号'), 400

    thread = threading.Thread(
        target=download_qq_avatar_async,
        args=(event_id, selected_face, qq_number)
    )
    thread.start()

    user_data = verify_auth_token(request.headers.get('Authorization').replace('Bearer ', ''))
    user_id = user_data.get('user_id') if user_data else None

    log_activity(
        level="INFO",
        module="图片处理",
        action="上传QQ头像",
        user_id=user_id,
        event_id=event_id,
        details={"face": selected_face, "qq_number": qq_number}
    )

    return jsonify(message='头像上传成功'), 202  # HTTP 202 Accepted


@app.route('/event/<event_id>')
def event_page(event_id):
    """用于前端路由跳转，实际内容由前端 Vue 应用渲染。"""
    return app.send_static_file('index.html')


@app.route('/api/verify-token', methods=['GET'])
def verify_token_api():
    token = None
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]

    if not token:
        return jsonify(error='未提供token'), 401

    user_data = verify_auth_token(token)
    if not user_data:
        return jsonify(error='无效或过期的token'), 401

    return jsonify(role=user_data.get('role'), event_id=user_data.get('event_id'))


@app.route('/api/logs', methods=['GET'])
@requires_admin_permission
def get_system_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    level = request.args.get('level')
    module = request.args.get('module')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    logs_data = get_logs(page, per_page, level, module, start_date, end_date)
    return jsonify(logs_data)


@app.route('/api/events/<int:event_id>/upload-pic', methods=['POST'])
@requires_admin_permission
def upload_event_pic(event_id):
    try:
        if 'file' not in request.files:
            return jsonify(error='No file part'), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify(error='No selected file'), 400

        if file and allowed_file(file.filename):
            # 确保事件目录存在
            event_dir = os.path.join('event', str(event_id))
            os.makedirs(event_dir, exist_ok=True)

            # 保存临时文件
            temp_path = os.path.join(event_dir, 'temp_input.jpg')
            file.save(temp_path)

            # 异步处理图片
            process_image_async(event_id, temp_path)

            log_activity(
                level="INFO",
                module="活动管理",
                action="上传活动图片",
                user_id="admin",
                event_id=str(event_id),
                details={"filename": file.filename}
            )

            return jsonify(message='图片上传成功，正在处理人脸识别'), 202

        return jsonify(error='不支持的文件类型'), 400

    except Exception as e:
        return jsonify(error=f'上传失败: {str(e)}'), 500


@app.route('/api/events/<int:event_id>/process-status', methods=['GET'])
@requires_admin_permission
def get_process_status(event_id):
    try:
        event_dir = os.path.join('event', str(event_id))
        faces_info_path = os.path.join(event_dir, 'faces_info.json')

        if os.path.exists(faces_info_path):
            with open(faces_info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                faces_count = len(data.get('faces', []))

            return jsonify(
                status="completed",
                faces_count=faces_count,
                message=f"处理完成，识别到 {faces_count} 个人脸"
            ), 200
        else:
            # 检查临时文件是否存在，判断是否正在处理
            temp_path = os.path.join(event_dir, 'temp_input.jpg')
            if os.path.exists(temp_path):
                return jsonify(status="processing", message="正在处理中"), 200
            else:
                return jsonify(status="not_started", message="尚未上传图片"), 404

    except Exception as e:
        return jsonify(error=f'获取状态失败: {str(e)}'), 500

@app.route('/')
def index():
    return redirect("https://activity.gdutbandori.org/event")


if __name__ == '__main__':
    app.run(port=5001, debug=True)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)
