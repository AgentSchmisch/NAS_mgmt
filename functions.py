import os
import shutil
import subprocess
from typing import List
from PIL import Image, ExifTags
import time

from config_helper import load_conf

import psutil
import re


def get_disks():
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
    #  parse and convert date to YYYY_MM_DD
    raw_date = ""
    try:
     raw_date = Image.open(path + "/" + image).getexif()[306]
    except Exception as e:
        file = open("log.txt","w+")
        file.write(str(e))
        file.close()

    # output: YYYY:MM:DD HH:MM:SS
    # ...split string before space...
    raw_date_array = raw_date.split(" ")
    # ...and replace : with _
    capture_date = raw_date_array[0].replace(":", "_")
    return capture_date


def convert_to_dng(path, image):
    # TODO: get path of dnglab install from config.json
    config_obj = load_conf()
    path_dnglab = config_obj["folders"]["dnglab"]
    source = path + "/" + image
    output = path + "/" + image.replace("CR3", "DNG")
    proc = subprocess.Popen([path_dnglab, "convert", source, output])
    while proc.poll() is None:
        time.sleep(2)

# TODO: reading image EXIF after conversion

def get_file_extension(file):
    temp = file.split(".")
    if len(temp) == 1:
        if os.path.isdir(file):  # check if the file is a folder, return the extension "folder"
            extension = "folder"
            file_name = temp[len(temp) - 1]
        else:  # if it is a file without any extension return an empty string
            extension = ""
            file_name = temp[len(temp) - 1]
    else:
        extension = temp[len(temp) - 1]
        file_name = temp[0]
    return file_name, extension


def sort_new_images():
    config_obj = load_conf()
    pathx = config_obj["folders"]
    path = pathx["ftp_path"]
    files = os.listdir(path)
    allowed_image_types = ["jpg", "jpeg", "cr3", "cr2", "DNG", "dng", "CR3"]
    folders = []
    images_to_convert = []
    images = []
    for file in files:
        filename, extension = get_file_extension(file)
        if extension == "folder":  # append the folders to the folders list
            folders.append(file)
        elif extension in allowed_image_types:  # append all images to the images list
            images.append(file)
            if extension == "cr3" or extension == "CR3":  # if the image is cr3 append it to the to do list for the converter
                images_to_convert.append(file)
    for image in images_to_convert:
        # convert the image from cr3 to dng
        convert_to_dng(path, image)

    for image in images:
        filename, extension = get_file_extension(image)
        # only send .dng files to the function, cr3 images will be moved due to their names
        if extension == "dng":
            date = get_capture_date(path, image)
        else:
            continue
        # get exif Data to read the date & check whether file is cr3 thus needing to be converted

        # if a folder with the image date exists, move the file to the folder
        # if the folder doesn't exist...create it
        if os.path.exists(path+"/"+date):
            shutil.move(path + "/" + image, path + "/" + date + "/" + image)
            shutil.move(path + "/" + image.replace("dng", "CR3"), path + "/" + date + "/" + image.replace("dng", "CR3"))
            print("moved to folder")
        else:
            os.mkdir(path + "/" + date)
            shutil.move(path + "/" + image, path + "/" + date + "/" + image)
            shutil.move(path + "/" + image.replace("dng", "CR3"), path + "/" + date + "/" + image.replace("dng", "CR3"))
