import tkinter as tk
import tkinter.colorchooser as tkColorChooser
from sys import maxsize


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


class ColorEntry(tk.Button):
    def __init__(self, parent, color):
        tk.Button.__init__(self, parent, width=3, text="",
                           bg=color, command=self.press)
        self.changing = False
        self.color = color
        self.parent = parent

    def press(self, x=0):
        if not self.changing:
            self.changing = True
            chosen = tkColorChooser.askcolor(self.color)[1]
            self.changing = False

            if chosen != None:
                self.color = chosen
                self.config(bg=chosen)
            
            self.parent.focus()

    def get(self):
        return self.color