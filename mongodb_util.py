from constants import *
from pymongo import MongoClient
import os


class MongodbUtil():
    def __init__(self, connection_string) -> None:
        self.mongodb_client = MongoClient(connection_string)
        self.database = self.mongodb_client.get_database("EzWorksDb")
        self.ops_collection = self.database.get_collection(UserTypes.OPS)
        self.client_collection = self.database.get_collection(UserTypes.CLIENT)

    def verifyCredentialsWithDb(self, user_type, username, password):
        collection = None
        if user_type == UserTypes.CLIENT:
            collection = self.client_collection
        elif user_type == UserTypes.OPS:
            collection = self.ops_collection
        else:
            return False
        
        print("TAG", collection.database)

        user = collection.find_one(
            {"username": username}
        )

        if user is None:
            return False
        elif user["password"] == password:
            return True
        else:
            return False

    def addSession(self, user_type, username, session_id, jwt):
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

    def deleteSession(self, user_type, username, session_id):
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

    def addUser(self, user_type, username, password):
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

    def removeUser(self, user_type, username):
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
