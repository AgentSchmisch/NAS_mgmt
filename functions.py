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


def get_disk_space():
    regex = r"/dev/sd"
    all_disk = psutil.disk_partitions()
    physical_disks = []
    physical_disk_space = []
    y = 0
    for x in all_disk:
        temp = all_disk[y][0]
        match = re.match(regex, temp)

        if (match is not None):
            physical_disks.append(all_disk[y][1])  # returns disk mounting point of all disks
        else:
            continue
        y += 1

    for disk in physical_disks:
        physical_disk_space.append(shutil.disk_usage(disk))
    return physical_disk_space


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

    cmd = "python3 get_capture_dates.py -p " + path + " -i " + image
    raw_cmd_out = os.popen(cmd).read()

    dates = re.findall(expr, raw_cmd_out)
    date = dates[0] + "_" + dates[1] + "_" + dates[2]
    return date


def convert_to_dng(path, folder):
    config_obj = load_conf()
    path_dnglab = config_obj["folders"]["dnglab"]
    source = path + "/" + folder
    files = os.listdir(source)
    # check if the file has already been converted
    for file in files:
        if file.replace("CR3", "dng") in files:
            continue
        # ...if not convert it
        else:
            proc = subprocess.Popen(
                [path_dnglab, "convert", source + "/" + file, source + "/" + file.replace("CR3", "dng")])
            while proc.poll() is None:
                time.sleep(2)



def get_file_extension(file):
    temp = file.split(".")
    extension = temp[len(temp) - 1]
    file_name = temp[0]
    return file_name, extension


def sort_new_images():
    config_obj = load_conf()
    pathx = config_obj["folders"]
    path = pathx["ftp_path"]
    try:
        files = os.listdir(path)
        allowed_image_types = ["jpg", "jpeg", "cr3", "cr2", "DNG", "dng", "CR3"]
        images_to_convert = []
        folders = []
        images = []
        for file in files:
            filename, extension = get_file_extension(file)
            if extension in allowed_image_types:  # append all images to the images list
                images.append(file)
                if extension == "cr3" or extension == "CR3":  # if the image is cr3 append it to the to do list for the converter
                    images_to_convert.append(file)

        for image in images:
            filename, extension = get_file_extension(image)
            # only send .dng files to the function, cr3 images will be moved due to their names
            if extension == "CR3":
                date = get_capture_date(path, image)
            else:
                continue
            # get exif Data to read the date & check whether file is cr3 thus needing to be converted

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


def update_system_status():
    storage = get_disk_space()
    cpu_load = get_CPU_usage()

    status = {
        "cpu": cpu_load,
        "storage": storage
    }

    post_system_status = requests.post("http://localhost:1880/api/cpuload", status)
    return post_system_status.text
