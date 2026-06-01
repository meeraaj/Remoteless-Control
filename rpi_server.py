from flask import Flask
import subprocess
import time

app = Flask(__name__)

# NOTE: Change 'MyTV' to the name you configured in your LIRC lircd.conf file
TV_REMOTE_NAME = "Samsung_TV" 

def send_ir_mute_toggle():
    """Fires the IR LED using LIRC to toggle the TV's mute state."""
    try:
        # irsend SEND_ONCE <remote_name> <key_name>
        subprocess.run(["irsend", "SEND_ONCE", TV_REMOTE_NAME, "KEY_MUTE"], check=True)
        print("--> IR Mute Signal Fired!")
    except Exception as e:
        print(f"Error firing IR signal: {e}")

@app.route('/mute', methods=['GET'])
def mute_tv():
    print("[SERVER]: Mute command received from Laptop (Ad Started)")
    send_ir_mute_toggle()
    return "Muted", 200

@app.route('/unmute', methods=['GET'])
def unmute_tv():
    print("[SERVER]: Unmute command received from Laptop (Ad Ended)")
    # Mute buttons are usually toggles, so we send the exact same IR code to unmute
    send_ir_mute_toggle()
    return "Unmuted", 200

if __name__ == '__main__':
    print("Starting Raspberry Pi IR Control Server...")
    # host='0.0.0.0' exposes the server to your local Wi-Fi network so the laptop can reach it
    app.run(host='0.0.0.0', port=5000)