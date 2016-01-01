import os


WTF_CSRF_ENABLED = True
SECRET_KEY = 'pml-is-the-greatest'

# APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(os.path.abspath(os.path.join('.', 'app')))

UPLOAD_DIR = os.path.join(APP_ROOT, 'uploads')
