from flask import Flask, render_template
import os,string
import functions
import shutil

app=Flask(__name__)






@app.route("/")
def main():

    # get disk spaces of all the drive and render it to the template
    # get the status of the disks and render it to the template

    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    var = []


    var.append(functions.diskUsage("/"))


    return render_template("index.html", drives=available_drives,space=var)

if __name__ == "__main__":
    app.run("0.0.0.0",debug=True)

