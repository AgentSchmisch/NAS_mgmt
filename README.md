# NAS-Mgmt

The aim of this Project is to create a simple, yet powerful User-Interface/Dashboard to control a 4 Disk self hosted NAS System.

## Setup

- It is important to start the software as root so all the PC's commands can be executed without prompting for a password


## Website auto Updater

The website auto Updater is used to pull a specific repository from a self-hosted Gitea when pushing into a branch
- create a branch that will be listened to as the "production" branch
- In a repository create a webhook routing to your webserver on the address `localhost:5000/api/v1/newCommit` 
- push to the "production" branch and your local repository will be automatically updated

## Dashboard
The dashboard is used to control a variety of different functions from the server:

### Hot swap drives
In the Dashboard you can use the buttons labeled `unmount drive` to disconnect the drive from the PC and therefore being able to change the drive to a new one

### View current capacity of Drives
In the Dashboard you can see the remaining capacity of the connected drives

### View CPU Usage
In the Dashboard you can inspect the CPU Usage of your System

### Server Control Section
In this section there will be some controls for your server, like restarting  


## Contributors


<img src = "https://contrib.rocks/image?repo=AgentSchmisch/NAS_mgmt"/>
