# dashboard.py - Supervisor Dashboard
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file
from flask_cors import CORS
import json
import os
import sys
import signal
from datetime import datetime
import threading
import pandas as pd
from io import BytesIO

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from app.services.detection_service import DetectionService
from app.database import DatabaseManager
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import base64

app = Flask(__name__, template_folder='../../templates')
app.secret_key = 'safety_monitoring_secret_key'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# Enable CORS for React frontend
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://localhost:3001'], 
     allow_headers=['Content-Type', 'Authorization'], 
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])


# Database and detection service
db_manager = DatabaseManager()
detection_service = DetectionService()

# Fallback authentication
SUPERVISOR_USERNAME = "supervisor"
SUPERVISOR_PASSWORD = "admin123"

# Global variables for real-time data
violation_history = []
camera_process = None

def load_violations():
    """Load violations from database or log file"""
    global violation_history
    try:
        if db_manager.connected:
            # Load from database
            violation_history = db_manager.get_violations()
        else:
            # Fallback to file
            log_path = 'data/logs/ppe_violations.log'
            if os.path.exists(log_path):
                with open(log_path, 'r') as f:
                    violation_history = [json.loads(line.strip()) for line in f if line.strip()]
    except Exception as e:
        print(f"Error loading violations: {e}")

@app.route('/')
def login():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    # Handle both form data and JSON
    if request.is_json or request.content_type == 'application/json':
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
    else:
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
    
    print(f"Login attempt - Username: '{username}', Password: '{password}'")
    print(f"Expected - Username: '{SUPERVISOR_USERNAME}', Password: '{SUPERVISOR_PASSWORD}'")
    
    # Use hardcoded credentials only
    if username == SUPERVISOR_USERNAME and password == SUPERVISOR_PASSWORD:
        session['logged_in'] = True
        session['supervisor_name'] = 'Default Supervisor'
        session['supervisor_username'] = username
        session.permanent = False
        
        # Return JSON response for API calls
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return redirect(url_for('dashboard'))
    else:
        # Return JSON error for API calls
        if request.is_json or request.content_type == 'application/json':
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        else:
            return render_template('login.html', error='Invalid credentials')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    load_violations()
    return render_template('dashboard.html')

@app.route('/employees')
def employees():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    return render_template('employees.html')

@app.route('/api/violations')
def get_violations():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    load_violations()
    return jsonify({
        'history': violation_history[-100:]  # Last 100 violations
    })

@app.route('/api/mark_notified', methods=['POST'])
def mark_notified():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        violation_timestamp = data.get('violation_id')
        
        if violation_timestamp is None:
            return jsonify({'error': 'Missing violation timestamp'}), 400
        
        # Load current violations
        global violation_history
        load_violations()
        
        # Find violation by timestamp
        for i, violation in enumerate(violation_history):
            if violation.get('timestamp') == violation_timestamp:
                violation_history[i]['notified'] = True
                violation_history[i]['notified_at'] = datetime.now().isoformat()
                violation_history[i]['notified_by'] = session.get('supervisor_username', 'supervisor')
                
                # Update database if connected
                if db_manager.connected:
                    try:
                        db_manager.update_violation_notification(violation_timestamp, True)
                    except Exception as db_error:
                        print(f"Database update error: {db_error}")
                
                # Save back to file
                os.makedirs('data/logs', exist_ok=True)
                with open('data/logs/ppe_violations.log', 'w') as f:
                    for v in violation_history:
                        f.write(json.dumps(v) + '\n')
                
                # Update Excel file
                update_excel_notification(violation)
                
                return jsonify({'success': True})
        
        return jsonify({'error': 'Violation not found'}), 404
            
    except Exception as e:
        print(f"Mark notified error: {e}")
        return jsonify({'error': str(e)}), 500

def update_excel_notification(violation):
    """Update Excel file with notification status"""
    try:
        excel_path = 'data/reports/ppe_violations.xlsx'
        os.makedirs('data/reports', exist_ok=True)
        
        # Load existing Excel or create new
        if os.path.exists(excel_path):
            df = pd.read_excel(excel_path)
        else:
            df = pd.DataFrame()
        
        # Create new row for this violation
        timestamp = datetime.fromisoformat(violation['timestamp'].replace('Z', '+00:00'))
        new_row = {
            'Date': timestamp.strftime('%Y-%m-%d'),
            'Time': timestamp.strftime('%H:%M:%S'),
            'Employee ID': violation.get('employee_id', 'Unknown'),
            'Employee Name': violation.get('employee_name', 'Unknown'),
            'Missing PPE': ', '.join(violation.get('missing_ppe', [])),
            'Location': violation.get('location', 'Main Camera'),
            'Severity': 'High' if len(violation.get('missing_ppe', [])) > 1 else 'Medium',
            'Employee Notified': 'Yes'
        }
        
        # Check if violation already exists in Excel
        violation_exists = False
        if not df.empty:
            for idx, row in df.iterrows():
                if (row['Employee ID'] == new_row['Employee ID'] and 
                    row['Date'] == new_row['Date'] and 
                    row['Time'] == new_row['Time']):
                    # Update existing row
                    df.loc[idx, 'Employee Notified'] = 'Yes'
                    violation_exists = True
                    break
        
        # Add new row if not exists
        if not violation_exists:
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Save Excel file
        df.to_excel(excel_path, index=False)
        print(f"✅ Excel updated: {excel_path}")
        
    except Exception as e:
        print(f"Excel update error: {e}")

