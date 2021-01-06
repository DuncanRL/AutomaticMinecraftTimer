from threading import Thread
import tkinter as tk
import time
import tkinter.font as tkFont
import tkinter.colorchooser as tkColorChooser
import tkinter.filedialog as tkFileDialog
from sys import maxsize, platform
import webbrowser
from os import getcwd, mkdir, system, listdir
from os.path import expanduser, isfile, isdir, getmtime
import json
import tkinter.messagebox

amctVersion = "v1.4"


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

        try:
            parent.iconbitmap("AutoMCTimer.exe")
        except:
            print("Failed to load icon")

        self.startTime = 0
        self.addedTime = 0
        self.isRunning = False
        self.isWaiting = False

        self.parent = parent
        self.dataPath = dataPath

        self.rtaFont = tk.font.Font(self, ("DS-Digital", 50))
        self.igtFont = tk.font.Font(self, ("DS-Digital", 30))

        self.rtaText = tk.StringVar(self)
        self.igtText = tk.StringVar(self)
        self.rtaText.set("0:00.000")
        self.igtText.set("IGT: 0:00.000")

        self.rtaTimer = tk.Label(
            self, textvariable=self.rtaText, font=self.rtaFont, width=20, anchor="w")
        self.igtTimer = tk.Label(
            self, textvariable=self.igtText, font=self.igtFont, width=20, anchor="w")

        self.rtaTimer.grid(row=0, column=0, sticky="w")
        self.igtTimer.grid(row=1, column=0, sticky="w")

        self.optionsMenu = None

        parent.protocol("WM_DELETE_WINDOW", self.exit)
        parent.bind("<Escape>", self.openOptionMenu)

        self.optionsJson = None
        self.loadOptions()

        startw = self.optionsJson["windowSize"][0]
        starth = self.optionsJson["windowSize"][1]

        self.parent.geometry(str(startw)+"x"+str(starth))

        self.loadKeys()

        self.parent.focus()

        self.after(0, self.loop)
        self.after(0, self.rtaUpdate)

        if self.optionsJson["welcomeMessage"]:

            self.update()

            tk.messagebox.askokcancel("AutoMCTimer: Welcome", "Welcome!\nPress escape with the timer open to access the options." + (
                "\n\nSince you are on linux, please set your .minecraft installation directory." if "linux" in platform else ""))

            self.optionsJson["welcomeMessage"] = False

            if "linux" in platform:
                self.openOptionMenu(1)
        
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
        self.after(10, self.rtaUpdate)
        if self.isRunning:
            self.rtaText.set(self.convertSeconds(
                time.time() - self.startTime + self.addedTime))
        else:
            self.rtaText.set(self.convertSeconds(self.addedTime))

    def loop(self):
        self.after(500, self.loop)

        igt = self.getIGT()
        self.igtText.set("IGT: " + self.convertSeconds(igt))

        if igt == 0 and not self.isWaiting:
            print("YEP WORLD")
            self.isRunning = False
            self.addedTime = 0
            self.isWaiting = True
            self.after(10, self.startWorld)

    def startWorld(self):
        igt = self.getIGT()
        if igt != 0.0:
            self.isRunning = True
            self.addedTime = 0
            self.startTime = time.time()
            self.isWaiting = False
        else:
            self.after(10, self.startWorld)

    def setKeys(self, pauseKey, resetKey,):
        pass

    @staticmethod
    def validateOptionsJson(optionsJson):
        vv = AutoMCTimer._validateValue
        defaultPath = getcwd()
        if "win" in platform:
            defaultPath = expanduser("~/AppData/Roaming/.minecraft/")
        vv(optionsJson, "mcPath", defaultPath)
        vv(optionsJson, "welcomeMessage", True)
        vv(optionsJson, "windowSize", [500, 150])
        keybinds = vv(optionsJson, "keybinds", {})
        vv(keybinds, "pause", "\\")
        vv(keybinds, "reset", "]")
        display = vv(optionsJson, "display", {})
        vv(display, "font", "Arial")
        vv(display, "size1", 50)
        vv(display, "size2", 30)
        vv(display, "fontColour", "#ffffff")
        vv(display, "bgColour", "#000000")

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
                self.saveSize()
                self.parent.destroy()
        else:
            self.saveSize()
            self.parent.destroy()

    def saveSize(self):
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
                pass
            with open(self.dataPath+"options.json", "w+") as optionsFile:
                self.optionsJson = {'display': {'font': 'Arial', 'size1': 50,
                                                'size2': 30, 'fontColour': '#ffffff', 'bgColour': '#000000'}}
                json.dump(self.optionsJson, optionsFile, indent=4)
                optionsFile.close()

        self.validateOptionsJson(self.optionsJson)

        display = self.optionsJson["display"]

        self.changeDisplay(display["font"], display["size1"],
                           display["size2"], display["fontColour"], display["bgColour"])

    def saveOptions(self, optionsJson):
        self.optionsJson = optionsJson
        self.validateOptionsJson(self.optionsJson)
        with open(self.dataPath+"options.json", "w+") as optionsFile:
            optionsFile.write(json.dumps(optionsJson, indent=4))
            optionsFile.close()

    def openOptionMenu(self, x):
        if self.optionsMenu == None or not self.optionsMenu.winfo_exists():
            self.unloadKeys()
            self.optionsMenu = OptionsMenu(self)

    def changeDisplay(self, fontName=None, fontSize1=None, fontSize2=None, fontColour=None, bgColour=None):
        if fontName != None:
            for timerFont in [self.rtaFont, self.igtFont]:
                timerFont.config(family=fontName)
        if fontSize1 != None:
            self.rtaFont.config(size=fontSize1)
        if fontSize2 != None:
            self.igtFont.config(size=fontSize2)
        if fontColour != None:
            for timerLabel in [self.rtaTimer, self.igtTimer]:
                timerLabel.config(fg=fontColour)
        if bgColour != None:
            for timerLabel in [self.rtaTimer, self.igtTimer]:
                timerLabel.config(bg=bgColour)
            self.config(bg=bgColour)
            self.parent.config(bg=bgColour)

    def getTimerFrame(self):
        return self


