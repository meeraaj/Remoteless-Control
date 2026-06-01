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

### Step 3: Hardware Setup (Raspberry Pi)
The Raspberry Pi handles the physical IR transmission. Because GPIO pins max out at ~16mA, you must use an NPN Transistor (like a 2N2222) to pull 5V directly from the Pi's power rail to give the IR LED enough range to reach the TV.

**Circuit Schematic:**
![Circuit Schematic](images/Screenshot%202026-06-01%20160426.png)

**Physical Breadboard Wiring:**
![Breadboard Setup](images/WhatsApp%20Image%202026-06-01%20at%2019.48.52.jpeg)

1. Wire the IR LED to **GPIO 17** (Physical Pin 11) using the transistor circuit above.
2. Install and configure `lirc` on your Raspberry Pi with your specific TV's hex codes.
3. Open an SSH session into your Raspberry Pi and start the Flask server:
   ```bash
   python3 rpi_server.py
   ```
4. Leave this SSH terminal open so the server continues listening for commands.

### Step 4: Launch the System
1. Aim your laptop's webcam directly at the TV screen.
2. Open a terminal on your laptop, navigate to the project folder, and run the detection script:
   ```bash
   python live_ad_blocker.py
   ```
3. Watch the terminal output. When an ad appears, the laptop will successfully ping the Pi, the Pi will flash the IR LED, and the TV will mute!
