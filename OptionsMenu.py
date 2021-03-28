import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox
import os


class OptionsMenu(tk.Toplevel):
    def __init__(self, timerApp=None):
        tk.Toplevel.__init__(self, timerApp)
        self.timerApp = timerApp
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.wm_attributes("-topmost", 1)
        self.timerApp.keybindManager.stop()
        tk.Label(self,text="\n\nOptions menu still not here but I did a lot of the work to make it possible :)\n\n").pack()


    def exit(self):
        self.timerApp.optionsMenu = None
        self.timerApp.saveOptions()
        self.timerApp.optionsInit()
        self.destroy()


if __name__ == "__main__":
    os.system("python AutoMCTimer.pyw")
