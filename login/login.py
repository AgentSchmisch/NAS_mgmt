import hashlib
import json
import mariadb

from config_helper import load_conf
from login.db import init_db_objs
from login.db import _select, _from, _where as query


def validate_credentials(username, password):
    try:
        config_obj = load_conf()
        data = config_obj["mysql"]
        db = mariadb.connect(
            host=data['host'],
            user=data["username"],
            password=data["password"],
            database=data["database"],
        )
        cursor = db.cursor()
        cursor.execute("Select username,password from users where username in ('" + username + "');")
        db_result = cursor.fetchall()
        db_username, db_password = db_result[0]
        print(db_username, db_password)
        if db_password == "":
            print("login failed")
            return False
        elif db_password == password:
            print("login successful")
            return True
    except Exception as ex:
        return False


def create_user(username, password):
    status = "error"

    # TODO: push new user to DB

    return status
