import os
import logging
from flask import Flask
# from ImgSearch.imgsearch import ImgSearch

app = Flask(__name__)
app.config.from_object('config')

if not os.path.exists(app.config['UPLOAD_DIR']):
    os.mkdir(app.config['UPLOAD_DIR'])

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from app import views
