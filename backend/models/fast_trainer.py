#!/usr/bin/env python3
"""
Fast YOLO Training - Optimized for Speed
"""
import os
os.environ['TORCH_WEIGHTS_ONLY'] = 'False'
from ultralytics import YOLO

DATA_YAML = 'datasets/Helmet-Vest-Belt.v1i.yolov8/data.yaml'

def fast_train():
    """Ultra-fast training configuration"""
    
    print("⚡ Starting FAST YOLO training...")
    
    # Use smallest, fastest model
    model = YOLO('yolov8n.pt')
    
    # Speed-optimized parameters
    results = model.train(
        data=DATA_YAML,
        epochs=50,           # Much fewer epochs
        batch=32,            # Larger batch (if memory allows)
        imgsz=416,           # Smaller image size
        project='runs/detect',
        name='ppe_fast',
        
        # Minimal hyperparameters
        lr0=0.01,
        lrf=0.01,
        momentum=0.9,
        weight_decay=0.0005,
        warmup_epochs=1,     # Minimal warmup
        
        # Reduced augmentation for speed
        hsv_h=0.01,
        hsv_s=0.3,
        hsv_v=0.2,
        degrees=5.0,
        translate=0.05,
        scale=0.9,
        shear=0.0,
        perspective=0.0,
        flipud=0.0,
        fliplr=0.5,
        mosaic=0.5,          # Reduced mosaic
        mixup=0.0,           # No mixup
        copy_paste=0.0,      # No copy-paste
        
        # Speed settings
        patience=10,         # Early stopping
        save_period=25,      # Save less frequently
        val=True,
        plots=False,         # No plots for speed
        device='cpu',
        workers=4,           # More workers
        cache=True           # Cache images in RAM
    )
    
    # Quick validation
    metrics = model.val()
    map_score = metrics.box.map50_95
    
    print(f"⚡ Fast training complete!")
    print(f"📊 mAP@0.5-0.95: {map_score:.3f} ({map_score*100:.1f}%)")
    
    return map_score

if __name__ == '__main__':
    print("⚡ FAST PPE Detection Training")
    print("=" * 40)
    
    accuracy = fast_train()
    print(f"✅ Done in minimal time! Accuracy: {accuracy*100:.1f}%")