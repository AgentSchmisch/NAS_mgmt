from flask import Flask, render_template, request, redirect, url_for
import os
import hashlib
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from functions import *
import multitasking
from ftp import init_ftp_server


from logger import logger, cleanup_old_logs
from config_helper import load_conf

# TODO: error handling with log files that get written into a folder that is presented in a nextcloud share



#log = logger(logging.DEBUG,"api")

@multitasking.task
def start_flask():
    app = Flask(__name__)
    @app.get("/ping")
    def pingpong():
        return "pong"

    # DEPRECATED FUNCTION
    def post_cpu_load():
        cpu_load = functions.get_CPU_usage()

        json = {"test": cpu_load}
        
        re = requests.post("http://localhost:1880/api/cpuload", json)
        return re.text

    # DEPRECATED FUNCTION
    def post_drive_space():
        drive_space = functions.get_disk_space()

        json = {"test": drive_space}
        
        re = requests.post("http://localhost:1880/api/drivespace", json)
        return re.text

    # function to shutdown the machine
    @app.route("/api/v1/shutdown", methods=["POST"])
    def shutdown():
        log.info("system shutdown")
        os.system("systemctl shutdown")
        return render_template("statusmsg.html", status="heruntergefahren")

    # function to reboot the machine
    @app.route("/api/v1/reboot", methods=["POST"])
    def reboot():
        log.info("system rebooting")
        os.system("systemctl reboot")
        return render_template("statusmsg.html", status="in den Ruhezustand versetzt")

    # function to send the machine to hibernation
    @app.route("/api/v1/hibernate", methods=["POST"])
    def hibernate():
        log.info("system suspending")
        os.system("systemctl suspend")
        return render_template("statusmsg.html", status="in Bereitschaft versetzt")

    # function to automatically pull the latest changes of the release/production branch from a given Repository
    @app.route("/api/v1/newCommit", methods=['POST'])
    def newCommit():
        try:
            os.system("cd /var/www/Website")
            os.system("git pull")
            log.info("Website successfully deployed")
            return "success"
        except Exception as ex:
            log.error("Failed to deploy Website " +ex)
            return "error"

    app.run(host="0.0.0.0")


# TODO: exit debug mode before deploy to a server
if __name__ == "__main__":

    scheduler = BackgroundScheduler()
    scheduler.add_job(functions.sort_remaining_images, "cron", day_of_week= 'mon-sun', hour = 2)
    scheduler.add_job(cleanup_old_logs, "cron", day_of_week= 'mon-sun', hour = 0)
    scheduler.add_job(functions.sort_new_images, 'interval', seconds=10)
    scheduler.add_job(update_machine, 'interval', days=118)
    scheduler.add_job(update_system_status, 'interval', seconds=1.75)
    scheduler.start()
    start_flask()
    init_ftp_server()
