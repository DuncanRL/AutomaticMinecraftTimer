import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox

class OptionsMenu(tk.Toplevel):
    def __init__(self, timerApp=None):
        tk.Toplevel.__init__(self,timerApp)
        self.timerApp = timerApp
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.wm_attributes("-topmost",1)
    
    def exit(self):
        self.timerApp.optionsMenu = None
        self.destroy()