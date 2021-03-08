import tkinter as tk
import tkinter.font as tkFont

class Element(tk.Frame):

    @staticmethod
    def fromIdentifier(id: str, timerApp):
        ids = {
            "rta": RTAElement,
            "igt": IGTElement,
            "attempts": AttemptsElement,
            "endermen": EndermenElement,
            "blaze": BlazeElement
        }
        return ids[id](timerApp)

    def __init__(self, timerApp):
        tk.Frame.__init__(self,timerApp)
        self.isVisible = True
        self.timerApp = timerApp
        self.options = ElementOptions(self)
        self.font = tkFont.Font(self, ("Arial", 50))
        self.stringVar = tk.StringVar(self, "")
        self.label = tk.Label(self,font=self.font,textvariable=self.stringVar,anchor="w")
        self.label.grid(row=0,column=0,sticky="w")
        self.updateDisplay()

    def updateDisplay(self):
        self.font.config(family=self.options.font, size=self.options.size)
        self.label.config(fg=self.options.color,bg=self.timerApp.bg)
        self.place_forget()
        pos = self.options.position
        if self.isVisible:
            self.place(x=pos[0], y=pos[1],anchor = "nw")
        
    def edit(self):
        return ElementEditor(self.timerApp,self)
    
    def remove(self):
        self.destroy()
    
    def setVisible(self,isVisible: bool):
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


class RTAElement(Element):
    def __init__(self, timerApp):
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000//65,self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getRTA())


class IGTElement(Element):
    def __init__(self, timerApp):
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000,self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getIGT())


class AttemptsElement(Element):
    def __init__(self, timerApp):
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        self.after(1000, self.loop)
        self.stringVar.set(self.options.prefix+self.timerApp.getIGT())


class EndermenElement(Element):
    def __init__(self, timerApp):
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        pass


class BlazeElement(Element):
    def __init__(self, timerApp):
        Element.__init__(self, timerApp)
        self.after(0, self.loop)

    def loop(self):
        pass

class ElementEditor(tk.Toplevel):
    def __init__(self,timerApp,element):
        tk.Toplevel.__init__(self,timerApp)
        self.exists = True
        self.element = element
        self.timerApp = timerApp
        self.protocol("WM_DELETE_WINDOW", self.exit)

        self.after(0, self.loop)

    def loop(self):
        self.after(200,self.loop)
        print("yaaass")

    
    def exit(self):
        self.exists = False
        self.destroy()



if __name__ == "__main__":
    from AutoMCTimer import *
    root = TimerApp()
    e = RTAElement(root)
    editor= None
    def edit(x=0):
        global editor
        if editor == None or not editor.exists:
            editor = e.edit()
    
    root.bind("e",edit)

    root.mainloop()