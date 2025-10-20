import time
import threading
import json
import statistics
from collections import deque, defaultdict
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import queue
import psutil

try:
    from pynput import keyboard, mouse
    from pynput.keyboard import Key
except ImportError:
    print("Please install pynput: pip install pynput")
    raise

@dataclass
class KeystrokeData:
    """Stores metadata about keystrokes without actual key content"""
    timestamp: float
    key_type: str  # 'letter', 'number', 'space', 'special', 'modifier'
    is_modifier: bool
    press_duration: Optional[float] = None

@dataclass
class MouseData:
    """Stores mouse movement and click data"""
    timestamp: float
    x: int
    y: int
    action: str  # 'move', 'click', 'scroll'
    button: Optional[str] = None
    scroll_direction: Optional[str] = None

@dataclass
class TypingMetrics:
    """Comprehensive typing analysis metrics"""
    wpm: float
    raw_wpm: float
    accuracy_score: float
    rhythm_consistency: float
    fatigue_score: float
    health_score: float
    avg_keystroke_interval: float
    keystroke_variance: float
    pause_frequency: float
    typing_bursts: int

@dataclass
class MouseMetrics:
    """Mouse activity analysis metrics"""
    total_distance: float
    avg_speed: float
    click_frequency: float
    scroll_frequency: float
    movement_smoothness: float
    idle_periods: int
    active_time_percentage: float