@app.route('/api/get_active_violations')
def get_active_violations():
    """Get violations that need alerts (not notified)"""
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        load_violations()
        active_violations = []
        
        # Get all unnotified violations (these are already filtered by 10-second rule in camera)
        for violation in violation_history:
            if not violation.get('notified', False):
                active_violations.append(violation)
        
        return jsonify({'violations': active_violations})
        
    except Exception as e:
        print(f"Active violations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    global camera_process
    try:
        import subprocess
        import signal
        
        # Kill any existing camera processes first
        try:
            subprocess.run(['pkill', '-f', 'run.py camera'], check=False)
        except:
            pass
        
        # Get the project directory
        project_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Start camera detection using subprocess
        camera_process = subprocess.Popen(
            ['python3', 'run.py', 'camera'],
            cwd=project_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Give it a moment to start
        import time
        time.sleep(1)
        
        # Check if process is still running
        if camera_process.poll() is None:
            return jsonify({'success': True, 'message': 'PPE detection started successfully'})
        else:
            # Process died immediately, get error
            stdout, stderr = camera_process.communicate()
            error_msg = stderr.decode() if stderr else 'Unknown error'
            return jsonify({'error': f'Detection failed to start: {error_msg}'}), 500
        
    except Exception as e:
        print(f"Camera start error: {e}")
        return jsonify({'error': f'Failed to start detection: {str(e)}'}), 500

@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    global camera_process
    try:
        import signal
        import subprocess
        
        # Kill all python processes running camera detection
        try:
            subprocess.run(['pkill', '-f', 'run.py camera'], check=False)
        except:
            pass
        
        # Kill the specific process if we have it
        if camera_process and camera_process.poll() is None:
            try:
                # Kill the entire process group
                os.killpg(os.getpgid(camera_process.pid), signal.SIGTERM)
                camera_process.wait(timeout=3)
            except:
                # Force kill if graceful termination fails
                try:
                    os.killpg(os.getpgid(camera_process.pid), signal.SIGKILL)
                except:
                    pass
        
        camera_process = None
        return jsonify({'success': True, 'message': 'PPE detection stopped successfully'})
        
    except Exception as e:
        print(f"Camera stop error: {e}")
        return jsonify({'error': f'Failed to stop detection: {str(e)}'}), 500

@app.route('/api/clear_data', methods=['POST'])
def clear_data():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    global violation_history
    try:
        # Clear database if connected
        if db_manager.connected:
            db_manager.clear_violations()
        
        # Clear log file
        log_path = 'data/logs/ppe_violations.log'
        if os.path.exists(log_path):
            open(log_path, 'w').close()
        
        # Clear in-memory data
        violation_history = []
        
        return jsonify({'success': True, 'message': 'All violation data cleared'})
        
    except Exception as e:
        print(f"Clear data error: {e}")
        return jsonify({'error': f'Failed to clear data: {str(e)}'}), 500



@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Read image
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image format'}), 400
        
        # Detect PPE
        result = detection_service.detect_all(image)
        ppe_detections = result['ppe_detections']
        
        # Check for missing PPE
        detected_classes = [item['class'].lower() for item in ppe_detections]
        required_ppe = ['helmet', 'vest']
        missing_ppe = [item for item in required_ppe if item not in detected_classes]
        
        # Draw detections on image
        annotated_image = image.copy()
        for detection in ppe_detections:
            bbox = detection['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{detection['class']} {detection['confidence']:.2f}"
            cv2.putText(annotated_image, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Convert annotated image to base64
        _, buffer = cv2.imencode('.jpg', annotated_image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'detections': ppe_detections,
            'missing_ppe': missing_ppe,
            'has_violations': len(missing_ppe) > 0,
            'annotated_image': f'data:image/jpeg;base64,{img_base64}',
            'message': f'Missing PPE: {", ".join(missing_ppe)}' if missing_ppe else 'All required PPE detected'
        })
        
    except Exception as e:
        print(f"Image upload error: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

@app.route('/api/employees')
def get_employees():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        employees = db_manager.get_employees() if db_manager.connected else []
        return jsonify({'employees': employees})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/add_employee', methods=['POST'])
def add_employee():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        employee_id = data.get('employee_id', '').strip()
        name = data.get('name', '').strip()
        department = data.get('department', '').strip()
        position = data.get('position', '').strip()
        
        if not all([employee_id, name, department, position]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if db_manager.connected:
            success = db_manager.add_employee(employee_id, name, department, position)
            if success:
                return jsonify({'success': True, 'message': 'Employee added successfully'})
            else:
                return jsonify({'error': 'Failed to add employee'}), 500
        else:
            return jsonify({'error': 'Database not connected'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_employee', methods=['POST'])
def delete_employee():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        employee_id = data.get('employee_id', '').strip()
        
        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400
        
        if db_manager.connected:
            success = db_manager.delete_employee(employee_id)
            if success:
                return jsonify({'success': True, 'message': 'Employee deleted successfully'})
            else:
                return jsonify({'error': 'Failed to delete employee'}), 500
        else:
            return jsonify({'error': 'Database not connected'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export_excel')
def export_excel():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Read violations directly from file
        violations_data = []
        log_path = 'data/logs/ppe_violations.log'
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                for line in f:
                    if line.strip():
                        violations_data.append(json.loads(line.strip()))
        
        if not violations_data:
            return jsonify({'error': 'No violations to export'}), 400
        
        print(f"Exporting {len(violation_history)} violations to Excel")
        
        # Prepare data for Excel
        excel_data = []
        for i, violation in enumerate(violations_data):
            try:
                # Parse timestamp safely
                timestamp_str = violation.get('timestamp', '')
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        # ISO format
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                        except:
                            # Fallback parsing
                            timestamp = datetime.strptime(timestamp_str.split('+')[0], '%Y-%m-%dT%H:%M:%S')
                    else:
                        # Try parsing as simple format
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                else:
                    timestamp = datetime.now()
                
                # Get missing PPE safely
                missing_ppe = violation.get('missing_ppe', [])
                if isinstance(missing_ppe, str):
                    try:
                        missing_ppe = json.loads(missing_ppe)
                    except:
                        missing_ppe = [missing_ppe]
                elif not isinstance(missing_ppe, list):
                    missing_ppe = []
                
                # Check notification status
                notified = violation.get('notified', False)
                notified_at = violation.get('notified_at', '')
                
                excel_data.append({
                    'Date': timestamp.strftime('%Y-%m-%d'),
                    'Time': timestamp.strftime('%H:%M:%S'),
                    'Employee ID': violation.get('employee_id', 'Unknown'),
                    'Employee Name': violation.get('employee_name', 'Unknown'),
                    'Missing PPE': ', '.join(missing_ppe) if missing_ppe else 'None',
                    'Location': violation.get('location', 'Main Camera'),
                    'Severity': 'High' if len(missing_ppe) > 1 else 'Medium' if missing_ppe else 'Low',
                    'Employee Notified': 'Yes' if notified else 'No'
                })
                
            except Exception as row_error:
                print(f"Error processing violation {i}: {row_error}")
                # Add a basic row with error info
                excel_data.append({
                    'Date': datetime.now().strftime('%Y-%m-%d'),
                    'Time': datetime.now().strftime('%H:%M:%S'),
                    'Employee ID': 'ERROR',
                    'Employee Name': f'Error processing row {i}',
                    'Missing PPE': str(row_error),
                    'Location': 'Error',
                    'Severity': 'Error',
                    'Employee Notified': 'No'
                })
        
        if not excel_data:
            return jsonify({'error': 'No valid data to export'}), 400
        
        print(f"Prepared {len(excel_data)} rows for Excel export")
        
        # Create DataFrame
        df = pd.DataFrame(excel_data)
        
        # Create Excel file in memory
        output = BytesIO()
        
        try:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='PPE Violations', index=False)
                
                # Get workbook and worksheet for formatting
                try:
                    workbook = writer.book
                    worksheet = writer.sheets['PPE Violations']
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if cell.value and len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max(max_length + 2, 10), 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                except Exception as format_error:
                    print(f"Warning: Could not format Excel file: {format_error}")
                    # Continue without formatting
        
        except Exception as excel_error:
            print(f"Excel creation error: {excel_error}")
            return jsonify({'error': f'Failed to create Excel file: {str(excel_error)}'}), 500
        
        output.seek(0)
        
        # Generate filename with current date
        filename = f"PPE_Violations_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        print(f"Sending Excel file: {filename}")
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        print(f"Excel export error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/logs', exist_ok=True)
    port = int(os.environ.get('PORT', 3001))
    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False, threaded=True)