# main.py - Main application entry point
import sys
import os
import argparse

# Add app to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def run_dashboard():
    """Start the web dashboard"""
    from app.web.dashboard import app
    import os
    port = int(os.environ.get('PORT', 3001))
    debug_mode = os.environ.get('PORT') is None
    print("🌐 Starting Safety Monitoring Dashboard...")
    print(f"📊 Access dashboard at: http://localhost:{port}")
    print("👤 Login: supervisor / admin123")
    app.run(debug=debug_mode, host='0.0.0.0', port=port, use_reloader=False)

def run_detection():
    """Start real-time PPE detection"""
    from app.camera_app import CameraApp
    print("📹 Starting real-time PPE detection...")
    print("❌ Press 'q' to quit")
    app = CameraApp()
    app.run()

def train_model():
    """Train YOLO model"""
    from models.yolo_trainer import train_model
    print("🤖 Starting YOLO model training...")
    train_model()



def main():
    parser = argparse.ArgumentParser(description='Safety Monitoring System')
    parser.add_argument('command', choices=['dashboard', 'detect', 'train-model'], 
                       help='Command to run')
    
    args = parser.parse_args()
    
    print("🛡️ Safety Monitoring System v1.0.0")
    print("=" * 50)
    
    if args.command == 'dashboard':
        run_dashboard()
    elif args.command == 'detect':
        run_detection()
    elif args.command == 'train-model':
        train_model()


if __name__ == '__main__':
    main()