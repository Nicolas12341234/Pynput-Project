# 🖥️ Behavioral Monitor Setup Guide - Windows 11 with Python 3.10.7

## 📋 Prerequisites
- ✅ Windows 11
- ✅ Python 3.10.7 (Perfect version!)
- 🔧 Administrator privileges
- 📁 Basic command line knowledge

---

## 🚀 Step-by-Step Installation Guide

### Step 1: Verify Python Installation
Open **Command Prompt** or **PowerShell** and verify your Python installation:

```cmd
python --version
```
**Expected output:** `Python 3.10.7`

```cmd
pip --version
```
**Expected output:** `pip 22.x.x from ...`

If Python is not recognized, add it to your PATH or reinstall Python with "Add to PATH" checked.

---

### Step 2: Create Project Directory

```cmd
# Create project folder on Desktop (or anywhere you prefer)
cd %USERPROFILE%\Desktop
mkdir BehavioralMonitor
cd BehavioralMonitor

# Verify location
echo %cd%
```

**Expected location:** `C:\Users\YourUsername\Desktop\BehavioralMonitor`

---

### Step 3: Create Virtual Environment

```cmd
# Create virtual environment named 'monitor_env'
python -m venv monitor_env

# Verify creation
dir monitor_env
```

**You should see folders:** `Include`, `Lib`, `Scripts`, `pyvenv.cfg`

---

### Step 4: Activate Virtual Environment

```cmd
# Activate the virtual environment
monitor_env\Scripts\activate
```

**Your prompt should change to:**
```cmd
(monitor_env) C:\Users\YourUsername\Desktop\BehavioralMonitor>
```

**✅ Success indicator:** The `(monitor_env)` prefix shows the virtual environment is active.

---

### Step 5: Install Dependencies

```cmd
# Upgrade pip first (recommended)
python -m pip install --upgrade pip

# Install required packages
pip install pynput==1.7.6
pip install psutil==5.9.4

# Verify installations
pip list
```

**Expected output should include:**
```
Package    Version
---------- -------
pip        xx.x.x
psutil     5.9.4
pynput     1.7.6
setuptools xx.x.x
...
```

---

### Step 6: Create Requirements File

```cmd
# Generate requirements.txt for future use
pip freeze > requirements.txt

# View the file
type requirements.txt
```

**Contents should be:**
```
psutil==5.9.4
pynput==1.7.6
six==1.16.0
```

---

### Step 7: Download Project Files

Create the main monitoring script:

```cmd
# Create the main Python file
echo. > behavioral_monitor.py

# Create test script
echo. > test_installation.py
```

Now copy the code from the artifacts into these files using Notepad or your preferred editor:

```cmd
# Open files for editing
notepad behavioral_monitor.py
notepad test_installation.py
```

---

### Step 8: Windows 11 Permissions Setup

#### A. Run as Administrator (Required)
1. **Close current Command Prompt**
2. **Right-click** on Command Prompt in Start Menu
3. **Select "Run as administrator"**
4. **Navigate back to project:**
   ```cmd
   cd %USERPROFILE%\Desktop\BehavioralMonitor
   monitor_env\Scripts\activate
   ```

#### B. Windows Security Configuration
1. **Open Windows Security:**
   - Press `Win + I` → Privacy & Security → Windows Security
   - Click "Virus & threat protection"

2. **Add Exclusions:**
   - Click "Manage settings" under Virus & threat protection settings
   - Click "Add or remove exclusions"
   - Add folder: `C:\Users\YourUsername\Desktop\BehavioralMonitor`

#### C. Privacy Settings (Important!)
1. **Open Settings:** `Win + I`
2. **Go to:** Privacy & Security → Privacy → App permissions
3. **Enable for Python/Terminal:**
   - **Microphone:** Off (not needed)
   - **Camera:** Off (not needed)  
   - **Location:** Off (not needed)
   - **Diagnostic data:** On (recommended)

---

### Step 9: Test Installation

```cmd
# Make sure virtual environment is active
(monitor_env) C:\Users\YourUsername\Desktop\BehavioralMonitor>

# Run the test script
python test_installation.py
```

**If test script asks for permissions:**
- Type `y` to install dependencies (if prompted)
- Type `y` to run the monitoring test
- **Type something and move your mouse** during the 10-second test

**Expected successful output:**
```
🔧 Behavioral Monitor - Installation Test
==================================================
🐍 Python version: 3.10.7
✅ Python version compatible
✅ pynput imported successfully
✅ psutil imported successfully
✅ Standard library imports successful
✅ Listeners created successfully
🧪 Running monitoring test...
📝 Please type something and move your mouse in the next 10 seconds...

📊 Test Results:
   Keystrokes: 15
   Mouse moves: 89
   Mouse clicks: 3
✅ Monitoring test successful!
🎉 Installation test completed successfully!
```