class BehavioralMonitor:
    def __init__(self, 
                 analysis_window: int = 60,  # seconds
                 inactivity_threshold: int = 30,  # seconds
                 data_retention: int = 3600):  # seconds (1 hour)
        
        # Configuration
        self.analysis_window = analysis_window
        self.inactivity_threshold = inactivity_threshold
        self.data_retention = data_retention
        
        # Data storage
        self.keystroke_data = deque(maxlen=10000)
        self.mouse_data = deque(maxlen=10000)
        self.key_press_times = {}  # Track press/release for duration
        
        # Metrics tracking
        self.current_metrics = {
            'typing': TypingMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            'mouse': MouseMetrics(0, 0, 0, 0, 0, 0, 0),
            'last_activity': time.time(),
            'session_start': time.time(),
            'total_keystrokes': 0,
            'total_mouse_events': 0
        }
        
        # Application monitoring
        self.current_app = None
        self.app_usage = defaultdict(float)
        self.app_start_time = time.time()
        
        # Threading
        self.running = False
        self.analysis_thread = None
        self.app_monitor_thread = None
        
        # Event queues for thread safety
        self.keystroke_queue = queue.Queue()
        self.mouse_queue = queue.Queue()
        
        # Listeners
        self.keyboard_listener = None
        self.mouse_listener = None

    def _classify_key(self, key) -> Tuple[str, bool]:
        """Classify key type without storing actual key content"""
        if hasattr(key, 'char') and key.char:
            if key.char.isalpha():
                return 'letter', False
            elif key.char.isdigit():
                return 'number', False
            elif key.char.isspace():
                return 'space', False
            else:
                return 'special', False
        else:
            # Handle special keys
            key_name = str(key).lower()
            modifiers = ['ctrl', 'alt', 'shift', 'cmd', 'win']
            is_modifier = any(mod in key_name for mod in modifiers)
            return 'modifier' if is_modifier else 'special', is_modifier

    def _on_key_press(self, key):
        """Handle keyboard press events"""
        if not self.running:
            return
            
        timestamp = time.time()
        key_type, is_modifier = self._classify_key(key)
        
        # Store press time for duration calculation
        key_id = str(key)
        self.key_press_times[key_id] = timestamp
        
        # Queue keystroke data
        keystroke = KeystrokeData(
            timestamp=timestamp,
            key_type=key_type,
            is_modifier=is_modifier
        )
        
        try:
            self.keystroke_queue.put_nowait(keystroke)
        except queue.Full:
            pass  # Skip if queue is full

    def _on_key_release(self, key):
        """Handle keyboard release events"""
        if not self.running:
            return
            
        timestamp = time.time()
        key_id = str(key)
        
        # Calculate press duration if we have press time
        if key_id in self.key_press_times:
            press_duration = timestamp - self.key_press_times[key_id]
            del self.key_press_times[key_id]
            
            # Update the last keystroke with duration
            if self.keystroke_data and self.keystroke_data[-1].timestamp == self.key_press_times.get(key_id, 0):
                self.keystroke_data[-1].press_duration = press_duration

    def _on_mouse_move(self, x, y):
        """Handle mouse movement events"""
        if not self.running:
            return
            
        mouse_data = MouseData(
            timestamp=time.time(),
            x=x,
            y=y,
            action='move'
        )
        
        try:
            self.mouse_queue.put_nowait(mouse_data)
        except queue.Full:
            pass

    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        if not self.running:
            return
            
        if pressed:  # Only track press events to avoid duplicates
            mouse_data = MouseData(
                timestamp=time.time(),
                x=x,
                y=y,
                action='click',
                button=str(button)
            )
            
            try:
                self.mouse_queue.put_nowait(mouse_data)
            except queue.Full:
                pass

    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        if not self.running:
            return
            
        direction = 'up' if dy > 0 else 'down' if dy < 0 else 'horizontal'
        
        mouse_data = MouseData(
            timestamp=time.time(),
            x=x,
            y=y,
            action='scroll',
            scroll_direction=direction
        )
        
        try:
            self.mouse_queue.put_nowait(mouse_data)
        except queue.Full:
            pass

    def _process_queued_data(self):
        """Process queued keystroke and mouse data"""
        current_time = time.time()
        
        # Process keystrokes
        while not self.keystroke_queue.empty():
            try:
                keystroke = self.keystroke_queue.get_nowait()
                self.keystroke_data.append(keystroke)
                self.current_metrics['total_keystrokes'] += 1
                self.current_metrics['last_activity'] = current_time
            except queue.Empty:
                break
        
        # Process mouse events
        while not self.mouse_queue.empty():
            try:
                mouse_event = self.mouse_queue.get_nowait()
                self.mouse_data.append(mouse_event)
                self.current_metrics['total_mouse_events'] += 1
                self.current_metrics['last_activity'] = current_time
            except queue.Empty:
                break

    def _clean_old_data(self):
        """Remove data older than retention period"""
        current_time = time.time()
        cutoff_time = current_time - self.data_retention
        
        # Clean keystroke data
        while self.keystroke_data and self.keystroke_data[0].timestamp < cutoff_time:
            self.keystroke_data.popleft()
        
        # Clean mouse data
        while self.mouse_data and self.mouse_data[0].timestamp < cutoff_time:
            self.mouse_data.popleft()

    def _calculate_typing_metrics(self) -> TypingMetrics:
        """Calculate comprehensive typing metrics"""
        current_time = time.time()
        window_start = current_time - self.analysis_window
        
        # Filter recent keystrokes
        recent_keystrokes = [
            ks for ks in self.keystroke_data 
            if ks.timestamp >= window_start and not ks.is_modifier
        ]
        
        if len(recent_keystrokes) < 2:
            return TypingMetrics(0, 0, 0, 0, 0, 50, 0, 0, 0, 0)
        
        # Calculate basic WPM (assuming average word length of 5 characters)
        time_span = current_time - recent_keystrokes[0].timestamp
        if time_span > 0:
            chars_per_minute = (len(recent_keystrokes) / time_span) * 60
            wpm = chars_per_minute / 5
            raw_wpm = wpm  # Same as WPM since we don't track errors
        else:
            wpm = raw_wpm = 0
        
        # Calculate keystroke intervals
        intervals = []
        for i in range(1, len(recent_keystrokes)):
            interval = recent_keystrokes[i].timestamp - recent_keystrokes[i-1].timestamp
            intervals.append(interval)
        
        avg_interval = statistics.mean(intervals) if intervals else 0
        interval_variance = statistics.variance(intervals) if len(intervals) > 1 else 0
        
        # Rhythm consistency (lower variance = better consistency)
        max_variance = 0.5  # Maximum expected variance for good rhythm
        rhythm_consistency = max(0, 100 - (interval_variance / max_variance) * 100)
        
        # Detect pauses (intervals > 2 seconds)
        pauses = sum(1 for interval in intervals if interval > 2.0)
        pause_frequency = (pauses / len(intervals)) * 100 if intervals else 0
        
        # Detect typing bursts (rapid sequences)
        bursts = 0
        burst_threshold = 0.1  # Less than 100ms between keystrokes
        consecutive_fast = 0
        
        for interval in intervals:
            if interval < burst_threshold:
                consecutive_fast += 1
            else:
                if consecutive_fast >= 3:  # At least 3 fast keystrokes = burst
                    bursts += 1
                consecutive_fast = 0
        
        # Fatigue score (higher pause frequency + lower WPM + higher variance = more fatigue)
        baseline_wpm = 40  # Assumed baseline WPM
        wpm_factor = max(0, (baseline_wpm - wpm) / baseline_wpm) * 100
        variance_factor = min(100, (interval_variance / max_variance) * 100)
        fatigue_score = (wpm_factor + variance_factor + pause_frequency) / 3
        
        # Health score (inverse of fatigue, with rhythm bonus)
        health_score = max(0, 100 - fatigue_score + (rhythm_consistency - 50) / 2)
        health_score = min(100, health_score)
        
        # Accuracy score (simplified - in real scenario would need error tracking)
        accuracy_score = max(0, 100 - (pause_frequency / 2) - (interval_variance * 100))
        accuracy_score = min(100, accuracy_score)
        
        return TypingMetrics(
            wpm=round(wpm, 2),
            raw_wpm=round(raw_wpm, 2),
            accuracy_score=round(accuracy_score, 2),
            rhythm_consistency=round(rhythm_consistency, 2),
            fatigue_score=round(fatigue_score, 2),
            health_score=round(health_score, 2),
            avg_keystroke_interval=round(avg_interval, 3),
            keystroke_variance=round(interval_variance, 3),
            pause_frequency=round(pause_frequency, 2),
            typing_bursts=bursts
        )

    def _calculate_mouse_metrics(self) -> MouseMetrics:
        """Calculate comprehensive mouse metrics"""
        current_time = time.time()
        window_start = current_time - self.analysis_window
        
        # Filter recent mouse data
        recent_mouse = [
            md for md in self.mouse_data 
            if md.timestamp >= window_start
        ]
        
        if not recent_mouse:
            return MouseMetrics(0, 0, 0, 0, 0, 0, 0)
        
        # Calculate total distance traveled
        total_distance = 0
        movement_events = [md for md in recent_mouse if md.action == 'move']
        
        for i in range(1, len(movement_events)):
            prev = movement_events[i-1]
            curr = movement_events[i]
            distance = ((curr.x - prev.x) ** 2 + (curr.y - prev.y) ** 2) ** 0.5
            total_distance += distance
        
        # Calculate average speed (pixels per second)
        time_span = current_time - recent_mouse[0].timestamp
        avg_speed = (total_distance / time_span) if time_span > 0 else 0
        
        # Calculate click and scroll frequencies
        clicks = sum(1 for md in recent_mouse if md.action == 'click')
        scrolls = sum(1 for md in recent_mouse if md.action == 'scroll')
        click_frequency = (clicks / self.analysis_window) * 60  # clicks per minute
        scroll_frequency = (scrolls / self.analysis_window) * 60  # scrolls per minute
        
        # Calculate movement smoothness (based on direction changes)
        direction_changes = 0
        prev_direction = None
        
        for i in range(1, len(movement_events)):
            if i == len(movement_events) - 1:
                break
                
            prev = movement_events[i-1]
            curr = movement_events[i]
            next_event = movement_events[i+1]
            
            # Calculate movement vectors
            vec1 = (curr.x - prev.x, curr.y - prev.y)
            vec2 = (next_event.x - curr.x, next_event.y - curr.y)
            
            # Detect significant direction changes
            if vec1 != (0, 0) and vec2 != (0, 0):
                # Calculate angle between vectors
                dot_product = vec1[0] * vec2[0] + vec1[1] * vec2[1]
                mag1 = (vec1[0] ** 2 + vec1[1] ** 2) ** 0.5
                mag2 = (vec2[0] ** 2 + vec2[1] ** 2) ** 0.5
                
                if mag1 > 0 and mag2 > 0:
                    cos_angle = dot_product / (mag1 * mag2)
                    cos_angle = max(-1, min(1, cos_angle))  # Clamp to valid range
                    
                    if cos_angle < 0.5:  # Significant direction change (>60 degrees)
                        direction_changes += 1
        
        movement_smoothness = max(0, 100 - (direction_changes / len(movement_events)) * 100) if movement_events else 100
        
        # Detect idle periods (no mouse activity for >5 seconds)
        idle_periods = 0
        last_timestamp = recent_mouse[0].timestamp
        
        for event in recent_mouse[1:]:
            if event.timestamp - last_timestamp > 5.0:
                idle_periods += 1
            last_timestamp = event.timestamp
        
        # Calculate active time percentage
        active_time = time_span - (idle_periods * 5)  # Approximate
        active_time_percentage = (active_time / time_span) * 100 if time_span > 0 else 0
        active_time_percentage = max(0, min(100, active_time_percentage))
        
        return MouseMetrics(
            total_distance=round(total_distance, 2),
            avg_speed=round(avg_speed, 2),
            click_frequency=round(click_frequency, 2),
            scroll_frequency=round(scroll_frequency, 2),
            movement_smoothness=round(movement_smoothness, 2),
            idle_periods=idle_periods,
            active_time_percentage=round(active_time_percentage, 2)
        )

    def _monitor_applications(self):
        """Monitor active applications"""
        while self.running:
            try:
                # Get active window (simplified - would need platform-specific code)
                current_time = time.time()
                
                # Update app usage time
                if self.current_app:
                    session_time = current_time - self.app_start_time
                    self.app_usage[self.current_app] += session_time
                
                # Reset for next measurement
                self.app_start_time = current_time
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"Application monitoring error: {e}")
                time.sleep(5)

    def _analysis_loop(self):
        """Main analysis loop running in background"""
        while self.running:
            try:
                # Process queued data
                self._process_queued_data()
                
                # Clean old data
                self._clean_old_data()
                
                # Update metrics
                self.current_metrics['typing'] = self._calculate_typing_metrics()
                self.current_metrics['mouse'] = self._calculate_mouse_metrics()
                
                # Sleep for analysis interval
                time.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Analysis loop error: {e}")
                time.sleep(5)

    def start_monitoring(self):
        """Start the behavioral monitoring system"""
        if self.running:
            print("Monitoring is already running")
            return
        
        print("Starting behavioral monitoring...")
        self.running = True
        
        # Start keyboard listener
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        # Start mouse listener
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()
        
        # Start analysis thread
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
        # Start application monitoring thread
        self.app_monitor_thread = threading.Thread(target=self._monitor_applications)
        self.app_monitor_thread.daemon = True
        self.app_monitor_thread.start()
        
        print("Behavioral monitoring started successfully")

    def stop_monitoring(self):
        """Stop the behavioral monitoring system"""
        if not self.running:
            print("Monitoring is not running")
            return
        
        print("Stopping behavioral monitoring...")
        self.running = False
        
        # Stop listeners
        if self.keyboard_listener:
            self.keyboard_listener.stop()
        if self.mouse_listener:
            self.mouse_listener.stop()
        
        # Wait for threads to finish
        if self.analysis_thread and self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=5)
        if self.app_monitor_thread and self.app_monitor_thread.is_alive():
            self.app_monitor_thread.join(timeout=5)
        
        print("Behavioral monitoring stopped")

    def get_current_metrics(self) -> Dict:
        """Get current behavioral metrics"""
        current_time = time.time()
        session_duration = current_time - self.current_metrics['session_start']
        time_since_last_activity = current_time - self.current_metrics['last_activity']
        
        is_inactive = time_since_last_activity > self.inactivity_threshold
        
        return {
            'timestamp': current_time,
            'session_duration': round(session_duration, 2),
            'time_since_last_activity': round(time_since_last_activity, 2),
            'is_inactive': is_inactive,
            'typing_metrics': asdict(self.current_metrics['typing']),
            'mouse_metrics': asdict(self.current_metrics['mouse']),
            'total_keystrokes': self.current_metrics['total_keystrokes'],
            'total_mouse_events': self.current_metrics['total_mouse_events'],
            'app_usage': dict(self.app_usage)
        }

    def get_fatigue_indicators(self) -> Dict:
        """Get specific fatigue indicators"""
        typing_metrics = self.current_metrics['typing']
        mouse_metrics = self.current_metrics['mouse']
        
        indicators = {
            'typing_fatigue': {
                'low_wpm': typing_metrics.wpm < 30,
                'high_pause_frequency': typing_metrics.pause_frequency > 20,
                'irregular_rhythm': typing_metrics.rhythm_consistency < 50,
                'high_fatigue_score': typing_metrics.fatigue_score > 70
            },
            'mouse_fatigue': {
                'low_activity': mouse_metrics.active_time_percentage < 30,
                'jerky_movements': mouse_metrics.movement_smoothness < 50,
                'excessive_idle': mouse_metrics.idle_periods > 5
            },
            'overall_fatigue_level': (typing_metrics.fatigue_score + (100 - mouse_metrics.active_time_percentage)) / 2
        }
        
        return indicators

    def export_data(self, filename: str = None):
        """Export monitoring data to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"behavioral_data_{timestamp}.json"
        
        export_data = {
            'session_info': {
                'start_time': self.current_metrics['session_start'],
                'export_time': time.time(),
                'total_keystrokes': self.current_metrics['total_keystrokes'],
                'total_mouse_events': self.current_metrics['total_mouse_events']
            },
            'current_metrics': self.get_current_metrics(),
            'fatigue_indicators': self.get_fatigue_indicators(),
            'configuration': {
                'analysis_window': self.analysis_window,
                'inactivity_threshold': self.inactivity_threshold,
                'data_retention': self.data_retention
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"Data exported to {filename}")
        except Exception as e:
            print(f"Export failed: {e}")

def main():
    """Example usage of the behavioral monitoring system"""
    monitor = BehavioralMonitor(
        analysis_window=60,  # Analyze last 60 seconds
        inactivity_threshold=30,  # 30 seconds of inactivity
        data_retention=3600  # Keep 1 hour of data
    )
    
    try:
        # Start monitoring
        monitor.start_monitoring()
        
        print("\nBehavioral monitoring is running...")
        print("Press Ctrl+C to stop and view results")
        print("Type something and move your mouse to generate data\n")
        
        # Monitor for a while and display periodic updates
        start_time = time.time()
        while True:
            time.sleep(10)  # Update every 10 seconds
            
            metrics = monitor.get_current_metrics()
            typing = metrics['typing_metrics']
            mouse = metrics['mouse_metrics']
            
            print(f"\n--- Metrics Update (Session: {metrics['session_duration']:.1f}s) ---")
            print(f"Typing: WPM={typing['wpm']:.1f}, Health={typing['health_score']:.1f}, "
                  f"Fatigue={typing['fatigue_score']:.1f}")
            print(f"Mouse: Speed={mouse['avg_speed']:.1f}px/s, Smoothness={mouse['movement_smoothness']:.1f}, "
                  f"Active={mouse['active_time_percentage']:.1f}%")
            print(f"Activity: Keystrokes={metrics['total_keystrokes']}, "
                  f"Mouse Events={metrics['total_mouse_events']}")
            
            if metrics['is_inactive']:
                print(f"⚠️  INACTIVE for {metrics['time_since_last_activity']:.1f}s")
            
            # Show fatigue indicators
            fatigue = monitor.get_fatigue_indicators()
            if fatigue['overall_fatigue_level'] > 60:
                print(f"⚠️  HIGH FATIGUE DETECTED: {fatigue['overall_fatigue_level']:.1f}")
    
    except KeyboardInterrupt:
        print("\n\nStopping monitoring...")
        monitor.stop_monitoring()
        
        # Show final results
        print("\n=== Final Session Results ===")
        final_metrics = monitor.get_current_metrics()
        typing = final_metrics['typing_metrics']
        mouse = final_metrics['mouse_metrics']
        
        print(f"\nSession Duration: {final_metrics['session_duration']:.1f} seconds")
        print(f"Total Keystrokes: {final_metrics['total_keystrokes']}")
        print(f"Total Mouse Events: {final_metrics['total_mouse_events']}")
        
        print(f"\nTyping Analysis:")
        print(f"  WPM: {typing['wpm']:.1f}")
        print(f"  Health Score: {typing['health_score']:.1f}/100")
        print(f"  Fatigue Score: {typing['fatigue_score']:.1f}/100")
        print(f"  Rhythm Consistency: {typing['rhythm_consistency']:.1f}/100")
        print(f"  Average Keystroke Interval: {typing['avg_keystroke_interval']:.3f}s")
        
        print(f"\nMouse Analysis:")
        print(f"  Distance Traveled: {mouse['total_distance']:.1f} pixels")
        print(f"  Average Speed: {mouse['avg_speed']:.1f} px/s")
        print(f"  Movement Smoothness: {mouse['movement_smoothness']:.1f}/100")
        print(f"  Active Time: {mouse['active_time_percentage']:.1f}%")
        
        # Export data
        monitor.export_data()
        print("\nSession data exported to file")

if __name__ == "__main__":
    main()