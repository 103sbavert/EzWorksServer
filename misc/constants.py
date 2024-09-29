class UserTypes:
    OPS = "ops"
    CLIENT = "client"


class JwtPayload:
    ISS = "EzWorks"

class LoginCreds:
    USERNAME = "username"
    PASSWORD = "password"

class SignupDetails:
    NAME = "name"
    EMAIL = "email"
    USERNAME = LoginCreds.USERNAME
    PASSWORD = LoginCreds.PASSWORD
    PW_HASH = "pwhash"


class SessionManagement:
    JWT = "jwt"
    SESSION_ID = "session_id"
