from flask import Flask, render_template, request
import os
import hashlib
import requests
import functions
from login.login import validate_credentials

app = Flask(__name__)
allowed = False


@app.route("/")
def loginpage():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    test = validate_credentials(username, hashlib.sha256(password.encode()).hexdigest())
    db_username = "test"
    db_password = "test2"
    if username == db_username and password == db_password:
        allowed = True
        return render_template("login.html", stautus="success"), requests.get("/main")
    else:
        allowed = False
        return render_template("login.html", status="Login Fehlgeschlagen")

@app.route("/main")
def main():
    if allowed == True:
        # get disk spaces of all the drive and render it to the template
        # get the status of the disks and render it to the template
        cpuUsage = functions.get_CPU_usage()
        available_drives = functions.get_disks()
        return render_template("index.html", drives=available_drives, CPUusage=cpuUsage)

    else:
        return render_template("login.html", status="nicht angemeldet")

@app.get("/api/v1/cpuload")
def cpuLoad():
    cpu_load = functions.get_CPU_usage()
    return render_template("cpu_status.html", load=cpu_load)


@app.route("/api/v1/shutdown", methods=["POST"])
def shutdown():
    os.system("systemctl suspend")
    return render_template("statusmsg.html", status="heruntergefahren")


@app.route("/api/v1/reboot", methods=["POST"])
def reboot():
    os.system("systemctl suspend")
    return render_template("statusmsg.html", status="in den Ruhezustand versetzt")


@app.route("/api/v1/hibernate", methods=["POST"])
def hibernate():
    os.system("systemctl suspend")
    return render_template("statusmsg.html", status="in Bereitschaft versetzt")


@app.route("/api/v1/newCommit", methods=['POST'])
def newCommit():
    os.system("cd /var/www/html")
    os.system("git pull")

    return "1"


@app.route("/api/v1/unmount", methods=["POST"])
def unmountDrive():
    drive = request.args_get("drive")

    os.system("systemctl unmount " + drive)


# TODO: exit debug mode before deploy to a server
if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