class OptionsMenu(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        try:
            self.iconbitmap("AutoMCTimer.exe")
        except:
            print("Failed to load icon")
        self.wm_resizable(False, False)
        self.parent = parent
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
        fontOptions = self.optionsMenuFrame.displaySettings.fontOptions
        colorOptions = self.optionsMenuFrame.displaySettings.colorOptions
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
                    "size1": fontOptions.size1.get(),
                    "size2": fontOptions.size2.get(),
                    "fontColour": colorOptions.color1,
                    "bgColour": colorOptions.color2
                }
            }
        )
        self.destroy()
        self.getTimerFrame().loadKeys()

    def exitWithoutSave(self):
        self.getTimerFrame().loadOptions()
        self.destroy()
        self.getTimerFrame().loadKeys()

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class OptionsMenuFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        exitButtonsFrame = tk.Frame(self)
        exitButtonsFrame.grid(row=100, column=0, pady=5, padx=5)

        exitButton = tk.Button(
            exitButtonsFrame, text="Apply", command=parent.saveAndExit)
        exitButton.grid(row=0, column=0, sticky="w", pady=0, padx=5)

        exitButton = tk.Button(
            exitButtonsFrame, text="Cancel", command=parent.exitWithoutSave)
        exitButton.grid(row=0, column=1, sticky="w", pady=0, padx=5)

        self.generalSettings = GeneralSettings(self)
        self.generalSettings.config(highlightthickness=1,
                                    highlightbackground="black")
        self.generalSettings.grid(row=1, column=0, sticky="w", pady=5, padx=5)

        self.displaySettings = DisplaySettings(self)
        self.displaySettings.config(highlightthickness=1,
                                    highlightbackground="black")
        self.displaySettings.grid(row=2, column=0, sticky="w", pady=5, padx=5)

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class GeneralSettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        tk.Label(self, text="General Settings", font=tkFont.Font(
            self, font=("Arial", 15))).grid(padx=2, pady=2, row=0, column=0, sticky="w")
        self.mcPath = tk.StringVar(
            self, self.getTimerFrame().optionsJson["mcPath"])

        tk.Label(self, text=".minecraft Path:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=1, column=0, sticky="w")

        pathFrame = tk.Frame(self)
        pathFrame.grid(padx=2, pady=2, row=2, column=0)

        self.keyPause = tk.StringVar(self)
        self.keyPause.set(
            self.getTimerFrame().optionsJson["keybinds"]["pause"])
        self.keyReset = tk.StringVar(self)
        self.keyReset.set(
            self.getTimerFrame().optionsJson["keybinds"]["reset"])

        self.settingKey = False

        tk.Label(self, text="Keybinds:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=3, column=0, sticky="w")

        self.keyPauseButton = tk.Button(
            self, text="Pause/Continue: "+self.keyPause.get(), width=29, command=self.setKeyPause)
        self.keyPauseButton.grid(padx=2, pady=2, row=4, column=0, sticky="w")
        self.keyResetButton = tk.Button(
            self, text="Reset: "+self.keyReset.get(), width=29, command=self.setKeyReset)
        self.keyResetButton.grid(padx=2, pady=2, row=5, column=0, sticky="w")

        folderbutton = "O"
        if "win" in platform:
            folderbutton = "📁"

        tk.Button(pathFrame, text=folderbutton, command=self.choosePath).grid(padx=2, pady=2,
                                                                              row=0, column=0, sticky="w")
        tk.Entry(pathFrame, textvariable=self.mcPath,
                 width=30).grid(padx=2, pady=2, row=0, column=1, sticky="w")

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
            self, font=("Arial", 15))).grid(padx=2, pady=2, row=0, column=0, sticky="w")
        tk.Label(self, text="Font:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=1, column=0, sticky="w")

        self.fontOptions = FontOptions(self)
        self.fontOptions.grid(padx=2, pady=2, row=2, column=0, sticky="w")

        tk.Label(self, text="Color (Font, Background):", font=tkFont.Font(
            self, font=("Arial", 12))).grid(padx=2, pady=2, row=3, column=0, sticky="w")

        self.colorOptions = ColorOptions(self)
        self.colorOptions.grid(padx=2, pady=2, row=4, column=0, sticky="w")

        self.lastFont = ""
        self.after(0, self.loop)

    def getTimerFrame(self):
        return self.parent.getTimerFrame()

    def toInt(self, x):
        return 0 if x == "" else int(x)

    def loop(self):
        self.getTimerFrame().changeDisplay(fontName=self.fontOptions.fontName.get().rstrip(), fontSize1=self.toInt(self.fontOptions.size1.get()),
                                           fontSize2=self.toInt(self.fontOptions.size2.get()), fontColour=self.colorOptions.color1, bgColour=self.colorOptions.color2)

        self.after(200, self.loop)


class FontOptions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        display = self.getTimerFrame().optionsJson["display"]

        self.fontName = tk.StringVar(self, value=display["font"])
        tk.Button(self, text="Open List", command=self.openFontList, width=7).grid(padx=2, pady=2,
                                                                                   row=0, column=0, sticky="w")
        tk.Entry(self, textvariable=self.fontName, width=15).grid(padx=2, pady=2,
                                                                  row=0, column=1, sticky="w")

        self.size1 = IntEntry(self, 100)
        self.size1.config(width=3)
        self.size1.grid(padx=2, pady=2, row=0, column=2)
        self.size1.insert(0, str(display["size1"]))

        self.size2 = IntEntry(self, 100)
        self.size2.config(width=3)
        self.size2.insert(0, str(display["size2"]))
        self.size2.grid(padx=2, pady=2, row=0, column=3)

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
