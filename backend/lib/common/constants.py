import os
EVENT_FILE = 'event.json'
CROPPED_FACES_FOLDER = 'cropped_faces'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
DATABASE = 'event/app.db'

SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'default_admin_password')