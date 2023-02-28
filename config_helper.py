import json


def load_conf():
    with open("config.json", "r") as jsonfile:
        data = json.load(jsonfile)
    return data