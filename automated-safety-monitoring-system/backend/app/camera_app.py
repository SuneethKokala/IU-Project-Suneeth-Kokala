import cv2
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from app.services.detection_service import DetectionService
from app.violation_logger import ViolationLogger

class CameraApp:
    def __init__(self):
        self.detection_service = DetectionService()
        self.violation_logger = ViolationLogger()
        self.violation_start_time = {}  # Track when violation started
        self.violation_threshold = 10  # 10 seconds continuous violation
        self.last_logged_violation = {}  # Prevent duplicate logging
        self.current_violations = {}  # Track current violation status
    
    def check_violations(self, ppe_detections):
        import time
        current_time = time.time()
        
        # Required PPE items
        required_ppe = ['helmet', 'vest']
        detected_ppe = [item['class'].lower() for item in ppe_detections]
        missing_ppe = [item for item in required_ppe if item not in detected_ppe]
        
        employee_id = "UNKNOWN"
        employee_name = "Unknown Worker"
        
        if missing_ppe:
            # Start tracking violation time
            if employee_id not in self.violation_start_time:
                self.violation_start_time[employee_id] = current_time
                self.current_violations[employee_id] = missing_ppe
                print(f"⏱️ PPE violation started - missing {', '.join(missing_ppe)}")
            
            # Check if violation has been continuous for 10 seconds
            violation_duration = current_time - self.violation_start_time[employee_id]
            
            if violation_duration >= self.violation_threshold:
                # Check cooldown to avoid spam (log once per minute after 10-second threshold)
                if employee_id not in self.last_logged_violation or \
                   current_time - self.last_logged_violation.get(employee_id, 0) > 60:
                    
                    self.violation_logger.log_violation(employee_id, employee_name, missing_ppe)
                    self.last_logged_violation[employee_id] = current_time
                    print(f"🚨 PPE VIOLATION ALERT! Continuous for {violation_duration:.1f}s - missing {', '.join(missing_ppe)}")
            else:
                print(f"⚠️ PPE violation ongoing ({violation_duration:.1f}s/{self.violation_threshold}s) - missing {', '.join(missing_ppe)}")
        else:
            # Reset violation tracking when PPE is detected
            if employee_id in self.violation_start_time:
                duration = current_time - self.violation_start_time[employee_id]
                print(f"✅ PPE violation resolved after {duration:.1f}s")
                del self.violation_start_time[employee_id]
                if employee_id in self.current_violations:
                    del self.current_violations[employee_id]
            else:
                print(f"✅ All required PPE detected")
    
    def run(self):
        # Try different camera indices
        cap = None
        for i in range(3):
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                ret, frame = test_cap.read()
                if ret:
                    print(f"✅ Using camera index {i}")
                    cap = test_cap
                    break
                else:
                    test_cap.release()
            else:
                test_cap.release()
        
        if cap is None:
            print("❌ Error: No working camera found")
            print("Please check camera permissions and availability")
            return
        
        print("✅ Camera opened successfully")
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"❌ Error: Could not read frame (processed {frame_count} frames)")
                print("Camera may be in use by another application or permission denied")
                break
            
            frame_count += 1
            
            # Get detections
            result = self.detection_service.detect_all(frame)
            
            # Check for violations
            self.check_violations(result['ppe_detections'])
            
            # Draw PPE detections with corrected labels
            annotated_frame = frame.copy()
            for detection in result['ppe_detections']:
                bbox = detection['bbox']
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"{detection['class']} {detection['confidence']:.2f}"
                cv2.putText(annotated_frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Add frame counter
            cv2.putText(annotated_frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            cv2.imshow('Safety Monitoring System', annotated_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    app = CameraApp()
    app.run()