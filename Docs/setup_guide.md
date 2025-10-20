# Behavioral Monitoring Module - Installation & Setup Guide

## 📋 System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimal (< 50MB)
- **Permissions**: Administrator/root access for keyboard/mouse monitoring

## 🔧 Step 1: Install Python Dependencies

### Option A: Using pip (Recommended)
```bash
# Install required packages
pip install pynput psutil

# Optional: Create virtual environment (recommended)
python -m venv behavioral_monitor_env
source behavioral_monitor_env/bin/activate  # On Windows: behavioral_monitor_env\Scripts\activate
pip install pynput psutil
```

### Option B: Using conda
```bash
conda install -c conda-forge pynput psutil
```

### Package Details:
- **pynput**: Monitors keyboard and mouse events
- **psutil**: System and process utilities for application monitoring

## 📁 Step 2: Project Setup

### Create project directory:
```bash
mkdir behavioral_monitor_project
cd behavioral_monitor_project
```

### File structure:
```
behavioral_monitor_project/
├── behavioral_monitor.py    # Main module (from artifact)
├── requirements.txt         # Dependencies
├── config.py               # Configuration (optional)
└── data/                   # Data export directory
```

### Create requirements.txt:
```txt
pynput>=1.7.6
psutil>=5.9.0
```

## 🚀 Step 3: Running the Module

### Basic Usage:
```bash
# Navigate to project directory
cd behavioral_monitor_project

# Run the module
python behavioral_monitor.py
```

### Running in Background:
```bash
# Linux/macOS - run in background
nohup python behavioral_monitor.py > monitor.log 2>&1 &

# Windows - run in background (PowerShell)
Start-Process python -ArgumentList "behavioral_monitor.py" -WindowStyle Hidden
```

## 🔒 Step 4: Permissions Setup

### Windows:
1. **Run as Administrator** - Right-click Command Prompt → "Run as administrator"
2. **Antivirus Exception** - Add script to antivirus whitelist if needed
3. **Windows Defender** - May flag keyboard monitoring, add exception

### macOS:
1. **Terminal Permissions**:
   ```bash
   # Give Terminal accessibility permissions
   System Preferences → Security & Privacy → Privacy → Accessibility
   # Add Terminal to allowed applications
   ```

2. **Python Permissions**:
   ```bash
   # If using system Python, may need to add Python to accessibility
   System Preferences → Security & Privacy → Privacy → Accessibility
   # Add Python or your IDE to allowed applications
   ```

### Linux:
```bash
# Install additional dependencies for X11 (if needed)
sudo apt-get install python3-xlib  # Ubuntu/Debian
sudo yum install python3-xlib      # CentOS/RHEL

# Run with appropriate permissions
sudo python behavioral_monitor.py  # If needed
```

## 📝 Step 5: Basic Test Script

Create `test_monitor.py` to verify installation:

```python
#!/usr/bin/env python3
"""
Test script for behavioral monitoring module
"""
import time
from behavioral_monitor import BehavioralMonitor

def test_installation():
    """Test if all dependencies are working"""
    print("Testing Behavioral Monitor Installation...")
    
    try:
        # Test imports
        import pynput
        import psutil
        print("✅ All dependencies imported successfully")
        
        # Test monitor creation
        monitor = BehavioralMonitor(analysis_window=30)
        print("✅ Monitor object created successfully")
        
        # Test monitoring start (brief)
        print("\n🔄 Starting monitoring test (10 seconds)...")
        print("Please type something and move your mouse...")
        
        monitor.start_monitoring()
        time.sleep(10)
        
        # Get metrics
        metrics = monitor.get_current_metrics()
        monitor.stop_monitoring()
        
        print("✅ Monitoring test completed!")
        print(f"📊 Keystrokes recorded: {metrics['total_keystrokes']}")
        print(f"📊 Mouse events recorded: {metrics['total_mouse_events']}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: pip install pynput psutil")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_installation()
    if success:
        print("\n🎉 Installation successful! Ready to use behavioral monitoring.")
    else:
        print("\n❌ Installation failed. Check error messages above.")
```

Run the test:
```bash
python test_monitor.py
```

## ⚙️ Step 6: Configuration Options

Create `config.py` for custom settings:

