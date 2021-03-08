import global_hotkeys
import os
import time
import threading
import json
import tkinter as tk
import tkinter.font as tkFont
from Element import *
from Timer import *
from KeybindManager import *
amctVersion = "v2.0.0-preview"

hotkeylist = '''Possible Hotkeys:

0,1,2...
a,b,c...
numpad_0,numpad_1,numpad_2...
f1,f2,f3...
+,-./`;[\]'`

backspace, tab, clear, enter, shift, control, alt, pause, caps_lock, escape, space, page_up, page_down, end, home, left, up, right, down, select, print, execute, enter, print_screen, insert, delete, help

multiply_key, add_key, separator_key, subtract_key, decimal_key, divide_key, num_lock, scroll_lock, left_shift, right_shift,  left_control, right_control, left_menu, right_menu, browser_back, browser_forward, browser_refresh, browser_stop, browser_search, browser_favorites, browser_start_and_home, volume_mute, volume_Down, volume_up, next_track, previous_track, stop_media, play/pause_media, start_mail, select_media, start_application_1, start_application_2, attn_key, crsel_key, exsel_key, play_key, zoom_key, clear_key

'''


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class TimerApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.translation = {
            "rta": "Real-Time Attack",
            "igt": "In-Game Time",
            "attempts": "Attempts Counter"
        }

        self.bg = "#000000"
        self.config(bg=self.bg)

        self.defaultSettings = {
            "settingsVersion": 0,
            "keybinds": {
                "pause": "\\",
                "reset": "]"
            },
            "elements": [
                {
                    "type": "rta",
                    "position": [0, 0],
                    "color":"#ffffff",
                    "prefix":"",
                    "font":"DS-Digital",
                    "size":50
                },
                {
                    "type": "igt",
                    "position": [0, 70],
                    "color":"#ffffff",
                    "prefix":"IGT: ",
                    "font":"DS-Digital",
                    "size":30
                },
                # {
                #    "type": "attempts",
                #    "position": [0, 100],
                #    "color":"#ffffff",
                #    "prefix":"Attempt #",
                #    "font":"DS-Digital",
                #    "size":15
                # }
            ],
            "windowSize": [400, 150],
            "attemptCounters": [
                {
                    "name": "1.16.1 RSG",
                    "count": 0
                }
            ],
            "paths": [
                os.path.expanduser(
                    "~/AppData/Roaming/.minecraft").replace("\\", "/")
            ]
        }

        self.title("AutoMCTimer "+amctVersion)
        self.timer = Timer("C:\\Users\\Duncan\\AppData\\Roaming\\.minecraft\\1.15.2 Fabric")
        self.selectedAttempts = "1.16.1 RSG"

        self.keybindManager = KeybindManager(self)

        self.keybindManager.bind(["\\"],"alt+\\".split("+"))

        self.elements = []
        #self.loadElements(self.defaultSettings["elements"])

    def exit(self,x=0):
        self.stop()
        self.destroy()

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
            i.remove()
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
        return self.convertSeconds(self.timer.getRTA())

    def getIGT(self):
        return self.convertSeconds(self.timer.getIGT())

    def convertSeconds(self, seconds: float):
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
    try:
        timerApp = TimerApp()

        timerApp.geometry("353x122")
        timerApp.lift()
        timerApp.wm_attributes("-topmost", True)

        

        timerApp.mainloop()
    except ValueError:
        print(ValueError)
    