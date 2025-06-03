from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController
import time

class MacroPlayer:
    def __init__(self, events, speed=1.0):
        self.events = events
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.speed = speed
        self._paused = False
        self._stopped = False

    def play(self):
        last_time = 0
        for event in self.events:
            if self._stopped:
                break

            while self._paused:
                time.sleep(0.1)
                if self._stopped:
                    return

            etype, delay, *data = event
            sleep_time = max((delay - last_time) / self.speed, 0)
            time.sleep(sleep_time)
            last_time = delay

            if etype == 'mouse':
                x, y, button, pressed = data
                self.mouse.position = (x, y)
                if pressed:
                    self.mouse.press(button)
                else:
                    self.mouse.release(button)
            elif etype == 'keyboard':
                key, pressed = data
                if pressed:
                    self.keyboard.press(key)
                else:
                    self.keyboard.release(key)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def stop(self):
        self._stopped = True
        self._paused = False  # Ensure it exits pause loop
