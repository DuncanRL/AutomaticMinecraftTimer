import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox
import os
from Element import *
from Entry import *

def resource_path(relative_path):
    try:
        from sys import _MEIPASS
        base_path = _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class OptionsMenu(tk.Toplevel):
    def __init__(self, timerApp=None):
        tk.Toplevel.__init__(self, timerApp)
        self.geometry(
            f"+{str(timerApp.winfo_width()+timerApp.winfo_x()+10)}+{str(timerApp.winfo_y())}")
        self.timerApp = timerApp
        self.iconbitmap(resource_path("Icon.ico"))
        self.title("AutoMCTimer: Options Menu")
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.wm_attributes("-topmost", 1)
        self.timerApp.keybindManager.stop()
        #tk.Label(self,text="\n\nOptions menu still not here but I did a lot of the work to make it possible :)\n\n").pack()

        self.oldOptions = {
            "settingsVersion": 0,
            "keybinds": timerApp.keybinds,
            "elements": [i.toDict() for i in timerApp.elements],
            "windowSize": [timerApp.winfo_width(), timerApp.winfo_height()],
            "background": timerApp.bg,
            "attempts": timerApp.timer.getAttempts(),
            "mcPath": timerApp.mcPath
        }

        self.elementFrame = tk.LabelFrame(self)
        self.elementFrame.grid(row=0, column=1, padx=5, pady=5, sticky="nw")

        self.leftSide = tk.Frame(self)
        self.leftSide.grid(row=0, column=0, sticky="nw")

        self.profileChanger = ProfileChanger(self.leftSide, self)
        self.profileChanger.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        tk.Label(self.elementFrame, text="Elements", font=tkFont.Font(self, font=("Arial", 15))).grid(
            row=0, column=0, padx=5, pady=5, sticky="w")

        tk.Label(self.elementFrame, text="Add:", font=tkFont.Font(self, font=("Arial", 10))).grid(
            row=1, column=0, padx=5, pady=5, sticky="w")

        self.addElementFrame = tk.Frame(self.elementFrame)
        self.addElementFrame.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "rta"), text=timerApp.translation["rta"]).grid(row=0, column=0, sticky="NESW")
        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "igt"), text=timerApp.translation["igt"]).grid(row=1, column=0, sticky="NESW")
        tk.Button(self.addElementFrame, command=lambda: self.elementList.add(
            "attempts"), text=timerApp.translation["attempts"]).grid(row=2, column=0, sticky="NESW")

        tk.Label(self.elementFrame, text="Current Elements:", font=tkFont.Font(self, font=("Arial", 10))).grid(
            row=3, column=0, padx=5, pady=5, sticky="w")
        self.elementList = ElementList(self.elementFrame, self)
        self.elementList.grid(row=4, column=0, padx=5, pady=5, sticky="w")

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
                self.timerApp.saveOptions()
            else:
                self.timerApp.loadOptions(self.oldOptions)
            self.timerApp.optionsMenu = None
            self.destroy()

        return ans


class ProfileChanger(tk.LabelFrame):
    def __init__(self, parent, optionsMenu=None):
        if optionsMenu is None:
            optionsMenu = parent
        self.optionsMenu = optionsMenu
        tk.LabelFrame.__init__(self, parent)
        selectedProfile = self.getProfile()
        tk.Label(self, text="Selected Profile:\n"+selectedProfile, font=tkFont.Font(
            self, font=("Arial", 15))).grid(row=0, column=0, padx=5, pady=5)

        tk.Label(self, text="Change/Create Profile:").grid(
            row=1, column=0, padx=5, pady=5)

        self.entryFrame = tk.Frame(self)
        self.entryFrame.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.entry = tk.Entry(self.entryFrame, width=20)
        self.entry.grid(row=0, column=0)

        tk.Button(self.entryFrame, text="AutoFill", command=self.autoFill).grid(
            row=0, column=1)

        tk.Button(self.entryFrame, text="Select", command=self.select).grid(
            row=0, column=2)

    def getProfile(self):
        selectFilePath = os.path.join(
            self.optionsMenu.timerApp.path, "selected.txt")
        with open(selectFilePath, "r") as selectFile:
            ans = selectFile.read().rstrip()
            selectFile.close()
        return ans

    def autoFill(self):
        words = [i.lower() for i in self.entry.get().rstrip().split()]
        for profile in [i[:-5] for i in os.listdir(self.optionsMenu.timerApp.path) if i[-5:] == ".json"]:
            success = True
            for word in words:
                if word not in profile.lower():
                    success = False
                    break
            if success:
                self.entry.delete(0, 'end')
                self.entry.insert(0, profile)
                break

    def select(self):
        selectFilePath = os.path.join(
            self.optionsMenu.timerApp.path, "selected.txt")
        newProfile = self.entry.get().rstrip()

        if newProfile != "":
            ans = self.optionsMenu.exit()

            if ans is not None:
                print("Changing")
                with open(selectFilePath, "w+") as selectFile:
                    selectFile.write(newProfile)
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


'''
TODO:
- Background Color
- Attempts Counter
- Minecraft Path
- Keybinds
'''
