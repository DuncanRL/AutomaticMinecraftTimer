import global_hotkeys

class KeybindManager:
    def __init__(self, timerApp):
        self.timerApp = timerApp
        self.pause = False
        self.reset = False
        self.pauseKeys = []
        self.resetKeys = []

    def stop(self):
        global_hotkeys.clear_hotkeys()
        global_hotkeys.stop_checking_hotkeys()

    cancel = end = stop

    def bind(self, pause, reset):
        self.stop()
        self.pauseKeys = pause
        self.resetKeys = reset

        bindings = [[pause, self._pausePress, self._pauseRelease],
                    [reset, self._resetPress, self._resetRelease]]
        bindings.sort(reverse=True,key=lambda kb: len(kb[0]))

        global_hotkeys.register_hotkeys(bindings)
        global_hotkeys.start_checking_hotkeys()

    rebind = bind

    def _pausePress(self):
        self.pause = True
        if not self.reset:
            self.timerApp.togglePause()

    def _resetPress(self):
        self.reset = True
        if not self.pause:
            self.timerApp.resetTimer()

    def _pauseRelease(self):
        self.pause = False

    def _resetRelease(self):
        self.reset = False


if __name__ == "__main__":

    class mockTimerApp:
        def __init__(self):
            self.keybindManager = KeybindManager(self)
            self.keybindManager.bind(["\\"], ["control","\\"])
            self.keybindManager.bind(["\\"], ["alt","\\"])

        def resetTimer(self):
            print("Timer Reset")

        def togglePause(self):
            print("Timer Pause")

    mockTimerApp()

    import time
    time.sleep(10000) 
