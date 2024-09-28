from flask import Blueprint, request, Response, send_file
import os
from blueprints.common import verifySession
from utils.mongodb_util import MongodbUtil
from misc.constants import *

mongo_client = MongodbUtil()
files_bp = Blueprint("files", __name__)

@files_bp.route(f"/{UserTypes.OPS}/upload", methods=['POST'])
def upload_file():
    bearer = request.headers["Authorization"]
    token = bearer.split()[-1]
    payload = verifySession(token, UserTypes.OPS)

    if payload is None:
        return Response("Invalid JWT", status=403)

    file = request.files["request_file"]

    if file is None:
        return Response("A file is required", 400)

    dir_path = f"/tmp/{payload["sub"]}/"
    file_path = f"{dir_path}{file.filename}"

    if os.path.exists(file_path):
        os.remove(file_path)

    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    file.save(file_path)
    file_reader = open(file_path, "rb")
    binary = file_reader.read()
    mongo_client.upload_file(payload["sub"], file.filename, binary)
    file_reader.close()

    return Response("File uploaded", status=201)


@files_bp.route(f"/{UserTypes.CLIENT}/files/<ops_username>", methods=["GET"])
def get_file_names(ops_username):
    bearer = request.headers["Authorization"]
    token = bearer.split()[-1]
    payload = verifySession(token, UserTypes.CLIENT)

    if payload is None:
        return Response("Invalid JWT", status=403)

    file_names = mongo_client.get_files(ops_username)

    return Response(file_names, status=200)


@files_bp.route(f"/{UserTypes.CLIENT}/files/<ops_username>/<file_name>", methods=["GET"])
def download_file(ops_username, file_name):
    bearer = request.headers["Authorization"]
    token = bearer.split()[-1]
    payload = verifySession(token, UserTypes.CLIENT)

    if payload is None:
        return Response("Invalid JWT", status=403)
    
    mongo_file = mongo_client.get_file_by_name(ops_username, file_name)
    
    if mongo_file is None:
        return Response("No such file uploaded", status=404)
    
    download_path = f"/tmp/{file_name}"
    with open(download_path, "wb") as downloaded_file:
        downloaded_file.write(mongo_file["data"])

    return send_file(download_path, as_attachment=True)

    
