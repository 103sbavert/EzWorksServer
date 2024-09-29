import time
import os
import jwt
from misc.constants import JwtPayload, UserTypes
from utils.mongodb_util import MongodbUtil
import datetime

mongo_client = MongodbUtil()
secret = os.getenv("JWT_SECRET")
algo = os.getenv("JWT_ALGO")


def verifySession(token, expected_aud=[UserTypes.CLIENT, UserTypes.OPS]):
    payload = None

    try:
        payload = jwt.decode(
            token, secret, algorithms=algo, audience=expected_aud
        )
    except jwt.InvalidAudienceError as e:
        return None

    username = payload["sub"]
    aud = payload["aud"]
    session_id = payload["sid"]
    expiry = payload["exp"]
    session = mongo_client.get_sessions_by_username_and_sid(
        aud, username, session_id)

    if session is None or expiry < time.time():
        return None
    return {"sub": username, "aud": aud, "sid": session_id, "exp": expiry}


def generate_token(user_type, username, session_id):
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
