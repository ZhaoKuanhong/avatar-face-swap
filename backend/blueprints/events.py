import os
import json
import threading
import cv2
from flask import Blueprint, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

from lib.common.constants import ALLOWED_EXTENSIONS, CROPPED_FACES_FOLDER
from lib.utils import (
    query_db, execute_db, log_activity, load_events, load_event,
    download_qq_avatar_async, get_logs, process_image_async,
    requires_admin_permission, requires_event_permission
)

events_bp = Blueprint('events', __name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@events_bp.route('/api/events', methods=['GET'])
@requires_admin_permission
def get_events():
    return jsonify(events=load_events())

@events_bp.route('/api/events', methods=['POST'])
@requires_admin_permission
def add_event():
    data = request.get_json()
    if not data:
        return jsonify(error="未提供任何数据"), 400

    description = data.get('description')
    token = data.get('token')
    event_date = data.get('event_date')
    is_open = data.get('is_open')
    try:
            if not all([description, token, event_date]):
                return jsonify(error="新建事件需要 description、token、event_date"), 400
            isOpen = int(is_open) if is_open is not None else 0
            last_id =  execute_db('INSERT INTO event (description, token, event_date, is_open) VALUES (?, ?, ?, ?)',
                       [ description, token, event_date, isOpen])
            log_activity("INFO", "活动管理", "创建活动", event_id=last_id, details={"description": description})
            return jsonify(message="事件已创建",event_id=last_id), 201
    except Exception as e:
        return jsonify(error=f"数据库错误: {e}"), 500

@events_bp.route('/api/events/<int:event_id>', methods=['PUT'])
@requires_admin_permission
def update_event(event_id):
    data = request.get_json()
    if not data:
        return jsonify(error="未提供任何数据"), 400

    description = data.get('description')
    token = data.get('token')
    event_date = data.get('event_date')
    is_open = data.get('is_open')

    try:
        existing = query_db('SELECT * FROM event WHERE event_id = ?', [event_id], one=True)
        if existing:
            fields, values = [], []
            if description is not None: fields.append('description = ?'); values.append(description)
            if token is not None: fields.append('token = ?'); values.append(token)
            if event_date is not None: fields.append('event_date = ?'); values.append(event_date)
            if is_open is not None: fields.append('is_open = ?'); values.append(int(is_open))

            if not fields:
                return jsonify(message="未提供需要更新的字段"), 400

            update_sql = f'UPDATE event SET {", ".join(fields)} WHERE event_id = ?'
            values.append(event_id)
            execute_db(update_sql, values)
            log_activity("INFO", "活动管理", "更新活动", event_id=event_id, details={"description": description})
            return jsonify(message="事件已更新"), 200
        else:
            if not all([description, token, event_date]):
                return jsonify(error="新建事件需要 description、token、event_date"), 400
            isOpen = int(is_open) if is_open is not None else 0
            execute_db('INSERT INTO event (event_id, description, token, event_date, is_open) VALUES (?, ?, ?, ?, ?)',
                       [event_id, description, token, event_date, isOpen])
            log_activity("INFO", "活动管理", "创建活动", event_id=event_id, details={"description": description})
            return jsonify(message="事件已创建"), 201
    except Exception as e:
        return jsonify(error=f"数据库错误: {e}"), 500


@events_bp.route('/api/events/<int:event_id>', methods=['DELETE'])
@requires_admin_permission
def delete_event(event_id):
    try:
        if not query_db('SELECT * FROM event WHERE event_id = ?', [event_id], one=True):
            return jsonify(error=f"事件 ID '{event_id}' 不存在"), 404
        execute_db('DELETE FROM event WHERE event_id = ?', [event_id])
        log_activity("WARNING", "活动管理", "删除活动", event_id=str(event_id))
        return jsonify(message=f"事件 {event_id} 已成功删除"), 200
    except Exception as e:
        return jsonify(error=f"删除事件时发生错误: {str(e)}"), 500


@events_bp.route('/api/events/<event_id>/faces/<face_filename>/info')
@requires_event_permission
def get_face_qq_info(event_id, face_filename):
    try:
        base_filename = os.path.splitext(face_filename)[0]
        json_path = os.path.join('event', event_id, 'upload', f"{base_filename}.json")
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(qq_number=data.get('qq_number'), filename=data.get('filename'))
        return jsonify(qq_number=None, filename=face_filename)
    except Exception as e:
        return jsonify(error=str(e), qq_number=None), 500


@events_bp.route('/api/events/<event_id>/qq-nickname/<qq_number>')
@requires_event_permission
def get_qq_nickname(event_id, qq_number):
    try:
        import requests
        url = f"https://api.ilingku.com/int/v1/qqname?qq={qq_number}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        data = response.json()
        if data.get('code') == 200 and data.get('name'):
            return jsonify(nickname=data['name'], qq_number=qq_number, success=True)
        return jsonify(nickname=f'QQ用户{qq_number}', qq_number=qq_number, success=False)
    except Exception as e:
        log_activity("ERROR", "工具", "获取QQ昵称失败", details={"error": str(e)})
        return jsonify(nickname=f'QQ用户{qq_number}', qq_number=qq_number, success=False, error=str(e))


@events_bp.route('/api/events/<event_id>/token', methods=['GET'])
@requires_admin_permission
def get_event_qr_code(event_id):
    token = load_event(event_id).get('token')
    if not token:
        return jsonify(error='Event not found or token missing'), 404
    return jsonify(token=token)


@events_bp.route('/api/events/<event_id>/pic', methods=['GET'])
@requires_event_permission
def get_event_pic(event_id):
    return send_from_directory(os.path.join('event', event_id), 'input.jpg')


@events_bp.route('/api/events/<event_id>/pic/info', methods=['GET'])
@requires_admin_permission
def get_event_pic_info(event_id):
    try:
        info_path = os.path.join('event', event_id, 'faces_info.json')
        with open(info_path, 'r') as f: info = json.load(f)['image_info']
        return jsonify(pic_info=info, event_id=event_id)
    except Exception as e:
        return jsonify(error=str(e)), 500


@events_bp.route('/api/events/<event_id>/faces')
@requires_event_permission
def get_event_faces(event_id):
    faces_folder = os.path.join('event', event_id, CROPPED_FACES_FOLDER)
    if not os.path.exists(faces_folder):
        return jsonify(error=f"Event ID '{event_id}' 的人脸文件夹不存在"), 404
    face_files = [f for f in os.listdir(faces_folder) if os.path.isfile(os.path.join(faces_folder, f))]
    return jsonify(faces=face_files, event_id=event_id)


@events_bp.route('/api/events/<event_id>/faces/info')
@requires_admin_permission
def get_event_faces_info(event_id):
    try:
        info_path = os.path.join('event', event_id, 'faces_info.json')
        with open(info_path, 'r') as f: info = json.load(f)['faces']
        return jsonify(faces=info, event_id=event_id)
    except Exception as e:
        return jsonify(error=str(e)), 500


@events_bp.route('/api/events/<int:event_id>/faces/<face_filename>', methods=['DELETE'])
@requires_admin_permission
def delete_face(event_id, face_filename):
    try:
        event_dir = os.path.join('event', str(event_id))
        os.remove(os.path.join(event_dir, CROPPED_FACES_FOLDER, face_filename))
        base_filename = os.path.splitext(face_filename)[0]
        for ext in ['jpg', 'jpeg', 'png']:
            upload_file = os.path.join(event_dir, 'upload', f"{base_filename}.{ext}")
            if os.path.exists(upload_file): os.remove(upload_file); break
        json_file = os.path.join(event_dir, 'upload', f"{base_filename}.json")
        if os.path.exists(json_file): os.remove(json_file)
        
        faces_info_path = os.path.join(event_dir, 'faces_info.json')
        if os.path.exists(faces_info_path):
            with open(faces_info_path, 'r+', encoding='utf-8') as f:
                faces_info = json.load(f)
                faces_info['faces'] = [face for face in faces_info['faces'] if face.get('filename') != face_filename]
                f.seek(0); f.truncate()
                json.dump(faces_info, f, indent=4, ensure_ascii=False)

        log_activity("WARNING", "活动管理", "删除误识别人脸", event_id=str(event_id), details={"deleted_face": face_filename})
        return jsonify(message=f'人脸 {face_filename} 已成功删除'), 200
    except Exception as e:
        return jsonify(error=f'删除人脸失败: {str(e)}'), 500


@events_bp.route('/api/events/<int:event_id>/faces/add-manual', methods=['POST'])
@requires_admin_permission
def add_manual_face(event_id):
    try:
        data = request.get_json()
        x1, y1, x2, y2 = data['x1'], data['y1'], data['x2'], data['y2']
        face_id = data.get('face_id', f'manual_{int(os.times().user)}')

        event_dir = os.path.join('event', str(event_id))
        input_image_path = os.path.join(event_dir, 'input.jpg')
        img = cv2.imread(input_image_path)
        img_h, img_w = img.shape[:2]
        x1, y1, x2, y2 = max(0, min(x1, img_w)), max(0, min(y1, img_h)), max(x1, min(x2, img_w)), max(y1, min(y2, img_h))
        
        face_roi = img[y1:y2, x1:x2]
        face_filename = f"{face_id}.jpg"
        os.makedirs(os.path.join(event_dir, CROPPED_FACES_FOLDER), exist_ok=True)
        cv2.imwrite(os.path.join(event_dir, CROPPED_FACES_FOLDER, face_filename), face_roi)

        faces_info_path = os.path.join(event_dir, 'faces_info.json')
        faces_info = {} 
        if os.path.exists(faces_info_path): 
            with open(faces_info_path, 'r') as f: faces_info = json.load(f)
        else: 
            faces_info = {"image_info": {"width": img_w, "height": img_h, "filename": "input.jpg"}, "faces": []}

        new_face = {"filename": face_filename, "coordinates": {"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)}, "confidence": 1.0, "manual": True, "face_id": face_id}
        faces_info["faces"].append(new_face)
        
        with open(faces_info_path, 'w') as f: json.dump(faces_info, f, indent=4, ensure_ascii=False)
        log_activity("INFO", "图片处理", "手动添加人脸", event_id=str(event_id), details={"face_id": face_id, "coordinates": new_face["coordinates"]})
        return jsonify(message='人脸添加成功', face_info=new_face), 201
    except Exception as e:
        return jsonify(error=f'添加人脸失败: {str(e)}'), 500


@events_bp.route('/api/events/<event_id>/faces/<filename>')
@requires_event_permission
def get_event_face_image(event_id, filename):
    return send_from_directory(os.path.join('event', event_id, CROPPED_FACES_FOLDER), filename)


@events_bp.route('/api/events/<event_id>/faces/upload/<filename>')
@requires_event_permission
def get_upload_face_image(event_id, filename):
    return send_from_directory(os.path.join('event', event_id, 'upload'), filename)


@events_bp.route('/api/upload/<event_id>/<selected_face>', methods=['POST'])
@requires_event_permission
def upload_file(event_id, selected_face):
    if 'file' not in request.files: return jsonify(error='No file part'), 400
    file = request.files['file']
    if file.filename == '': return jsonify(error='No selected file'), 400
    if file and allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        new_filename = f"{os.path.splitext(selected_face)[0]}.{ext}"
        upload_folder = os.path.join('event', event_id, 'upload')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, secure_filename(new_filename)))
        return jsonify(message='头像上传成功', filename=new_filename)
    return jsonify(error='Allowed file types are png, jpg, jpeg'), 400


@events_bp.route('/api/upload-qq-avatar/<event_id>/<selected_face>', methods=['POST'])
@requires_event_permission
def upload_qq_avatar(event_id, selected_face):
    qq_number = request.json.get('qqNumber')
    if not qq_number: return jsonify(error='缺少 QQ 号'), 400
    threading.Thread(target=download_qq_avatar_async, args=(event_id, selected_face, qq_number)).start()
    log_activity("INFO", "图片处理", "上传QQ头像", event_id=event_id, details={"face": selected_face, "qq_number": qq_number})
    return jsonify(message='头像上传成功'), 202


@events_bp.route('/api/logs', methods=['GET'])
@requires_admin_permission
def get_system_logs():
    args = request.args
    return jsonify(get_logs(args.get('page', 1, type=int), args.get('per_page', 20, type=int), args.get('level'), args.get('module'), args.get('start_date'), args.get('end_date')))


@events_bp.route('/api/events/<int:event_id>/upload-pic', methods=['POST'])
@requires_admin_permission
def upload_event_pic(event_id):
    if 'file' not in request.files: return jsonify(error='No file part'), 400
    file = request.files['file']
    if file.filename == '': return jsonify(error='No selected file'), 400
    if file and allowed_file(file.filename):
        event_dir = os.path.join('event', str(event_id))
        os.makedirs(event_dir, exist_ok=True)
        temp_path = os.path.join(event_dir, 'temp_input.jpg')
        file.save(temp_path)
        process_image_async(event_id, temp_path)
        log_activity("INFO", "活动管理", "上传活动图片", event_id=str(event_id), details={"filename": file.filename})
        return jsonify(message='图片上传成功，正在处理人脸识别'), 202
    return jsonify(error='不支持的文件类型'), 400


@events_bp.route('/api/events/<int:event_id>/process-status', methods=['GET'])
@requires_admin_permission
def get_process_status(event_id):
    try:
        info_path = os.path.join('event', str(event_id), 'faces_info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r') as f: faces_count = len(json.load(f).get('faces', []))
            return jsonify(status="completed", faces_count=faces_count, message=f"处理完成，识别到 {faces_count} 个人脸")
        elif os.path.exists(os.path.join('event', str(event_id), 'temp_input.jpg')):
            return jsonify(status="processing", message="正在处理中")
        else:
            return jsonify(status="not_started", message="尚未上传图片"), 404
    except Exception as e:
        return jsonify(error=f'获取状态失败: {str(e)}'), 500
