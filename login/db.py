import json
import mariadb
from config_helper import load_conf

def init_db_objs(config_obj):
    data = config_obj["mysql"]
    db = mariadb.connect(
        host=data['host'],
        user=data["username"],
        password=data["password"],
        database=data["database"],
    )
    exec = db.cursor()
    return exec

def get_all_users():

    config_obj = load_conf()
    data = config_obj["mysql"]
    db = mariadb.connect(
        host=data['host'],
        user=data["username"],
        password=data["password"],
        database=data["database"],
    )
    cursor = db.cursor()
    cursor.execute("Select username, password, admin from users;")
    users = cursor.fetchall()
    return users

def _select(object):
    return "SELECT " + str(object)


def _from(database):
    return "FROM " + str(database)


def _where(condition):
    return "WHERE" + str(condition)
