# COC Auto Farm Bot – Oracle Cloud / ADB Edition

A thread-safe Clash of Clans farming bot designed to run on **Oracle Cloud Free Tier** (Ampere A1 ARM) and control a real Android phone over **ADB**.

No Windows PC required.

---

## Oracle Cloud Free Tier Notes (2026)

- Shape: **VM.Standard.A1.Flex** (Ampere ARM)
- Current free limit: **2 OCPU + 12 GB RAM**
- OS: Ubuntu 22.04 or 24.04 (recommended)
- No GPU → `gpu = False` is already the default
- Capacity is often full → you may need to retry creating the instance

12 GB RAM is usable. YOLO + EasyOCR will run slower than on a GPU machine, but it works.

---

## 1. Create the Oracle Instance

1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
2. Create a new **Compute Instance**
3. Choose:
   - Image: **Canonical Ubuntu 22.04** or **24.04**
   - Shape: **VM.Standard.A1.Flex**
   - OCPU: **2**
   - Memory: **12 GB**
4. Add your SSH public key
5. Create the instance and note the public IP

---

## 2. First login & basic setup

```bash
ssh ubuntu@YOUR_ORACLE_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y adb python3-pip python3-venv python3-tk xvfb git unzip
```

---

## 3. Install the bot

```bash
git clone https://github.com/aditya95595/My-main.git
cd My-main

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

Place your trained YOLO model:

```bash
mkdir -p models
# Upload best.pt into models/best.pt (use scp or any method)
```

---

## 4. Connect your Android phone (Wireless ADB)

On your phone:

1. Enable **Developer options** → **Wireless debugging**
2. Note the IP and port (example: `192.168.1.25:45679`)

On the Oracle VPS:

```bash
adb connect YOUR_PHONE_IP:PORT
adb devices
```

You should see the device listed as `device`.

You can also hard-code it in `config.py`:

```python
adb_device = "192.168.1.25:45679"
```

---

## 5. Run the bot

Because Oracle instances have no monitor, use Xvfb:

```bash
source venv/bin/activate
xvfb-run -a python main.py
```

The GUI will start in the background. You can also run it inside `tmux` or `screen` so it survives SSH disconnect:

```bash
sudo apt install -y tmux
tmux new -s coc
xvfb-run -a python main.py
# Detach with Ctrl+B then D
```

---

## Configuration (`config.py`)

| Setting       | Recommended for Oracle      | Notes                          |
|---------------|-----------------------------|--------------------------------|
| `gpu`         | `False`                     | Oracle has no GPU              |
| `adb_device`  | your phone IP:port or None  | Auto-detect if only one device |
| `conf`        | `0.45` – `0.5`              | Lower if detections miss often |
| `max_retries` | `4`                         | Keep default                   |

---

## Important Oracle tips

- **Keep the instance alive** – Oracle can reclaim idle Always Free instances. Run a simple keep-alive (ping or a small script) if needed.
- **Outbound traffic** is free up to the monthly limit (usually enough).
- **ARM architecture** – All current packages (`ultralytics`, `easyocr`, `opencv-python-headless`) support ARM64.
- If `pip install` fails on some packages, try:
  ```bash
  pip install --upgrade pip setuptools wheel
  pip install -r requirements.txt
  ```

---

## Troubleshooting

**No ADB device found**
```bash
adb kill-server
adb start-server
adb connect YOUR_PHONE_IP:PORT
adb devices
```
Accept the RSA fingerprint on the phone the first time.

**Out of memory / very slow**
- Close other programs on the phone
- Lower phone resolution if possible
- 12 GB is the minimum comfortable size for continuous YOLO + EasyOCR

**GUI / display errors**
Always use:
```bash
xvfb-run -a python main.py
```

**Instance keeps getting terminated**
Oracle reclaims idle free instances. Keep a light process running or use a simple cron job that pings something every few minutes.

---

## Warning

Automating Clash of Clans violates Supercell’s Terms of Service.  
Your account can be permanently banned. Use only on accounts you are willing to lose.

---

## License

MIT
