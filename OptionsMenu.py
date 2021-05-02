import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
import tkinter.simpledialog as tkSimpleDialog
from tkinter import ttk
import os
from Element import *
from Entry import *
import webbrowser

hotkeyText = '''Possible Hotkeys (Comma Seperated):

0,1,2...
a,b,c...
numpad_0,numpad_1,numpad_2...
f1,f2,f3...

+, -, ., /, `, ;, [, \, ], ', `

backspace, tab, clear, enter, shift, control, alt, pause, caps_lock, escape, space, page_up, page_down, end, home, left, up, right, down, select, print, execute, enter, print_screen, insert, delete, help
multiply_key, add_key, separator_key, subtract_key, decimal_key, divide_key, num_lock, scroll_lock, left_shift, right_shift,  left_control, right_control, left_menu, right_menu, browser_back, browser_forward, browser_refresh, browser_stop, browser_search, browser_favorites, browser_start_and_home, volume_mute, volume_Down, volume_up, next_track, previous_track, stop_media, play/pause_media, start_mail, select_media, start_application_1, start_application_2, attn_key, crsel_key, exsel_key, play_key, zoom_key, clear_key

(you can also use "," for the comma itself)'''


def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class OptionsMenu(tk.Toplevel):
    def __init__(self, timerApp=None):
        self.makeHotkeyList()
        tk.Toplevel.__init__(self, timerApp)
        self.resizable(0, 0)
        self.timerApp = timerApp
        self.reposition()
        self.iconbitmap(resource_path("Icon.ico"))
        self.title("AutoMCTimer: Options Menu")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.wm_attributes("-topmost", 1)
        self.timerApp.keybindManager.stop()

        self.oldOptions = {
            "settingsVersion": 0,
            "keybinds": timerApp.keybinds,
            "elements": [i.toDict() for i in timerApp.elements],
            "windowSize": [timerApp.winfo_width(), timerApp.winfo_height()],
            "background": timerApp.bg,
            "attempts": timerApp.timer.getAttempts(),
            "mcPath": timerApp.mcPath,
            "auto": timerApp.doesAuto
        }

        self.elementFrame = tk.LabelFrame(self)
        self.elementFrame.grid(row=1, column=1, padx=5, pady=5, sticky="nw")

        self.leftSide = tk.Frame(self)
        self.leftSide.grid(row=1, column=0, sticky="nw")

        self.profileChanger = ProfileChanger(self, self)
        self.profileChanger.grid(
            row=0, column=0, padx=5, pady=5, columnspan=2, sticky="")

        tk.Label(self.elementFrame, text="Elements", font=tkFont.Font(self, font=("Arial", 15))).grid(
            row=0, column=0, padx=5, pady=5)

        tk.Label(self.elementFrame, text="Add:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w")

        self.addElementFrame = tk.Frame(self.elementFrame)
        self.addElementFrame.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "rta"), text=timerApp.translation["rta"]).grid(row=0, column=0, sticky="NESW")
        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "igt"), text=timerApp.translation["igt"]).grid(row=1, column=0, sticky="NESW")
        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "attempts"), text=timerApp.translation["attempts"]).grid(row=2, column=0, sticky="NESW")
        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "endermen"), text=timerApp.translation["endermen"]).grid(row=3, column=0, sticky="NESW")
        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "blaze"), text=timerApp.translation["blaze"]).grid(row=4, column=0, sticky="NESW")
        #Goodbye forever level.dat Time
        #tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
        #    "glitchigt"), text=timerApp.translation["glitchigt"]).grid(row=5, column=0, sticky="NESW")

        tk.Label(self.elementFrame, text="Current Elements:", font=tkFont.Font(self, font=("Arial", 10))).grid(
            row=3, column=0, padx=5, pady=5, sticky="w")
        self.elementList = ElementList(self.elementFrame, self)
        self.elementList.grid(row=4, column=0, padx=5, pady=5, sticky="w")

        self.keybinds = KeybindOptions(self.leftSide, self)
        self.keybinds.grid(row=1, column=0, padx=5, pady=5)

        self.otherOptions = tk.LabelFrame(self.leftSide, width=232)
        self.otherOptions.grid(row=2, column=0, padx=5, pady=5)
        self.update()

        tk.Canvas(self.otherOptions, width=232-8,
                  height=0).grid(row=0, column=0)

        tk.Label(self.otherOptions, text="Other Options", font=tkFont.Font(
            self, font=("Arial", 15))).grid(row=1, column=0, padx=5, pady=5)

        for i in range(4):
            ttk.Separator(self.otherOptions, orient="horizontal").grid(
                row=10*i+5, column=0, sticky='we')

        self.bgFrame = tk.Frame(self.otherOptions)
        self.bgFrame.grid(row=10, column=0, sticky="w")

        tk.Label(self.bgFrame, text="Background Colour:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")

        self.bgEntry = ColorEntry(
            self.bgFrame, self.oldOptions["background"])
        self.bgEntry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.bgEntry.addChangeCall(self.changeBackground)

        self.attemptsFrame = tk.Frame(self.otherOptions)
        self.attemptsFrame.grid(row=20, column=0, sticky="w")

        tk.Label(self.attemptsFrame, text="Attempts:").grid(
            row=0, column=0, padx=5, pady=5)

        self.attemptsEntry = IntEntry(self.attemptsFrame)
        self.attemptsEntry.grid(row=0, column=1, padx=5, pady=5)
        self.attemptsEntry.config(width=6)
        self.attemptsEntry.insert(0, str(self.oldOptions["attempts"]))

        tk.Button(self.attemptsFrame, text="Set", command=self.setAttempts).grid(
            row=0, column=2, padx=5, pady=5)

        self.pathFrame = tk.Frame(self.otherOptions)
        self.pathFrame.grid(row=30, column=0, sticky="w")

        self.lowerPathFrame = tk.Frame(self.pathFrame)
        self.lowerPathFrame.grid(row=1, column=0, sticky="w")

        tk.Label(self.pathFrame, text=".minecraft Path:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Button(self.lowerPathFrame, command=self.setPath, text="📁").grid(
            row=0, column=0, padx=5, pady=5)
        self.pathLabel = tk.Label(
            self.lowerPathFrame, text=self.oldOptions["mcPath"], width=25, anchor="e")
        self.pathLabel.grid(row=0, column=1, padx=5, pady=5)

        self.autoFrame = tk.Frame(self.otherOptions)
        self.autoFrame.grid(row=40, column=0, sticky="w")

        tk.Label(self.autoFrame, text="Automatically start timer \nwhen creating new world").grid(
            row=0, column=1,padx=5,pady=5)
        self.autoSwitchButton = tk.Button(
            self.autoFrame, text="✅" if self.timerApp.doesAuto else "❎", command=self.autoSwitch)
        self.autoSwitchButton.grid(row=0, column=0,padx=5,pady=5)

    def autoSwitch(self):
        self.timerApp.doesAuto = not self.timerApp.doesAuto
        self.timerApp.timer.doesAuto = self.timerApp.doesAuto
        self.autoSwitchButton.config(text="✅" if self.timerApp.doesAuto else "❎")

    def makeHotkeyList(self):
        with open(resource_path("hotkeys.html"), "w+") as site:
            site.write("<!DOCTYPE html><html><body><p>" +
                       hotkeyText.replace("\n", "<br>")+"</p></body></html>")
            site.close()

    def openHotkeyList(self):
        webbrowser.open(
            "file:///"+resource_path("hotkeys.html").replace("\\", "/"))

    def reposition(self):
        self.geometry(
            f"+{str(self.timerApp.winfo_width()+self.timerApp.winfo_x()+10)}+{str(self.timerApp.winfo_y())}")

    def setPath(self):
        ans = tkFileDialog.askdirectory()
        if ans is not None and ans != "":
            self.timerApp.timer.updatePath(ans)
            self.timerApp.mcPath = ans
            self.pathLabel.config(text=ans)

    def setAttempts(self):
        num = int(self.attemptsEntry.get())
        self.timerApp.timer.setAttempts(num)

    def changeBackground(self):
        bg = self.bgEntry.get()
        self.timerApp.bg = bg
        self.timerApp.config(bg=bg)

        for i in self.timerApp.elements:
            i.updateDisplay()

    def refresh(self):
        self.elementList.refresh()

    def exit(self, ans=None):

        for i in self.timerApp.elements:
            if i.editor is not None:
                i.editor.cancel()
        if ans == None:
            ans = tkMessageBox.askyesnocancel("AMCT: Save?", "Save options?")

        if ans is not None:
            if ans:
                self.timerApp.keybinds = self.keybinds.get()
                self.timerApp.saveOptions()
            else:
                self.timerApp.loadOptions(self.oldOptions)
            self.timerApp.optionsMenu = None
            self.timerApp.rebind()
            self.destroy()

        return ans


