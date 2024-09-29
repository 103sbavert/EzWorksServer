from flask import request, Response
from blueprints.common import generate_token, verifySession
from utils.mongodb_util import MongodbUtil
import time
from misc.constants import *
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)
mongo_client = MongodbUtil()


@auth_bp.route("/<user_type>/login", methods=["POST"])
def login(user_type):
    username = request.form[LoginCreds.USERNAME]
    password = request.form[LoginCreds.PW_HASH]

    result = mongo_client.verify_credentials(
        user_type, username, password)

    if result:
        session_id = int(time.time())
        token = generate_token(user_type, username, session_id)
        if mongo_client.add_session(user_type, username, session_id, token):
            return Response(token, 200)
        else:
            return Response(status=500)

    return Response(status=404)


@auth_bp.route("/<user_type>/signup", methods=["POST"])
def signup(user_type):
    name = request.form[SignupDetails.NAME]
    email = request.form[SignupDetails.EMAIL]
    username = request.form[SignupDetails.USERNAME]
    password = request.form[SignupDetails.PASSWORD]

    if mongo_client.is_username_taken(user_type, username):
        return Response("Username taken", 409)

    if mongo_client.add_user(user_type, username, password):
        return Response(status=201)

    return Response(status=500)


@auth_bp.route("/logout", methods=["GET"])
def logout():
    bearer = request.headers["Authorization"]
    token = bearer.split()[-1]
    payload = verifySession(token)
    username = payload["sub"]
    session_id = payload["sid"]
    user_type = payload["aud"]

    if mongo_client.delete_session(user_type, username, session_id):
        return Response(status=200)

    return Response(status=500)


