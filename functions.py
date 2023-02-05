import shutil
from typing import List

import psutil
import re


def get_disks():

    regex=r"/dev/sd"
    all_disk = psutil.disk_partitions()
    physical_disks=[]
    y=0
    for x in all_disk:
        temp=all_disk[y][0]
        match=re.match(regex,temp)

        if(match is not None):
            physical_disks.append(all_disk[y][1]) #returns disk mounting point of all disks
            physical_disks.append(shutil.disk_usage(all_disk[y][1])) # get space of the connected disk
        else:
            continue
        y+=1
    return physical_disks

#get cpu usage and frequency per core
def get_CPU_usage():
    usage=psutil.cpu_percent(interval=1,percpu=True)
    freq1=psutil.cpu_freq(percpu=True)
    freq=[]
    y=0
    for _ in freq1:
        freq.append(freq1[y][0])
    y+=1
    return usage,freq


