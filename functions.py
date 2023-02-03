import shutil


def diskUsage(name):
    total,used,free=shutil.disk_usage(name)
    return total,used,free



