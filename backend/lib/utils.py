import inspect
import json
import threading
from datetime import datetime, timedelta

import cv2
import dlib
import jwt
import requests
from flask import jsonify, request
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import URLSafeTimedSerializer as Serializer
from lib.common.constants import *
from lib.db_utils import execute_db, query_db
from werkzeug.utils import secure_filename

# 导入增强版人脸检测器
try:
    from lib.face_detection.enhanced_detector import detect_faces_in_image
    ENHANCED_DETECTION_AVAILABLE = True
    print('[Utils] ✓ 增强版人脸检测器可用（包含RetinaFace支持）')
except ImportError as e:
    ENHANCED_DETECTION_AVAILABLE = False
    print(f'[Utils] ⚠ 增强版人脸检测器不可用: {e}')
    print('[Utils] 将使用传统dlib检测器')

token_serializer = Serializer(SECRET_KEY)

def create_jwt_token(user_id: str, role: str, user_email: str = None):
    payload = {
        'sub': user_id,
        'role': role,
        'user_email': user_email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=int(os.getenv('JWT_EXPIRES_IN', 3600)))
    }
    token = jwt.encode(payload, os.getenv('JWT_SECRET'), algorithm='HS256')
    return token

def load_events(user_email=None):
    """
    从 SQLite 数据库中加载 event 表的数据。
    如果提供了 user_email，则只加载该用户创建的活动。
    """
    query = 'SELECT event_id, description, event_date, is_open FROM event'
    args = []

    if user_email is not None:
        query += ' WHERE creator = ?'
        args.append(user_email)

    try:
        rows = query_db(query, args=tuple(args))
        events = [
            {
                "event_id": row["event_id"],
                "description": row["description"],
                "event_date": row["event_date"],
                "is_open": bool(row["is_open"])
            } for row in rows
        ]
        return events
    except Exception as e:
        print(f"[load_events] 数据库读取失败: {e}")
        return []

def load_event(event_id):
    """根据 event_id 从 SQLite 数据库中加载单个活动。"""
    try:
        row = query_db('SELECT event_id, description, event_date, is_open, token FROM event WHERE event_id = ?', (event_id,), one=True)
        if row:
            return {
                "event_id": row["event_id"],
                "description": row["description"],
                "event_date": row["event_date"],
                "is_open": bool(row["is_open"]) if row["is_open"] is not None else False,
                "token": row["token"]
            }
        else:
            return None
    except Exception as e:
        print(f"[load_event] 数据库读取失败: {e}")
        return None


def write_event(event_id, description, token, event_date):
    """
    将事件写入 SQLite 数据库。如果 event_id 已存在，则更新记录；否则插入新记录。
    """
    try:
        # 检查事件是否已存在
        existing = query_db('SELECT 1 FROM event WHERE event_id = ?', [event_id], one=True)

        if existing:
            # 更新已有事件
            execute_db('''
                UPDATE event
                SET description = ?, token = ?, event_date = ?
                WHERE event_id = ?
            ''', [description, token, event_date, event_id])
        else:
            # 插入新事件
            execute_db('''
                INSERT INTO event (event_id, description, token, event_date)
                VALUES (?, ?, ?, ?)
            ''', [event_id, description, token, event_date])
    except Exception as e:
        print(f"Error writing event: {e}")


