from flask import Flask, render_template, request
import os,string
import requests
import functions
import login
import hashlib
app=Flask(__name__)

@app.route("/")
def login():
    #TODO: Client Side Hashing
    username=request.form.get("username")
    password=request.form.get("password")

    db_username,db_password=login.validate_credentials(username)

    if username==db_username and password==db_password:
        return render_template("login.html",stautus="success"),requests.get("/main")
    else:
        return render_template("login.html",status="Login Fehlgeschlagen")


@app.route("/main")
def main():
    # get disk spaces of all the drive and render it to the template
    # get the status of the disks and render it to the template
    cpuUsage=functions.get_CPU_usage()
    available_drives=functions.get_disks()
    return render_template("index.html", drives=available_drives,CPUusage=cpuUsage)

@app.route("/api/v1/shutdown", methods=["POST"])
def shutdown():
    os.system("systemctl suspend")
    return render_template("statusmsg.html", status="heruntergefahren")
@app.route("/api/v1/reboot", methods=["POST"])
def reboot():
    os.system("systemctl suspend")
    return render_template("statusmsg.html",status="in den Ruhezustand versetzt")

@app.route("/api/v1/hibernate", methods=["POST"])
def hibernate():
    os.system("systemctl suspend")
    return render_template("statusmsg.html",status="in Bereitschaft versetzt")

@app.route("/api/v1/newCommit", methods=['POST'])
def newCommit():
    os.system("cd /var/www/html")
    os.system("git pull")

    return "1"

@app.route("/api/v1/unmount",methods=["POST"])
def unmountDrive():
    drive=request.args_get("drive")

    os.system("systemctl unmount "+drive)



#TODO: exit debug mode before deploy to a server
if __name__ == "__main__":
    app.run("0.0.0.0",debug=True)

