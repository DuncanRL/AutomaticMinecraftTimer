from threading import Thread
import tkinter as tk
import time
import tkinter.font as tkFont
import tkinter.colorchooser as tkColorChooser
import tkinter.filedialog as tkFileDialog
from tkinter import ttk
from sys import maxsize, platform
import webbrowser
from os import getcwd, mkdir, system, listdir
from os.path import expanduser, isfile, isdir, getmtime
import json
import tkinter.messagebox

amctVersion = "v1.5"


def readKey(timeout):
    keyr = keyReader()
    key = keyr.readKey(timeout)
    del(keyr)
    return key


class keyReader():
    def readKey(self, timeout):
        self.key = None
        self.rkt = Thread(target=self.readKeyThread)
        self.rkt.start()
        startTime = time.time()

        while time.time() - startTime < timeout and self.key == None:
            time.sleep(0.01)
        return self.key

    def readKeyThread(self):
        self.key = keyboard.read_hotkey(suppress=False)


class AutoMCTimer(tk.Frame):

    def __init__(self, parent, dataPath="default", *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        if dataPath == "default":
            if "win" in platform:
                dataPath = expanduser("~/AppData/Roaming/.automctimer/")
            else:
                dataPath = getcwd()+"/.automctimer/"

        if not isdir(dataPath):
            mkdir(dataPath)

        self.iconName = None
        for i in listdir(getcwd()):
            if "AutoMCTimer" in i and ".exe" in i:
                self.iconName = i

        if self.iconName != None:
            parent.iconbitmap(self.iconName)

        self.startTime = 0
        self.addedTime = 0
        self.isRunning = False
        self.isWaiting = False
        self.inOptions = False

        self.parent = parent
        self.dataPath = dataPath

        self.rtaFont = tk.font.Font(self, ("Arial", 50))
        self.igtFont = tk.font.Font(self, ("Arial", 30))
        self.attemptFont = tk.font.Font(self, ("Arial", 1))

        self.rtaText = tk.StringVar(self)
        self.igtText = tk.StringVar(self)
        self.attemptText = tk.StringVar(self)

        self.rtaPrefix = tk.StringVar(self)
        self.igtPrefix = tk.StringVar(self)
        self.attemptPrefix = tk.StringVar(self)

        self.rtaTimer = tk.Label(
            self, textvariable=self.rtaText, font=self.rtaFont, width=20, anchor="w")
        self.igtTimer = tk.Label(
            self, textvariable=self.igtText, font=self.igtFont, width=20, anchor="w")
        self.attemptLabel = tk.Label(
            self, textvariable=self.attemptText, font=self.attemptFont, width=20, anchor="w")

        self.rtaTimer.grid(row=0, column=0, sticky="w")
        self.igtTimer.grid(row=1, column=0, sticky="w")
        self.attemptLabel.grid(row=2, column=0, sticky="w")

        self.optionsMenu = None

        parent.protocol("WM_DELETE_WINDOW", self.exit)
        parent.bind("<Escape>", self.openOptionsMenu)

        self.optionsJson = None
        self.loadOptions()

        startw = self.optionsJson["windowSize"][0]
        starth = self.optionsJson["windowSize"][1]

        self.parent.geometry(str(startw)+"x"+str(starth))

        self.attempts = self.optionsJson["attempts"]

        self.loadKeys()

        self.parent.focus()

        self.after(0, self.loop)
        self.after(0, self.rtaUpdate)

        if self.optionsJson["welcomeMessage"]:

            self.update()

            tk.messagebox.askokcancel("AutoMCTimer: Welcome", "Welcome!\nPress escape with the timer open to access the options." + (
                "\n\nSince you are on linux, please set your .minecraft installation directory." if "linux" in platform else ""))

            if "linux" in platform:
                self.openOptionsMenu(1)

        parent.focus()

    def loadKeys(self):
        self.hotkeyPause = keyboard.add_hotkey(
            self.optionsJson["keybinds"]["pause"], self.pauseKey)
        self.hotkeyReset = keyboard.add_hotkey(
            self.optionsJson["keybinds"]["reset"], self.resetKey)

    def unloadKeys(self):
        keyboard.remove_hotkey(self.hotkeyPause)
        keyboard.remove_hotkey(self.hotkeyReset)

    def pauseKey(self):
        if self.isRunning:
            self.isRunning = False
            self.addedTime = time.time() - self.startTime + self.addedTime
        else:
            self.isRunning = True
            self.startTime = time.time()

    def resetKey(self):
        self.isRunning = False
        self.addedTime = 0

    def getIGT(self):
        latestWorld = self.getLatestWorld()
        if latestWorld == None:
            return 1
        try:
            statsDir = self.getLatestWorld()+"stats\\"
            if isdir(statsDir):
                with open(statsDir+listdir(statsDir)[0], "r") as statsFile:
                    statsJson = json.load(statsFile)
                    statsFile.close()
                return statsJson["stats"]["minecraft:custom"]["minecraft:play_one_minute"]/20
            else:
                return 0
        except:
            return 0

    @staticmethod
    def convertSeconds(x):
        Seconds = "%.3f" % (x-(int(x)-(int(x) % 60)))
        if x % 60 < 10:
            Seconds = "0" + Seconds
        Minutes = str(int(x/(60)) % 60)
        Hours = str(int(x/(60*60)))

        if len(Minutes) < 2 and Hours != "0":
            Minutes = "0" + Minutes

        return ((Hours+":") if Hours != "0" else "")+Minutes+":"+Seconds

    def getLatestWorld(self):
        try:
            worlds = []
            for i in listdir(self.expandMCPath("saves")):
                if isfile(self.expandMCPath("saves/"+i+"/level.dat")):
                    worlds.append(i)

            latestWorld = None
            lastestTime = 0
            for i in worlds:
                timeForI = getmtime(self.expandMCPath("saves/"+i))
                if timeForI > lastestTime:
                    lastestTime = timeForI
                    latestWorld = i

            return self.expandMCPath("saves/"+latestWorld+"/")

        except:
            return None

    def expandMCPath(self, path):
        return self.optionsJson["mcPath"] + path

    def rtaUpdate(self):
        if self.inOptions:
            self.after(100, self.rtaUpdate)
            self.rtaText.set(self.rtaPrefix.get() +
                             self.convertSeconds(0))
        else:
            self.after(10, self.rtaUpdate)
            if self.isRunning:
                self.rtaText.set(self.rtaPrefix.get() + self.convertSeconds(
                    time.time() - self.startTime + self.addedTime))
            else:
                self.rtaText.set(self.rtaPrefix.get() +
                                 self.convertSeconds(self.addedTime))

    def loop(self):
        if not self.inOptions:
            self.after(500, self.loop)

            self.attemptText.set(self.attemptPrefix.get()+str(self.attempts))

            igt = self.getIGT()
            self.igtText.set(self.igtPrefix.get() + self.convertSeconds(igt))

            if igt == 0 and not self.isWaiting:
                self.attempts += 1
                self.isRunning = False
                self.addedTime = 0
                self.isWaiting = True
                self.after(10, self.startWorld)

        else:
            self.after(100, self.loop)
            self.igtText.set(self.igtPrefix.get() + self.convertSeconds(0))
            self.attemptText.set(self.attemptPrefix.get()+str(self.attempts))

    def startWorld(self):
        igt = self.getIGT()
        if igt != 0.0:
            self.isRunning = True
            self.addedTime = 0
            self.startTime = time.time()
            self.isWaiting = False
        else:
            self.after(10, self.startWorld)

    @staticmethod
    def validateOptionsJson(optionsJson):
        vv = AutoMCTimer._validateValue
        defaultPath = getcwd()
        if "win" in platform:
            defaultPath = expanduser("~/AppData/Roaming/.minecraft/")

        vv(optionsJson, "mcPath", defaultPath)
        vv(optionsJson, "welcomeMessage", True)
        vv(optionsJson, "attempts", 0)
        vv(optionsJson, "windowSize", [500, 200])

        keybinds = vv(optionsJson, "keybinds", {})
        vv(keybinds, "pause", "\\")
        vv(keybinds, "reset", "]")

        display = vv(optionsJson, "display", {})
        vv(display, "font", "Arial")
        vv(display, "fontColour", "#ffffff")
        vv(display, "bgColour", "#000000")
        rta = vv(display, "rta", {})
        vv(rta, "size", "50")
        vv(rta, "prefix", "")
        igt = vv(display, "igt", {})
        vv(igt, "size", "30")
        vv(igt, "prefix", "IGT: ")
        ac = vv(display, "attemptCounter", {})
        vv(ac, "size", "20")
        vv(ac, "prefix", "Attempt #")

    @staticmethod
    def _validateValue(jsonThing, value, default):
        try:
            return jsonThing[value]
        except:
            jsonThing[value] = default
            return default

    def exit(self):
        if not (self.optionsMenu == None or not self.optionsMenu.winfo_exists()):
            if(self.optionsMenu.exit() != None):
                self.quickSave()
                self.parent.destroy()
        else:
            self.quickSave()
            self.parent.destroy()

    def quickSave(self):
        self.optionsJson["welcomeMessage"] = False
        self.optionsJson["attempts"] = self.attempts
        w = self.parent.winfo_width()
        h = self.parent.winfo_height()
        self.optionsJson["windowSize"] = [w, h]
        self.saveOptions(self.optionsJson)

    def loadOptions(self):
        if isfile(self.dataPath+"options.json"):
            try:
                with open(self.dataPath+"options.json", "r") as optionsFile:
                    self.optionsJson = json.load(optionsFile)
                    optionsFile.close()
            except:
                self.optionsJson = {}
        else:
            if not isdir(self.dataPath):
                mkdir(self.dataPath)
            self.optionsJson = {}

        self.validateOptionsJson(self.optionsJson)

        self.changeDisplay(self.optionsJson["display"])

    def saveOptions(self, optionsJson):
        self.optionsJson = optionsJson
        self.validateOptionsJson(self.optionsJson)
        with open(self.dataPath+"options.json", "w+") as optionsFile:
            optionsFile.write(json.dumps(optionsJson, indent=4))
            optionsFile.close()

    def openOptionsMenu(self, x):
        if not self.inOptions:
            self.resetKey()
            self.inOptions = True
            self.unloadKeys()
            self.optionsMenu = OptionsMenu(self)

    def changeDisplay(self, displayJson={}):

        self.parent.config(background=displayJson["bgColour"])
        self.config(background=displayJson["bgColour"])

        fonts = [self.rtaFont, self.igtFont, self.attemptFont]
        labels = [self.rtaTimer, self.igtTimer, self.attemptLabel]
        sizes = [displayJson["rta"]["size"], displayJson["igt"]
                 ["size"], displayJson["attemptCounter"]["size"]]
        prefixes = [displayJson["rta"]["prefix"], displayJson["igt"]
                    ["prefix"], displayJson["attemptCounter"]["prefix"]]
        prefixVariables = [self.rtaPrefix, self.igtPrefix, self.attemptPrefix]

        for i in range(3):
            inv = False
            if sizes[i] in ["0", 0, "", None]:
                s = 1
                inv = True
            else:
                s = sizes[i]
            fonts[i].config(family=displayJson["font"], size=s)
            if inv:
                labels[i].config(fg=displayJson["bgColour"],
                                 bg=displayJson["bgColour"])
            else:
                labels[i].config(fg=displayJson["fontColour"],
                                 bg=displayJson["bgColour"])

            prefixVariables[i].set(prefixes[i])

    def getTimerFrame(self):
        return self


class OptionsMenu(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent

        ico = self.getTimerFrame().iconName
        if ico != None:
            self.iconbitmap(ico)
        self.wm_resizable(False, False)
        self.title("AutoMCTimer: Options")

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.optionsMenuFrame = OptionsMenuFrame(self)
        self.optionsMenuFrame.grid(row=0, column=0, padx=10, pady=10)
        self.attributes("-topmost", True)

        self.focus()

    def exit(self):
        response = tk.messagebox.askyesnocancel(
            "AutoMCTimer: Save", "Save Options?")
        if response != None:
            if response:
                self.saveAndExit()
            else:
                self.exitWithoutSave()

        else:
            self.focus()
        return response

    def saveAndExit(self):
        displaySettings = self.optionsMenuFrame.displaySettings
        fontOptions = displaySettings.fontOptions
        colorOptions = displaySettings.colorOptions
        generalSettings = self.optionsMenuFrame.generalSettings
        self.getTimerFrame().saveOptions(
            {
                "mcPath": generalSettings.mcPath.get(),
                "keybinds": {
                    "pause": generalSettings.keyPause.get(),
                    "reset": generalSettings.keyReset.get()
                },
                "display": {
                    "font": fontOptions.fontName.get(),
                    "fontColour": colorOptions.color1,
                    "bgColour": colorOptions.color2,
                    "rta": {
                        "size": displaySettings.RTA.size.get(),
                        "prefix": displaySettings.RTA.prefix.get()
                    },
                    "igt": {
                        "size": displaySettings.IGT.size.get(),
                        "prefix": displaySettings.IGT.prefix.get()
                    },
                    "attemptCounter": {
                        "size": displaySettings.AttemptCounter.size.get(),
                        "prefix": displaySettings.AttemptCounter.prefix.get()
                    }
                }
            }
        )
        self.destroy()
        self.getTimerFrame().loadKeys()
        self.parent.inOptions = False

    def exitWithoutSave(self):
        self.getTimerFrame().loadOptions()
        self.getTimerFrame().attempts = self.optionsMenuFrame.generalSettings.oldAttempts
        self.destroy()
        self.getTimerFrame().loadKeys()
        self.parent.inOptions = False

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class OptionsMenuFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        exitButtonsFrame = tk.Frame(self)
        exitButtonsFrame.grid(row=0, column=1, pady=5, padx=5, sticky="s")

        exitButton = tk.Button(
            exitButtonsFrame, text="Apply", command=parent.saveAndExit)
        exitButton.grid(row=0, column=0, sticky="w", pady=0, padx=5)

        exitButton2 = tk.Button(
            exitButtonsFrame, text="Cancel", command=parent.exitWithoutSave)
        exitButton2.grid(row=0, column=1, sticky="w", pady=0, padx=5)

        self.generalSettings = GeneralSettings(self)
        self.generalSettings.config(highlightthickness=1,
                                    highlightbackground="black")
        self.generalSettings.grid(row=0, column=1, sticky="n", pady=5, padx=5)

        self.displaySettings = DisplaySettings(self)
        self.displaySettings.config(highlightthickness=1,
                                    highlightbackground="black")
        self.displaySettings.grid(row=0, column=0, sticky="w", pady=5, padx=5)

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class GeneralSettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        tk.Label(self, text="General Settings", font=tkFont.Font(
            self, font=("Arial", 15))).grid(padx=2, pady=2, row=0, column=0)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            pady=2, row=1, column=0, sticky="we")

        self.mcPath = tk.StringVar(
            self, self.getTimerFrame().optionsJson["mcPath"])

        tk.Label(self, text=".minecraft Path:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=2, column=0)

        pathFrame = tk.Frame(self)
        pathFrame.grid(padx=2, pady=2, row=3, column=0)

        folderbutton = "O"
        if "win" in platform:
            folderbutton = "📁"

        tk.Button(pathFrame, text=folderbutton, command=self.choosePath).grid(padx=2, pady=2,
                                                                              row=0, column=0, sticky="w")
        tk.Entry(pathFrame, textvariable=self.mcPath,
                 width=30).grid(padx=2, pady=2, row=0, column=1, sticky="w")

        self.keyPause = tk.StringVar(self)
        self.keyPause.set(
            self.getTimerFrame().optionsJson["keybinds"]["pause"])
        self.keyReset = tk.StringVar(self)
        self.keyReset.set(
            self.getTimerFrame().optionsJson["keybinds"]["reset"])

        self.settingKey = False

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            pady=2, row=4, column=0, sticky="we")

        attemptsFrame = tk.Frame(self)
        attemptsFrame.grid(padx=2, pady=2, row=5, column=0)

        tk.Label(attemptsFrame, text="Attempts:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=0, row=0, column=0)

        self.oldAttempts = self.getTimerFrame().attempts

        self.attemptsEntry = IntEntry(attemptsFrame)
        self.attemptsEntry.configure(width=8)
        self.attemptsEntry.grid(padx=2, pady=0, row=0, column=1)
        self.attemptsEntry.insert(0, str(self.oldAttempts))

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            pady=2, row=6, column=0, sticky="we")

        tk.Label(self, text="Keybinds:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=7, column=0)

        self.keyPauseButton = tk.Button(
            self, text="Pause/Continue: "+self.keyPause.get(), width=29, command=self.setKeyPause)
        self.keyPauseButton.grid(padx=2, pady=2, row=8, column=0)
        self.keyResetButton = tk.Button(
            self, text="Reset: "+self.keyReset.get(), width=29, command=self.setKeyReset)
        self.keyResetButton.grid(padx=2, pady=2, row=9, column=0)

        self.after(0, self.loop)

    def loop(self):
        self.after(100, self.loop)
        self.getTimerFrame().attempts = 0 if self.attemptsEntry.get(
        ) == "" else int(self.attemptsEntry.get())

    def setKeyPause(self):
        if not self.settingKey:
            self.settingKey = True
            key = readKey(5)
            if key != None:
                self.keyPause.set(key)
                self.keyPauseButton.config(text="Pause/Continue: "+key)
            self.settingKey = False

    def setKeyReset(self):
        if not self.settingKey:
            self.settingKey = True
            key = readKey(5)
            if key != None:
                self.keyReset.set(key)
                self.keyResetButton.config(text="Reset: "+key)
            self.settingKey = False

    def choosePath(self):
        response = tkFileDialog.askdirectory()
        if response != "":
            self.mcPath.set(response+"/")

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class DisplaySettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        tk.Label(self, text="Display Settings", font=tkFont.Font(
            self, font=("Arial", 15))).grid(padx=2, pady=2, row=0, column=0)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            pady=2, row=1, column=0, sticky="we")

        tk.Label(self, text="Font:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=2, column=0)

        self.fontOptions = FontOptions(self)
        self.fontOptions.grid(padx=2, pady=2, row=3, column=0)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            pady=2, row=4, column=0, sticky="we")

        tk.Label(self, text="Color (Font, Background):", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=5, column=0)

        self.colorOptions = ColorOptions(self)
        self.colorOptions.grid(padx=2, pady=2, row=6, column=0)

        ttk.Separator(self, orient=tk.HORIZONTAL).grid(
            pady=2, row=7, column=0, sticky="we")

        tk.Label(self, text="Sizes/Prefixes:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=8, column=0)

        display = self.getTimerFrame().optionsJson["display"]

        self.RTA = TextOption(
            self, "RTA", display["rta"]["size"], display["rta"]["prefix"])
        self.RTA.grid(padx=2, pady=2, row=9, column=0, sticky="e")

        self.IGT = TextOption(
            self, "IGT", display["igt"]["size"], display["igt"]["prefix"])
        self.IGT.grid(padx=2, pady=2, row=10, column=0, sticky="e")

        self.AttemptCounter = TextOption(
            self, "Attempts", display["attemptCounter"]["size"], display["attemptCounter"]["prefix"])
        self.AttemptCounter.grid(padx=2, pady=2, row=11, column=0, sticky="e")

        self.after(0, self.loop)

    def getTimerFrame(self):
        return self.parent.getTimerFrame()

    def toInt(self, x):
        return 0 if x == "" else int(x)

    def loop(self):
        self.getTimerFrame().changeDisplay(displayJson={
            "font": self.fontOptions.fontName.get(),
            "fontColour": self.colorOptions.color1,
            "bgColour": self.colorOptions.color2,
            "rta": {
                "size": self.RTA.size.get(),
                "prefix": self.RTA.prefix.get()
            },
            "igt": {
                "size": self.IGT.size.get(),
                "prefix": self.IGT.prefix.get()
            },
            "attemptCounter": {
                "size": self.AttemptCounter.size.get(),
                "prefix": self.AttemptCounter.prefix.get()
            }
        })
        self.after(200, self.loop)


class TextOption(tk.Frame):
    def __init__(self, parent, textName="RTA", defaultSize="50", defaultPrefix=""):
        tk.Frame.__init__(self, parent)
        tk.Label(self, text=textName+": ").grid(padx=2,
                                                pady=2, row=0, column=0)
        self.size = IntEntry(self, max=100)
        self.size.grid(padx=2, pady=2, row=0, column=1, sticky="w")
        self.size.config(width=3)
        self.size.insert(0, defaultSize)
        self.prefix = tk.Entry(self, width=18)
        self.prefix.grid(
            padx=2, pady=2, row=0, column=2, sticky="w")
        self.prefix.insert(0, defaultPrefix)

    def get(self):
        return {
            "size": self.size.get(),
            "prefix": self.prefix.get()
        }

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class FontOptions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        display = self.getTimerFrame().optionsJson["display"]

        self.fontName = tk.StringVar(self, value=display["font"])
        tk.Button(self, text="Open List", command=self.openFontList, width=7).grid(padx=2, pady=2,
                                                                                   row=0, column=0, sticky="w")
        tk.Entry(self, textvariable=self.fontName, width=22).grid(padx=2, pady=2,
                                                                  row=0, column=1, sticky="w")

    def openFontList(self):
        filename = "AMCTfonts.html"
        with open(filename, "w") as fontfile:
            fontfile.write("<!DOCTYPE html><html><body>")
            for i in tk.font.families(self):
                fontfile.write("<p>"+i+"</p>")
            fontfile.write("</body></html>")
            fontfile.close()

        webbrowser.open(getcwd()+"/"+filename)

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class ColorOptions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        display = self.getTimerFrame().optionsJson["display"]

        self.button1 = tk.Button(self, width=13, command=self.chooseColour1)
        self.button2 = tk.Button(self, width=13, command=self.chooseColour2)
        self.button1.grid(padx=2, pady=2, row=0, column=0)
        self.button2.grid(padx=2, pady=2, row=0, column=1)

        self.color1 = display["fontColour"]
        self.color2 = display["bgColour"]

        self.button1.configure(bg=self.color1)
        self.button2.configure(bg=self.color2)

    def chooseColour1(self):
        self.color1 = tk.colorchooser.askcolor(self.color1)[1]
        self.button1.configure(bg=self.color1)
        self.focus()

    def chooseColour2(self):
        self.color2 = tk.colorchooser.askcolor(self.color2)[1]
        self.button2.configure(bg=self.color2)
        self.focus()

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class IntEntry(tk.Entry):
    def __init__(self, parent, max=maxsize):
        self.max = max
        self.parent = parent
        vcmd = (self.parent.register(self.validateInt),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        tk.Entry.__init__(self, parent, validate='key', validatecommand=vcmd)

    def validateInt(self, action, index, value_if_allowed,
                    prior_value, text, validation_type, trigger_type, widget_name):
        if value_if_allowed == "":
            return True
        if value_if_allowed:
            try:
                if (len(value_if_allowed) > 1 and value_if_allowed[0] == "0") or (int(value_if_allowed) > self.max):
                    return False
                return True
            except ValueError:
                return False
        else:
            return False


if __name__ == "__main__":
    root = tk.Tk()

    try:
        import keyboard
    except:
        if tk.messagebox.askokcancel("AutoMCTimer: Required Module", "Install keyboard module? This module is required to run AutoMCTimer."):
            system('python3 -m pip install keyboard')
            system('python -m pip install keyboard')
            import keyboard
        else:
            exit()

    try:
        import mouse
    except:
        if tk.messagebox.askokcancel("AutoMCTimer: Required Module", "Install mouse module? This module is required to run AutoMCTimer."):
            system('python3 -m pip install mouse')
            system('python -m pip install mouse')
            import mouse
        else:
            exit()

    root.title("AutoMCTimer "+amctVersion)
    root.attributes("-topmost", True)
    timer = AutoMCTimer(root)
    timer.grid(padx=2, pady=2, row=0, column=0, sticky="w")
    root.mainloop()
