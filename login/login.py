import hashlib
import json
import mariadb

from config_helper import load_conf
from login.db import init_db_objs
from login.db import _select, _from, _where as query


def validate_credentials(username, password):
    is_admin = 0
    allowed = False
    admin = False
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
        cursor.execute("Select username, password, admin from users where username in ('" + username + "');")
        db_result = cursor.fetchall()
        print(db_result)
        db_username, db_password, is_admin = db_result[0]
        if is_admin == 1:
            admin = True
        else:
            admin = False
        if db_password == "":
            print("login failed")
            return False, admin
        elif db_password == password:
            print("login successful")
            allowed = True
            return allowed, admin
    except Exception as ex:
        print(ex)
        return False, admin


def create_user(username, password):
    status = "error"

    # TODO: push new user to DB

    return status
