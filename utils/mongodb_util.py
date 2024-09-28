import bson.binary
import time
from misc.constants import *
from pymongo import MongoClient
import bson
import os


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
            {"username": username}
        )

        if user is None:
            return False
        elif user["password"] == password:
            return True
        else:
            return False

    def _get_sessions_by_username(self, user_type, username):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        user = collection.find_one(
            {"username": username}
        )

        if user is None:
            return None
        elif user["sessions"] is not None:
            return user["sessions"]
        else:
            return None

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
            {"username": username}, {
                "$push": {
                    "sessions": {"session_id": session_id, "jwt": jwt}
                }
            }
        )

        if result.modified_count >= 1:
            return True
        else:
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
            {"username": username},
            {
                "$pull": {
                    "sessions": {"session_id": session_id}
                }
            }
        )

        if result.modified_count >= 1:
            return True
        else:
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
            {"username": username}
        )

        return result is not None

    def add_user(self, user_type, username, password):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        result = collection.insert_one(
            {
                "username": username, "password": password
            }
        )

        if result.inserted_id is not None:
            print(result.inserted_id)
            return True

        return False

    def remove_user(self, user_type, username):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False

        result = collection.delete_one({"username": username})

        if result.modified_count >= 1:
            return True
        else:
            return False

    def upload_file(self, ops_username, filename, data):
        collection = self.ops_collection

        result = collection.update_one(
            {"username": ops_username},
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
        result = collection.find_one({"username": ops_username})
        files = result["files"]

        file_names = []

        for file in files:
            file_names += file["name"]

        return file_names

    def get_file_by_name(self, ops_username, file_name):
        collection = self.ops_collection
        result = collection.find_one({"username": ops_username})
        files = result["files"]

        for file in files:
            if file["name"] == file_name:
                return file
                # file_name = f"/tmp/{file_name}.pdf"
                # with open(file_name, "wb") as downloaded_file:
                #     downloaded_file.write(file["data"])
