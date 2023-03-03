import hashlib
import json
import mysql.connector

from config_helper import load_conf
from login.db import init_db_objs
from login.db import _select, _from, _where as query


def validate_credentials(usrname, password):
    config_obj=load_conf()
    data = config_obj["mysql"]
    db = mysql.connector.connect(
        host="localhost", #data['host'],
        user="florian",#data["username"],
        password="admin",#data["password"],
       # database=data["database"],
    )
    cursor = db.cursor()
    db_password = cursor.execute("SHOW DATABASES")
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
