import os
from flask import request, Response
from utils.mongodb_util import MongodbUtil
import time
import datetime
import jwt
from misc.constants import *
from flask import Blueprint

_mongodb_util = MongodbUtil()
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/<user_type>/login", methods=["POST"])
def login(user_type):
    username = request.form[LoginCreds.USERNAME]
    password = request.form[LoginCreds.PASSWORD]

    result = _mongodb_util.verify_credentials(
        user_type, username, password)

    if result:
        session_id = int(time.time())
        token = _generate_token(user_type, username, session_id)
        if _mongodb_util.add_session(user_type, username, session_id, token):
            return Response(token, 200)
        else:
            return Response(status=500)

    return Response(status=404)


@auth_bp.route("/<user_type>/signup", methods=["POST"])
def signup(user_type):
    username = request.form[LoginCreds.USERNAME]
    password = request.form[LoginCreds.PASSWORD]

    if _mongodb_util.is_username_taken(user_type, username):
        return Response("Username taken", 409)

    if _mongodb_util.add_user(user_type, username, password):
        return Response(status=201)

    return Response(status=500)


@auth_bp.route("/<user_type>/logout", methods=["POST"])
def logout(user_type):
    username = request.form["username"]
    session_id = request.form["session_id"]
    if session_id == None or username == None:
        return "Invalid session id or username", 405

    if _mongodb_util.delete_session(user_type, username, session_id):
        return Response(status=200)

    return Response(status=500)


def _generate_token(user_type, username, session_id):
    secret = os.getenv("JWT_SECRET")
    algo = os.getenv("JWT_ALGO")
    print("the algo name is", algo)

    payload = {
        "iss": JwtPayload.ISS,
        "sub": username,
        "aud": user_type,
        "sid": session_id,
        "exp": int(time.time()) + int(datetime.timedelta(days=365).total_seconds())
    }

    token = jwt.encode(payload, secret, algo)

    return token
