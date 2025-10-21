import os
from flask import Blueprint, redirect, session, url_for, jsonify, request
from lib.extensions import oauth
from lib.utils import log_activity, create_jwt_token, query_db, ADMIN_PASSWORD
import jwt

auth_bp = Blueprint('auth', __name__)

FRONTEND_BASE_URL = os.environ.get('FRONTEND_BASE_URL', 'http://localhost:5173')


@auth_bp.route('/api/login')
def login():
    redirect_uri = url_for('auth.auth', _external=True)
    return oauth.keycloak.authorize_redirect(redirect_uri)


@auth_bp.route('/api/auth')
def auth():
    token = oauth.keycloak.authorize_access_token()
    userinfo = token.get('userinfo', {})
    session['user'] = userinfo

    user_email = userinfo.get('email')
    username = userinfo.get('preferred_username')
    role = 'admin'

    jwt_token = create_jwt_token(username, role, user_email)

    log_activity(
        level="INFO",
        module="用户认证",
        action="SSO管理员登录",
        user_id=username,
        details={"email": user_email}
    )

    redirect_url = f"{FRONTEND_BASE_URL}/event/{role}?token={jwt_token}"
    return redirect(redirect_url)


@auth_bp.route('/api/logout')
def logout():
    session.pop('user', None)
    # Ensure server_metadata is loaded
    if not oauth.keycloak.server_metadata:
        oauth.keycloak.fetch_server_metadata()
    keycloak_issuer = oauth.keycloak.server_metadata.get('issuer')
    logout_endpoint = oauth.keycloak.server_metadata.get('end_session_endpoint')

    if not logout_endpoint:
        # Fallback for older Keycloak versions
        logout_endpoint = f"{keycloak_issuer}/protocol/openid-connect/logout"

    # Redirect to the main page of the frontend app after logout
    post_logout_redirect_uri = f"{FRONTEND_BASE_URL}"
    
    return redirect(f"{logout_endpoint}?post_logout_redirect_uri={post_logout_redirect_uri}&client_id={oauth.keycloak.client_id}")


@auth_bp.route('/api/profile')
def profile():
    user = session.get('user')
    if not user:
        return jsonify(error='Unauthorized'), 401
    return jsonify(user)


@auth_bp.route('/api/verify', methods=['POST'])
def verify_token():
    """验证口令并返回 event_id 和 description"""
    data = request.get_json()
    if not data or 'token' not in data:
        return jsonify(error='缺少 token'), 400

    token = data['token']
    if token == ADMIN_PASSWORD:
        log_activity(
            level="INFO",
            module="用户认证",
            action="管理员登录",
            user_id="admin",
            details={"ip": request.remote_addr}
        )
        jwt_token = create_jwt_token('local_admin', 'admin')
        return jsonify(event_id='admin', token=jwt_token)
    else:
        result = query_db(
            'SELECT event_id, description, is_open FROM event WHERE token = ?',
            [token],
            one=True
        )
        if result:
            if result['is_open']:
                log_activity(
                    level="INFO",
                    module="用户认证",
                    action="用户登录",
                    event_id=result['event_id'],
                    details={"ip": request.remote_addr}
                )
                jwt_token = create_jwt_token('local_user', role=result['event_id'])
                return jsonify(event_id=result['event_id'], description=result['description'], token=jwt_token)
            else:
                return jsonify(error='活动未开始或已结束采集'), 400
        else:
            return jsonify(error='无效的 token'), 404


@auth_bp.route('/api/verify-token', methods=['POST'])
def check_token():
    data = request.get_json()
    token = data.get('token')

    if not token:
        return jsonify(error='缺少 token'), 400

    try:
        payload = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return jsonify({
            'user': payload['sub'],
            'role': payload['role'],
            'event_id': payload['role']
        })
    except jwt.ExpiredSignatureError:
        return jsonify(error='Token 已过期'), 401
    except jwt.InvalidTokenError:
        return jsonify(error='无效 token'), 401
