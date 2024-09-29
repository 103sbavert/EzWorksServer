from constants import LoginCreds

class UserTypes:
    OPS = "ops"
    CLIENT = "client"


class JwtPayload:
    ISS = "EzWorks"


class SignupDetails:
    NAME = "name"
    EMAIL = "email"
    USERNAME = LoginCreds.USERNAME
    PASSWORD = "password"
    PW_HASH = LoginCreds.PW_HASH


class LoginCreds:
    USERNAME = "username"
    PW_HASH = "pwhash"


class SessionManagement:
    JWT = "jwt"
    SESSION_ID = "session_id"