```python
# Configuration for Behavioral Monitor

# Analysis settings
ANALYSIS_WINDOW = 60        # seconds to analyze
INACTIVITY_THRESHOLD = 30   # seconds before marking inactive
DATA_RETENTION = 3600       # seconds to keep data (1 hour)

# Export settings
EXPORT_INTERVAL = 300       # auto-export every 5 minutes
EXPORT_DIRECTORY = "./data"

# Monitoring settings
UPDATE_INTERVAL = 1         # metrics update frequency (seconds)
LOG_LEVEL = "INFO"         # DEBUG, INFO, WARNING, ERROR

# Fatigue detection
WPM_BASELINE = 40          # baseline WPM for fatigue calculation
FATIGUE_THRESHOLD = 70     # score above which indicates high fatigue
HEALTH_THRESHOLD = 30      # score below which indicates poor health
```

## 🏃‍♂️ Step 7: Running Examples

### Example 1: Quick Test
```python
from behavioral_monitor import BehavioralMonitor

# Create monitor
monitor = BehavioralMonitor()

# Start monitoring
monitor.start_monitoring()
print("Monitoring started. Type and move mouse for 30 seconds...")

import time
time.sleep(30)

# Get results
metrics = monitor.get_current_metrics()
print(f"WPM: {metrics['typing_metrics']['wpm']}")
print(f"Health Score: {metrics['typing_metrics']['health_score']}")

monitor.stop_monitoring()
```

### Example 2: Continuous Monitoring
```python
from behavioral_monitor import BehavioralMonitor
import time

monitor = BehavioralMonitor()
monitor.start_monitoring()

try:
    while True:
        time.sleep(60)  # Check every minute
        metrics = monitor.get_current_metrics()
        
        # Check for fatigue
        fatigue = monitor.get_fatigue_indicators()
        if fatigue['overall_fatigue_level'] > 70:
            print("⚠️ High fatigue detected! Consider taking a break.")
        
        # Export data every hour
        if int(time.time()) % 3600 == 0:
            monitor.export_data()
            
except KeyboardInterrupt:
    print("Stopping monitor...")
    monitor.stop_monitoring()
```

## 🛠️ Step 8: Troubleshooting

### Common Issues:

#### 1. Permission Denied
```bash
# Solution: Run with elevated privileges
sudo python behavioral_monitor.py  # Linux/macOS
# Windows: Run Command Prompt as Administrator
```

#### 2. Import Error - pynput not found
```bash
# Solution: Reinstall pynput
pip uninstall pynput
pip install pynput
```

#### 3. No events detected
- **Check permissions**: Ensure accessibility permissions granted
- **Check antivirus**: Add script to whitelist
- **Check virtual environment**: Ensure packages installed in correct environment

#### 4. High CPU usage
```python
# Increase update interval in configuration
monitor = BehavioralMonitor(analysis_window=120)  # Longer window
```

#### 5. macOS Catalina+ Issues
```bash
# Grant full disk access to Terminal
System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add Terminal application
```

### Debug Mode:
```python
# Add debug prints
import logging
logging.basicConfig(level=logging.DEBUG)

# Run with debug
monitor = BehavioralMonitor()
monitor.start_monitoring()
```

## 📈 Step 9: Integration Examples

### Web Dashboard Integration:
```python
from flask import Flask, jsonify
from behavioral_monitor import BehavioralMonitor

app = Flask(__name__)
monitor = BehavioralMonitor()
monitor.start_monitoring()

@app.route('/metrics')
def get_metrics():
    return jsonify(monitor.get_current_metrics())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Database Integration:
```python
import sqlite3
import json
from behavioral_monitor import BehavioralMonitor

def save_to_database(metrics):
    conn = sqlite3.connect('behavioral_data.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics
        (timestamp REAL, data TEXT)
    ''')
    
    cursor.execute(
        'INSERT INTO metrics VALUES (?, ?)',
        (metrics['timestamp'], json.dumps(metrics))
    )
    
    conn.commit()
    conn.close()

# Usage
monitor = BehavioralMonitor()
monitor.start_monitoring()

# Periodically save to database
import time
while True:
    time.sleep(300)  # Every 5 minutes
    metrics = monitor.get_current_metrics()
    save_to_database(metrics)
```

## 🎯 Next Steps

1. **Run the test script** to verify installation
2. **Start with basic monitoring** using the main script
3. **Customize configuration** based on your needs
4. **Set up automated exports** for data collection
5. **Integrate with your project** using the API methods

## 📞 Support

If you encounter issues:

1. **Check Python version**: `python --version` (should be 3.7+)
2. **Verify package installation**: `pip list | grep pynput`
3. **Check permissions**: Ensure accessibility permissions granted
4. **Review logs**: Check console output for error messages
5. **Test dependencies**: Run the test script provided

The module is now ready for use in your project! 🚀