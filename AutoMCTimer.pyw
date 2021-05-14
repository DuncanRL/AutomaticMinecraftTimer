# other modules
import global_hotkeys
import os
import time
import threading
import json
import webbrowser
import traceback
import tkinter as tk
import tkinter.font as tkFont
import tkinter.simpledialog as tkSimpleDialog
from sys import platform
# modules for this project
from Element import *
from Timer import *
from KeybindManager import *
from DragableWindow import *
from OptionsMenu import *
import AMCTVersionHelper

# info
amctVersion = "v2.3.1"
hotkeylist = '''Possible Hotkeys:

0,1,2...
a,b,c...
numpad_0,numpad_1,numpad_2...
f1,f2,f3...
+,-./`;[\]'`

backspace, tab, clear, enter, shift, control, alt, pause, caps_lock, escape, space, page_up, page_down, end, home, left, up, right, down, select, print, execute, enter, print_screen, insert, delete, help

multiply_key, add_key, separator_key, subtract_key, decimal_key, divide_key, num_lock, scroll_lock, left_shift, right_shift,  left_control, right_control, left_menu, right_menu, browser_back, browser_forward, browser_refresh, browser_stop, browser_search, browser_favorites, browser_start_and_home, volume_mute, volume_Down, volume_up, next_track, previous_track, stop_media, play/ \
    pause_media, start_mail, select_media, start_application_1, start_application_2, attn_key, crsel_key, exsel_key, play_key, zoom_key, clear_key'''




