from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
from login_util import auth_bp
from mongodb_util import *

load_dotenv()
ezworks_api = Flask("EZ Works API")
ezworks_api.register_blueprint(auth_bp)