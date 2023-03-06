![**Version**: 06-03-2023](https://img.shields.io/badge/version-06--03--2023-blueviolet?style=flat&logo=circle)
<h1 align="center"> NAS-Mgmt</h1>

....a simple, yet powerful User-Interface/Dashboard to control a up to 4 Disk, self hosted NAS System.

---

## 🧭 Contents
* [🧭 Contents](#-contents)
* [🖥️ Setup](#-setup)
* [📤 Website Auto Updater](#-website-auto-updater)
* [🔒 Login](#-login)
* [📊 Dashboard](#-dashboard)
  * [⏏️ Hot Swap Drives](#-hot-swap-drives)
  * [💾 Drive Capacity](#-drive-capacity)
  * [📈 CPU Usage](#-cpu-usage)
  * [⚙️ Server Control](#-server-control-section)
* [🔁 DNG Converter](#-dng-converter)
* [✅Requirements](#-requirements)
* [Contributors](#contributors)
---
## 🖥️ Setup

- It is important to start the software as root so all the PC's commands can be executed without prompting for a password
- there will be a packaged version of the repository so setup will be easier
- start off by installing all the requirements listed in [✅Requirements](#-requirements)

To Start the program afterwards, use...

```bash
cd your/project/folder
python3 main.py
```
...thats it, you should be up and running

---

## 📤 Website Auto Updater

The website auto Updater is used to pull a specific repository from a self-hosted Gitea when pushing into a branch
- create a branch that will be listened to as the "production" branch
- In a repository create a webhook routing to your webserver on the address `localhost:5000/api/v1/newCommit` 
- push to the "production" branch and your local repository will be automatically updated

---

## 🔒 Login
To access the Dashboard you need to create an account in a MariaDB Database, the scheme of the database is currently the following

| id           | username     | password     | is_admin |
|--------------|--------------|--------------|----------|
| varchar(100) | varchar(100) | varchar(100) | tinyint  |   

<details>
  <summary>Column Details</summary>

- id (uuid4 string)
- username (str)
- password (sha256 hash)
- is_admin (boolean)
  
</details>

---

## 📊 Dashboard
The dashboard is used to control a variety of different functions from the server:

### ⏏️ Hot swap drives
In the Dashboard you can use the buttons labeled `unmount drive` to disconnect the drive from the PC and therefore being able to change the drive to a new one

### 💾 Drive capacity
In the Dashboard you can see the current memory usage and remaining capacity of the connected drives

### 📈 CPU Usage
In the Dashboard you can inspect the CPU Usage of your System

### ⚙️ Server Control Section
In this section there will be some controls for your server, like restarting, putting it to hibernation and shutting down the server

---
## 🔁 DNG Converter
This feature will automatically check if there are new files in a certain folders with .cr3 images and convert them to .dng

- The converter check for new files in a certain folder you can copy the images there or use ftp to upload them to the folder
- It is necessary that the images are pasted without any parent folder, the Converter will automatically sort them by date with the scheme `DD-MM-YYYY` 
- the capture date of the images are read from the EXIF data of the image, so make sure the date of your camera is set correctly
- the converter will, by now, only convert `.cr3` images to `.dng`
- it is mandatory for the feature to work to install [pydngconverter](https://github.com/BradenM/pydngconverter)

---

## ✅ Requirements

In the Package all the requirements will be included in a file called `requirements.txt`
<details>
  <summary>Required Packages</summary>

| Package          |
|------------------|
| ✅ Flask          |
| ✅ pydngconverter |
| ✅ PIL            |
| ✅ MariaDB        |
| ✅ requests       |
| ✅ os             |
| ✅ shutil         |
| ✅ psutil         |
| ✅ re             |
| ✅ hashlib        |
| ✅ asyncio        |             

 It is also necessary to install following packages manually with:

```bash
sudo apt-get install libmariadb3 libmariadb-dev
sudo apt-get install gcc python3-dev
```

</details>

---

## Contributors

<img src = "https://contrib.rocks/image?repo=AgentSchmisch/NAS_mgmt"/>
