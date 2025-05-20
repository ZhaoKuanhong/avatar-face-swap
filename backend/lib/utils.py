import json
import os

import requests
from flask import request, jsonify
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired
from lib.common.constants import *
from lib.db_utils import query_db, execute_db

token_serializer = Serializer(SECRET_KEY)

def load_events():
    """从 SQLite 数据库中加载 event 表的数据。"""
    try:
        rows = query_db('SELECT event_id, description, event_date, is_open FROM event')
        events = []
        for row in rows:
            events.append({
                "event_id": row["event_id"],
                "description": row["description"],
                "event_date": row["event_date"],
                "is_open": bool(row["is_open"]) if row["is_open"] is not None else False  # 转为布尔值
            })
        return events
    except Exception as e:
        print(f"[load_events] 数据库读取失败: {e}")
        return []


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
        response = requests.get(qq_avatar_url, stream=True, timeout=5)
        response.raise_for_status()

        avatar_filename = f"{os.path.splitext(secure_selected_face)[0]}.jpg"
        filepath = os.path.join(event_upload_folder, avatar_filename)

        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[✓] QQ头像下载成功: {avatar_filename}")

    except Exception as e:
        print(f"[✗] 下载/保存 QQ 头像失败: {e}")


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
        user = verify_auth_token(token)
        if not user:
            return jsonify(error='无效或过期的 token'), 401
        if user['role'] == 'admin' or str(user.get('event_id')) == str(event_id):
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
        user = verify_auth_token(token)
        if not user:
            return jsonify(error='无效或过期的 token'), 401
        if user.get('role') == 'admin':
            return func(*args, **kwargs)
        else:
            return jsonify(error='需要管理员权限'), 403
    wrapper.__name__ = func.__name__
    return wrapper