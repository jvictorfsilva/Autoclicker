import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import os
import ctypes

import keyboard

CONFIG_FILE = os.path.join(os.getcwd(), "autoclicker_config.json")

# Constants for mouse events
INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


class ApplicationPreferences:
    def __init__(self):
        # Default preferences
        self.cps = 10.0
        self.left_hotkey = "f6"
        self.right_hotkey = "f7"
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.cps = data.get("cps", self.cps)
                    self.left_hotkey = data.get("left_hotkey", self.left_hotkey)
                    self.right_hotkey = data.get("right_hotkey", self.right_hotkey)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preferences: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(
                    {
                        "cps": self.cps,
                        "left_hotkey": self.left_hotkey,
                        "right_hotkey": self.right_hotkey,
                    },
                    f,
                    indent=4,
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {e}")


class AutoClicker:
    def __init__(self, button_widget, get_interval, button_type="left"):
        self.button_widget = button_widget
        self.get_interval = get_interval
        self.button_type = button_type
        self.running = False
        self.thread = None

    def click(self):
        # perform a system-level click via ctypes for better performance
        if self.button_type == "left":
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        else:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            self.button_widget.config(relief=tk.SUNKEN)

    def stop(self):
        if self.running:
            self.running = False
            self.thread = None
            self.button_widget.config(relief=tk.RAISED)

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def _run(self):
        while self.running:
            self.click()
            time.sleep(self.get_interval())


class App:
    def __init__(self, root):
        self.root = root
        root.title("Bedrock Clicker")
        root.resizable(False, False)

        self.prefs = ApplicationPreferences()

        # CPS
        tk.Label(root, text="Clicks per Second:").grid(row=0, column=0, padx=5, pady=5)
        self.cps_var = tk.DoubleVar(value=self.prefs.cps)
        self.cps_entry = tk.Entry(root, textvariable=self.cps_var, width=10)
        self.cps_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Save CPS", command=self.save_cps).grid(
            row=0, column=2, padx=5, pady=5
        )

        # Left click hotkey
        tk.Label(root, text="Left Toggle Hotkey:").grid(row=1, column=0, padx=5, pady=5)
        self.left_key_label = tk.Label(root, text=self.prefs.left_hotkey)
        self.left_key_label.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Set Left", command=self.set_left_hotkey).grid(
            row=1, column=2, padx=5, pady=5
        )

        # Right click hotkey
        tk.Label(root, text="Right Toggle Hotkey:").grid(
            row=2, column=0, padx=5, pady=5
        )
        self.right_key_label = tk.Label(root, text=self.prefs.right_hotkey)
        self.right_key_label.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(root, text="Set Right", command=self.set_right_hotkey).grid(
            row=2, column=2, padx=5, pady=5
        )

        # Click buttons
        self.left_btn = tk.Button(
            root, text="Left Clicker Off", width=20, relief=tk.RAISED
        )
        self.left_btn.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        self.right_btn = tk.Button(
            root, text="Right Clicker Off", width=20, relief=tk.RAISED
        )
        self.right_btn.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # Initialize auto clickers
        self.left_clicker = AutoClicker(
            self.left_btn, lambda: 1.0 / self.prefs.cps, "left"
        )
        self.right_clicker = AutoClicker(
            self.right_btn, lambda: 1.0 / self.prefs.cps, "right"
        )

        # Bind hotkeys
        self.bind_hotkeys()

        # Clean up on close
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def save_cps(self):
        try:
            cps = float(self.cps_entry.get())
            if cps <= 0:
                raise ValueError("CPS must be positive")
            self.prefs.cps = cps
            self.prefs.save()
            messagebox.showinfo("Saved", f"Clicks per second set to {cps}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid CPS: {e}")

    def set_left_hotkey(self):
        messagebox.showinfo(
            "Hotkey", "Press the desired hotkey for left clicker... (ESC to cancel)"
        )
        key = keyboard.read_hotkey(suppress=False)
        if key:
            self.unbind_hotkey(self.prefs.left_hotkey)
            self.prefs.left_hotkey = key
            self.left_key_label.config(text=key)
            self.prefs.save()
            keyboard.add_hotkey(key, self.left_clicker.toggle)

    def set_right_hotkey(self):
        messagebox.showinfo(
            "Hotkey", "Press the desired hotkey for right clicker... (ESC to cancel)"
        )
        key = keyboard.read_hotkey(suppress=False)
        if key:
            self.unbind_hotkey(self.prefs.right_hotkey)
            self.prefs.right_hotkey = key
            self.right_key_label.config(text=key)
            self.prefs.save()
            keyboard.add_hotkey(key, self.right_clicker.toggle)

    def bind_hotkeys(self):
        keyboard.add_hotkey(self.prefs.left_hotkey, self.left_clicker.toggle)
        keyboard.add_hotkey(self.prefs.right_hotkey, self.right_clicker.toggle)

    def unbind_hotkey(self, key):
        try:
            keyboard.remove_hotkey(key)
        except KeyError:
            pass

    def on_close(self):
        # Stop clickers
        self.left_clicker.stop()
        self.right_clicker.stop()
        self.prefs.save()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