class KeybindOptions(tk.LabelFrame):
    def __init__(self, parent, optionsMenu=None):
        if optionsMenu is None:
            optionsMenu = parent
        self.optionsMenu = optionsMenu
        tk.LabelFrame.__init__(self, parent)

        tk.Canvas(self, width=232-8, height=0).grid(row=0, column=0)

        tk.Label(self, text="Keybinds", font=tkFont.Font(
            self, font=("Arial", 15))).grid(row=1, column=0, padx=5, pady=5)

        self.pause = KeybindOption(
            self, optionsMenu.oldOptions["keybinds"]["pause"])
        self.reset = KeybindOption(
            self, optionsMenu.oldOptions["keybinds"]["reset"])

        self.pause.grid(row=10, column=0, padx=5, pady=5, sticky="w")
        self.reset.grid(row=20, column=0, padx=5, pady=5, sticky="w")

        tk.Label(self, text="Start/Pause:").grid(row=5, column=0, sticky="w")
        tk.Label(self, text="Reset:").grid(row=15, column=0, sticky="w")
        tk.Button(self, text="Available Keybinds", command=optionsMenu.openHotkeyList).grid(
            row=100, column=0, sticky="w", padx=5, pady=5)

    def get(self):
        return {
            "pause": self.pause.get(),
            "reset": self.reset.get()
        }


