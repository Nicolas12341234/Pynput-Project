#!/usr/bin/env python3
"""
Installation Test Script for Behavioral Monitor
This script tests if all dependencies are properly installed
"""

import sys
import time
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ required")
        return False
    else:
        print("✅ Python version compatible")
        return True

def install_dependencies():
    """Install required packages"""
    packages = ['pynput', 'psutil']
    
    print("\n📦 Installing dependencies...")
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
            print(f"💡 Try manually: pip install {package}")
            return False
    
    return True

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🔍 Testing imports...")
    
    try:
        import pynput
        from pynput import keyboard, mouse
        print("✅ pynput imported successfully")
    except ImportError as e:
        print(f"❌ pynput import failed: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil imported successfully")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    try:
        import threading, queue, json, statistics, time
        from collections import deque, defaultdict
        from datetime import datetime, timedelta
        from dataclasses import dataclass, asdict
        print("✅ Standard library imports successful")
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
        return False
    
    return True

def test_permissions():
    """Test if we have required permissions"""
    print("\n🔒 Testing permissions...")
    
    try:
        from pynput import keyboard, mouse
        
        # Test keyboard listener creation
        def dummy_key_handler(key):
            pass
        
        def dummy_mouse_handler(*args):
            pass
        
        # Create listeners without starting them
        kb_listener = keyboard.Listener(on_press=dummy_key_handler)
        mouse_listener = mouse.Listener(on_move=dummy_mouse_handler)
        
        print("✅ Listeners created successfully")
        print("💡 Actual permissions will be tested during monitoring")
        return True
        
    except Exception as e:
        print(f"❌ Permission test failed: {e}")
        print("💡 You may need to grant accessibility permissions")
        return False

def run_quick_test():
    """Run a quick 10-second monitoring test"""
    print("\n🧪 Running monitoring test...")
    print("📝 Please type something and move your mouse in the next 10 seconds...")
    
    try:
        # Import the behavioral monitor
        sys.path.append('.')  # Add current directory to path
        
        # Create a minimal test version
        from pynput import keyboard, mouse
        import threading
        import queue
        
        events_recorded = {'keystrokes': 0, 'mouse_moves': 0, 'mouse_clicks': 0}
        event_queue = queue.Queue()
        
        def on_key_press(key):
            event_queue.put(('keystroke', time.time()))
        
        def on_mouse_move(x, y):
            event_queue.put(('mouse_move', time.time()))
        
        def on_mouse_click(x, y, button, pressed):
            if pressed:
                event_queue.put(('mouse_click', time.time()))
        
        # Start listeners
        kb_listener = keyboard.Listener(on_press=on_key_press)
        mouse_listener = mouse.Listener(
            on_move=on_mouse_move,
            on_click=on_mouse_click
        )
        
        kb_listener.start()
        mouse_listener.start()
        
        # Monitor for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                event_type, timestamp = event_queue.get_nowait()
                events_recorded[event_type] = events_recorded.get(event_type, 0) + 1
            except queue.Empty:
                pass
            time.sleep(0.1)
        
        # Stop listeners
        kb_listener.stop()
        mouse_listener.stop()
        
        # Show results
        print(f"\n📊 Test Results:")
        print(f"   Keystrokes: {events_recorded.get('keystroke', 0)}")
        print(f"   Mouse moves: {events_recorded.get('mouse_move', 0)}")
        print(f"   Mouse clicks: {events_recorded.get('mouse_click', 0)}")
        
        total_events = sum(events_recorded.values())
        if total_events > 0:
            print("✅ Monitoring test successful!")
            return True
        else:
            print("⚠️ No events recorded - check permissions")
            return False
            
    except Exception as e:
        print(f"❌ Monitoring test failed: {e}")
        return False

def show_platform_specific_help():
    """Show platform-specific setup instructions"""
    import platform
    os_name = platform.system().lower()
    
    print(f"\n🖥️ Platform-specific setup ({os_name}):")
    
    if os_name == "darwin":  # macOS
        print("""
        macOS Setup:
        1. System Preferences → Security & Privacy → Privacy → Accessibility
        2. Add Terminal (or your Python IDE) to allowed applications
        3. You may need to add Python itself to the list
        4. For macOS Catalina+: Also add to "Full Disk Access" if needed
        
        If still having issues:
        - Run: sudo python test_installation.py
        - Temporarily disable SIP (not recommended for production)
        """)
    
    elif os_name == "linux":
        print("""
        Linux Setup:
        1. Install X11 development libraries:
           sudo apt-get install python3-xlib  # Ubuntu/Debian
           sudo yum install python3-xlib      # CentOS/RHEL
        
        2. If running in virtual environment, ensure packages are installed there
        
        3. For Wayland users: May need X11 compatibility layer
        
        4. Run with sudo if permission issues persist
        """)
    
    elif os_name == "windows":
        print("""
        Windows Setup:
        1. Run Command Prompt as Administrator
        2. Add script to Windows Defender exclusions if needed
        3. Some antivirus software may block keyboard monitoring
        
        PowerShell alternative:
        Start-Process python -ArgumentList "test_installation.py" -Verb RunAs
        """)

def main():
    """Main installation test function"""
    print("🔧 Behavioral Monitor - Installation Test")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install dependencies
    install_choice = input("\n📦 Install dependencies automatically? (y/n): ").lower().strip()
    if install_choice == 'y':
        if not install_dependencies():
            return False
    else:
        print("💡 Please install manually: pip install pynput psutil")
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Try reinstalling dependencies.")
        return False
    
    # Test permissions
    if not test_permissions():
        show_platform_specific_help()
        return False
    
    # Run monitoring test
    test_choice = input("\n🧪 Run 10-second monitoring test? (y/n): ").lower().strip()
    if test_choice == 'y':
        if not run_quick_test():
            print("\n⚠️ Monitoring test had issues. Check permissions.")
            show_platform_specific_help()
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Installation test completed successfully!")
    print("\nNext steps:")
    print("1. Save the main behavioral_monitor.py script")
    print("2. Run: python behavioral_monitor.py")
    print("3. Check the setup guide for advanced configuration")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Installation test failed. Check error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Installation test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)