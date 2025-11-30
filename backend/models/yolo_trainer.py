# yolo_trainer.py - YOLO model training
import os
os.environ['TORCH_WEIGHTS_ONLY'] = 'False'
from ultralytics import YOLO

# Configuration
DATA_YAML = 'datasets/Helmet-Vest-Belt.v1i.yolov8/data.yaml'
MODEL_SAVE = 'runs/detect/helmet_vest'

def train_model(epochs=150, batch_size=16, img_size=640):
    """Train YOLO model for PPE detection with optimized parameters"""
    print("🚀 Starting YOLO training for PPE detection...")
    
    # Use small model for balanced speed/accuracy
    model = YOLO('yolov8s.pt')  # Balanced model
    
    # Train with optimized parameters for 95+ accuracy
    model.train(
        data=DATA_YAML, 
        epochs=epochs, 
        batch=batch_size, 
        imgsz=img_size, 
        project='runs/detect', 
        name='helmet_vest_optimized', 
        lr0=0.01,           # Initial learning rate
        lrf=0.001,          # Final learning rate
        momentum=0.937,     # SGD momentum
        weight_decay=0.0005, # Weight decay
        warmup_epochs=3,    # Warmup epochs
        warmup_momentum=0.8, # Warmup momentum
        box=0.05,           # Box loss gain
        cls=0.5,            # Class loss gain
        dfl=1.5,            # DFL loss gain
        pose=12.0,          # Pose loss gain
        kobj=1.0,           # Keypoint obj loss gain
        label_smoothing=0.0, # Label smoothing
        nbs=64,             # Nominal batch size
        hsv_h=0.015,        # HSV-Hue augmentation
        hsv_s=0.7,          # HSV-Saturation augmentation
        hsv_v=0.4,          # HSV-Value augmentation
        degrees=0.0,        # Rotation degrees
        translate=0.1,      # Translation
        scale=0.5,          # Scale
        shear=0.0,          # Shear degrees
        perspective=0.0,    # Perspective
        flipud=0.0,         # Flip up-down probability
        fliplr=0.5,         # Flip left-right probability
        mosaic=1.0,         # Mosaic probability
        mixup=0.0,          # Mixup probability
        copy_paste=0.0,     # Copy-paste probability
        patience=50,        # Early stopping patience
        save_period=10      # Save checkpoint every N epochs
    )
    
    print('✅ Training finished. Best weights in runs/detect/helmet_vest/weights/best.pt')
    return model

if __name__ == '__main__':
    train_model()