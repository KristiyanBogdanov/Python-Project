import os
import json


class UsernameAlreadyUsed(Exception):
    pass


class InvalidUsername(Exception):
    pass


class InvalidPassword(Exception):
    pass


class JsonDb:
    def __init__(self):
        self.db_file = "db.json"
        self.current_user = None
        self.check_db()

    def check_db(self):
        if not os.path.exists(self.db_file):
            self.write_json({
                "Users": []
            })

    def write_json(self, data):
        with open(self.db_file, "w") as f:
            json.dump(data, f, indent=4)

    def check_user(self, username, password):
        with open(self.db_file, "r") as f:
            data = json.load(f)

            for user in data["Users"]:
                if user["Username"] == username and \
                        user["Password"] == password:
                    self.current_user = username
                    return True
            return False

    def register_user(self, username, password):
        with open(self.db_file, "r") as f:
            data = json.load(f)

            if not 2 <= len(username) <= 20:
                raise InvalidUsername

            for user in data["Users"]:
                if user["Username"] == username:
                    raise UsernameAlreadyUsed

            if not 4 <= len(password) <= 16:
                raise InvalidPassword

            temp = data["Users"]
            temp.append({
                "Username": username,
                "Password": password,
                "Board": {
                    "Events": [
                        {
                            "Title": "Downloaded TC4S",
                            "Description": None,
                            "Deadline": "Today",
                            "Attached": False
                        }
                    ],
                    "ToDo": [
                        {
                            "Title": "Test application :)",
                            "Description": None,
                            "Deadline": "As soon as possible",
                            "Attached": False
                        }
                    ],
                    "Done": [
                        {
                            "Title": "Make TC4S account",
                            "Description": None,
                            "Deadline": "Just right now",
                            "Attached": False
                        }
                    ]
                }
            })
            self.write_json(data)
            self.current_user = username

    def add_frame(self, section, info):
        with open(self.db_file, "r") as f:
            data = json.load(f)

            for user in data["Users"]:
                if user["Username"] == self.current_user:
                    temp = user["Board"][section]

        temp.append(info)
        self.write_json(data)

    def delete_frame(self, section, title):
        with open(self.db_file, "r") as f:
            data = json.load(f)

            for user in data["Users"]:
                if user["Username"] == self.current_user:
                    for frame in user["Board"][section]:
                        if frame["Title"] == title:
                            user["Board"][section].remove(frame)

        self.write_json(data)

    def get_user_board(self):
        with open(self.db_file, "r") as f:
            data = json.load(f)

            for user in data["Users"]:
                if user["Username"] == self.current_user:
                    return user["Board"]
