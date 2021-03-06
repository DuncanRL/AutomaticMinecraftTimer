import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as tkMessageBox

from Entry import *


class Element(tk.Frame):

    @staticmethod
    def fromIdentifier(id: str, timerApp):
        ids = {
            "rta": RTAElement,
            "igt": IGTElement,
            "attempts": AttemptsElement,
            "endermen": EndermenElement,
            "blaze": BlazeElement,
            "glitchigt": GlitchIGTElement,
            "text": TextElement
        }
        return ids[id](timerApp)

    def __init__(self, timerApp):
        tk.Frame.__init__(self, timerApp)
        self.isVisible = True
        self.timerApp = timerApp
        self.options = ElementOptions(self)
        self.font = tkFont.Font(self, ("Arial", 50))
        self.stringVar = tk.StringVar(self, "")
        self.label = tk.Label(self, font=self.font,
                              textvariable=self.stringVar, anchor="w")
        self.label.grid(row=0, column=0, sticky="w")
        self.updateDisplay()
        self.exists = True
        self.beingEdited = False
        self.editor = None

    def toDict(self):
        return {
            "type": self.type,
            "position": self.options.position,
            "color": self.options.color,
            "prefix": self.options.prefix,
            "font": self.options.font,
            "size": self.options.size,
            "align": self.options.align
        }

    def updateDisplay(self):
        self.font.config(family=self.options.font, size=self.options.size)
        self.label.config(fg=self.options.color, bg=self.timerApp.bg)
        self.updatePosition()

    def updatePosition(self):
        if self.isVisible:
            pos = self.options.position
            align = self.options.align
            self.place(x=pos[0], y=pos[1], anchor="n"+align)
        else:
            self.place_forget()

    def edit(self):
        self.timerApp.optionsMenu.withdraw()
        return ElementEditor(self)

    def remove(self):
        self.destroy()
        self.exists = False
        self.timerApp.removeDeadElements()

    def setVisible(self, isVisible: bool):
        self.isVisible = isVisible
        self.updateDisplay()


class ElementOptions:
    def __init__(self, timerApp):
        self.timerApp = timerApp
        self.font = "Arial"
        self.size = 50
        self.position = [0, 0]
        self.color = "#ffffff"
        self.prefix = ""
        self.align = "w"

    def copy(self):
        opt = ElementOptions(self.timerApp)
        opt.font = self.font
        opt.size = self.size
        opt.position = self.position[:]
        opt.color = self.color
        opt.prefix = self.prefix
        return opt


class RTAElement(Element):
    def __init__(self, timerApp):
        self.type = "rta"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000//65, self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getRTA())


class IGTElement(Element):
    def __init__(self, timerApp):
        self.type = "igt"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getIGT())


class AttemptsElement(Element):
    def __init__(self, timerApp):
        self.type = "attempts"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getAttempts())


class EndermenElement(Element):
    def __init__(self, timerApp):
        self.type = "endermen"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix +
                           self.timerApp.getKills("enderman"))


class BlazeElement(Element):
    def __init__(self, timerApp):
        self.type = "blaze"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getKills("blaze"))


class GlitchIGTElement(Element):
    def __init__(self, timerApp):
        self.type = "glitchigt"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getAltIGT())


class TextElement(Element):
    def __init__(self, timerApp):
        self.type = "text"
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix)


