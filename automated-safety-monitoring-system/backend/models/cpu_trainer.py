#!/usr/bin/env python3
"""
CPU-Optimized YOLO Training for macOS
"""
import os
os.environ['TORCH_WEIGHTS_ONLY'] = 'False'
from ultralytics import YOLO

DATA_YAML = 'datasets/Helmet-Vest-Belt.v1i.yolov8/data.yaml'

def train_for_accuracy():
    """Train YOLO model optimized for CPU and high accuracy"""
    
    print("🚀 Training YOLOv8 for 95+ accuracy on CPU...")
    
    # Use YOLOv8s for better accuracy than nano
    model = YOLO('yolov8s.pt')
    
    # CPU-optimized training parameters
    results = model.train(
        data=DATA_YAML,
        epochs=150,          # Reduced for CPU
        batch=4,             # Small batch for CPU
        imgsz=640,
        project='runs/detect',
        name='ppe_high_accuracy',
        
        # Optimized hyperparameters
        lr0=0.01,
        lrf=0.001,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        
        # Enhanced data augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=15.0,        # More rotation
        translate=0.1,
        scale=0.8,           # More scale variation
        shear=2.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,          # Add mixup
        copy_paste=0.1,      # Add copy-paste
        
        # Training settings
        patience=25,
        save_period=15,
        val=True,
        plots=True,
        device='cpu',
        workers=2            # Limit workers for CPU
    )
    
    # Validate the model
    metrics = model.val()
    map_score = metrics.box.map50_95
    
    print(f"\n📊 Training Results:")
    print(f"mAP@0.5-0.95: {map_score:.4f} ({map_score*100:.2f}%)")
    print(f"mAP@0.5: {metrics.box.map50:.4f} ({metrics.box.map50*100:.2f}%)")
    
    if map_score >= 0.95:
        print("🎉 SUCCESS! Achieved 95%+ accuracy!")
    elif map_score >= 0.90:
        print("📈 Good progress! Consider fine-tuning for 95%+")
    else:
        print("📊 Need more training. Try increasing epochs or data augmentation")
    
    return map_score

if __name__ == '__main__':
    print("🛡️ CPU-Optimized PPE Detection Training")
    print("=" * 50)
    
    accuracy = train_for_accuracy()
    print(f"\n✅ Final accuracy: {accuracy*100:.2f}%")