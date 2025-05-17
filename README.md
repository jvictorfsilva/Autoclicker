# AutoClicker

A user-friendly auto-clicker for Windows, built with Python and Tkinter, featuring customizable click rates, global hotkeys, sound alerts, and persistent settings.

## Features

- **Left and Right Click Modes**: Independently configure CPS (clicks per second) for left and right mouse buttons.
- **Global Hotkeys**: Default toggles are `F6` for left-click and `F7` for right-click; fully customizable.
- **Sound Notifications**: Optional audible feedback when clicking is active or stopped.
- **Persistent Settings**: Preferences saved to `autoclicker_config.json` in the working directory.
- **Simple GUI**: Easy-to-use interface to start/stop, adjust CPS, toggle sound, and set hotkeys.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/jvictorfsilva/Autoclicker.git
   cd Autoclicker
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows PowerShell: .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:

```bash
python autoclicker.py
```

1. Use the GUI sliders or entry fields to set your desired CPS for left/right clicks.
2. Click the start/stop buttons or use the hotkeys to toggle auto-clicking:

   - Left-click toggle: `F6` (default)
   - Right-click toggle: `F7` (default)

3. Enable or disable sound alerts using the "Sound" checkbox.
4. Preferences are saved automatically on exit.

## Configuration

- **autoclicker_config.json**: Stores your last-used CPS, hotkeys, and sound preference.
- You can edit this file directly or via the GUI.

## Requirements

- Python 3.6 or higher
- Windows OS (uses `winsound` and low-level Windows APIs)
- `keyboard` Python package

## License

This project is released under the MIT License. See `LICENSE` for details.
