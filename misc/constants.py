class UserTypes:
    OPS = "ops"
    CLIENT = "client"


class JwtPayload:
    ISS = "EzWorks"

class LoginCreds:
    USERNAME = "username"
    PW_HASH = "pwhash"

class SignupDetails:
    NAME = "name"
    EMAIL = "email"
    USERNAME = LoginCreds.USERNAME
    PASSWORD = "password"
    PW_HASH = LoginCreds.PW_HASH


class SessionManagement:
    JWT = "jwt"
    SESSION_ID = "session_id"
