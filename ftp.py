import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

import functions
from config_helper import load_conf
import logging
from logger import logger,http_logger

log = logger(logging.INFO, "ftp")


class ftphandler(FTPHandler):
    def on_file_recieved(self,file):
        #os.chmod(file,0o555) # change file permissions

        file_extension = functions.get_file_extension(file)

        if self.username == "camera":
            if file_extension in functions.allowed_image_types:
                # TODO could try to execute the sort_new_images function, possibility is that there will be images that drop under the table bc of the images being transferred faster than they are converted
                functions.sort_new_images(file)
                print("allowed file")
                log.info("%s uploaded file %s"%(self.username,file))
            else:
                os.remove(file)
                self.response("550 File %s is not allowed to be uploaded as user: %s"%( file, self.username))
                log.warning("user %s tried to upload an illegal file of type %s"% (self.username, file_extension))

    def on_incomplete_file(self,file):
        print(file," incomplete")
        log.warning("file %s was not uploaded completely"%file) 

def init_ftp_server():
    print("init")
    #log.INFO("started ftp server")
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
        
