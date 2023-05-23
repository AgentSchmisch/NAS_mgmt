import os
from pyftplib import DummyAuthorizer, FTPHandler, FTPServer
import functions
import config_helper
import logging
from logger import logger

log = logger(logging.DEBUG, "ftp")

class ftphandler(FTPHandler):
    def on_file_recieved(self,file):
        #os.chmod(file,0o555) # change file permissions

        file_extension = functions.get_file_extension(file)

        if self.username == "camera":
            if file_extension in functions.allowed_image_types:
                # TODO could try to execute the sort_new_images function, possibility is that there will be images that drop under the table bc of the images being transferred faster than they are converted
                print("allowed file")
                log.info("%u uploaded file %f",self.username,file)
            else:
                os.remove(file)
                self.response("550 File %f is not allowed to be uploaded as user: %u", file, self.username)
                log.warning(msg)("user %u tried to upload an illegal file of type %f", self.username, file_extension)

    def on_incomplete_file(self,file):
        print(file," incomplete")
        log.warning("file %f was not uploaded completely", file) 

config_obj = load_conf()
ftp_path = config_obj["folders"]["ftp_path"]

authorizer = DummyAuthorizer()

for user in config_obj["ftp_users"]: # creating all the users in the config file
    authorizer.add_user(user["ftp_username"], user["ftp_password"], fpt_path, perm="elradfmwMT")

handler = MyFTPHandler
handler.authorizer = authorizer

# Create the FTP server
server = FTPServer(("0.0.0.0", 21), handler)
