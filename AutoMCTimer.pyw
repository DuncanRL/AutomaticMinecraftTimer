import tkinter as tk
import time
import tkinter.font as tkFont
import tkinter.colorchooser as tkColorChooser
import tkinter.filedialog as tkFileDialog
from sys import maxsize
import webbrowser
from os import getcwd, mkdir
from os.path import expanduser, isfile, isdir
import json
import tkinter.messagebox


class AutoMCTimer(tk.Frame):

    def __init__(self, parent, dataPath=expanduser(
            "~\\AppData\\Roaming\\.automctimer\\"), *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        print("Using datapath: "+dataPath)

        self.parent = parent
        self.dataPath = dataPath

        self.rtaFont = tk.font.Font(self, ("DS-Digital", 50))
        self.igtFont = tk.font.Font(self, ("DS-Digital", 30))

        self.rtaText = tk.StringVar(self)
        self.igtText = tk.StringVar(self)
        self.rtaText.set("32:22.050")
        self.igtText.set("IGT: "+"32:22.050")

        self.rtaTimer = tk.Label(
            self, textvariable=self.rtaText, font=self.rtaFont)
        self.igtTimer = tk.Label(
            self, textvariable=self.igtText, font=self.igtFont)

        self.rtaTimer.grid(row=0, column=0, sticky="w")
        self.igtTimer.grid(row=1, column=0, sticky="w")

        self.optionsMenu = None

        self.parent.protocol("WM_DELETE_WINDOW", self.exit)
        self.parent.bind("<Key>", self.openOptionMenu)

        self.optionsJson = None
        self.loadOptions()

        self.parent.focus()

        self.after(0, self.loop)

    @staticmethod
    def validateOptionsJson(optionsJson):
        vv = AutoMCTimer._validateValue
        display = vv(optionsJson, "display", {})
        vv(display, "font", "Arial")
        vv(display, "size1", 50)
        vv(display, "size2", 30)
        vv(display, "fontColour", "#ffffff")
        vv(display, "bgColour", "#000000")
        vv(optionsJson, "mcPath", expanduser(
            "~\\AppData\\Roaming\\.minecraft\\"))

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
                self.parent.destroy()
        else:
            self.parent.destroy()

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

    def loop(self):
        self.after(5, self.loop)

    def getTimerFrame(self):
        return self


class OptionsMenu(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("AutoMCTimer Options")

        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.optionsMenuFrame = OptionsMenuFrame(self)
        self.optionsMenuFrame.config(highlightthickness=10)
        self.optionsMenuFrame.grid(row=0, column=0)

        self.focus()

    def exit(self):
        response = tk.messagebox.askyesnocancel(
            "AutoMCTimer: Save", "Save Options?")
        if response != None:
            if response:
                fontOptions = self.optionsMenuFrame.displaySettings.fontOptions
                colorOptions = self.optionsMenuFrame.displaySettings.colorOptions
                gameSettings = self.optionsMenuFrame.gameSettings
                self.getTimerFrame().saveOptions(
                    {
                        "display": {
                            "font": fontOptions.fontName.get(),
                            "size1": fontOptions.size1.get(),
                            "size2": fontOptions.size2.get(),
                            "fontColour": colorOptions.color1,
                            "bgColour": colorOptions.color2
                        },
                        "mcPath": gameSettings.mcPath.get()
                    }
                )
            else:
                self.getTimerFrame().loadOptions()
            self.destroy()
        else:
            self.focus()
        return response

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class OptionsMenuFrame(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        exitButton = tk.Button(self, text="Exit", command=parent.exit)
        exitButton.grid(row=0, column=0, sticky="w")

        self.displaySettings = DisplaySettings(self)
        self.displaySettings.config(highlightthickness=1,
                                    highlightbackground="black")
        self.displaySettings.grid(row=1, column=0, sticky="w")

        self.gameSettings = GameSettings(self)
        self.gameSettings.config(highlightthickness=1,
                                 highlightbackground="black")
        self.gameSettings.grid(row=2, column=0, sticky="w")

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class GameSettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        tk.Label(self, text="Game Settings", font=tkFont.Font(
            self, font=("Arial", 15))).grid(row=0, column=0, sticky="w")
        self.mcPath = tk.StringVar(
            self, self.getTimerFrame().optionsJson["mcPath"])
        
        pathFrame = tk.Frame(self)
        pathFrame.grid(row=1,column=0)

        tk.Button(pathFrame, text="📁", command=self.choosePath).grid(
            row=0, column=0, sticky="w")
        tk.Entry(pathFrame, textvariable=self.mcPath,
                 width=30).grid(row=0, column=1, sticky="w")

    def choosePath(self):
        response = tkFileDialog.askdirectory()
        if response != "":
            self.mcPath.set(response.replace("/","\\")+"\\")

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class DisplaySettings(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        tk.Label(self, text="Display Settings", font=tkFont.Font(
            self, font=("Arial", 15))).grid(row=0, column=0, sticky="w")
        tk.Label(self, text="Font:", font=tkFont.Font(
            self, font=("Arial", 12))).grid(row=1, column=0, sticky="w")

        self.fontOptions = FontOptions(self)
        self.fontOptions.grid(row=2, column=0, sticky="w")

        tk.Label(self, text="Color (Font, Background):", font=tkFont.Font(
            self, font=("Arial", 12))).grid(row=3, column=0, sticky="w")

        self.colorOptions = ColorOptions(self)
        self.colorOptions.grid(row=4, column=0, sticky="w")

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
        tk.Button(self, text="Open List", command=self.openFontList, width=7).grid(
            row=0, column=0, sticky="w")
        tk.Entry(self, textvariable=self.fontName, width=15).grid(
            row=0, column=1, sticky="w")

        self.size1 = IntEntry(self, 100)
        self.size1.config(width=3)
        self.size1.grid(row=0, column=2)
        self.size1.insert(0, str(display["size1"]))

        self.size2 = IntEntry(self, 100)
        self.size2.config(width=3)
        self.size2.insert(0, str(display["size2"]))
        self.size2.grid(row=0, column=3)

    def openFontList(self):
        with open("AMCTfonts.txt", "w") as fontfile:
            for i in tk.font.families(self):
                fontfile.write(i+"\n")
            fontfile.close()
        webbrowser.open(getcwd()+"\\AMCTfonts.txt")

    def getTimerFrame(self):
        return self.parent.getTimerFrame()


class ColorOptions(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        display = self.getTimerFrame().optionsJson["display"]

        self.button1 = tk.Button(self, width=13, command=self.chooseColour1)
        self.button2 = tk.Button(self, width=13, command=self.chooseColour2)
        self.button1.grid(row=0, column=0)
        self.button2.grid(row=0, column=1)

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
    root.geometry("500x150")
    root.title("AutoMCTimer")
    timer = AutoMCTimer(root)
    timer.grid(row=0, column=0, sticky="w")
    root.mainloop()
