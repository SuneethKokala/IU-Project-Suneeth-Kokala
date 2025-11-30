#!/usr/bin/env python3
import cv2
from app.model_manager import ModelManager

def test_latest_model():
    # Load latest model
    manager = ModelManager()
    manager.list_models()
    model = manager.load_model()
    
    # Test with webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("🎥 Testing model with live camera feed")
    print("Press 'q' to quit")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Run detection
        results = model(frame, conf=0.3)
        annotated = results[0].plot()
        
        # Show detections info
        if results[0].boxes is not None:
            detections = []
            for box in results[0].boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names.get(cls, f"class_{cls}")
                detections.append(f"{class_name}({conf:.2f})")
            
            if detections:
                cv2.putText(annotated, f"Detected: {', '.join(detections)}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
        
        cv2.imshow('Latest Model Test', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_latest_model()