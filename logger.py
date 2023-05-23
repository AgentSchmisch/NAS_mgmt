import logging
import time
import config_helper
import requests
""" Log levels
Debug
info
warning
error
critical
"""

def logger(level,name):
    config_obj = config_helper.load_conf()
    log_folder = config_obj["folders"]["log_path"]

    filename = "log_", datetime.today().strftime('%Y_%m_%d')
    logger = logging.getLogger(name)
    logger.setLevel(level)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)
    
    # add ch to logger
    logger.addHandler(ch)
    logging.basicConfig(filename=filename, encoding='utf-8', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    return logger

def log(level,name,text):

    #TODO create log function to log into the file as well as send the level to nodered


    log = logger(logging.DEBUG,name)

    if level == "info":
        log.info(text)
        send_logs_to_nodered(level,name)
        return 1
    elif level == "warning":
        log.warning(text)
        send_logs_to_nodered(level,name)
        return 2
    elif level == "error":
        log.error(text)
        send_logs_to_nodered(level,name)
        return 3
    elif level == "critical":
        log.critical(text)
        send_logs_to_nodered(level,name)
        return 4
    else:
        return "not logged"

def cleanup_old_logs():
    #TODO: check if there are logs older than x days, and delete them
    log = logger(logging.DEBUG,"logs")
    log.info("deleted old logs")
    return true

def send_logs_to_nodered(level, name):
    config_obj = config_helper.load_conf()
    nodered = config_obj["addresses"]["nodered"]
    requests.post("http://"+ nodered +"/api/v1/logging", log)
    #TODO Create request that will push formatted data from logs to nodered where it will be presented more appealing
    return true