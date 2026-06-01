import cv2
import requests
import time
from ultralytics import YOLO

def main():
    model = YOLO('runs/detect/hotstar_ad_v8/weights/best.pt')
    RPI_URL = "http://192.168.29.171:5000"
    
    # State tracking to manage mute/unmute
    is_muted = False
    last_ad_time = 0
    buffer_seconds = 5.0 # Delay before unmuting to prevent flickering if the AI misses a single frame

    cap = cv2.VideoCapture(1)

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # Running inference
        # Crop the frame to the right side where the TV is located
        height, width, _ = frame.shape
        # Adjust 'int(width/3)' if you need to move the crop line left or right
        roi_frame = frame[:, int(width/3):width] 

        # Running inference strictly on the cropped TV area
        results = model(roi_frame, conf=0.10, verbose=False, device='cpu') 
        annotated_frame = results[0].plot()

        ad_detected = len(results[0].boxes) > 0

        if ad_detected:
            last_ad_time = time.time()
            
            # If ad is detected and TV is NOT muted, send Mute
            if not is_muted:
                print("\n>>> [AI DETECTED AD]: Firing MUTE command to Raspberry Pi...")
                try:
                    requests.get(RPI_URL + "/mute", timeout=2)
                    is_muted = True
                except Exception as e:
                    print(f"Error reaching Pi: {e}")
        else:
            # If no ad is detected, check if TV IS muted
            if is_muted:
                # Only unmute if the ad has been gone for longer than the buffer time
                if (time.time() - last_ad_time) > buffer_seconds:
                    print("\n>>> [AD FINISHED]: Firing UNMUTE command to Raspberry Pi...")
                    try:
                        requests.get(RPI_URL + "/unmute", timeout=2)
                        is_muted = False
                    except Exception as e:
                        print(f"Error reaching Pi: {e}")

        cv2.imshow("IPL Live Ad Blocker", annotated_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()  