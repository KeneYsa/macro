from recorder import MacroRecorder
from player import MacroPlayer
import storage
from gui import run_gui

def main():
    print("Press ESC to stop recording...")
    recorder = MacroRecorder()
    events = recorder.start()

    storage.save_macro("macros/recorded_macro.pkl", events)

    print("Playing back the macro...")
    loaded_events = storage.load_macro("macros/recorded_macro.pkl")
    player = MacroPlayer(loaded_events)
    player.play()

if __name__ == "__main__":
    run_gui()
