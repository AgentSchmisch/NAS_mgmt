import hashlib
import json
import mariadb

from config_helper import load_conf
from login.db import init_db_objs
from login.db import _select, _from, _where as query


def validate_credentials(usrname, password):
    config_obj = load_conf()
    data = config_obj["mysql"]
    db = mariadb.connect(
        host=data['host'],
        user=data["username"],
        password=data["password"],
        database=data["database"],
    )
    cursor = db.cursor()
    db_password = cursor.execute("select * from users").fetchall()
    print(db_password)
    #db_password = exec.execute("select password from users where username = "+usrname+";")

    if db_password == "":
        return False
    elif db_password == password:
        return True



def create_user(username, password):
    status = "error"

    # TODO: push new user to DB

    return status
