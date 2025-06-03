import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import threading
import os
import glob
import keyboard  # for global hotkey

from recorder import MacroRecorder
from player import MacroPlayer
import storage

MACRO_FOLDER = "macros"

class MacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Macro Recorder")
        self.root.geometry("400x400")

        if not os.path.exists(MACRO_FOLDER):
            os.makedirs(MACRO_FOLDER)

        self.player = None
        self.play_thread = None

        # Dropdown for macros
        self.macro_label = tk.Label(root, text="Select Macro:")
        self.macro_label.pack(pady=(10, 0))
        
        self.macro_var = tk.StringVar()
        self.macro_combo = ttk.Combobox(root, textvariable=self.macro_var, state="readonly", width=30)
        self.macro_combo.pack()
        self.refresh_macro_list()

        # Repeat input
        self.repeat_label = tk.Label(root, text="Repeat Playback Count:")
        self.repeat_label.pack(pady=(10, 0))
        self.repeat_var = tk.StringVar(value="1")
        self.repeat_entry = tk.Entry(root, textvariable=self.repeat_var, width=10)
        self.repeat_entry.pack()

        # Buttons
        self.record_button = tk.Button(root, text="Start Recording", command=self.record_macro, bg="lightblue")
        self.record_button.pack(pady=10)

        self.play_button = tk.Button(root, text="Play", command=self.play_macro, bg="lightgreen")
        self.play_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", command=self.stop_macro, bg="red", state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Speed Control
        self.speed_label = tk.Label(root, text="Playback Speed:")
        self.speed_label.pack()
        self.speed_scale = tk.Scale(root, from_=0.1, to=3.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.speed_scale.set(1.0)
        self.speed_scale.pack()

        self.quit_button = tk.Button(root, text="Quit", command=root.quit, bg="salmon")
        self.quit_button.pack(pady=10)

    def refresh_macro_list(self):
        files = glob.glob(os.path.join(MACRO_FOLDER, "*.pkl"))
        macros = [os.path.splitext(os.path.basename(f))[0] for f in files]
        self.macro_combo['values'] = macros
        if macros:
            self.macro_combo.current(0)
        else:
            self.macro_combo.set("")

    def record_macro(self):
        self.disable_all()
        threading.Thread(target=self._record_thread, daemon=True).start()

    def _record_thread(self):
        try:
            self.root.after(0, lambda: messagebox.showinfo("Recording", "Recording started. Press ESC to stop."))

            recorder = MacroRecorder()
            events = recorder.start()

            def ask_and_save():
                try:
                    macro_name = simpledialog.askstring("Save Macro", "Enter macro name to save:")
                    if not macro_name:
                        messagebox.showwarning("Cancelled", "Macro not saved (no name entered).")
                        self.enable_all()
                        return
                    
                    filename = os.path.join(MACRO_FOLDER, macro_name + ".pkl")
                    if os.path.exists(filename):
                        overwrite = messagebox.askyesno("Overwrite?", f"Macro '{macro_name}' already exists. Overwrite?")
                        if not overwrite:
                            messagebox.showinfo("Cancelled", "Macro not saved.")
                            self.enable_all()
                            return

                    storage.save_macro(filename, events)
                    messagebox.showinfo("Success", f"Macro '{macro_name}' recorded and saved.")
                    self.refresh_macro_list()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
                finally:
                    self.enable_all()

            self.root.after(0, ask_and_save)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, self.enable_all)

    def play_macro(self):
        macro_name = self.macro_var.get()
        if not macro_name:
            messagebox.showwarning("No Macro", "Please select a macro to play.")
            return

        filename = os.path.join(MACRO_FOLDER, macro_name + ".pkl")
        if not os.path.exists(filename):
            messagebox.showwarning("Not Found", f"Macro '{macro_name}' file not found.")
            self.refresh_macro_list()
            return

        try:
            repeat_count = int(self.repeat_var.get())
            if repeat_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showwarning("Invalid Repeat Count", "Please enter a valid positive integer for repeat count.")
            return

        self.disable_all()
        self.stop_button.config(state=tk.NORMAL)

        speed = self.speed_scale.get()
        events = storage.load_macro(filename)
        self.player = MacroPlayer(events, speed)

        self.play_thread = threading.Thread(target=self._play_thread, args=(repeat_count,), daemon=True)
        self.play_thread.start()

    def _play_thread(self, repeat_count):
        try:
            self.player._stopped = False

            # Register global spacebar hotkey to stop playback
            keyboard.add_hotkey('space', lambda: self.player.stop())

            for _ in range(repeat_count):
                if getattr(self.player, '_stopped', False):
                    break
                self.player.play()
        finally:
            keyboard.remove_hotkey('space')
            self.enable_all()
            self.stop_button.config(state=tk.DISABLED)

    def stop_macro(self):
        if self.player:
            self.player.stop()
        self.enable_all()
        self.stop_button.config(state=tk.DISABLED)

    def disable_all(self):
        self.record_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.macro_combo.config(state=tk.DISABLED)
        self.speed_scale.config(state=tk.DISABLED)
        self.repeat_entry.config(state=tk.DISABLED)

    def enable_all(self):
        self.record_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.NORMAL)
        self.macro_combo.config(state="readonly")
        self.speed_scale.config(state=tk.NORMAL)
        self.repeat_entry.config(state=tk.NORMAL)

def run_gui():
    root = tk.Tk()
    app = MacroApp(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
