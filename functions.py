import os
import shutil
import subprocess
import json
from typing import List
from PIL import Image, ExifTags
import time
import requests

from config_helper import load_conf

import psutil
import re
from threading import Lock
import logging
from logger import logger

lock = Lock()
# TODO: complete logging in this script
# TODO: check wheter there is a transaction to the ftp folder going on not to interrupt any transfer and get a loss of data
# TODO: skip failing images in the folder

log = logger(logging.DEBUG, "functions")

allowed_image_types = ["jpg", "jpeg", "cr3", "cr2", "dng"]

def get_disk_space():

    drives = ["/","/mnt/array"]
    space = []

    for drive in drives:
        total,used,free = shutil.disk_usage(drive)    
        space.append(used//(2**30))  
    return space

# get cpu usage and frequency per core
def get_CPU_usage():
    usage = psutil.cpu_percent(interval=1, percpu=True)
    freq1 = psutil.cpu_freq(percpu=True)
    freq = []
    y = 0
    for _ in freq1:
        freq.append(freq1[y][0])
    y += 1
    return usage  # , freq


def get_capture_date(path, image):

    expr = r'\d+'
    print(image)
    cmd = "python3 get_capture_dates.py -p " + path + " -i " + image
    raw_cmd_out = os.popen(cmd).read()
    time.sleep(3)
    print("raw" + raw_cmd_out)
    dates = re.findall(expr, raw_cmd_out)
    print(dates)
    date = dates[0] + "_" + dates[1] + "_" + dates[2]
    return date


def convert_to_dng(path, folder):
    config_obj = load_conf()
    source = path + "/" + folder
    files = os.listdir(source)
    # check if the file has already been converted
    for file in files:
        if file.replace("CR3", "dng") in files:
            continue
        # ...if not convert it
        else:
            proc = subprocess.Popen(["dnglab convert", source + "/" + file, source + "/" + file.replace("CR3", "dng")])
            while proc.poll() is None:
                time.sleep(2)

def get_file_extension(file):
    temp = file.split(".")
    extension = temp[len(temp) - 1]
    file_name = temp[0]
    return file_name, extension.lower()

def get_capture_date_jpg(path,image):
    img = Image.open(path+"/"+image)

    raw_date = img.getexif()[306]
    # output: YYYY:MM:DD HH:MM:SS
    # ...split string before space...
    raw_date_array = raw_date.split(" ")
    # ...and replace : with _
    capture_date = raw_date_array[0].replace(":", "_")
    return capture_date

def sort_remaining_images():
    #this function will be executed by a BackgroundScheduler every day at 2am to clean up all the images that might have gotten overlooked by the execution after the transfer
    config_obj = load_conf()
    pathx = config_obj["folders"]
    path = pathx["ftp_path"]
    try:
      files = os.listdir(path)
    except Exception as ex:
       with open(path + "log.txt", "w+") as file:
            file.write(str(ex))
            file.close()
    # TODO: in this function also check the folders if there are the same number of dngs as cr3s 

def sort_new_images(file): # TODO alter the function to recieve a path and a image name to only execute when a file got recieved and was being transferred properly
    #TODO: might be good to seperate the function into a part that is being executed with a backgroundScheduler every day at X o'clock and the second part that will be executed by the periodic function as well as the ftp server
    with lock:
        try:      
            images_to_convert = []
            folders = []
            images = []

            filename, extension = get_file_extension(file)
            if extension in allowed_image_types:  # append all images to the images list
                images.append(file)
                if extension == "cr3":  # if the image is cr3 append it to the to do list for the converter
                    images_to_convert.append(file)

            for image in images:
                filename, extension = get_file_extension(image)
                # only send .dng files to the function, cr3 images will be moved due to their names
                if extension == "cr3":
                    date = get_capture_date(path, image)
                elif extension == "jpg":
                    date = get_capture_date_jpg(path, image)
                else:
                    continue

                # if a folder with the image date exists, move the file to the folder
                # if the folder doesn't exist...create it
                if os.path.exists(path + "/" + date):
                    folders.append(date)
                    shutil.move(path + "/" + image, path + "/" + date + "/" + image)
                else:
                    os.mkdir(path + "/" + date)
                    folders.append(date)
                    shutil.move(path + "/" + image, path + "/" + date + "/" + image)

            for folder in folders:
                # convert the whole folder from cr3 to dng
                convert_to_dng(path, folder)
        except Exception as ex:
            with open(path + "log.txt", "w+") as file:
                file.write(str(ex))
                file.close()


def update_machine():
    proc = subprocess.Popen("apt update")
    while proc.poll() is None:
        time.sleep(2)

    proc = subprocess.Popen("apt upgrade")
    while proc.poll() is None:
        time.sleep(2)


def update_system_status(): # function to send the system status consisting of cpu load and storage use to the node red api
    storage = get_disk_space()
    cpu_load = get_CPU_usage()

    status = {
        "cpu": cpu_load,
        "storage": storage
    }
    config_obj = load_conf()
    nodered = config_obj["addresses"]["nodered"]

    post_system_status = requests.post("http://" + nodered + "/api/cpuload", status)
    return post_system_status.text
