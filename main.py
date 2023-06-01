from flask import Flask, render_template, request, redirect, url_for
import os
import hashlib
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from functions import (sort_remaining_images,
                       update_system_status,
                       update_machine,
                       check_for_unconverted_folders
                       )

import multitasking
from ftp import init_ftp_server


from logger import logger, cleanup_old_logs
from config_helper import load_conf
import logging

log = logger(logging.DEBUG,"api")

@multitasking.task
def start_flask():
    app = Flask(__name__)
    @app.get("/ping")
    def pingpong():
        return "pong"

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

if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(sort_remaining_images, "cron", day_of_week= 'mon-sun', hour = 2)
    scheduler.add_job(check_for_unconverted_folders,'interval', minutes = 5)
    scheduler.add_job(cleanup_old_logs, "cron", day_of_week= 'mon-sun', hour = 0)
    #scheduler.add_job(sort_new_images, 'interval', seconds=10)
    scheduler.add_job(update_machine, 'interval', days=118)
    scheduler.add_job(update_system_status, 'interval', seconds=1.75)
    scheduler.start()
    start_flask()
    init_ftp_server()