class ElementEditor(tk.Toplevel):
    def __init__(self, element):
        tk.Toplevel.__init__(self, element.timerApp)
        timerApp = element.timerApp
        self.geometry(
            f"+{str(timerApp.winfo_width()+timerApp.winfo_x()+10)}+{str(timerApp.winfo_y())}")
        self.exists = True
        self.element = element
        self.timerApp = timerApp
        self.protocol("WM_DELETE_WINDOW", self.exit)
        self.title("Edit Element")
        self.wm_attributes("-topmost", 1)

        self.resizable(0, 0)

        self.old = element.options.copy()

        self.entries = tk.Frame(self)
        self.topEntries = tk.Frame(self.entries)
        self.topEntries.grid(row=0, column=0, sticky="w")
        self.bottomEntries = tk.Frame(self.entries)
        self.bottomEntries.grid(row=1, column=0, sticky="w")

        self.fontEntry = tk.Entry(self.topEntries)
        self.fontEntry.config(width=10)
        self.fontEntry.insert(0, element.options.font)

        self.prefixEntry = tk.Entry(self.bottomEntries)
        self.prefixEntry.config(width=23)
        self.prefixEntry.insert(0, element.options.prefix)

        self.alignVar = tk.StringVar(self, element.options.align)
        self.alignBox = tk.Checkbutton(
            self.bottomEntries, command=lambda *x: self.swapAlign(), variable=self.alignVar, onvalue="e", offvalue="w")

        self.sizeEntry = IntEntry(self.topEntries, 200)
        self.sizeEntry.insert(0, str(element.options.size))
        self.sizeEntry.config(width=4)

        self.colorEntry = ColorEntry(self.topEntries, element.options.color)

        self.posFrame = tk.Frame(self.topEntries)

        self.posXEntry = IntEntry(self.posFrame)
        self.posXEntry.config(width=4)
        self.posXEntry.insert(0, str(element.options.position[0]))

        self.posYEntry = IntEntry(self.posFrame)
        self.posYEntry.config(width=4)
        self.posYEntry.insert(0, str(element.options.position[1]))

        self.posXEntry.grid(row=0, column=0, padx=5, pady=0, sticky="w")
        self.posYEntry.grid(row=0, column=1, padx=5, pady=0, sticky="w")

        tk.Label(self.topEntries, text="Font").grid(
            row=3, column=0, padx=3, pady=0, sticky="w")
        tk.Label(self.topEntries, text="Size").grid(
            row=3, column=1, padx=3, pady=0, sticky="w")
        tk.Label(self.topEntries, text="Color").grid(
            row=3, column=2, padx=3, pady=0, sticky="w")
        tk.Label(self.topEntries, text="Position").grid(
            row=3, column=3, padx=3, pady=0, sticky="w")
        tk.Label(self.bottomEntries, text="Prefix" if element.type != "text" else "Text").grid(
            row=1, column=0, padx=3, pady=0, sticky="w")
        tk.Label(self.bottomEntries, text="Right Align").grid(
            row=1, column=1, padx=3, pady=0, sticky="w")

        self.fontEntry.grid(row=5, column=0, padx=5, pady=0, sticky="w")
        self.sizeEntry.grid(row=5, column=1, padx=5, pady=0, sticky="w")
        self.colorEntry.grid(row=5, column=2, padx=5, pady=0, sticky="w")
        self.posFrame.grid(row=5, column=3, padx=0, pady=0, sticky="w")
        self.prefixEntry.grid(row=2, column=0, padx=5, pady=0, sticky="w")
        self.alignBox.grid(row=2, column=1, padx=5, pady=0, sticky="w")

        self.entries.grid(row=0, column=0)

        self.canvas = tk.Canvas(self, width=200, height=200)

        self.canvas.bind("<B1-Motion>", self.canvasDrag)
        self.canvas.bind("<Button 1>", self.canvasDrag)

        tk.Label(self, text="Click/Drag to position:").grid(
            row=1, column=0, padx=5, pady=0, sticky="w")

        self.canvas.grid(row=2, column=0, padx=5, pady=5)
        self.canvas.config(bg="white")

        buttons = tk.Frame(self)
        buttons.grid(row=4, column=0)
        tk.Button(buttons, text="Remove", command=self.remove).grid(
            row=0, column=0, padx=5, pady=5)
        tk.Button(buttons, text="Save", command=self.save).grid(
            row=0, column=1, padx=5, pady=5)
        tk.Button(buttons, text="Cancel", command=self.cancel).grid(
            row=0, column=2, padx=5, pady=5)

        self.after(0, self.loop)

        if element.beingEdited:
            self.destroy()
        else:
            element.beingEdited = True
            element.editor = self

    def swapAlign(self):
        self.element.options.align = self.alignVar.get()
        self.element.updateDisplay()

    def remove(self, x=0):
        self.destroy()
        self.element.remove()
        if self.element.timerApp.optionsMenu is not None:
            self.element.timerApp.optionsMenu.elementList.refresh()
        self.timerApp.optionsMenu.deiconify()
        self.timerApp.optionsMenu.reposition()

    def canvasDrag(self, event):
        x = int(self.timerApp.winfo_width() * (min(max(event.x, 0), 200))/200)
        y = int(self.timerApp.winfo_height() * (min(max(event.y, 0), 200))/200)
        self.posXEntry.delete(0, 'end')
        self.posYEntry.delete(0, 'end')
        self.posXEntry.insert(0, str(x))
        self.posYEntry.insert(0, str(y))
        self.element.options.position = [x, y]
        self.element.updatePosition()

    def loop(self):
        self.after(200, self.loop)

        if not self.exists:
            self.cancel()
        elif self.verify():
            self.updateDisplay()

    def updateDisplay(self):
        opt = self.element.options
        opt.font = self.fontEntry.get()
        opt.color = self.colorEntry.get()
        opt.size = self.sizeEntry.get()
        opt.prefix = self.prefixEntry.get()
        opt.position = [int(self.posXEntry.get()), int(self.posYEntry.get())]
        self.element.updateDisplay()

    def verify(self):
        return (self.posXEntry.get() != "" and self.posYEntry.get() != "" and self.sizeEntry.get() != "")

    def exit(self, x=0):
        ans = tkMessageBox.askyesnocancel(
            "Save Element?", "Save options for this element?")
        if ans:
            self.save()
        elif ans == False:
            self.cancel()
        else:
            self.focus()
        return ans

    def save(self):
        if self.verify():
            self.exists = False
            self.destroy()
            self.element.beingEdited = False
            self.element.editor = None
            self.timerApp.optionsMenu.deiconify()
            self.timerApp.optionsMenu.reposition()

    def cancel(self, x=0):
        self.destroy()
        self.element.options = self.old
        self.element.updateDisplay()
        self.exists = False
        self.element.beingEdited = False
        self.element.editor = None
        self.timerApp.optionsMenu.deiconify()
        self.timerApp.optionsMenu.reposition()


if __name__ == "__main__":
    import os
    os.system("python AutoMCTimer.pyw")
