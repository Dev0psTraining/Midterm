import requests
import time
import json
import os
import sys
from datetime import datetime

# Configuration
APP_URL = "http://localhost:5000/api/tasks"
LOG_FILE = "health_check.log"
CHECK_INTERVAL = 60  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def check_health():
    """
    Check if the application is responding properly.
    Returns True if healthy, False otherwise.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(APP_URL, timeout=10)
            
            # Check if response is successful
            if response.status_code == 200:
                # Verify we can parse the JSON
                data = response.json()
                if isinstance(data, list):
                    return True
                else:
                    log_message(f"Warning: API returned unexpected data format: {data}")
            else:
                log_message(f"Warning: API returned status code {response.status_code}")
                
        except requests.RequestException as e:
            log_message(f"Error connecting to application: {str(e)}")
            
        # If we get here, there was an issue - retry after delay
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)
    
    return False

def log_message(message):
    """Log a message with timestamp to the log file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    print(log_entry, end="")
    
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)

def main():
    log_message("Health check service started")
    
    while True:
        is_healthy = check_health()
        
        if is_healthy:
            log_message("Application health check: PASSED")
        else:
            log_message("Application health check: FAILED")
            # In a more advanced setup, this could trigger an automatic rollback
            # or send notifications
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_message("Health check service stopped")
        sys.exit(0)