import hashlib
import mysql.connector
import json


with open("config.json", "r") as jsonfile:
    data = json.load(jsonfile)

db=mysql.connector.connect(
    host=data['host'],
    username=data["username"],
    password=data["password"]
)
exec=db.cursor()

def validate_credentials(usrname):

    db_password=exec.execute("select password from t_users where username in "+usrname)

    if db_password == "":
        return "Benutzer nicht gefunden"

    return db_password,usrname

def create_user(username,password):
    status="error"

    #TODO: push new user to DB



    return status