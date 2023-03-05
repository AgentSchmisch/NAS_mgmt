import json
import mariadb


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


def _select(object):
    return "SELECT " + str(object)


def _from(database):
    return "FROM " + str(database)


def _where(condition):
    return "WHERE" + str(condition)
