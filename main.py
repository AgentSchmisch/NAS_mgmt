from threading import Thread

from flask import Flask, render_template, request, redirect, url_for
import os
import hashlib
import requests
import functions
import mariadb

from login.db import get_all_users
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
    global is_admin
    global allowed
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        is_in_db, is_admin = validate_credentials(username, hashlib.sha256(password.encode()).hexdigest())
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
    # check whether user is in db and allowed to enter the page
    if allowed == True:
        return render_template("index.html", is_admin=is_admin)

    else:
        return render_template("login.html", status="nicht angemeldet")

@app.route("/api/v1/admin")
def admin():

    users = get_all_users()

    return render_template("admin.html", users=users)

@app.get("/api/v1/cpuload")
def cpu_load():

    Cpu_load = functions.get_CPU_usage()

    #req = requests.post("localhost:1880/api/test",Cpu_load)

    return render_template("cpu_status.html", load=Cpu_load)

def post_cpu_load():
    cpu_load = functions.get_CPU_usage()

    json = {"test": cpu_load}
    #print(json)

    re = requests.post("http://localhost:1880/api/cpuload", json)
    return re.text

@app.get("/api/v1/diskspace")
def disk_space():
    Disk_space = functions.get_disk_space()
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


@app.get("/services/pihole")
def route_to_pihole():
        return redirect("http://10.0.0.20/admin/")

# TODO: exit debug mode before deploy to a server
if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(functions.sort_new_images, 'interval', seconds=10)
    scheduler.add_job(functions.update_machine, 'interval', days=118)
    scheduler.add_job(post_cpu_load, 'interval', seconds=1.75)
    scheduler.start()
    app.run("0.0.0.0", debug=True)
