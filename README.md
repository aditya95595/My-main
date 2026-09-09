# COC Auto Farm Bot – VPS / ADB Edition

A thread-safe Clash of Clans farming bot that runs on a **Linux VPS** and controls a real Android phone (or emulator) over **ADB**.

This is the adapted version of the original Windows + LDPlayer bot. It no longer depends on `pywinauto` or a Windows desktop.

## Features

- Automated farming (search bases → read resources with EasyOCR → attack when thresholds are met)
- Works with real Android phones via USB or wireless ADB
- Also works with emulators that expose ADB
- Thread-safe Tkinter GUI
- Graceful stop
- Retry logic for detections

## Requirements

### On the VPS (Linux)

- Python 3.9+
- ADB (`sudo apt update && sudo apt install -y adb`)
- Enough RAM (recommended **6–8 GB** for YOLO + EasyOCR)

### On the Android phone

- USB Debugging enabled (Developer options)
- Or Wireless ADB enabled
- Clash of Clans installed and logged in

## Installation on VPS

```bash
# 1. Clone / upload the project
git clone https://github.com/aditya95595/My-main.git
cd My-main

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place your YOLO model
mkdir -p models
# copy best.pt into models/best.pt
```

## Connect your phone

### Option A – USB (easiest for first test)

1. Connect phone to a computer that can reach the VPS (or use USB over IP solutions).
2. Enable USB debugging and authorize the computer.
3. On the VPS run:
   ```bash
   adb devices
   ```
   You should see your device listed as `device`.

### Option B – Wireless ADB (recommended for long-term)

1. On the phone enable Wireless debugging / ADB over network.
2. Note the IP and port (usually `192.168.x.x:5555` or similar).
3. On the VPS:
   ```bash
   adb connect YOUR_PHONE_IP:5555
   adb devices
   ```

You can also set the device in `config.py`:

```python
adb_device: str = "192.168.1.25:5555"   # or leave None for auto-detect
```

## Running the bot

### With GUI (needs a display)

If your VPS has no monitor, use Xvfb:

```bash
sudo apt install -y xvfb
xvfb-run -a python main.py
```

Or use a VNC / RDP solution and run normally:

```bash
python main.py
```

## Configuration

Edit `config.py`:

| Setting        | Meaning                                      | Default          |
|----------------|----------------------------------------------|------------------|
| `model_path`   | Path to YOLO `.pt` file                      | `models/best.pt` |
| `adb_device`   | Device serial or `IP:port` (None = auto)     | `None`           |
| `conf`         | YOLO confidence threshold                    | `0.5`            |
| `gpu`          | Use GPU (almost always `False` on VPS)       | `False`          |
| `max_retries`  | How many times to retry a detection          | `4`              |

## Architecture changes from original

| Original (Windows)      | New (VPS / ADB)              |
|-------------------------|------------------------------|
| `pywinauto`             | ADB (`adb exec-out screencap`) |
| `pyautogui`             | `adb shell input tap`        |
| Window title matching   | Device serial / wireless ADB |
| Screen coordinates + offset | Pure device coordinates   |

## Important warnings

- Automating Clash of Clans violates Supercell’s Terms of Service.
- Accounts can be permanently banned.
- Use at your own risk, preferably on a secondary account.
- Keep the phone charged and connected to a stable network.

## Troubleshooting

**“No ADB device found”**
```bash
adb kill-server
adb start-server
adb devices
```
Accept the RSA fingerprint on the phone.

**Slow detections**
- VPS has no GPU → set `gpu = False` (already default).
- Lower resolution on the phone if possible.
- 8 GB RAM VPS is strongly recommended.

**GUI does not open**
```bash
xvfb-run -a python main.py
```

## License

MIT
