import bson.binary
import time
from misc.constants import *
from pymongo import MongoClient
import bson
import os
import bcrypt


class MongodbUtil():
    def __init__(self) -> None:
        self.connection_string = os.getenv("MONGO_CONNECTION_STRING")
        self.mongodb_client = MongoClient(self.connection_string)
        self.database = self.mongodb_client.get_database("EzWorksDb")
        self.ops_collection = self.database.get_collection(UserTypes.OPS)
        self.client_collection = self.database.get_collection(UserTypes.CLIENT)

    def verify_credentials(self, user_type, username, password):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        user = collection.find_one(
            {LoginCreds.USERNAME: username}
        )

        if user is None: 
            return False
        
        pw_hash = user[SignupDetails.PW_HASH]

        if pw_hash is None:
            return False
        
        return bcrypt.checkpw(bytes(password, 'utf-8'), pw_hash)

    def _get_sessions_by_username(self, user_type, username):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return None

        user = collection.find_one(
            {LoginCreds.USERNAME: username}
        )

        if user is None or user["sessions"] is None or len(user["sessions"]) == 0:
            return None

        return user["sessions"]

    def get_sessions_by_username_and_sid(self, user_type, username, sid):
        sessions = self._get_sessions_by_username(user_type, username)

        for i in sessions:
            if i["session_id"] == sid:
                return i

        return None

    def add_session(self, user_type, username, session_id, jwt):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        result = collection.update_one(
            {LoginCreds.USERNAME: username}, {
                "$push": {
                    "sessions": {"session_id": session_id, "jwt": jwt}
                }
            }
        )

        if result.modified_count >= 1:
            return True
        return False

    def delete_session(self, user_type, username, session_id):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        result = collection.update_one(
            {LoginCreds.USERNAME: username},
            {
                "$pull": {
                    "sessions": {"session_id": session_id}
                }
            }
        )

        if result.modified_count >= 1:
            return True
        return False

    def is_username_taken(self, user_type, username):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        result = collection.find_one(
            {SignupDetails.USERNAME: username}
        )

        return result is not None

    def add_user(self, user_type, **user_info):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        name = user_info[SignupDetails.NAME]
        email = user_info[SignupDetails.EMAIL]
        username = user_info[SignupDetails.USERNAME]
        password = user_info[SignupDetails.PASSWORD]



        pw_bytes = bytes(password, 'utf-8')
        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(pw_bytes, salt)

        result = collection.insert_one(
            {
                SignupDetails.USERNAME: name,
                SignupDetails.EMAIL: email,
                SignupDetails.USERNAME: username,
                SignupDetails.PW_HASH: pw_hash
            }
        )

        if result.inserted_id is not None:
            return True

        return False

    def delete_user(self, user_type, username):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        result = collection.delete_one({LoginCreds.USERNAME: username})

        if result.modified_count >= 1:
            return True
        else:
            return False

    def upload_file(self, ops_username, filename, data):
        collection = self.ops_collection

        result = collection.update_one(
            {LoginCreds.USERNAME: ops_username},
            {
                "$push": {
                    "files": {"name": filename,  "data": bson.Binary(data)}
                }
            }
        )

        if result.modified_count >= 1:
            return True

        return False

    def get_files(self, ops_username):
        collection = self.ops_collection
        result = collection.find_one({LoginCreds.USERNAME: ops_username})
        files = result["files"]

        file_names = []

        for file in files:
            file_names += file["name"]

        return file_names

    def get_file_by_name(self, ops_username, file_name):
        collection = self.ops_collection
        result = collection.find_one({LoginCreds.USERNAME: ops_username})
        files = result["files"]

        for file in files:
            if file["name"] == file_name:
                return file
