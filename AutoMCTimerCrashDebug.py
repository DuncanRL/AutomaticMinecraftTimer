from AutoMCTimer import *
import traceback

if __name__ == "__main__":
    try:
        timerApp = TimerApp()
        timerApp.iconbitmap(resource_path("Icon.ico"))
        timerApp.mainloop()
    except:
        traceback.print_exc()
        input("Press enter here to close.")