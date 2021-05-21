class DragableWindow:
    def __init__(self):
        self.bind("<Button 1>", self.click)
        self.bind("<B1-Motion>", self.drag)
        self.bind("b", self.switchBorder)
        self.hasBorder = True
        self.overrideredirect(0)
        self.x = 0
        self.y = 0
        self.ox, self.oy = self.winfo_x, self.winfo_y
        self.wm_attributes("-topmost", 1)

    def switchBorder(self, x=0):
        if self.hasBorder:
            self.hasBorder = False
            self.overrideredirect(1)
        else:
            self.hasBorder = True
            self.overrideredirect(0)

    def click(self, event):
        self.x, self.y = (event.x, event.y)

    def drag(self, event):
        x, y = (event.x-self.x, event.y-self.y)
        self.geometry(f"+{x+self.ox()}+{y+self.oy()}")
