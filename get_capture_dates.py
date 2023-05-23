import os
import json
from config_helper import load_conf

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--image")
parser.add_argument("-p", "--path")

args = parser.parse_args()
image = args.image
path = args.path

# WARNING: if using this function, the print statements are used as the output of the command.....not the return value

def get_capture_date(path,image):
    # parse and convert date to YYYY_MM_DD
    config_obj = load_conf()
    source = path + "/" + image

    cmd = "dnglab analyze --meta " + source

    raw_cmd_out = os.popen(cmd).read()

    raw_meta = json.loads(raw_cmd_out)

    raw_date = raw_meta["data"]["metadata"]["rawMetadata"]["exif"]["create_date"]

    # output: YYYY:MM:DD HH:MM:SS
    # ...split string before space...
    raw_date_array = raw_date.split(" ")
    # ...and replace : with _
    capture_date = raw_date_array[0].replace(":", "_")
    print(capture_date)
    return capture_date

get_capture_date(path, image)

