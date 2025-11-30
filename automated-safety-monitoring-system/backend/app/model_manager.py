import os
from ultralytics import YOLO

class ModelManager:
    def __init__(self):
        self.available_models = self._scan_models()
    
    def _scan_models(self):
        models = {}
        base_path = 'runs/detect'
        
        if os.path.exists(base_path):
            for folder in os.listdir(base_path):
                weights_path = os.path.join(base_path, folder, 'weights', 'best.pt')
                if os.path.exists(weights_path):
                    models[folder] = weights_path
        
        return models
    
    def list_models(self):
        print("📋 Available trained models:")
        for name, path in self.available_models.items():
            size = os.path.getsize(path) / (1024*1024)  # MB
            print(f"  • {name}: {path} ({size:.1f}MB)")
    
    def load_model(self, model_name=None):
        if model_name and model_name in self.available_models:
            path = self.available_models[model_name]
            print(f"✅ Loading {model_name}: {path}")
            return YOLO(path)
        
        # Auto-select best model (highest epoch count or latest)
        priority = ['ppe_200_epochs', 'ppe_100_epochs', 'helmet_vest_optimized2']
        for p in priority:
            if p in self.available_models:
                path = self.available_models[p]
                print(f"✅ Auto-selected {p}: {path}")
                return YOLO(path)
        
        # Fallback to any available model
        if self.available_models:
            name, path = next(iter(self.available_models.items()))
            print(f"✅ Using {name}: {path}")
            return YOLO(path)
        
        print("⚠️ No trained models found, using default")
        return YOLO('yolov8n.pt')

if __name__ == "__main__":
    manager = ModelManager()
    manager.list_models()