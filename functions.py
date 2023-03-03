import os
import shutil
from typing import List
import asyncio
from pydngconverter import DNGConverter, flags
from PIL import Image, ExifTags

from config_helper import load_conf


import psutil
import re


def get_disks():
    regex = r"/dev/sd"
    all_disk = psutil.disk_partitions()
    physical_disks = []
    y = 0
    for x in all_disk:
        temp = all_disk[y][0]
        match = re.match(regex, temp)

        if (match is not None):
            physical_disks.append(all_disk[y][1])  # returns disk mounting point of all disks
            physical_disks.append(shutil.disk_usage(all_disk[y][1]))  # get space of the connected disk
        else:
            continue
        y += 1
    return physical_disks


# get cpu usage and frequency per core
def get_CPU_usage():
    usage = psutil.cpu_percent(interval=1, percpu=True)
    freq1 = psutil.cpu_freq(percpu=True)
    freq = []
    y = 0
    for _ in freq1:
        freq.append(freq1[y][0])
    y += 1
    return usage #, freq


def get_capture_date(path, image):
    # TODO: parse and convert date format to DD_MM_YYYY
    return Image.open(path+image)._getexif()[36867]


async def convert_to_dng(path, image):

    dng_converter = DNGConverter(path+image,
                                 dest=path,
                                 jpeg_preview=flags.JPEGPreview.NONE,
                                 fast_load=True)
    return await dng_converter.convert()


def sort_new_images():
    path = ""
    files = os.listdir(path)
    allowed_image_types = ["jpg", "jpeg", "cr3", "cr2", "DNG", "dng"]
    folders = []
    images_to_convert = []
    images = []

    for file in files:
        temp = file.split(".")
        if temp[len(temp) - 1] != "":
            folders.append(file)
        elif temp[len(temp) - 1] in allowed_image_types:  # append all files to the images list
            images.append(file)
            if temp[len(temp) - 1] == "cr3":  # if the image is cr3 append it to the to do list for the converter
                images_to_convert.append(file)

    for image in images_to_convert:
        # convert the image from cr3 to dng
        loop = asyncio.get_event_loop()
        loop.run_until_complete(convert_to_dng(path, image))
        loop.close()



    for image in images:
        # get exif Data to read the date & check whether file is cr3 thus needing to be converted
        date = get_capture_date(path,image)

        # if a folder with the image date exists, move the file to the folder
        # if the folder doesn't exist...create it
        if date in folders:
            shutil.move(path + image, path + date + image)
        else:
            os.mkdir(path + date)
