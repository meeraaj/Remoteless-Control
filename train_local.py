from ultralytics import YOLO

def main():
    # Load the lightweight YOLOv8 Nano model
    model = YOLO("yolov8n.pt")

    print("Initializing hardware-accelerated training on RTX 5070 Ti...")
    
    # Start the training process
    model.train(
        data="dataset/data.yaml",   # Points to your dataset configuration
        epochs=50,                  # 50 cycles is plenty for a static UI element
        imgsz=640,                  # Resolution for training
        batch=16,                   # Batch size (RTX 5070 Ti handles this easily)
        device='cpu',                   # Forces execution on your dedicated NVIDIA GPU
        name="hotstar_ad_v8"        # Folder name where your final weights will be saved
    )

    print("\nTraining Complete! Your model is saved at: runs/detect/hotstar_ad_v8/weights/best.pt")

if __name__ == "__main__":
    main()