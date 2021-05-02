import threading
import os
import time
import json
from python_nbt import nbt


class SavesTracker:
    def __init__(self, path):
        self.path = path
        self.running = True
        self.mtime = 0
        self.latestWorld = None
        self.savesLen = 0
        self.worldList = []
        self.newWorldCalls = []
        self.updateWorldList()
        threading.Thread(target=self.loop).start()

    def stop(self):
        self.running = False

    def addNewWorldCall(self, func, args=""):
        self.newWorldCalls.append((func, args))

    def newWorldEvent(self):
        for i in self.newWorldCalls:
            i[0](*i[1])

    def getIGT(self, world=None):
        try:
            if world is None:
                world = self.latestWorld

            if world is None:
                return 0
            else:
                statsPath = os.path.join(self.path, world, "stats")
                statsFiles = os.listdir(statsPath)
                if len(statsFiles) > 0:
                    with open(os.path.join(statsPath, statsFiles[0]), "r") as statsFile:
                        statsJson = json.load(statsFile)
                        statsFile.close()
                    try:
                        return statsJson["stats"]["minecraft:custom"]["minecraft:play_one_minute"]/20
                    except:
                        return statsJson["stat.playOneMinute"]/20
                else:
                    return 0
        except:
            return 0

    def getAltIGT(self, world=None):
        try:
            if world == None:
                world = self.latestWorld

            if world is None:
                return 0
            else:
                levelDatPath = os.path.join(self.path, world, "level.dat")
                levelDatNBT = nbt.read_from_nbt_file(levelDatPath)["Data"]

                return levelDatNBT["Time"].value/20
        except:
            return 0

    def getKills(self, mobName, world=None):
        try:
            if world == None:
                world = self.latestWorld

            if self.world is None:
                return 0
            else:
                statsPath = os.path.join(self.path, world, "stats")
                statsFiles = os.listdir(statsPath)
                if len(statsFiles) > 0:
                    with open(os.path.join(statsPath, statsFiles[0]), "r") as statsFile:
                        statsJson = json.load(statsFile)
                        statsFile.close()
                    try:
                        return statsJson["stats"]["minecraft:killed"][f"minecraft:{mobName.lower()}"]
                    except:
                        return statsJson[f"stat.killEntity.{mobName[0].upper()+mobName[1:].lower()}"]
                else:
                    return 0
        except:
            return 0

    def updateWorldList(self):
        oldList = self.worldList[:]
        self.worldList = []
        newLatestWorld = None
        max = 0
        for worldName in os.listdir(self.path):
            if os.path.isfile(os.path.join(self.path, worldName, "level.dat")):
                self.worldList.append(worldName)
                wtime = os.path.getctime(os.path.join(self.path, worldName))
                if wtime > max:
                    newLatestWorld = worldName
                    max = wtime
                    if worldName not in oldList:
                        self.newWorldEvent()
            else:
                threading.Thread(target=self.waitForWorld,
                                 args=(worldName,)).start()
        self.latestWorld = newLatestWorld

    def waitForWorld(self, worldName):
        while self.running:
            time.sleep(0.5)
            if not os.path.isdir(os.path.join(self.path, worldName)):
                return
            elif os.path.isfile(os.path.join(self.path, worldName, "level.dat")):
                self.updateWorldList()
                return

    def loop(self):
        while self.running:
            time.sleep(0.1)
            newlen = len(os.listdir(self.path))
            newmtime = os.path.getmtime(self.path)
            if self.mtime != newmtime or self.savesLen != newlen:
                self.savesLen = newlen
                self.mtime = newmtime
                self.updateWorldList()


class LogsTracker:
    def __init__(self, path):
        self.path = path
        self.logPath = os.path.join(os.path.join(self.path, "latest.log"))
        self.running = True
        self.hasThread = False

    def cancel(self):
        self.running = False

    stop = cancel

    def refresh(self):
        self.start = time.time()

    def listenUntilWorldStart(self, timeout, responseCall, args=""):
        if not self.hasThread:
            threading.Thread(target=self._listenThread,
                             args=(timeout, responseCall, args)).start()
        else:
            self.refresh()

    def _listenThread(self, timeout, responseCall, args):
        self.hasThread = True
        try:
            if os.path.isfile(self.logPath):
                self.start = time.time()
                self.running = True
                lineLen = len(self.getLines())
                mtime = os.path.getmtime(self.logPath)
                while self.running and time.time() - self.start < timeout:
                    time.sleep(0.1)
                    newmtime = os.path.getmtime(self.logPath)
                    if mtime != newmtime:
                        mtime - newmtime
                        lines = self.getLines()
                        newLen = len(lines)
                        if newLen > lineLen:
                            for line in lines[lineLen: newLen]:
                                if "logged in with entity id" in line:
                                    responseCall(*args)
                        lineLen = newLen
            else:
                print("latest.log not found")
        except ValueError:
            print(ValueError)
        self.hasThread = False
        self.running = False

    def getLines(self):
        with open(self.logPath) as logFile:
            lines = [i.rstrip() for i in logFile.readlines()]
            logFile.close()
            return lines
