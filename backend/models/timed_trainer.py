#!/usr/bin/env python3
"""
Optimized 200-epoch training with time tracking
"""
import os
import time
os.environ['TORCH_WEIGHTS_ONLY'] = 'False'
from ultralytics import YOLO

DATA_YAML = 'datasets/Helmet-Vest-Belt.v1i.yolov8/data.yaml'

def train_100_epochs():
    """100-epoch training optimized for reasonable time"""
    
    start_time = time.time()
    print("⏱️ Starting 100-epoch training...")
    
    # Use small model for balance of speed/accuracy
    model = YOLO('yolov8s.pt')
    
    results = model.train(
        data=DATA_YAML,
        epochs=100,
        batch=16,            # Balanced batch size
        imgsz=640,
        project='runs/detect',
        name='ppe_100_epochs',
        
        # Optimized for reasonable training time
        lr0=0.01,
        lrf=0.001,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        
        # Moderate augmentation
        hsv_h=0.015,
        hsv_s=0.5,           # Reduced from 0.7
        hsv_v=0.3,           # Reduced from 0.4
        degrees=8.0,         # Reduced rotation
        translate=0.08,      # Reduced translation
        scale=0.8,
        fliplr=0.5,
        mosaic=0.8,          # Reduced mosaic
        mixup=0.1,           # Light mixup
        
        patience=25,
        save_period=25,      # Save less frequently
        device='cpu',
        workers=4,           # Use multiple workers
        cache=True,          # Cache for speed
        plots=False          # No plots during training
    )
    
    end_time = time.time()
    training_time = end_time - start_time
    
    # Calculate time metrics
    hours = int(training_time // 3600)
    minutes = int((training_time % 3600) // 60)
    
    # Validate results
    metrics = model.val()
    map_score = metrics.box.map50_95
    
    print(f"\n⏱️ Training Complete!")
    print(f"📊 Total time: {hours}h {minutes}m")
    print(f"🎯 mAP@0.5-0.95: {map_score:.3f} ({map_score*100:.1f}%)")
    print(f"⚡ Time per epoch: {training_time/100:.1f} seconds")
    
    return map_score, training_time

if __name__ == '__main__':
    accuracy, time_taken = train_100_epochs()