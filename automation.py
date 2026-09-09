"""
ADB-based automation controller.
Replaces the old pyautogui version.
"""

import logging
import subprocess
import time
from typing import Optional, Tuple, Union

logger = logging.getLogger(__name__)


class AutomationController:
    """
    Sends taps and key events to an Android device over ADB.
    """

    def __init__(self, device_serial: Optional[str] = None):
        self.device_serial = device_serial

    def _run_adb(self, *args, timeout: int = 10):
        cmd = ["adb"]
        if self.device_serial:
            cmd += ["-s", self.device_serial]
        cmd += list(args)

        result = subprocess.run(
            cmd,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            err = result.stderr.decode(errors="ignore").strip()
            logger.warning(f"ADB input command failed: {' '.join(cmd)} → {err}")
        return result

    def set_device(self, serial: str):
        """Update the target device serial (called after WindowManager connects)."""
        self.device_serial = serial

    def click(self, x: Union[int, float, Tuple], y: Optional[Union[int, float]] = None):
        """
        Tap at device coordinates (x, y).

        Args:
            x: x coordinate or a (x, y) tuple
            y: y coordinate
        """
        if y is None:
            x, y = x
        x, y = int(round(x)), int(round(y))
        self._run_adb("shell", "input", "tap", str(x), str(y))
        # Small delay so the game can react
        time.sleep(0.05)

    def send_key(self, key: str):
        """
        Send a key event.
        Common keys: KEYCODE_BACK, KEYCODE_HOME, KEYCODE_ENTER, etc.
        """
        key_map = {
            "back": "KEYCODE_BACK",
            "home": "KEYCODE_HOME",
            "enter": "KEYCODE_ENTER",
            "f12": "KEYCODE_F12",
        }
        keycode = key_map.get(key.lower(), key)
        self._run_adb("shell", "input", "keyevent", keycode)
