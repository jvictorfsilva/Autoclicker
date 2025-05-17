import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import os
import ctypes
import winsound
import keyboard

CONFIG_FILE = os.path.join(os.getcwd(), "autoclicker_config.json")

INPUT_MOUSE = 0
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010


class ApplicationPreferences:
    def __init__(self):
        self.left_cps = 10.0
        self.right_cps = 10.0
        self.left_hotkey = "f6"
        self.right_hotkey = "f7"
        self.sound_enabled = True
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.left_cps = data.get("left_cps", self.left_cps)
                    self.right_cps = data.get("right_cps", self.right_cps)
                    self.left_hotkey = data.get("left_hotkey", self.left_hotkey)
                    self.right_hotkey = data.get("right_hotkey", self.right_hotkey)
                    self.sound_enabled = data.get("sound_enabled", self.sound_enabled)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load preferences: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(
                    {
                        "left_cps": self.left_cps,
                        "right_cps": self.right_cps,
                        "left_hotkey": self.left_hotkey,
                        "right_hotkey": self.right_hotkey,
                        "sound_enabled": self.sound_enabled,
                    },
                    f,
                    indent=4,
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {e}")


class AutoClicker:
    def __init__(
        self,
        button_widget,
        get_interval,
        button_type="left",
        sound_enabled_getter=lambda: True,
    ):
        self.button_widget = button_widget
        self.get_interval = get_interval
        self.button_type = button_type
        self.sound_enabled_getter = sound_enabled_getter
        self.running = False
        self.thread = None

    def click(self):
        if self.button_type == "left":
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        else:
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

        if self.sound_enabled_getter():
            audio_path = os.path.join(os.getcwd(), "resources", "click-low.wav")
            winsound.PlaySound(audio_path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run)
            self.thread.daemon = True
            self.thread.start()
            if self.button_widget is not None:
                self.button_widget.config(
                    relief=tk.SUNKEN, text=f"{self.button_type.capitalize()} Clicker On"
                )

    def stop(self):
        if self.running:
            self.running = False
            self.thread = None
            if self.button_widget is not None:
                self.button_widget.config(
                    relief=tk.RAISED,
                    text=f"{self.button_type.capitalize()} Clicker Off",
                )

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

        tk.Label(root, text="Left Toggle Hotkey:").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.left_key_label = tk.Label(root, text=self.prefs.left_hotkey, width=10)
        self.left_key_label.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(root, text="Set Left", command=self.set_left_hotkey).grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )

        tk.Label(root, text="Left Clicks per Second:").grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        self.left_cps_var = tk.DoubleVar(value=self.prefs.left_cps)
        self.left_cps_entry = tk.Entry(root, textvariable=self.left_cps_var, width=10)
        self.left_cps_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(root, text="Save CPS", command=self.save_left_cps).grid(
            row=1, column=2, padx=5, pady=5, sticky="w"
        )

        tk.Label(root, text="Right Toggle Hotkey:").grid(
            row=2, column=0, padx=5, pady=5, sticky="e"
        )
        self.right_key_label = tk.Label(root, text=self.prefs.right_hotkey, width=10)
        self.right_key_label.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(root, text="Set Right", command=self.set_right_hotkey).grid(
            row=2, column=2, padx=5, pady=5, sticky="w"
        )

        tk.Label(root, text="Right Clicks per Second:").grid(
            row=3, column=0, padx=5, pady=5, sticky="e"
        )
        self.right_cps_var = tk.DoubleVar(value=self.prefs.right_cps)
        self.right_cps_entry = tk.Entry(root, textvariable=self.right_cps_var, width=10)
        self.right_cps_entry.grid(row=3, column=1, padx=5, pady=5)
        tk.Button(root, text="Save CPS", command=self.save_right_cps).grid(
            row=3, column=2, padx=5, pady=5, sticky="w"
        )

        tk.Label(root, text="Sound Toggle:").grid(
            row=4, column=0, padx=5, pady=5, sticky="e"
        )
        self.sound_on_img = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "resources", "sound_on.png")
        ).subsample(20, 20)
        self.sound_off_img = tk.PhotoImage(
            file=os.path.join(os.getcwd(), "resources", "sound_off.png")
        ).subsample(20, 20)
        self.sound_btn = tk.Button(
            root,
            image=self.sound_on_img if self.prefs.sound_enabled else self.sound_off_img,
            command=self.toggle_sound,
            relief=tk.FLAT,
        )
        self.sound_btn.grid(row=4, column=1, padx=5, pady=5)

        exit_btn = tk.Button(root, text="Exit", command=self.on_close)
        exit_btn.grid(row=5, column=0, columnspan=3, pady=10)

        self.left_clicker = AutoClicker(
            None,
            lambda: 1.0 / self.prefs.left_cps,
            "left",
            sound_enabled_getter=lambda: self.prefs.sound_enabled,
        )
        self.right_clicker = AutoClicker(
            None,
            lambda: 1.0 / self.prefs.right_cps,
            "right",
            sound_enabled_getter=lambda: self.prefs.sound_enabled,
        )

        self.left_hotkey_pressed = False
        self.right_hotkey_pressed = False

        self.bind_hotkeys()

        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def safe_unhook(self, handler):
        try:
            keyboard.unhook(handler)
        except KeyError:
            pass

    def save_left_cps(self):
        try:
            cps = float(self.left_cps_entry.get())
            if cps <= 0:
                raise ValueError("CPS must be positive")
            self.prefs.left_cps = cps
            self.prefs.save()
            messagebox.showinfo("Saved", f"Left Clicks per second set to {cps}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid CPS: {e}")

    def save_right_cps(self):
        try:
            cps = float(self.right_cps_entry.get())
            if cps <= 0:
                raise ValueError("CPS must be positive")
            self.prefs.right_cps = cps
            self.prefs.save()
            messagebox.showinfo("Saved", f"Right Clicks per second set to {cps}")
        except Exception as e:
            messagebox.showerror("Error", f"Invalid CPS: {e}")

    def read_single_key(self):
        key = keyboard.read_key(suppress=False)
        while keyboard.is_pressed(key):
            time.sleep(0.05)
        return key

    def set_left_hotkey(self):
        if hasattr(self, "left_press_handler"):
            self.safe_unhook(self.left_press_handler)
        if hasattr(self, "left_release_handler"):
            self.safe_unhook(self.left_release_handler)
        key = self.read_single_key()
        messagebox.showinfo(
            "Hotkey Selected",
            f"Hotkey '{key}' has been successfully set for Left Clicker.",
        )
        self.prefs.left_hotkey = key
        self.left_key_label.config(text=key)
        self.prefs.save()
        self.left_press_handler = keyboard.on_press_key(
            key, self.handle_left_hotkey_press, suppress=False
        )
        self.left_release_handler = keyboard.on_release_key(
            key, self.handle_left_hotkey_release, suppress=False
        )

    def set_right_hotkey(self):
        if hasattr(self, "right_press_handler"):
            self.safe_unhook(self.right_press_handler)
        if hasattr(self, "right_release_handler"):
            self.safe_unhook(self.right_release_handler)
        key = self.read_single_key()
        messagebox.showinfo(
            "Hotkey Selected",
            f"Hotkey '{key}' has been successfully set for Right Clicker.",
        )
        self.prefs.right_hotkey = key
        self.right_key_label.config(text=key)
        self.prefs.save()
        self.right_press_handler = keyboard.on_press_key(
            key, self.handle_right_hotkey_press, suppress=False
        )
        self.right_release_handler = keyboard.on_release_key(
            key, self.handle_right_hotkey_release, suppress=False
        )

    def bind_hotkeys(self):
        self.left_press_handler = keyboard.on_press_key(
            self.prefs.left_hotkey, self.handle_left_hotkey_press, suppress=False
        )
        self.left_release_handler = keyboard.on_release_key(
            self.prefs.left_hotkey, self.handle_left_hotkey_release, suppress=False
        )
        self.right_press_handler = keyboard.on_press_key(
            self.prefs.right_hotkey, self.handle_right_hotkey_press, suppress=False
        )
        self.right_release_handler = keyboard.on_release_key(
            self.prefs.right_hotkey, self.handle_right_hotkey_release, suppress=False
        )

    def system_modifier_pressed(self):
        try:
            super_pressed = keyboard.is_pressed("super")
        except ValueError:
            super_pressed = False
        return (
            keyboard.is_pressed("alt")
            or keyboard.is_pressed("ctrl")
            or keyboard.is_pressed("windows")
            or super_pressed
        )

    def handle_left_hotkey_press(self, event):
        if self.system_modifier_pressed():
            return
        if not self.left_hotkey_pressed:
            self.left_hotkey_pressed = True
            self.left_clicker.toggle()

    def handle_left_hotkey_release(self, event):
        self.left_hotkey_pressed = False

    def handle_right_hotkey_press(self, event):
        if self.system_modifier_pressed():
            return
        if not self.right_hotkey_pressed:
            self.right_hotkey_pressed = True
            self.right_clicker.toggle()

    def handle_right_hotkey_release(self, event):
        self.right_hotkey_pressed = False

    def toggle_sound(self):
        self.prefs.sound_enabled = not self.prefs.sound_enabled
        self.prefs.save()
        if self.prefs.sound_enabled:
            self.sound_btn.config(image=self.sound_on_img)
        else:
            self.sound_btn.config(image=self.sound_off_img)

    def on_close(self):
        try:
            self.safe_unhook(self.left_press_handler)
            self.safe_unhook(self.left_release_handler)
            self.safe_unhook(self.right_press_handler)
            self.safe_unhook(self.right_release_handler)
        except Exception:
            pass
        self.prefs.save()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
