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


log = logger(logging.DEBUG, "functions")

allowed_image_types = ["jpg", "jpeg", "cr3", "cr2", "dng","mp4"]

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
    return usage


def get_capture_date(path, image):
    parent_folder = path.replace(image,"")
    expr = r'\d+'
    cmd = "python3 get_capture_dates.py -p " + parent_folder + " -i " + image
    raw_cmd_out = os.popen(cmd).read()
    time.sleep(3)
    print("raw" + raw_cmd_out)
    dates = re.findall(expr, raw_cmd_out)
    print(dates)
    date = dates[0] + "_" + dates[1] + "_" + dates[2]
    return date


def convert_single_image(path,image):
    """
    Parameters
    path: full path of the parent folder
    image: image to be converted

    this function converts a single image from .cr3 to .dng

    Return Value:
    True on success
    False on Error
    """
    print("convert:" + path)
    try:
        proc = subprocess.Popen(["dnglab","convert",path+image, path+image.replace("CR3","dng")])
        while proc.poll() is None:
            time.sleep(2)
        return True
    except:
        log.error("image %s could not be converted"%path+image)
        return False

def convert_to_dng(path, folder):
    """
    Parameters
    path: full path of the parent folder
    folder: folder to be converted

    this function converts a whole folder from .cr3 to .dng
    """
    config_obj = load_conf()
    source = path + "/" + folder
    files = os.listdir(source)
    # check if the file has already been converted
    for file in files:
        if file.replace("CR3", "dng") in files:
            continue
        # ...if not convert it
        else:
            proc = subprocess.Popen(["dnglab","convert", source + "/" + file, source + "/" + file.replace("CR3", "dng")])
            while proc.poll() is None:
                time.sleep(2)

def get_file_extension(file):
    """
    Parameters:
    file: any file with an extension

    this function will return the file extension for any image that is supplied to it

    Return Value:
    Tuple consisting of the file name and the lowercase extension
    """

    temp = file.split(".")
    extension = temp[len(temp) - 1]
    file_name = temp[0]
    return file_name, extension.lower()

def get_capture_date_jpg(path,image):
    """
    Parameters:
    path: full path of the image
    image: just the image name

    this function is used to get the capturedate of .jpg image

    Return Value:
    Capture date of the image
    """

    img = Image.open(path+"/"+image)

    raw_date = img.getexif()[306]
    # output: YYYY:MM:DD HH:MM:SS
    # ...split string before space...
    raw_date_array = raw_date.split(" ")
    # ...and replace : with _
    capture_date = raw_date_array[0].replace(":", "_")
    return capture_date

def sort_remaining_images():
    #TODO: rename to sort_orphaned_images
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

def get_or_create_folder(path,image,date):
    """
    Parameters: 
    path: full path of the image
    image: just the image name
    date: date that will be used as the foldername

    This function will either move the image into the corresponding dates folder 
    or create the folder and move the image into the folder afterwards

    Return Value:
    new path of the current image
    """
    path = path.replace(image,"") 
    print("---------------------")
    print("path: "+path)
    print("image: "+image)
    print("date: " + date)
    print("---------------------")
    
    if os.path.exists(path + "/" + date):
        shutil.move(path + "/" + image, path + "/" + date + "/" + image)
        new_path = path + date + "/"

    else:
        os.mkdir(path + "/" + date)
        shutil.move(path + "/" + image, path + "/" + date + "/" + image)
        new_path = path + date + "/"

    return new_path


def process_recieved_ftp_image(image,path):
    """
    Parameters:
    image: just the image name
    path: full path of the image

    this function gets called by the ftp server 
    and will sort the newly uploaded images as well as convert them

    Return Value:
    None
    """
    with lock:
        try:
            date = ""
            file_name,extension = get_file_extension(image)
            print("extension: "+extension)
            if extension == "cr3":
                date = get_capture_date(path, image)
            elif extension == "jpg":
                date = get_capture_date_jpg(path, image)
            print("date:" + date)
            new_path = get_or_create_folder(path,image,date)
            convert_single_image(new_path, image)

        except Exception as ex:
            log.error("process_recieved_ftp_image reported: %s"%ex)



def sort_new_images(file): # DEPRECATED
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
                log.error("sort_new_images reported: %s"%ex)


def check_dng_cr3_images(folder):
    """
    Parameters:
    folder: the folder that the images are stored in

    this function will check if there are a equal amount of cr3 images as well as dng images in the folder

    Return Value:
    True if the amount is equal
    False if the amount isn't equal
    """
    num_cr3 = 0
    num_dng = 0
    
    images = os.listdir(folder)
    for image in images:
        file_name, extension = get_file_extension(image)
        if extension == "cr3":
            num_cr3 += 1
        elif extension == "dng":
            num_dng += 1
        else:
            continue
    if num_cr3 == num_dng:
        return True
    else:
        return False


def check_for_unconverted_folders():
    """
    Parameters:
    none

    this function will check if there are images that need to be converted in any folder
    """
    log.info("started checking for unconverted images")
    photo_folder = load_conf()["folders"]["ftp_path"] 
    folders = []
    all_elements = os.listdir(photo_folder)
    for element in all_elements:
        if os.path.isdir(photo_folder+element):
            folders.append(photo_folder+element)
        else:
            continue
    for folder in folders:
        print(folder)
        if check_dng_cr3_images(folder):
            continue
        else:
            convert_to_dng(photo_folder, folder.replace(photo_folder,""))

def update_machine():
    # this function gets called by a BackgroundScheduler and updates the system
    try:
        proc = subprocess.Popen("apt update")
        while proc.poll() is None:
            time.sleep(2)

        proc = subprocess.Popen("apt upgrade")
        while proc.poll() is None:
            time.sleep(2)
    except Exception as ex:
        log.error("update_machine reported: "+ex)


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
