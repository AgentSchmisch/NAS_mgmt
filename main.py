from flask import Flask, render_template, request, redirect,url_for
import os
import hashlib
import requests
import functions
import mariadb
from login.login import validate_credentials

app = Flask(__name__)
allowed = False


@app.route("/")
def loginpage():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    global allowed
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        is_in_db = validate_credentials(username, hashlib.sha256(password.encode()).hexdigest())
        if is_in_db:
            allowed = True
            return redirect(url_for("main"))
        else:
            allowed = False
            return render_template("login.html", status="Login fehlgeschlagen")
    except mariadb.Error as e:
        return render_template("login.html", status="Login fehlgeschlagen")


@app.route("/main")
def main():
    if allowed == True:
        # get disk spaces of all the drive and render it to the template
        # get the status of the disks and render it to the template
        available_drives = functions.get_disks()
        return render_template("index.html", drives=available_drives)

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