def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class TimerApp(tk.Tk, DragableWindow):
    def __init__(self):
        tk.Tk.__init__(self)
        try:
            self.startup()
            self.after(0,self.loop)
        except:
            traceback.print_exc()
            self.stop()
            self.destroy()
    
    def loop(self):
        self.after(50,self.loop)
        self.timer.doesAuto = self.doesAuto

    def startup(self):
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.iconbitmap(resource_path("Icon.ico"))
        DragableWindow.__init__(self)

        self.translation = {
            "rta": "RTA Timer",
            "igt": "IGT Timer",
            "attempts": "Attempts Counter",
            "endermen": "Enderman Kill Counter",
            "blaze": "Blaze Kill Counter",
            "glitchigt": "level.dat Time",
            "text": "Basic Text"
        }

        self.defaultSettings = {
            "settingsVersion": 0,
            "keybinds": {
                "pause": ["\\"],
                "reset": ["]"]
            },
            "elements": [
                {
                    "type": "rta",
                    "position": [0, 0],
                    "color":"#ffffff",
                    "prefix":"",
                    "font":"Arial",
                    "size":50
                },
                {
                    "type": "igt",
                    "position": [0, 70],
                    "color":"#ffffff",
                    "prefix":"IGT: ",
                    "font":"Arial",
                    "size":30
                }
            ],
            "windowSize": [400, 150],
            "background": "#000000",
            "attempts": 0,
            "mcPath": os.path.expanduser("~/AppData/Roaming/.minecraft").replace("\\", "/"),
            "auto": True,
            "rtaAccuracy": 3,
            "igtAccuracy": 3
        }

        self.title("AutoMCTimer "+amctVersion)
        self.keybindManager = KeybindManager(self)
        self.optionsMenu = None
        self.path = expanduser(
            "~/AppData/Roaming/.automctimer/").replace("\\", "/")

        self.bind("<Escape>", self.openOptionsMenu)
        self.bind("r", self.refresh)
        self.bind("R", self.refresh)
        self.bind("s", self.setTime)
        self.bind("S", self.setTime)

        self.elements = []
        self.timer = None
        self.bg = "#000000"
        self.selectedAttempts = ""

        self.optionsInit()
        self.update()
        self.checkVersion()

    def checkVersion(self):

        versionInfo = AMCTVersionHelper.getLatestVersionInfo()
        if versionInfo is not None:
            lastSeenVersion = amctVersion
            lastSeenVersionPath = os.path.join(self.path, "lastSeenVersion")
            if os.path.isfile(lastSeenVersionPath):
                with open(lastSeenVersionPath, "r") as lsvFile:
                    lastSeenVersion = lsvFile.read()
                    lsvFile.close()
            if not AMCTVersionHelper.isUpdated(versionInfo[1], lastSeenVersion) and (not AMCTVersionHelper.isUpdated(versionInfo[1], amctVersion)):
                with open(lastSeenVersionPath, "w") as lsvFile:
                    lsvFile.write(versionInfo[1])
                    lsvFile.close()
                ans = tkMessageBox.askyesno("AMCT: Outdated Version", "Your current version is "+amctVersion +
                                            " but the latest version is "+versionInfo[1]+". Would you like to go to the downloads page?")
                if ans:
                    webbrowser.open(versionInfo[0])

    def setTime(self, x=0):
        if self.optionsMenu is None:
            self.wm_attributes("-topmost", 0)
            ans = tkSimpleDialog.askstring(
                "AMCT: Set Time", "Set the time using one of the following:\nxx:xx:xx.xxx\nxx:xx.xxx\nxx.xxx")
            self.wm_attributes("-topmost", 1)
            if ans is not None:
                try:
                    ans = [(i if float(i) > 0 else 0) for i in ans.split(":")]
                    if len(ans) == 1:
                        self.timer.setRTA(float(ans[0]))
                    elif len(ans) == 2:
                        self.timer.setRTA(60*int(ans[0])+float(ans[1]))
                    elif len(ans) == 3:
                        self.timer.setRTA(
                            60*60*int(ans[0])+60*int(ans[1])+float(ans[2]))
                    else:
                        int("Invalid Time Bro lmaooo gotem")
                except:
                    traceback.print_exc()
                    tkMessageBox.showerror("AMCT: Error", "Invalid time")

    def refresh(self, x=0):
        if self.optionsMenu is None:
            self.saveOptions()
            self.optionsInit()

    def removeDeadElements(self):
        toRemove = []
        for i in self.elements:
            if not i.exists:
                toRemove.append(i)

        for i in toRemove:
            self.elements.remove(i)

    def recenter(self):
        self.geometry("+0+0")

    def openOptionsMenu(self, x=0):
        if self.optionsMenu is None:
            self.optionsMenu = OptionsMenu(self)

    def optionsInit(self):
        # If there is no .automctimer, make the directories
        if not os.path.isdir(self.path):
            os.makedirs(self.path)

        # Get path to the selected.txt
        selectedFilePath = os.path.join(self.path, "selected.txt")

        # Check if there is a selected option stored, if not then create one with "default"
        if not os.path.isfile(selectedFilePath):
            with open(selectedFilePath, "w+") as selectedFile:
                selectedFile.write("default")
                selectedFile.close()

        # Get the name of the selected option
        with open(selectedFilePath, "r") as selectedFile:
            selectedText = selectedFile.read().rstrip()
            selectedFile.close()

        # Check if the selected option exists, if not then make one with defaults
        optionsPath = os.path.join(self.path, selectedText+".json")
        if not os.path.isfile(optionsPath):
            with open(optionsPath, "w+") as optionsFile:
                json.dump(self.defaultSettings, optionsFile, indent=4)
                optionsFile.close()

        # Load the options
        self.loadOptions(self.loadFile(optionsPath))

    def loadFile(self, filePath):
        # convert the json of a filepath to a python dict
        with open(filePath, "r") as optionsFile:
            optionsJson = json.load(optionsFile)
            optionsFile.close()
        return optionsJson

    def loadOptions(self, optionsJson):
        # Check that all keys in the dict exist
        for default in self.defaultSettings:
            if default not in optionsJson or type(optionsJson[default]) != type(self.defaultSettings[default]):
                optionsJson[default] = self.defaultSettings[default]

        # Setup keybinds
        self.keybinds = optionsJson["keybinds"]
        self.rebind()

        # Set window size
        self.geometry(str(optionsJson['windowSize'][0]) +
                      "x"+str(optionsJson['windowSize'][1]))

        # Create/update internal timer
        if self.timer is not None:
            self.timer.updatePath(optionsJson["mcPath"])
        else:
            self.timer = Timer(path=optionsJson["mcPath"])

        # Load other variables
        self.timer.setAttempts(optionsJson["attempts"])
        self.bg = optionsJson["background"]
        self.mcPath = optionsJson["mcPath"]
        self.doesAuto = optionsJson["auto"]
        self.rtaAccuracy = optionsJson["rtaAccuracy"]
        self.igtAccuracy = optionsJson["igtAccuracy"]
        self.config(bg=self.bg)
        self.loadElements(optionsJson["elements"])

    def rebind(self):

        self.keybindManager.bind(
            self.keybinds["pause"], self.keybinds["reset"])

    def saveOptions(self):
        selectedFilePath = os.path.join(self.path, "selected.txt")

        # Check if there is a selected option stored, if not then create one with "default"
        if not os.path.isfile(selectedFilePath):
            with open(selectedFilePath, "w+") as selectedFile:
                selectedFile.write("default")
                selectedFile.close()

        # Get the name of the selected option
        with open(selectedFilePath, "r") as selectedFile:
            selectedText = selectedFile.read().rstrip()
            selectedFile.close()

        options = {
            "settingsVersion": 0,
            "keybinds": self.keybinds,
            "elements": [i.toDict() for i in self.elements],
            "windowSize": [self.winfo_width(), self.winfo_height()],
            "background": self.bg,
            "attempts": self.timer.getAttempts(),
            "mcPath": self.mcPath,
            "auto": self.doesAuto,
            "rtaAccuracy": self.rtaAccuracy,
            "igtAccuracy": self.igtAccuracy
        }

        optionsPath = os.path.join(self.path, selectedText+".json")
        with open(optionsPath, "w+") as optionsFile:
            json.dump(options, optionsFile, indent=4)

    def exit(self, x=0):

        if self.optionsMenu is None:
            self.saveOptions()
            self.stop()
            self.destroy()
        else:
            ans = self.optionsMenu.exit()
            if ans is not None:
                self.exit()

    def stop(self):
        if self.timer is not None:
            self.timer.stop()

    def togglePause(self):
        if self.timer is not None:
            self.timer.togglePause()

    def resetTimer(self):
        if self.timer is not None:
            self.timer.reset()
            self.timer.savesTracker.updateWorldList()

    def loadElements(self, elements):
        for i in self.elements:
            i.destroy()
        self.elements = []
        for elementJson in elements:
            element = Element.fromIdentifier(elementJson["type"], self)
            opt = element.options

            opt.color = elementJson.get("color","#ffffff")
            opt.position = elementJson.get("position",[0,0])
            opt.prefix = elementJson.get("prefix","")
            opt.font = elementJson.get("font","Arial")
            opt.size = elementJson.get("size",50)
            opt.align = elementJson.get("align","w")

            element.updateDisplay()
            self.elements.append(element)

    def getRTA(self):
        if self.timer is not None:
            return self.convertSeconds(self.timer.getRTA(), self.rtaAccuracy)
        else:
            return self.convertSeconds(0, self.rtaAccuracy)

    def getIGT(self):
        if self.timer is not None:
            return self.convertSeconds(self.timer.getIGT(), self.igtAccuracy)
        else:
            return self.convertSeconds(0, self.igtAccuracy)

    def getAltIGT(self):
        if self.timer is not None:
            return self.convertSeconds(self.timer.getAltIGT(), self.igtAccuracy)
        else:
            return self.convertSeconds(0, self.igtAccuracy)

    def getAttempts(self):
        if self.timer is not None:
            return str(self.timer.getAttempts())
        else:
            return "0"

    def getKills(self, mobName):
        if self.timer is not None:
            return str(self.timer.getKills(mobName))
        else:
            return "0"

    @staticmethod
    def convertSeconds(seconds: float, accuracy=3):
        x=seconds#x = int(seconds*(10**accuracy))/10**accuracy
        if accuracy < 1:
            Seconds = str(int(x-(int(x)-(int(x) % 60))))
        else:
            Seconds = f"%.{str(accuracy)}f" % (x-(int(x)-(int(x) % 60)))
        if x % 60 < 10:
            Seconds = "0" + Seconds
        Minutes = str(int(x/(60)) % 60)
        Hours = str(int(x/(60*60)))

        if len(Minutes) < 2 and Hours != "0":
            Minutes = "0" + Minutes

        return ((Hours+":") if Hours != "0" else "")+Minutes+":"+Seconds


for i in range(60001):
    print(TimerApp.convertSeconds(i/1000,accuracy=1))


if __name__ == "__main__":
    timerApp = TimerApp()
    timerApp.mainloop()
