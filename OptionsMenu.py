import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox
import os

class OptionsMenu(tk.Toplevel):
    def __init__(self, timerApp=None):
        tk.Toplevel.__init__(self,timerApp)
        self.timerApp = timerApp
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.wm_attributes("-topmost",1)
        tk.Label(self,text=f"\n\nOptions menu is currently unavailable,\nyou can change the options at\n{os.path.join(timerApp.path,'default.json')}\n\n\n\n").pack()
    
    def exit(self):
        self.timerApp.optionsMenu = None
        self.destroy()