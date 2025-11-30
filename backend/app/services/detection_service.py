import os
import numpy as np
from ultralytics import YOLO
from app.model_manager import ModelManager

class DetectionService:
    def __init__(self):
        self.ppe_model = self._load_ppe_model()
    
    def _load_ppe_model(self):
        manager = ModelManager()
        return manager.load_model()
    
    def detect_ppe(self, image, conf=0.1, iou=0.45):
        results = self.ppe_model(image, conf=conf, iou=iou)
        detections = []
        
        for r in results:
            if r.boxes is not None:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    confidence = float(box.conf[0])
                    coords = box.xyxy[0].tolist()
                    # Fix swapped model labels
                    if cls == 0:  # model says helmet but detects vest
                        class_name = 'vest'
                    elif cls == 1:  # model says safety_vest but detects helmet
                        class_name = 'helmet'
                    else:
                        class_name = f"class_{cls}"
                    
                    # Filter out belt detections
                    if class_name.lower() != 'belt':
                        detections.append({
                            "type": "ppe",
                            "class": class_name,
                            "confidence": confidence,
                            "bbox": coords
                        })
        
        return detections
    

    
    def detect_all(self, image):
        ppe_detections = self.detect_ppe(image)
        
        return {
            "ppe_detections": ppe_detections,
            "total_detections": len(ppe_detections)
        }