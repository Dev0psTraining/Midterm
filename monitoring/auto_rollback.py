import requests
import time
import json
import os
import subprocess
import sys
from datetime import datetime
from flask import Flask, render_template, jsonify

# Configuration
APP_URL = "http://localhost:5000/api/tasks"
LOG_FILE = "health_check.log"
STATUS_FILE = "app_status.json"
CHECK_INTERVAL = 30  # seconds
FAILURE_THRESHOLD = 3  # consecutive failures before rollback
ANSIBLE_PATH = "../infrastructure/ansible"

# Setup Flask application for dashboard
dashboard = Flask(__name__)

def update_status(is_healthy, message):
    """Update the status file with current application status"""
    status = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "healthy": is_healthy,
        "message": message,
        "last_deployment": get_deployment_info(),
        "last_check": datetime.now().isoformat()
    }
    
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=2)
    
    return status

def get_deployment_info():
    """Get current deployment information"""
    try:
        # Run command to check which deployment is active
        result = subprocess.run(
            ["readlink", "-f", "/opt/taskmanager/current"],
            capture_output=True, text=True, check=True
        )
        
        path = result.stdout.strip()
        if path.endswith("/blue"):
            return "blue"
        elif path.endswith("/green"):
            return "green"
        else:
            return "unknown"
    except Exception as e:
        return f"Error: {str(e)}"

def check_health():
    """Check if the application is responding properly"""
    try:
        response = requests.get(APP_URL, timeout=10)
        
        if response.status_code == 200:
            # Verify we can parse the JSON
            data = response.json()
            if isinstance(data, list):
                return True, "Application is healthy"
            else:
                return False, f"API returned unexpected data format: {data}"
        else:
            return False, f"API returned status code {response.status_code}"
            
    except requests.RequestException as e:
        return False, f"Error connecting to application: {str(e)}"

def perform_rollback():
    """Execute Ansible rollback playbook"""
    log_message("Initiating automatic rollback")
    
    try:
        result = subprocess.run(
            ["ansible-playbook", "rollback.yml"],
            cwd=ANSIBLE_PATH,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            log_message("Rollback completed successfully")
            return True
        else:
            log_message(f"Rollback failed: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"Error during rollback: {str(e)}")
        return False

def log_message(message):
    """Log a message with timestamp to the log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry, end="")
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

# Dashboard routes
@dashboard.route('/')
def index():
    """Dashboard home page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Application Status Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .status-panel { padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .healthy { background-color: #d4edda; }
            .unhealthy { background-color: #f8d7da; }
            .status-info { display: flex; flex-wrap: wrap; }
            .info-item { margin-right: 30px; margin-bottom: 10px; }
            h2 { margin-top: 0; }
            .log-container { max-height: 300px; overflow-y: auto; background-color: #f8f9fa; 
                             padding: 10px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>TaskManager Application Status</h1>
        
        <div id="status-panel" class="status-panel">
            <h2 id="status-title">Loading status...</h2>
            <div class="status-info">
                <div class="info-item">
                    <strong>Last Check:</strong> <span id="last-check">-</span>
                </div>
                <div class="info-item">
                    <strong>Active Deployment:</strong> <span id="deployment">-</span>
                </div>
                <div class="info-item">
                    <strong>Status Message:</strong> <span id="status-message">-</span>
                </div>
            </div>
        </div>
        
        <h2>Recent Logs</h2>
        <div class="log-container" id="logs">
            Loading logs...
        </div>
        
        <script>
            // Function to update dashboard with latest status
            function updateStatus() {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        // Update status panel
                        const statusPanel = document.getElementById('status-panel');
                        statusPanel.className = 'status-panel ' + (data.healthy ? 'healthy' : 'unhealthy');
                        
                        document.getElementById('status-title').textContent = 
                            data.healthy ? 'Application is Healthy' : 'Application is Unhealthy';
                        
                        document.getElementById('last-check').textContent = 
                            new Date(data.last_check).toLocaleString();
                            
                        document.getElementById('deployment').textContent = 
                            data.last_deployment;
                            
                        document.getElementById('status-message').textContent = 
                            data.message;
                    })
                    .catch(err => {
                        console.error('Error fetching status:', err);
                    });
                    
                // Load logs
                fetch('/api/logs')
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('logs').innerHTML = 
                            '<pre>' + data + '</pre>';
                    })
                    .catch(err => {
                        console.error('Error fetching logs:', err);
                    });
            }
            
            // Update initially and every 10 seconds
            updateStatus();
            setInterval(updateStatus, 10000);
        </script>
    </body>
    </html>
    """
    return html

@dashboard.route('/api/status')
def status_api():
    """API endpoint to get current status"""
    try:
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)
        return jsonify(status)
    except FileNotFoundError:
        return jsonify({"error": "Status not available yet"})

@dashboard.route('/api/logs')
def get_logs():
    """API endpoint to get recent logs"""
    try:
        with open(LOG_FILE, "r") as f:
            # Get last 50 lines
            lines = f.readlines()[-50:]
        return "".join(lines)
    except FileNotFoundError:
        return "No logs available yet."

def run_dashboard():
    """Run the dashboard in a separate thread"""
    from threading import Thread
    Thread(target=lambda: dashboard.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)).start()

def main():
    log_message("Health check and auto-rollback service started")
    
    # Initialize dashboard
    run_dashboard()
    
    failure_count = 0
    
    while True:
        is_healthy, message = check_health()
        
        status = update_status(is_healthy, message)
        
        if is_healthy:
            log_message("Application health check: PASSED")
            failure_count = 0
        else:
            log_message(f"Application health check: FAILED - {message}")
            failure_count += 1
            
            if failure_count >= FAILURE_THRESHOLD:
                log_message(f"Threshold reached: {failure_count} consecutive failures")
                if perform_rollback():
                    failure_count = 0
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("Health check service stopped")
        sys.exit(0)