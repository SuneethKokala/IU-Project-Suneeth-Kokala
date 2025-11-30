#!/usr/bin/env python3
"""
Advanced YOLO Training for 95+ Accuracy
Trains multiple model sizes and selects the best performing one
"""
import os
os.environ['TORCH_WEIGHTS_ONLY'] = 'False'
from ultralytics import YOLO
import yaml

DATA_YAML = 'datasets/Helmet-Vest-Belt.v1i.yolov8/data.yaml'

def train_multiple_models():
    """Train multiple YOLO models and compare performance"""
    
    models_to_train = [
        ('yolov8n.pt', 'nano', 8),      # Fastest - reduced batch for CPU
        ('yolov8s.pt', 'small', 6),     # Balanced - reduced batch for CPU
    ]
    
    best_model = None
    best_map = 0
    
    for model_path, size_name, batch_size in models_to_train:
        print(f"\n🚀 Training YOLOv8 {size_name} model...")
        
        model = YOLO(model_path)
        
        # Train with optimized hyperparameters
        results = model.train(
            data=DATA_YAML,
            epochs=200,
            batch=batch_size,
            imgsz=640,
            project='runs/detect',
            name=f'ppe_{size_name}',
            
            # Optimized hyperparameters for high accuracy
            lr0=0.01,
            lrf=0.001,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            box=0.05,
            cls=0.5,
            dfl=1.5,
            
            # Data augmentation for better generalization
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=10.0,        # Slight rotation
            translate=0.1,
            scale=0.9,           # Scale variation
            shear=2.0,           # Slight shear
            perspective=0.0001,  # Minimal perspective
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.1,           # Add mixup augmentation
            copy_paste=0.1,      # Add copy-paste augmentation
            
            # Training settings
            patience=30,
            save_period=20,
            val=True,
            plots=True,
            device='cpu'  # Use CPU for macOS
        )
        
        # Get validation mAP
        metrics = model.val()
        current_map = metrics.box.map50_95
        
        print(f"📊 {size_name} model mAP@0.5-0.95: {current_map:.4f}")
        
        if current_map > best_map:
            best_map = current_map
            best_model = (model_path, size_name, current_map)
    
    print(f"\n🏆 Best model: {best_model[1]} with mAP@0.5-0.95: {best_model[2]:.4f}")
    return best_model

def fine_tune_best_model(model_info):
    """Fine-tune the best performing model"""
    model_path, size_name, _ = model_info
    
    print(f"\n🔧 Fine-tuning {size_name} model...")
    
    # Load the best trained model
    model = YOLO(f'runs/detect/ppe_{size_name}/weights/best.pt')
    
    # Fine-tune with reduced learning rate
    model.train(
        data=DATA_YAML,
        epochs=100,
        batch=4,  # Small batch for CPU training
        imgsz=640,
        project='runs/detect',
        name=f'ppe_{size_name}_finetuned',
        
        # Reduced learning rates for fine-tuning
        lr0=0.001,
        lrf=0.0001,
        momentum=0.9,
        weight_decay=0.001,
        
        # Minimal augmentation for fine-tuning
        hsv_h=0.01,
        hsv_s=0.3,
        hsv_v=0.2,
        degrees=5.0,
        translate=0.05,
        scale=0.95,
        
        patience=20,
        save_period=10
    )
    
    # Final validation
    final_metrics = model.val()
    final_map = final_metrics.box.map50_95
    
    print(f"🎯 Final mAP@0.5-0.95: {final_map:.4f}")
    
    if final_map >= 0.95:
        print("🎉 SUCCESS! Achieved 95%+ accuracy!")
    else:
        print(f"📈 Current accuracy: {final_map*100:.2f}% - Consider more training data or epochs")
    
    return final_map

if __name__ == '__main__':
    print("🛡️ Advanced PPE Detection Training")
    print("=" * 50)
    
    # Train multiple models
    best_model = train_multiple_models()
    
    # Fine-tune the best one
    final_accuracy = fine_tune_best_model(best_model)
    
    print(f"\n✅ Training complete! Final accuracy: {final_accuracy*100:.2f}%")