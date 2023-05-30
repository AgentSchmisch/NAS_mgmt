import logging
from datetime import datetime
import config_helper
import requests
import os

""" Log levels
Debug
info
warning
error
critical
"""

class HTTPLogHandler(logging.Handler):
    def __init__(self, url):
        super().__init__()
        self.url = url

    def emit(self, record):
        log_entry = self.format(record)
        payload = {'log_entry': log_entry}

        try:
            response = requests.post(self.url, json=payload)
            # Check the response status code or handle the response as needed
        except requests.exceptions.RequestException as e:
            # Handle any exceptions that occurred during the HTTP request
            print("Failed to send log entry:", str(e))

def logger(level,name):

    config_obj = config_helper.load_conf()
    log_folder = config_obj["folders"]["log_path"]
    log_url = config_obj["addresses"]["logs"]

    filename = log_folder + "log_"+ str(datetime.now().date()).replace("-", "_")
    logger = logging.getLogger(name)
    logger.setLevel(level)

    http_logger = HTTPLogHandler(log_url)
    http_logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    http_logger.setFormatter(formatter)

    logging.basicConfig(filename=filename, encoding='utf-8', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return logger


def cleanup_old_logs():
    # this function will be executed every day at 12pm with a BackgroundScheduler to delete old logs 
    config_obj = config_helper.load_conf()
    log_folder = config_obj["folders"]["log_path"]

    log_files = os.listdir(log_folder)
    for log_file in log_files:
        log_date_raw = log_file.split("_")
        log_date = date(log_date_raw[1], log_date_raw[2], log_date_raw[3])
        if datetime.now().date - timedelta(days=7) > log_date:
            os.remove(log_folder + log_file)

    log = logger(logging.DEBUG,"logs")
    log.info("deleted old logs")
    return true

