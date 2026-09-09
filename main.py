"""
Entry point for the ADB / VPS version of the COC Auto Farm Bot.
Works on Linux VPS controlling a real Android phone or emulator via ADB.
"""

import logging
import os
import queue
import sys
import tkinter as tk
from tkinter import messagebox

from config import AppConfig
from logger import setup_logging
from window_manager import WindowManager
from vision import VisionManager
from automation import AutomationController
from bot import CocBot
from gui import BotGUI

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    config = AppConfig()

    # Resolve model path relative to this script
    model_full_path = os.path.join(os.path.dirname(__file__), config.model_path)
    if os.path.exists(model_full_path):
        config.model_path = model_full_path
    else:
        logger.warning(
            f"YOLO model not found at '{model_full_path}'. "
            "Place best.pt in the models/ folder."
        )

    # Connect to Android device via ADB
    try:
        window = WindowManager(config)
    except Exception as e:
        logger.error(f"Failed to connect to ADB device: {e}")
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "ADB Connection Error",
            f"Could not connect to any Android device.\n\n{e}\n\n"
            "Make sure:\n"
            "• ADB is installed (sudo apt install adb)\n"
            "• USB debugging is enabled\n"
            "• Phone is authorized (check the RSA prompt)\n"
            "• For wireless: adb connect IP:5555",
        )
        sys.exit(1)

    vision = VisionManager(config)
    automation = AutomationController(device_serial=window.device_serial)

    msg_queue = queue.Queue()
    bot = CocBot(config, window, vision, automation, msg_queue)

    root = tk.Tk()
    app = BotGUI(root, bot, msg_queue)

    # Optional: try to register F12 hotkey (works only if a real keyboard is present)
    try:
        import keyboard
        keyboard.add_hotkey("f12", bot.stop)
        logger.info("F12 emergency stop registered")
    except Exception as e:
        logger.warning(f"Could not register F12 hotkey (normal on headless VPS): {e}")

    logger.info("GUI started. Set thresholds and click Start Farm.")
    root.mainloop()


if __name__ == "__main__":
    main()
