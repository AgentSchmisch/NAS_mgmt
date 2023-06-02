import os
import threading
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer

from functions import get_file_extension, allowed_image_types, process_recieved_ftp_image
from config_helper import load_conf
import logging
from logger import logger
from hashlib import md5
import re

regex = r"/[0-9a-f]{64}/i"

log = logger(logging.INFO, "ftp")

class MD5Authorizer(DummyAuthorizer):
    def validate_authentication(self,username,password,handler):
        if sys.version_info>=(3,0):
            password=md5(password.encode("latin1"))
        hash = md5(password).hexdigest()
        try:
            if self.user_table[username]['pwd'] != hash:
                raise KeyError
        except KeyError:
            raise AuthenticationFailed

class ftphandler(FTPHandler):
    def on_file_received(self, file):
        #the parameter file represents the full file path here

        #os.chmod(file,0o555) # change file permissions

        file_name = file.split("/")[-1]
        file_name, file_extension = get_file_extension(file_name)

        if self.username == "camera":
            if file_extension in allowed_image_types:
                process_recieved_ftp_image(file_name+"."+file_extension.upper(),file.replace("/"+file_name+file_extension,""))
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

    # TODO: check if current password is already hashed if so, use this one for add_user..is the password not a hash, digest it and save it to the config file

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
        
