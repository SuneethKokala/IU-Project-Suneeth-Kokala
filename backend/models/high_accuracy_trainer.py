#!/usr/bin/env python3
"""
High Accuracy YOLO Training - Target 95%+ accuracy
"""
import os
os.environ['TORCH_WEIGHTS_ONLY'] = 'False'
from ultralytics import YOLO

DATA_YAML = 'datasets/Helmet-Vest-Belt.v1i.yolov8/data.yaml'

def train_for_95_percent():
    """Training configuration optimized for 95%+ accuracy"""
    
    print("🎯 Training for 95%+ accuracy...")
    
    # Use medium model for better accuracy
    model = YOLO('yolov8m.pt')
    
    # High accuracy parameters
    results = model.train(
        data=DATA_YAML,
        epochs=200,          # More epochs needed
        batch=8,             # Smaller batch for stability
        imgsz=640,           # Full resolution
        project='runs/detect',
        name='ppe_95_accuracy',
        
        # Optimized hyperparameters for accuracy
        lr0=0.01,
        lrf=0.0001,          # Lower final LR
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=5,
        warmup_momentum=0.8,
        
        # Enhanced data augmentation
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.7,           # More scale variation
        shear=2.0,
        perspective=0.0001,
        flipud=0.0,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.15,          # Add mixup for better generalization
        copy_paste=0.1,      # Copy-paste augmentation
        
        # Training settings for accuracy
        patience=30,         # More patience
        save_period=20,
        val=True,
        plots=True,
        device='cpu',
        workers=2,
        cache=True,
        
        # Loss function weights for better detection
        box=0.05,
        cls=0.3,             # Lower class loss weight
        dfl=1.5
    )
    
    # Validate and check accuracy
    metrics = model.val()
    map_score = metrics.box.map50_95
    map50 = metrics.box.map50
    
    print(f"\n🎯 High Accuracy Training Results:")
    print(f"mAP@0.5-0.95: {map_score:.4f} ({map_score*100:.2f}%)")
    print(f"mAP@0.5: {map50:.4f} ({map50*100:.2f}%)")
    
    if map_score >= 0.95:
        print("🎉 SUCCESS! Achieved 95%+ accuracy!")
    elif map_score >= 0.90:
        print("📈 Close! Try fine-tuning or more epochs")
        print("💡 Suggestion: Run fine-tuning with lower learning rate")
    else:
        print("📊 Need improvement. Consider:")
        print("  - More training data")
        print("  - Larger model (yolov8l.pt)")
        print("  - More epochs (300+)")
    
    return map_score

def fine_tune_model():
    """Fine-tune the best model for extra accuracy"""
    
    print("\n🔧 Fine-tuning for maximum accuracy...")
    
    # Load the best trained model
    model = YOLO('runs/detect/ppe_95_accuracy/weights/best.pt')
    
    # Fine-tune with very low learning rate
    model.train(
        data=DATA_YAML,
        epochs=50,
        batch=4,             # Small batch for fine-tuning
        imgsz=640,
        project='runs/detect',
        name='ppe_95_finetuned',
        
        # Very low learning rates
        lr0=0.001,
        lrf=0.00001,
        momentum=0.9,
        weight_decay=0.001,
        
        # Minimal augmentation for fine-tuning
        hsv_h=0.005,
        hsv_s=0.2,
        hsv_v=0.1,
        degrees=2.0,
        translate=0.02,
        scale=0.95,
        mosaic=0.3,
        mixup=0.0,
        
        patience=15,
        device='cpu',
        cache=True
    )
    
    # Final validation
    final_metrics = model.val()
    final_map = final_metrics.box.map50_95
    
    print(f"\n🏆 Final Results After Fine-tuning:")
    print(f"mAP@0.5-0.95: {final_map:.4f} ({final_map*100:.2f}%)")
    
    return final_map

if __name__ == '__main__':
    print("🎯 High Accuracy PPE Detection Training")
    print("=" * 50)
    
    # Main training
    accuracy = train_for_95_percent()
    
    # Fine-tune if close to 95%
    if accuracy >= 0.88:
        final_accuracy = fine_tune_model()
        print(f"\n✅ Final accuracy: {final_accuracy*100:.2f}%")
    else:
        print(f"\n📊 Current accuracy: {accuracy*100:.2f}%")
        print("💡 Consider using yolov8l.pt or more data for 95%+")