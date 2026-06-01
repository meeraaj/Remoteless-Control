# Remoteless Control: AI-Powered Live TV Ad Blocker

An automated hardware and software pipeline that uses Computer Vision (YOLOv8) to watch a live cricket match through a webcam, detects when a commercial break starts (via the Hotstar Ad badge), and sends a wireless command to a Raspberry Pi to physically mute the TV using Infrared (IR) until the game returns.

## 🚀 The System Architecture

The project bridges three completely different domains: AI/Computer Vision, Local Networking, and low-level Hardware GPIO control.

1. **The Brains (Laptop/Webcam):** A custom-trained YOLOv8 object detection model constantly scans a live webcam feed pointed at the TV.
2. **The Bridge (Local Wi-Fi):** When the AI detects the "Ad" badge, a Python script fires an HTTP request over the local network to a Flask server running on a Raspberry Pi.
3. **The Brawn (Raspberry Pi & IR):** The Flask server triggers `LIRC` (Linux Infrared Remote Control), which sends a raw hex code out of GPIO 17, through an NPN transistor, and out of an IR LED to mute the Samsung TV.

![System Pipeline](images/image_a7091e.jpg) 

## 🛠️ The Engineering Journey & Challenges Overcome

Building this system required debugging multiple layers of the stack, from the physical world to the AI algorithms. Here is the process of how it came together:

### 1. Hardware Constraints: The 16mA Limit
Initially, the IR LED was plugged directly into the Raspberry Pi's GPIO pin. The LED was firing, but the TV was ignoring it. 
* **The Fix:** Discovered that a Pi GPIO pin maxes out at ~16mA, whereas real TV remotes pulse at 100mA+. To fix the range issue, the circuit requires an NPN Transistor (like a 2N2222) acting as an amplifier switch to pull 5V directly from the Pi's power rail, boosting the invisible IR flash to reach across the room.

**Circuit Schematic:**
![Circuit Schematic](images/Screenshot2026-06-01160426.png)

**Physical Breadboard Wiring:**
![Breadboard Setup](images/WhatsAppImage2026-06-01at19.48.52.jpeg)

### 2. Wrestling with LIRC & Kernel Drivers
Setting up `lirc` on modern Raspberry Pi OS versions proved difficult due to driver lockouts and broken online databases.
* **The Fix:** The `irdb-get` SourceForge repository for Samsung TV remotes was throwing 404 errors. We completely bypassed the broken tool by manually creating a `/etc/lirc/lircd.conf.d/samsung.conf` file and injecting the raw 32-bit hex codes (`0xE0E0F00F` for Mute). We also had to re-route LIRC from the default `devinput` driver to the `default` hardware driver so it could access `/dev/lirc0`.

### 3. Computer Vision: Defeating "Domain Shift"
The YOLOv8 model was initially trained on perfect, high-resolution digital screenshots. When asked to look at a physical TV screen through a webcam, it went completely blind due to screen glare, pixelation, and compression.
* **The Fix:** Dropped the confidence threshold strictly to `0.10`, cropped the video feed to isolate just the TV (Region of Interest), and gathered a new real-world dataset directly from the webcam to retrain the model to understand the physical environment.

### 4. Debouncing: Fixing the "AI Blink"
Webcams run at 30 FPS. If a commercial changed to a dark scene, the AI would lose the badge for 1 second and immediately unmute the TV. A second later, it would find the badge and mute it again, causing the TV audio to glitch wildly.
* **The Fix:** Implemented a **15-second debounce buffer**. When the AI loses sight of the ad, it starts a countdown timer. If the badge reappears within 15 seconds, the timer resets and the TV stays muted. It only sends the "Unmute" command if the badge is completely gone for a sustained period, ensuring smooth audio transitions when the cricket match actually resumes.

## 💻 How to Run It

### Hardware Setup (Raspberry Pi)
1. Wire an IR LED to GPIO 17 (Physical Pin 11) using a transistor for range.
2. Install `lirc` and configure `/boot/firmware/config.txt` with `dtoverlay=gpio-ir-tx,gpio_pin=17`.
3. Run the backend server:
```bash
   python3 rpi_server.py