class KeybindOption(tk.Frame):
    def __init__(self, parent, default=["\\"]):
        tk.Frame.__init__(self, parent)

        self.availableKeys = ['backspace', 'tab', 'clear', 'enter', 'shift', 'control', 'alt', 'pause', 'caps_lock', 'escape', 'space', ' ', 'page_up', 'page_down', 'end', 'home', 'left', 'up', 'right', 'down', 'select', 'print', 'execute',  'enter', 'print_screen', 'insert', 'delete', 'help', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'numpad_0', 'numpad_1', 'numpad_2', 'numpad_3', 'numpad_4', 'numpad_5', 'numpad_6', 'numpad_7', 'numpad_8', 'numpad_9', 'multiply_key', 'add_key', 'separator_key', '|', 'subtract_key', 'decimal_key', 'divide_key', 'f1', 'f2', 'f3', 'f4',
                              'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f20', 'f21', 'f22', 'f23', 'f24', 'num_lock', 'scroll_lock', 'left_shift', 'right_shift', 'left_control', 'right_control', 'left_menu', 'right_menu', 'browser_back', 'browser_forward', 'browser_refresh', 'browser_stop', 'browser_search', 'browser_favorites', 'browser_start_and_home', 'volume_mute', 'volume_Down', 'volume_up', 'next_track', 'previous_track', 'stop_media', 'play/pause_media', 'start_mail', 'select_media', 'start_application_1', 'start_application_2', 'attn_key', 'crsel_key', 'exsel_key', 'play_key', 'zoom_key', 'clear_key', '+', ',', '-', '.', '/', '`', ';', '[', ']', "'", '`']

        self.control = tk.BooleanVar(self, False)
        self.shift = tk.BooleanVar(self, False)
        self.alt = tk.BooleanVar(self, False)
        for i in default[:-1]:
            if "control" == i:
                self.control.set(True)
            elif "shift" == i:
                self.shift.set(True)
            elif "alt" == i:
                self.alt.set(True)

        tk.Checkbutton(self, variable=self.control,
                       text="ctrl").grid(row=0, column=0)
        tk.Checkbutton(self, variable=self.alt,
                       text="alt").grid(row=0, column=1)
        tk.Checkbutton(self, variable=self.shift,
                       text="shift").grid(row=0, column=2)
        self.entry = tk.Entry(self, width=6)
        self.entry.insert(0, default[-1])
        self.entry.grid(row=0, column=6, padx=10)

    def get(self):
        val = []
        if self.control.get():
            val.append("control")
        if self.shift.get():
            val.append("shift")
        if self.alt.get():
            val.append("alt")

        if self.entry.get() in self.availableKeys:
            val.append(self.entry.get().rstrip())
        else:
            val.append("\\")
        return val


