# other modules
import global_hotkeys
import os
import time
import threading
import json
import traceback
import tkinter as tk
import tkinter.font as tkFont
from sys import platform
# modules for this project
from Element import *
from Timer import *
from KeybindManager import *
from DragableWindow import *
from OptionsMenu import *

# info
amctVersion = "v2.0.0-pre3"
hotkeylist = '''Possible Hotkeys:

0,1,2...
a,b,c...
numpad_0,numpad_1,numpad_2...
f1,f2,f3...
+,-./`;[\]'`

backspace, tab, clear, enter, shift, control, alt, pause, caps_lock, escape, space, page_up, page_down, end, home, left, up, right, down, select, print, execute, enter, print_screen, insert, delete, help

multiply_key, add_key, separator_key, subtract_key, decimal_key, divide_key, num_lock, scroll_lock, left_shift, right_shift,  left_control, right_control, left_menu, right_menu, browser_back, browser_forward, browser_refresh, browser_stop, browser_search, browser_favorites, browser_start_and_home, volume_mute, volume_Down, volume_up, next_track, previous_track, stop_media, play/ \
    pause_media, start_mail, select_media, start_application_1, start_application_2, attn_key, crsel_key, exsel_key, play_key, zoom_key, clear_key

'''


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
        except:
            traceback.print_exc()
            self.stop()
            self.destroy()

    def startup(self):
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.iconbitmap(resource_path("Icon.ico"))
        DragableWindow.__init__(self)

        self.translation = {
            "rta": "RTA Timer",
            "igt": "IGT Timer",
            "attempts": "Attempts Counter",
            "endermen": "Enderman Kill Counter",
            "blaze": "Blaze Kill Counter"
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
            "mcPath": os.path.expanduser("~/AppData/Roaming/.minecraft").replace("\\", "/")
        }

        self.title("AutoMCTimer "+amctVersion)
        self.keybindManager = KeybindManager(self)
        self.optionsMenu = None
        self.path = expanduser(
            "~/AppData/Roaming/.automctimer/").replace("\\", "/")

        self.bind("<Escape>", self.openOptionsMenu)
        self.bind("r", self.refresh)
        self.bind("R", self.refresh)

        self.elements = []
        self.timer = None
        self.bg = "#000000"
        self.selectedAttempts = ""

        self.optionsInit()

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
        with open(filePath, "r") as optionsFile:
            optionsJson = json.load(optionsFile)
            optionsFile.close()
        return optionsJson

    def loadOptions(self, optionsJson):

        for default in self.defaultSettings:
            if default not in optionsJson or type(optionsJson[default]) != type(self.defaultSettings[default]):
                optionsJson[default] = self.defaultSettings[default]

        self.keybinds = optionsJson["keybinds"]
        self.keybindManager.bind(
            optionsJson["keybinds"]["pause"], optionsJson["keybinds"]["reset"])

        self.geometry(str(optionsJson['windowSize'][0]) +
                      "x"+str(optionsJson['windowSize'][1]))
        if self.timer is not None:
            self.timer.updatePath(optionsJson["mcPath"])
        else:
            self.timer = Timer(path=optionsJson["mcPath"])
        self.timer.setAttempts(optionsJson["attempts"])
        self.bg = optionsJson["background"]
        self.mcPath = optionsJson["mcPath"]
        self.config(bg=self.bg)
        self.loadElements(optionsJson["elements"])

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
            "mcPath": self.mcPath
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

            opt.color = elementJson["color"]
            opt.position = elementJson["position"]
            opt.prefix = elementJson["prefix"]
            opt.font = elementJson["font"]
            opt.size = elementJson["size"]

            element.updateDisplay()
            self.elements.append(element)

    def getRTA(self):
        if self.timer is not None:
            return self.convertSeconds(self.timer.getRTA())
        else:
            return self.convertSeconds(0)

    def getIGT(self):
        if self.timer is not None:
            return self.convertSeconds(self.timer.getIGT())
        else:
            return self.convertSeconds(0)

    def getAttempts(self):
        if self.timer is not None:
            return str(self.timer.getAttempts())
        else:
            return "0"

    @staticmethod
    def convertSeconds(seconds: float):
        x = seconds
        Seconds = "%.3f" % (x-(int(x)-(int(x) % 60)))
        if x % 60 < 10:
            Seconds = "0" + Seconds
        Minutes = str(int(x/(60)) % 60)
        Hours = str(int(x/(60*60)))

        if len(Minutes) < 2 and Hours != "0":
            Minutes = "0" + Minutes

        return ((Hours+":") if Hours != "0" else "")+Minutes+":"+Seconds


if __name__ == "__main__":
    timerApp = TimerApp()
    timerApp.mainloop()
