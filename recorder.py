from pynput import mouse, keyboard
import time

class MacroRecorder:
    def __init__(self):
        self.events = []
        self.start_time = None

    def on_click(self, x, y, button, pressed):
        timestamp = time.time() - self.start_time
        self.events.append(('mouse', timestamp, x, y, button, pressed))

    def on_press(self, key):
        timestamp = time.time() - self.start_time
        self.events.append(('keyboard', timestamp, key, True))

    def on_release(self, key):
        timestamp = time.time() - self.start_time
        self.events.append(('keyboard', timestamp, key, False))
        if key == keyboard.Key.esc:
            return False

    def start(self):
        self.start_time = time.time()
        with mouse.Listener(on_click=self.on_click), \
             keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
        return self.events
