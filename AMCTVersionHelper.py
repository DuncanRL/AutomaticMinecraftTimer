import requests

def getLatestVersionInfo():
    try:
        response = requests.get("https://api.github.com/repos/DuncanRuns/AutomaticMinecraftTimer/releases/latest").json()
        return [response["html_url"],response["tag_name"]]
    except:
        return None


def isUpdated(latest,current):
    return getVersionInt(current) >= getVersionInt(latest)
    

def getVersionInt(version):
    if version[0] == "v":
        version = version[1:]
    versionsplit = [int(i) for i in version.split(".")]
    return versionsplit[0]*1000000 + versionsplit[1]*1000 + versionsplit[2]