import time
from Trackers import *
from os.path import expanduser


class Timer:
    def __init__(self, path=expanduser("~/AppData/Roaming/.minecraft/").replace("\\", "/")):
        self.path = path
        self.savesTracker = None
        self.logsTracker = None

        self.state = 0
        # 0 = Stopped, 1 = Going, 2 = Paused
        self.startTime = 0
        self.pauseTime = 0
        self.attempts = 0

        self.updatePath(path)

    def getIGT(self):
        if self.savesTracker is not None:
            return self.savesTracker.getIGT()
        else:
            return 0
        
    def newWorldStart(self):
        self.attempts += 1
        self.start()
        
    def setAttempts(self,attempts):
        self.attempts = attempts
    
    def getAttempts(self):
        return self.attempts

    def getRTA(self):
        if self.state == 0:
            return 0
        elif self.state == 1:
            return time.time() - self.startTime
        elif self.state == 2:
            return self.pauseTime

    def updatePath(self, path):
        self.end()
        self.savesTracker = SavesTracker(os.path.join(self.path, "saves"))
        self.logsTracker = LogsTracker(os.path.join(self.path, "logs"))
        self.savesTracker.addNewWorldCall(
            self.logsTracker.listenUntilWorldStart, (60, self.newWorldStart))
        self.savesTracker.addNewWorldCall(self.reset)

    def togglePause(self):
        if self.state in [0, 2]:
            self.start()
        elif self.state == 1:
            self.pause()

    def start(self):
        if self.state != 1:
            self.startTime = time.time() - (self.pauseTime if self.state == 2 else 0)
            self.state = 1

    def pause(self):
        if self.state == 1:
            self.pauseTime = time.time() - self.startTime
            self.state = 2

    def reset(self):
        self.state = 0
        self.pauseTime = 0
        self.startTime = 0

    def end(self):
        for tracker in [self.savesTracker, self.logsTracker]:
            if tracker is not None:
                tracker.stop()
        self.savesTracker = None
        self.logsTracker = None

    kill = end
    stop = end
