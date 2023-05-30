import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

from functions import get_file_extension, allowed_image_types, process_recieved_ftp_image
from config_helper import load_conf
import logging
from logger import logger

log = logger(logging.INFO, "ftp")


class ftphandler(FTPHandler):
    def on_file_received(self, file):
        #the parameter file represents the full file path here

        #os.chmod(file,0o555) # change file permissions

        print("here" + file)
        file_name = file.split("/")[-1]
        print(file_name)
        file_name, file_extension = get_file_extension(file_name)

        if self.username == "camera":
            if file_extension in allowed_image_types:
                # TODO could try to execute the sort_new_images function, possibility is that there will be images that drop under the table bc of the images being transferred faster than they are converted
                process_recieved_ftp_image(file_name+"."+file_extension.upper(),file.replace("/"+file_name+file_extension,""))
                print("allowed file")
                log.info("%s uploaded file %s"%(self.username, file))
            else:
                os.remove(file)
                log.warning("user %s tried to upload an illegal file of type %s"%(self.username, file_extension))
        log.info("%s uploaded file %s"%(self.username, file))    
    def on_incomplete_file_sent(self,file):

        log.warning("file %s was not uploaded completely"%file)

    def on_connect(self):
        print("connected" + self.remote_ip)

    def on_login(self,username):
        print("user %s logged in"%username)

def init_ftp_server():
    print(" * Starting FTP Server")
    log.info("started ftp server")
    config_obj = load_conf()
    ftp_path = config_obj["folders"]["ftp_path"]

    authorizer = DummyAuthorizer()
    for user in config_obj["ftp_users"]:
     authorizer.add_user(user["ftp_username"], user["ftp_username"], ftp_path, perm="elradfmwMT")
    handler = ftphandler
    handler.authorizer = authorizer
    try:
        # Create the FTP server
        server = ThreadedFTPServer(("0.0.0.0", 21), handler)
        server.serve_forever()
    except Exception as ex:
        log.error("Error: "+ex)
        
