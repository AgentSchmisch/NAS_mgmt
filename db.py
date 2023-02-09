import json
import mysql

def init_db_objs(config_obj):
    data=config_obj["mysql"]
    db = mysql.connector.connect(
        host=data['host'],
        username=data["username"],
        password=data["password"]
    )
    exec = db.cursor()
    return exec

def load_conf():
    with open("config.json", "r") as jsonfile:
        data = json.load(jsonfile)
    return data


def _select(object):
    return "SELECT "+str(object)

def _from (database):
    return "FROM "+str(database)

def _where (condition):
    return "WHERE"+str(condition)