def download_qq_avatar_async(event_id, selected_face, qq_number):
    try:
        # 构建路径
        secure_selected_face = secure_filename(selected_face)
        event_upload_folder = os.path.join('event', event_id, 'upload')
        os.makedirs(event_upload_folder, exist_ok=True)

        # 保存 JSON 元信息
        json_filename = f"{os.path.splitext(secure_selected_face)[0]}.json"
        json_filepath = os.path.join(event_upload_folder, json_filename)
        json_data = {
            'filename': secure_selected_face,
            'qq_number': qq_number
        }
        with open(json_filepath, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        # 下载头像
        qq_avatar_url = f"https://q1.qlogo.cn/g?b=qq&nk={qq_number}&s=640"
        response = requests.get(qq_avatar_url, stream=True, timeout=5, verify=False)
        response.raise_for_status()

        avatar_filename = f"{os.path.splitext(secure_selected_face)[0]}.jpg"
        filepath = os.path.join(event_upload_folder, avatar_filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[OK] QQ头像下载成功: {avatar_filename}")

    except Exception as e:
        print(f"[ERROR] 下载/保存 QQ 头像失败: {e}")


def verify_auth_token(token):
    try:
        data = token_serializer.loads(token, max_age=3600)
        return data
    except SignatureExpired:
        return None  # 过期
    except BadSignature:
        return None  # 无效


def requires_event_permission(func):
    def wrapper(event_id, *args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(error='缺少 token'), 401
        if token.startswith("Bearer "):
            token = token[7:]
        user = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        if not user:
            return jsonify(error='无效或过期的 token'), 401
        if user['role'] == 'admin' or str(user.get('role')) == str(event_id):
            return func(event_id, *args, **kwargs)
        else:
            return jsonify(error='无权限访问该资源'), 403

    wrapper.__name__ = func.__name__
    return wrapper


def requires_admin_permission(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify(error='缺少 token'), 401
        if token.startswith("Bearer "):
            token = token[7:]

        user = None
        # 尝试验证 JWT
        try:
            user = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        except Exception:
            # 回退到 itsdangerous 验证
            user = verify_auth_token(token)

        if not user:
            return jsonify(error='无效或过期的 token'), 401

        role = user.get('role') if isinstance(user, dict) else user.get('role', None)
        if role == 'admin':
            sig = inspect.signature(func)
            if 'user_email' in sig.parameters:
                return func(*args, user_email=user.get('user_email'), **kwargs)
            else:
                return func(*args, **kwargs)
        else:
            return jsonify(error='需要管理员权限'), 403

    wrapper.__name__ = func.__name__
    return wrapper

def get_real_ip():
    if 'CF-Connecting-IP' in request.headers:
        return request.headers['CF-Connecting-IP']
    elif 'X-Forwarded-For' in request.headers:
        return request.headers['X-Forwarded-For'].split(',')[0]
    else:
        return request.remote_addr


def log_activity(level, module, action, user_id=None, event_id=None, details=None):
    """activity logs"""
    try:
        ip_address = get_real_ip() if request else None
        details_json = json.dumps(details) if details else None

        execute_db('''
            INSERT INTO system_log (level, module, action, user_id, event_id, ip_address, details)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', [level, module, action, user_id, event_id, ip_address, details_json])

        return True
    except Exception as e:
        print(f"记录日志失败: {e}")
        return False


def get_logs(page=1, per_page=20, level=None, module=None, start_date=None, end_date=None):
    """获取系统日志，支持分页和筛选"""
    try:
        query = 'SELECT * FROM system_log WHERE 1=1'
        params = []

        if level:
            query += ' AND level = ?'
            params.append(level)

        if module:
            query += ' AND module = ?'
            params.append(module)

        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)

        # 添加排序和分页
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])

        # 获取总记录数
        count_query = 'SELECT COUNT(*) as count FROM system_log WHERE 1=1'
        count_params = []

        if level:
            count_query += ' AND level = ?'
            count_params.append(level)

        if module:
            count_query += ' AND module = ?'
            count_params.append(module)

        if start_date:
            count_query += ' AND timestamp >= ?'
            count_params.append(start_date)

        if end_date:
            count_query += ' AND timestamp <= ?'
            count_params.append(end_date)

        total_count_row = query_db(count_query, count_params, one=True)
        total_count = total_count_row['count'] if total_count_row else 0

        # 获取日志记录并转换为可JSON序列化的字典
        logs_rows = query_db(query, params)
        logs = []

        # 转换Row对象为普通字典
        for row in logs_rows:
            log_dict = dict(row)
            # 如果details是JSON字符串，可以选择解析它
            if log_dict.get('details'):
                try:
                    log_dict['details'] = json.loads(log_dict['details'])
                except:
                    pass  # 保持原样
            logs.append(log_dict)

        return {
            'logs': logs,
            'total': total_count,
            'page': page,
            'per_page': per_page
        }
    except Exception as e:
        print(f"获取日志失败: {e}")
        return {'logs': [], 'total': 0, 'page': page, 'per_page': per_page}


def process_image_enhanced(event_id, image_path, detection_strategy="balanced"):
    try:
        if not ENHANCED_DETECTION_AVAILABLE:
            print("[Enhanced] 增强检测器不可用，回退到dlib方法")
            return process_image(event_id, image_path)
        
        base_folder = os.path.join('event', str(event_id))
        cropped_faces_folder = os.path.join(base_folder, CROPPED_FACES_FOLDER)
        upload_folder = os.path.join(base_folder, 'upload')

        os.makedirs(cropped_faces_folder, exist_ok=True)
        os.makedirs(upload_folder, exist_ok=True)

        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            log_activity(
                level="ERROR",
                module="图片处理",
                action="增强人脸识别",
                event_id=event_id,
                details={"error": f"无法加载图像: {image_path}"}
            )
            return False

        # 获取图像尺寸
        height, width = img.shape[:2]
        print(f"[Enhanced] 处理图像: {width}x{height}")
        
        # 图片优化：如果图片过大，先缩小以提高处理速度
        max_dimension = 4096  # 最大尺寸
        if width > max_dimension or height > max_dimension:
            scale = max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            print(f"[Enhanced] 图片过大，缩放至: {new_width}x{new_height}")
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            height, width = img.shape[:2]

        # 使用增强版人脸检测（优先RetinaFace）
        faces_info = detect_faces_in_image(img, strategy=detection_strategy)
        
        # 如果检测结果不理想，尝试召回模式
        if len(faces_info) < 3:  # 对于团建照，期望至少3个以上的人脸
            print("[Enhanced] 检测到的人脸较少，尝试召回模式")
            faces_info = detect_faces_in_image(img, strategy="recall")
        
        print(f"[Enhanced] 检测到 {len(faces_info)} 个人脸")

        # 裁剪并保存人脸
        for face_info in faces_info:
            coords = face_info["coordinates"]
            x1, y1, x2, y2 = coords["x1"], coords["y1"], coords["x2"], coords["y2"]
            
            # 裁剪人脸区域
            cropped_face = img[y1:y2, x1:x2]
            
            if cropped_face.size > 0:
                # 优化：如果裁剪的人脸过大，进行压缩
                face_height, face_width = cropped_face.shape[:2]
                max_face_size = 400  # 人脸最大尺寸
                if face_width > max_face_size or face_height > max_face_size:
                    scale = max_face_size / max(face_width, face_height)
                    new_face_width = int(face_width * scale)
                    new_face_height = int(face_height * scale)
                    cropped_face = cv2.resize(cropped_face, (new_face_width, new_face_height), interpolation=cv2.INTER_AREA)
                
                # 保存裁剪的人脸（使用适当的压缩质量）
                output_path = os.path.join(cropped_faces_folder, face_info["filename"])
                cv2.imwrite(output_path, cropped_face, [cv2.IMWRITE_JPEG_QUALITY, 90])

        # 保存原始图像到事件目录（压缩）
        original_image_path = os.path.join(base_folder, 'input.jpg')
        cv2.imwrite(original_image_path, img, [cv2.IMWRITE_JPEG_QUALITY, 92])

        # 生成完整的输出数据（保持与原格式兼容）
        output_data = {
            "image_info": {
                "width": width,
                "height": height,
                "filename": os.path.basename(image_path)
            },
            "faces": faces_info,
            "detection_method": "enhanced",
            "detection_strategy": detection_strategy
        }

        # 保存JSON文件
        json_filename = os.path.join(base_folder, 'faces_info.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

        log_activity(
            level="INFO",
            module="图片处理",
            action="增强人脸识别完成",
            event_id=event_id,
            details={
                "faces_count": len(faces_info),
                "detection_method": "enhanced",
                "strategy": detection_strategy,
                "used_retinaface": True  # 标记使用了增强检测器
            }
        )

        return True
        
    except Exception as e:
        print(f"[Enhanced] 增强检测失败: {e}，回退到传统方法")
        
        log_activity(
            level="WARNING",
            module="图片处理",
            action="增强检测失败回退",
            event_id=event_id,
            details={"error": str(e)}
        )
        
        # 回退到传统方法
        return process_image(event_id, image_path)


def process_image_async(event_id, image_path, use_enhanced=True):
    """异步处理图像"""
    target_func = process_image_enhanced if (use_enhanced and ENHANCED_DETECTION_AVAILABLE) else process_image
    
    thread = threading.Thread(
        target=target_func,
        args=(event_id, image_path)
    )
    thread.start()
    return thread


def process_image(event_id, image_path):
    try:
        base_folder = os.path.join('event', str(event_id))
        cropped_faces_folder = os.path.join(base_folder, CROPPED_FACES_FOLDER)
        upload_folder = os.path.join(base_folder, 'upload')

        os.makedirs(cropped_faces_folder, exist_ok=True)
        os.makedirs(upload_folder, exist_ok=True)

        # 加载人脸检测器
        detector = dlib.get_frontal_face_detector()

        # 读取图像
        img = cv2.imread(image_path)
        if img is None:
            log_activity(
                level="ERROR",
                module="图片处理",
                action="人脸识别",
                event_id=event_id,
                details={"error": f"无法加载图像: {image_path}"}
            )
            return False

        # 获取图像尺寸
        height, width = img.shape[:2]
        
        # 图片优化：如果图片过大，先缩小
        max_dimension = 4096
        if width > max_dimension or height > max_dimension:
            scale = max_dimension / max(width, height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            height, width = img.shape[:2]

        # 将图像转换为灰度图，以提高检测效率
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 检测图像中的人脸
        faces = detector(gray)

        # 创建包含图像信息的字典
        output_data = {
            "image_info": {
                "width": width,
                "height": height,
                "filename": os.path.basename(image_path)
            },
            "faces": []
        }

        # 遍历检测到的人脸
        for i, face in enumerate(faces):
            # 获取人脸区域的坐标
            x1, y1 = face.left(), face.top()
            x2, y2 = face.right(), face.bottom()

            # 稍微扩大裁剪区域，以包含更多面部信息
            padding = 10
            cropped_x1 = max(0, x1 - padding)
            cropped_y1 = max(0, y1 - padding)
            cropped_x2 = min(width, x2 + padding)
            cropped_y2 = min(height, y2 + padding)

            # 裁剪人脸区域
            cropped_face = img[cropped_y1:cropped_y2, cropped_x1:cropped_x2]

            # 构建输出文件名
            output_filename = f"face_{i + 1}.jpg"
            output_path = os.path.join(cropped_faces_folder, output_filename)
            
            # 优化：压缩裁剪的人脸
            face_height, face_width = cropped_face.shape[:2]
            max_face_size = 400
            if face_width > max_face_size or face_height > max_face_size:
                scale = max_face_size / max(face_width, face_height)
                new_face_width = int(face_width * scale)
                new_face_height = int(face_height * scale)
                cropped_face = cv2.resize(cropped_face, (new_face_width, new_face_height), interpolation=cv2.INTER_AREA)

            # 保存裁剪的人脸图像（带压缩）
            cv2.imwrite(output_path, cropped_face, [cv2.IMWRITE_JPEG_QUALITY, 90])

            face_info = {
                "filename": output_filename,
                "coordinates": {
                    "x1": int(cropped_x1),
                    "y1": int(cropped_y1),
                    "x2": int(cropped_x2),
                    "y2": int(cropped_y2)
                }
            }
            output_data["faces"].append(face_info)

        if not faces:
            log_activity(
                level="WARNING",
                module="图片处理",
                action="人脸识别",
                event_id=event_id,
                details={"warning": f"在图像中未检测到人脸"}
            )

        # 保存原始图像到事件目录
        original_image_path = os.path.join(base_folder, 'input.jpg')
        cv2.imwrite(original_image_path, img, [cv2.IMWRITE_JPEG_QUALITY, 92])

        # 生成JSON文件
        json_filename = os.path.join(base_folder, 'faces_info.json')
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)

        log_activity(
            level="INFO",
            module="图片处理",
            action="人脸识别完成",
            event_id=event_id,
            details={"faces_count": len(faces)}
        )

        return True
    except Exception as e:
        log_activity(
            level="ERROR",
            module="图片处理",
            action="人脸识别",
            event_id=event_id,
            details={"error": str(e)}
        )
        return False
