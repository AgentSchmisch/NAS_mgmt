import hashlib
import mysql.connector
import json
from db import init_db_objs,load_conf as init
from db import _select,_from,_where as query
exec=init.init_db_objs(init.load_conf())

def validate_credentials(usrname):

    db_password=exec.execute(query._select("password") + query._from("t_users") + query._where("username in") + usrname)

    if db_password == "":
        return "Benutzer nicht gefunden"

    return db_password,usrname

def create_user(username,password):
    status="error"

    #TODO: push new user to DB



    return status