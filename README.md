# Remoteless Control: AI-Powered Live TV Ad Blocker

An automated hardware and software pipeline that uses Computer Vision (YOLOv8) to watch a live cricket match through a webcam, detects when a commercial break starts (via the Hotstar Ad badge), and sends a wireless command to a Raspberry Pi to physically mute the TV using Infrared (IR) until the game returns.

## 🚀 The System Architecture

The project bridges three completely different domains: AI/Computer Vision, Local Networking, and low-level Hardware GPIO control.

1. **The Brains (Laptop/Webcam):** A custom-trained YOLOv8 object detection model constantly scans a live webcam feed pointed at the TV.
2. **The Bridge (Local Wi-Fi):** When the AI detects the "Ad" badge, a Python script fires an HTTP request over the local network to a Flask server running on a Raspberry Pi.
3. **The Brawn (Raspberry Pi & IR):** The Flask server triggers `LIRC` (Linux Infrared Remote Control), which sends a raw hex code out of GPIO 17, through an NPN transistor, and out of an IR LED to mute the Samsung TV.


## 🛠️ Step-by-Step Setup Guide

### Step 1: Train the YOLOv8 Model
1. Gather images of the live TV screen showing the ad badge (to account for screen glare and pixelation).
2. Train your YOLOv8 model on this dataset. 
3. Once training is complete, locate your newly generated weights file (usually found at `runs/detect/train/weights/best.pt`).

### Step 2: Configure the AI (Laptop)
1. Copy the `best.pt` file into your main project directory.
2. Open `live_ad_blocker.py` and update the model path to point to your new weights file:
   ```python
   model = YOLO('path/to/your/best.pt')
   ```
3. Update the `RPI_URL` variable in the script to match your Raspberry Pi's local IP address:
   ```python
   RPI_URL = "http://<YOUR_PI_IP_ADDRESS>:5000"
   ```

### Step 3: Hardware Setup - Part A (Capturing Remote Codes)
Before the Pi can mute the TV, it needs to learn your specific TV remote's infrared signals using an IR Receiver module (like a TSOP38238).

**Receiver Circuit Schematic:**
![Receiver Schematic](images/Screenshot-2026-06-01-201836.png)

**Receiver Physical Breadboard Wiring:**
![Receiver Breadboard](images/WhatsApp-Image-2026-06-01-at-20.16.03.jpeg)

1. Wire the 3-pin IR Receiver: **VCC** to 3.3V, **GND** to Ground, and **DAT/OUT** to **GPIO 18** (Physical Pin 12).
2. Edit your Pi's boot config (`/boot/firmware/config.txt`) and add: `dtoverlay=gpio-ir,gpio_pin=18`
3. Reboot the Pi, then use the terminal to test the receiver:
   ```bash
   sudo systemctl stop lircd
   mode2 -d /dev/lirc0
   ```
4. Point your TV remote at the receiver and press "Mute". You will see raw pulse/space data appear on the screen. Map these hex codes to a `/etc/lirc/lircd.conf.d/your_tv.conf` file.

### Step 5: Hardware Setup - Part B (Transmitting to the TV)
Once the codes are captured, you can set up the transmitter. Because GPIO pins max out at ~16mA, you must use an NPN Transistor (like a 2N2222) to pull 5V directly from the Pi's power rail to give the IR LED enough range to reach the TV.

**Transmitter Circuit Schematic:**
![Transmitter Schematic](images/Screenshot%202026-06-01%20160426.png)

**Transmitter Physical Breadboard Wiring:**
![Transmitter Breadboard](images/WhatsApp%20Image%202026-06-01%20at%2019.48.52.jpeg)
4. Leave this SSH terminal open so the server continues listening for commands.

### Step 4: Launch the System
1. Aim your laptop's webcam directly at the TV screen.
2. Open a terminal on your laptop, navigate to the project folder, and run the detection script:
   ```bash
   python live_ad_blocker.py
   ```
3. Watch the terminal output. When an ad appears, the laptop will successfully ping the Pi, the Pi will flash the IR LED, and the TV will mute!