---

### Step 10: Run Main Monitor

```cmd
# Run the behavioral monitor
python behavioral_monitor.py
```

**Expected output:**
```
Starting behavioral monitoring...
Behavioral monitoring started successfully

Behavioral monitoring is running...
Press Ctrl+C to stop and view results
Type something and move your mouse to generate data

--- Metrics Update (Session: 10.1s) ---
Typing: WPM=42.3, Health=75.8, Fatigue=28.2
Mouse: Speed=145.2px/s, Smoothness=78.1, Active=62.4%
Activity: Keystrokes=89, Mouse Events=156
```

---

## 🔧 Windows 11 Specific Troubleshooting

### Issue 1: "Access Denied" or Permission Errors
**Solution:**
```cmd
# Ensure running as Administrator
# Right-click Command Prompt → "Run as administrator"

# If still issues, temporarily disable real-time protection:
# Windows Security → Virus & threat protection → Real-time protection (Off)
# Remember to turn it back on after testing!
```

### Issue 2: Python Not Found
**Solution:**
```cmd
# Use py launcher instead
py --version
py -m venv monitor_env
py -m pip install pynput psutil
```

### Issue 3: Virtual Environment Won't Activate
**Solution:**
```cmd
# Try PowerShell instead of Command Prompt
# Or use full path
C:\Users\YourUsername\Desktop\BehavioralMonitor\monitor_env\Scripts\activate.bat
```

### Issue 4: Antivirus Blocking
**Solution:**
1. **Temporarily disable real-time scanning**
2. **Add entire project folder to exclusions**
3. **Run the test, then re-enable protection**

### Issue 5: No Events Recorded
**Solution:**
1. **Ensure running as Administrator**
2. **Check Windows Privacy settings**
3. **Try running in compatibility mode**

---

## 📁 Final Project Structure

```
BehavioralMonitor/
├── monitor_env/               # Virtual environment
│   ├── Scripts/
│   │   ├── activate.bat      # Activation script
│   │   ├── python.exe        # Python interpreter
│   │   └── ...
│   └── Lib/                  # Installed packages
├── behavioral_monitor.py     # Main monitoring script
├── test_installation.py     # Test script
├── requirements.txt          # Dependencies
└── data/                     # Data exports (created automatically)
```

---

## 🎯 Daily Usage Commands

### Starting Your Session:
```cmd
# 1. Open Command Prompt as Administrator
# 2. Navigate to project
cd %USERPROFILE%\Desktop\BehavioralMonitor

# 3. Activate virtual environment
monitor_env\Scripts\activate

# 4. Run monitor
python behavioral_monitor.py
```

### Creating Desktop Shortcut:
Create `start_monitor.bat`:
```batch
@echo off
cd /d "%USERPROFILE%\Desktop\BehavioralMonitor"
call monitor_env\Scripts\activate
python behavioral_monitor.py
pause
```

**Right-click the .bat file → "Run as administrator"**

---

## 🔄 Environment Management Commands

```cmd
# Activate virtual environment
monitor_env\Scripts\activate

# Deactivate virtual environment
deactivate

# Update packages
pip install --upgrade pynput psutil

# Remove virtual environment (if needed)
rmdir /s monitor_env

# Recreate environment from requirements
python -m venv monitor_env
monitor_env\Scripts\activate
pip install -r requirements.txt
```

---

## ⚠️ Important Windows 11 Notes

1. **Always run as Administrator** for keyboard/mouse monitoring
2. **Add project folder to antivirus exclusions**
3. **Windows Defender may flag the script** - this is normal for input monitoring
4. **Keep virtual environment activated** while working with the project
5. **Privacy settings** don't typically affect this type of monitoring
6. **UAC (User Account Control)** should remain enabled for security

---

## 🎉 Success Checklist

- [ ] Python 3.10.7 verified
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] Test script runs without errors
- [ ] Main monitor records events
- [ ] No permission errors
- [ ] Antivirus exclusions added
- [ ] Running as Administrator

**You're all set! The behavioral monitor is ready for use on Windows 11.** 🚀

---

## 📞 Quick Help Commands

```cmd
# Check if venv is active
echo %VIRTUAL_ENV%

# Check Python location
where python

# Check installed packages
pip list

# Check package details
pip show pynput

# Reinstall if corrupted
pip uninstall pynput psutil
pip install pynput psutil
```