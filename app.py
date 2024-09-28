from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from blueprints import auth, files
from utils.mongodb_util import *

load_dotenv()
ezworks_api = Flask("EZ Works API")
ezworks_api.register_blueprint(auth.auth_bp)
ezworks_api.register_blueprint(files.files_bp)