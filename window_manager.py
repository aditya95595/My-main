"""
ADB-based window / device manager.
Replaces the old Windows pywinauto version.
Works on any Linux VPS controlling a real phone or emulator via ADB.
"""

import logging
import subprocess
import time
from typing import Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class WindowManager:
    """
    Controls an Android device (phone or emulator) over ADB.
    Provides screenshot capture and screen size information.
    Coordinates returned by vision are already device-relative,
    so no win_left / win_top offset is needed.
    """

    def __init__(self, config):
        self.config = config
        self.device_serial: Optional[str] = None
        self.win_width: int = 0
        self.win_height: int = 0
        # Kept for compatibility with old bot.py that still references them
        self.win_left: int = 0
        self.win_top: int = 0

        self._connect()

    def _run_adb(self, *args, timeout: int = 15) -> bytes:
        """Run an adb command and return stdout as bytes."""
        cmd = ["adb"]
        if self.device_serial:
            cmd += ["-s", self.device_serial]
        cmd += list(args)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                check=False,
            )
            if result.returncode != 0:
                err = result.stderr.decode(errors="ignore").strip()
                raise RuntimeError(f"ADB command failed: {' '.join(cmd)}\n{err}")
            return result.stdout
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"ADB command timed out: {' '.join(cmd)}")
        except FileNotFoundError:
            raise RuntimeError(
                "ADB not found. Install Android platform-tools and make sure "
                "'adb' is in your PATH.\n"
                "On Ubuntu/Debian: sudo apt install adb\n"
                "Or download from https://developer.android.com/tools/releases/platform-tools"
            )

    def _connect(self):
        """Find and connect to an ADB device."""
        # Start ADB server
        subprocess.run(["adb", "start-server"], capture_output=True)

        target = (self.config.adb_device or "").strip()

        if target and ":" in target:
            # Wireless ADB – try to connect
            logger.info(f"Connecting to wireless ADB device: {target}")
            connect_result = subprocess.run(
                ["adb", "connect", target],
                capture_output=True,
                text=True,
                timeout=10,
            )
            logger.info(connect_result.stdout.strip() or connect_result.stderr.strip())
            time.sleep(1)

        # List devices
        out = subprocess.check_output(["adb", "devices"], text=True, timeout=10)
        lines = [l.strip() for l in out.splitlines()[1:] if l.strip()]

        devices = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])

        if not devices:
            raise RuntimeError(
                "No ADB device found.\n\n"
                "Make sure:\n"
                "1. USB debugging is enabled on your phone\n"
                "2. Phone is connected via USB or wireless ADB (adb connect IP:5555)\n"
                "3. You accepted the RSA fingerprint prompt on the phone\n"
                "4. Run 'adb devices' to verify the device appears as 'device'"
            )

        if target:
            matched = [d for d in devices if target in d]
            if matched:
                self.device_serial = matched[0]
            else:
                self.device_serial = devices[0]
                logger.warning(
                    f"Requested device '{target}' not found exactly. "
                    f"Using first available device: {self.device_serial}"
                )
        else:
            self.device_serial = devices[0]

        logger.info(f"Using ADB device: {self.device_serial}")

        # Get screen size
        self._update_size()

    def _update_size(self):
        """Query current screen resolution."""
        try:
            out = self._run_adb("shell", "wm", "size").decode(errors="ignore")
            for line in out.splitlines():
                if "Physical size" in line or "Override size" in line:
                    size_str = line.split(":")[-1].strip()
                    w, h = size_str.split("x")
                    self.win_width = int(w)
                    self.win_height = int(h)
                    logger.info(f"Device resolution: {self.win_width}x{self.win_height}")
                    return
        except Exception as e:
            logger.warning(f"Could not read wm size: {e}")

        # Fallback: take a screenshot and read its shape
        frame = self.capture_window()
        self.win_height, self.win_width = frame.shape[:2]
        logger.info(f"Device resolution (from screenshot): {self.win_width}x{self.win_height}")

    def focus_window(self):
        """
        No-op on ADB (device is always 'focused').
        Kept for API compatibility with the original bot.
        """
        pass

    def get_rect(self):
        """Update size info. Kept for API compatibility."""
        if self.win_width == 0 or self.win_height == 0:
            self._update_size()

    def capture_window(self) -> np.ndarray:
        """
        Capture the current screen of the Android device.
        Returns a BGR OpenCV image.
        """
        raw = self._run_adb("exec-out", "screencap", "-p", timeout=20)

        if not raw:
            raise RuntimeError("Empty screenshot received from ADB")

        # Convert PNG bytes to OpenCV image
        arr = np.frombuffer(raw, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if frame is None:
            raise RuntimeError("Failed to decode screenshot from ADB")

        # Keep size in sync
        h, w = frame.shape[:2]
        self.win_width = w
        self.win_height = h

        return frame
