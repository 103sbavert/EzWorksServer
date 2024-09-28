import os
from flask import request, Response
from mongodb_util import MongodbUtil
from datetime import datetime, timedelta
from time import time
import jwt
from constants import *
from flask import Blueprint

connection_string = os.getenv("MONGO_CONNECTION_STRING")
mongodb_util = MongodbUtil(connection_string)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/<user_type>/login", methods=["POST"])
def login(user_type):
    username = request.form[LoginCreds.USERNAME]
    password = request.form[LoginCreds.PASSWORD]

    result = mongodb_util.verifyCredentialsWithDb(
        user_type, username, password)

    if result:
        session_id = int(time())
        token = generate_token(user_type, username, session_id)
        if mongodb_util.addSession(user_type, username, session_id, token):
            return Response(token, 200)
        else:
            return Response(status=500)

    return Response(status=404)


@auth_bp.route("/<user_type>/signup", methods=["POST"])
def signup(user_type):
    username = request.form[LoginCreds.USERNAME]
    password = request.form[LoginCreds.PASSWORD]

    if mongodb_util.addUser(user_type, username, password):
        return Response(status=201)

    return Response(status=500)


@auth_bp.route("/<user_type>/logout", methods=["POST"])
def logout(user_type):
    username = request.form["username"]
    session_id = request.form["session_id"]
    if session_id == None or username == None:
        return "Invalid session id or username", 405

    if mongodb_util.deleteSession(user_type, username, session_id):
        return Response(status=200)

    return Response(status=500)


def generate_token(user_type, username, session_id):
    secret = os.getenv("JWT_SECRET")
    algo = os.getenv("JWT_ALGO")
    print("the algo name is", algo)

    payload = {
        "iss": JwtPayload.ISS,
        "sub": username,
        "aud": user_type,
        "sid": session_id,
        "exp": datetime.now() + timedelta(days=365)
    }

    token = jwt.encode(payload, secret, algo)

    return token
