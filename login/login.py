import hashlib
import mysql.connector
import json
from config_helper import load_conf
from db import init_db_objs
from db import _select, _from, _where as query

exec = init_db_objs(load_conf())


def validate_credentials(usrname):
    db_password = exec.execute(
        query._select("password") + query._from("t_users") + query._where("username in") + usrname)

    if db_password == "":
        return "Benutzer nicht gefunden"

    return db_password, usrname


def create_user(username, password):
    status = "error"

    # TODO: push new user to DB

    return status
