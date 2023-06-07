from flask import Flask, render_template, request, redirect, url_for
import os
import hashlib
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from functions import (sort_orphaned_images,
                       update_system_status,
                       update_machine,
                       check_for_unconverted_folders,
                       allowed_image_types,
                       get_file_extension
                       )

import multitasking
from ftp import init_ftp_server
from GPSPhoto import gpsphoto

from logger import logger, cleanup_old_logs
from config_helper import load_conf
import logging

#TODO: create webpage that will appear once images have been exported in lightroom so we can set the location of the images
#TODO: in the ui there should be a list of not set folders, therefore after setting their location the folder should get a file as a checkmark kinda....(.set_loc) or smth like that
#       there also sould be a small map on which the coordinates can be set on the map to insert them into the images exif data, refer to the script alter_gps_data.py

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

    @app.route("/", methods=["GET"])
    def main():
        conf_obj = load_conf()
        export_path = conf_obj["folders"]["export_path"]

        folders_to_set_gps_data =[]
        folders = os.listdir(export_path)

        for folder in folders:
            if not os.path.exists(folder+".set_loc"):
                folders_to_set_gps_data.append(folder)
        print(folders)
        return render_template("map.html", folders_to_set_gps_data=folders_to_set_gps_data)
    @app.post("/coordinates")
    def coordinates():
        conf_obj = load_conf()
        export_path = conf_obj["folders"]["export_path"]

        resp = request.json

        folder = resp["folder"]
        coordinates = resp["coordinates"]
        
        print(folder)
        print(coordinates)

        files = os.listdir(export_path + "/" + folder)
        images = []
        for file in files:
            
            name,extension = get_file_extension(file)

            if extension in allowed_image_types:
                images.append(file)

        for image in images:
            photo = gpsphoto.GPSPhoto(export_path + "/" + folder + "/" + image)

            res = eval(coordinates)

            info = gpsphoto.GPSInfo(res) #48.440868, 16.692573

            photo.modGPSData(info, export_path + "/" + folder + "/" + image)

        #insert logic for creating the checkfiles and writing the metadata to the images
        # might be possible to scatter the images around the coordinate set

        open(export_path+"/"+folder+"/"+".set_loc", 'a').close()

        return "", 200


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
    scheduler.add_job(sort_orphaned_images, "cron", day_of_week= 'mon-sun', hour = 2)
    scheduler.add_job(check_for_unconverted_folders,'interval', minutes = 60)
    scheduler.add_job(cleanup_old_logs, "cron", day_of_week= 'mon-sun', hour = 0)
    #scheduler.add_job(sort_new_images, 'interval', seconds=10)
    scheduler.add_job(update_machine, 'interval', days=118)
    scheduler.add_job(update_system_status, 'interval', seconds=1.75)
    scheduler.start()
    start_flask()
    init_ftp_server()
