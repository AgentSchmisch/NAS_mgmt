from flask import Flask, render_template
import os,string
import functions
import shutil


app=Flask(__name__)






@app.route("/")
def main():

    # get disk spaces of all the drive and render it to the template
    # get the status of the disks and render it to the template
    cpuUsage=functions.get_CPU_usage()
    available_drives=functions.get_disks()


    return render_template("index.html", drives=available_drives,CPUusage=cpuUsage)


@app.route("/api/v1/newCommit", methods=['POST'])
def newCommit():

    os.system("cd /var/www/html")
    os.system("git pull")
    return "1"


if __name__ == "__main__":
    app.run("0.0.0.0",debug=True)

