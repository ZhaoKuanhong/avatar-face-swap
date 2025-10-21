import logging
import os
from flask import Flask, redirect, current_app
from flask_cors import CORS
from dotenv import load_dotenv

from lib.extensions import oauth
from blueprints.auth import auth_bp
from blueprints.events import events_bp

def create_app():
    """Application factory to create and configure the Flask app."""
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')

    # --- Configuration ---
    app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'a-strong-dev-secret-key')
    app.config['JWT_SECRET'] = os.environ.get('JWT_SECRET', 'a-strong-jwt-secret')
    CORS(app)

    # --- Initialize Extensions ---
    oauth.init_app(app)
    oauth.register(
        name='keycloak',
        client_id=os.environ.get('KEYCLOAK_CLIENT_ID'),
        client_secret=os.environ.get('KEYCLOAK_CLIENT_SECRET'),
        server_metadata_url=os.environ.get('KEYCLOAK_SERVER_URL'),
        client_kwargs={'scope': 'openid email profile'}
    )

    # --- Register Blueprints ---
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)

    # --- Main Routes ---
    @app.route('/')
    def index():
        frontend_base_url = os.environ.get('FRONTEND_BASE_URL', 'http://localhost:5173')
        return redirect(f"{frontend_base_url}/event")

    @app.route('/event/<path:path>')
    @app.route('/about')
    def serve_vue_app(path=None):
        """Serve the frontend Vue app for all relevant routes."""
        return current_app.send_static_file('index.html')

    # --- Gunicorn Logging Setup ---
    if __name__ != '__main__':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    return app


# This block is for local development only
if __name__ == '__main__':
    app = create_app()
    app.run(port=5001, debug=True)
