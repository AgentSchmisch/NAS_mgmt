from threading import Thread

from flask import Flask, render_template, request, redirect, url_for
import os
import hashlib
import requests
import functions
import mariadb
from apscheduler.schedulers.background import BackgroundScheduler
from login.login import validate_credentials

app = Flask(__name__)
allowed = False
is_admin = 0

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
    # chekc whether user is in db and allowed to enter the page
    if allowed == True:
        return render_template("index.html")

    else:
        return render_template("login.html", status="nicht angemeldet")


@app.get("/api/v1/cpuload")
def cpu_load():
    Cpu_load = functions.get_CPU_usage()
    return render_template("cpu_status.html", load=Cpu_load)


@app.get("/api/v1/diskspace")
def disk_space():
    Disk_space = functions.get_disks()
    return render_template("disk_space.html", space=Disk_space)


@app.route("/api/v1/shutdown", methods=["POST"])
def shutdown():
    os.system("systemctl shutdown")
    return render_template("statusmsg.html", status="heruntergefahren")


@app.route("/api/v1/reboot", methods=["POST"])
def reboot():
    os.system("systemctl reboot")
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


# TODO: exit debug mode before deploy to a server
if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(functions.sort_new_images, 'interval', seconds=20)
    scheduler.start()
    app.run("0.0.0.0", debug=True)