class ProfileChanger(tk.Frame):
    def __init__(self, parent, optionsMenu=None):
        if optionsMenu is None:
            optionsMenu = parent
        self.optionsMenu = optionsMenu
        tk.Frame.__init__(self, parent)
        selectedProfile = self.getProfile()
        tk.Label(self, text="Selected Profile:\n"+selectedProfile, font=tkFont.Font(
            self, font=("Arial", 15)), anchor="center").grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        # tk.Button(self.entryFrame, text="AutoFill", command=self.autoFill).grid(
        #    row=0, column=1)

        createFrame = tk.Frame(self)
        createFrame.grid(row=1, column=0, padx=5, pady=5)

        tk.Label(createFrame, text="Create:").grid(
            row=0, column=0, padx=5, pady=5)

        tk.Button(createFrame, text="New Profile", command=self.create).grid(
            row=1, column=0)

        self.profileList = [
            i[:-5] for i in os.listdir(self.optionsMenu.timerApp.path) if i[-5:] == ".json"]
        self.selectedForOpen = self.getProfile()

        if self.selectedForOpen not in self.profileList:
            self.profileList.append(self.selectedForOpen)

        self.selectedVariable = tk.StringVar(self, value=self.selectedForOpen)
        openFrame = tk.Frame(self)
        openFrame.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(openFrame, text="Open Profile:",
                 anchor="center").grid(row=0, column=0, padx=5, pady=5, columnspan=3, sticky="we")
        tk.Button(openFrame, textvariable=self.selectedVariable, command=self.openButton, width=10).grid(
            row=1, column=1)
        tk.Button(openFrame, text="<", command=self.previousButton).grid(
            row=1, column=0)
        tk.Button(openFrame, text=">", command=self.nextButton).grid(
            row=1, column=2)

    def getProfile(self):
        selectFilePath = os.path.join(
            self.optionsMenu.timerApp.path, "selected.txt")
        with open(selectFilePath, "r") as selectFile:
            ans = selectFile.read().rstrip()
            selectFile.close()
        return ans

    def create(self):
        selectFilePath = os.path.join(
            self.optionsMenu.timerApp.path, "selected.txt")
        newProfile = tkSimpleDialog.askstring(
            "AMCT: Create Profile", "Enter name of new profile:")

        if newProfile is not None and newProfile != "":
            newProfile = newProfile.rstrip()
            newProfilePath = os.path.join(
                self.optionsMenu.timerApp.path, newProfile+".json")
            oldProfilePath = os.path.join(
                self.optionsMenu.timerApp.path, self.getProfile()+".json")
            ans = self.optionsMenu.exit()

            if ans is not None:

                if not os.path.isfile(newProfilePath):
                    with open(oldProfilePath, "r") as profileFile:
                        copyData = profileFile.read()
                        profileFile.close()

                    with open(newProfilePath, "w+") as profileFile:
                        profileFile.write(copyData)
                        profileFile.close()

                with open(selectFilePath, "w+") as selectFile:
                    selectFile.write(newProfile)
                    selectFile.close()

            self.optionsMenu.timerApp.optionsInit()
            self.optionsMenu.timerApp.update()
            self.optionsMenu.timerApp.openOptionsMenu()

    def previousButton(self):
        self.selectedForOpen = self.profileList[self.profileList.index(
            self.selectedForOpen)-1]
        self.selectedVariable.set(self.selectedForOpen)

    def nextButton(self):
        nexti = self.profileList.index(self.selectedForOpen)+1
        if nexti >= len(self.profileList):
            nexti += -len(self.profileList)
        self.selectedForOpen = self.profileList[nexti]
        self.selectedVariable.set(self.selectedForOpen)

    def openButton(self):
        self.open(self.selectedForOpen)

    def open(self, profileName: str):
        profileName = profileName.rstrip()
        newProfilePath = os.path.join(
            self.optionsMenu.timerApp.path, profileName + ".json")
        selectFilePath = os.path.join(
            self.optionsMenu.timerApp.path, "selected.txt")
        ans = self.optionsMenu.exit()

        if ans is not None:
            with open(selectFilePath, "w+") as selectFile:
                selectFile.write(profileName)
                selectFile.close()

            self.optionsMenu.timerApp.optionsInit()
            self.optionsMenu.timerApp.update()
            self.optionsMenu.timerApp.openOptionsMenu()


class ElementList(tk.Frame):
    def __init__(self, parent, optionsMenu):
        tk.Frame.__init__(self, parent)
        self.optionsMenu = optionsMenu
        self.elementItems = []
        self.refresh()

    def refresh(self):
        for i in self.elementItems:
            i.destroy()

        row = 0
        for i in self.optionsMenu.timerApp.elements:
            ei = ElementItem(self, i, self.optionsMenu)
            ei.grid(row=row, column=0, sticky="W")
            self.elementItems.append(ei)
            row += 1

    def add(self, elementID):
        addit = True
        for i in self.optionsMenu.timerApp.elements:
            if i.type == elementID:
                addit = False
                if tkMessageBox.askyesno("AMCT: Confirm Element Add", "You already have a "+self.optionsMenu.timerApp.translation[elementID]+" element, are you sure you want to add another?") == True:
                    addit = True
                break

        if addit:
            e = Element.fromIdentifier(elementID, self.optionsMenu.timerApp)
            self.optionsMenu.timerApp.elements.append(e)
            e.edit()
            self.refresh()


class ElementItem(tk.LabelFrame):
    def __init__(self, parent, element, optionsMenu):
        tk.LabelFrame.__init__(self, parent)
        tk.Label(self, text=optionsMenu.timerApp.translation[element.type], anchor="e").grid(
            row=0, column=1, padx=5, pady=5)
        tk.Button(self, text="Edit", command=element.edit).grid(
            row=0, column=0, padx=5, pady=5)


if __name__ == "__main__":
    os.system("python AutoMCTimer.pyw")
