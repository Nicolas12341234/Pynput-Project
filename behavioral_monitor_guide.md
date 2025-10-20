# Behavioral Monitoring System - Complete Reference Guide

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Metrics Explained](#metrics-explained)
4. [Calculation Formulas](#calculation-formulas)
5. [Fatigue Detection](#fatigue-detection)
6. [Interpretation Guide](#interpretation-guide)
7. [Privacy & Security](#privacy--security)
8. [Installation & Usage](#installation--usage)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Configuration](#advanced-configuration)

---

## 🎯 Project Overview

### What is this?

The **Behavioral Monitoring System** is a Python-based application that tracks and analyzes user interaction patterns (typing and mouse behavior) to provide real-time insights into:

- **Productivity levels**
- **Fatigue indicators**
- **Typing health metrics**
- **Work patterns and rhythms**

### Key Features

✅ **Privacy-Preserving**: Never stores actual keystrokes or typed content  
✅ **Real-Time Analysis**: Continuous metric updates every second  
✅ **Comprehensive Metrics**: 18+ different behavioral indicators  
✅ **Fatigue Detection**: Automatic alerts for unhealthy work patterns  
✅ **Export Capabilities**: JSON data export for further analysis  

### Use Cases

- 💼 **Remote Work Monitoring**: Track productivity during WFH
- 🏥 **Health & Ergonomics**: Detect RSI risks and fatigue patterns
- 📊 **Personal Analytics**: Understand your work rhythms
- 🎯 **Focus Optimization**: Identify distraction patterns
- ⏱️ **Time Management**: Analyze active vs. idle time

---

## 🏗️ System Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                   Behavioral Monitor                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Keyboard   │  │    Mouse     │  │     App      │ │
│  │   Listener   │  │   Listener   │  │   Monitor    │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                  │                  │         │
│         ▼                  ▼                  ▼         │
│  ┌──────────────────────────────────────────────────┐ │
│  │            Event Processing Queue                 │ │
│  └──────────────────────────────────────────────────┘ │
│                         │                              │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │          Analysis Engine (1s interval)            │ │
│  │  • Calculate Typing Metrics                       │ │
│  │  • Calculate Mouse Metrics                        │ │
│  │  • Detect Fatigue Indicators                      │ │
│  │  • Clean Old Data                                 │ │
│  └──────────────────────────────────────────────────┘ │
│                         │                              │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │              Metrics Storage                      │ │
│  │  • Keystroke Data (deque, max 10k)               │ │
│  │  • Mouse Data (deque, max 10k)                   │ │
│  │  • Current Metrics                                │ │
│  │  • App Usage Statistics                           │ │
│  └──────────────────────────────────────────────────┘ │
│                         │                              │
│                         ▼                              │
│  ┌──────────────────────────────────────────────────┐ │
│  │            Export & Reporting                     │ │
│  │  • JSON Export                                    │ │
│  │  • Real-time Console Updates                     │ │
│  │  • Fatigue Alerts                                 │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Input**: Keyboard/mouse events captured by `pynput` library
2. **Classification**: Events categorized (letter/number/modifier/move/click)
3. **Queuing**: Thread-safe queue stores events temporarily
4. **Processing**: Analysis thread processes queue every 1 second
5. **Calculation**: Metrics computed using rolling window (default 60s)
6. **Storage**: Results stored in deque structures with automatic cleanup
7. **Output**: Metrics available via API calls or console display

---

## 📊 Metrics Explained

### Typing Metrics (10 Parameters)

#### 1. **WPM (Words Per Minute)**

**Definition**: Standard typing speed measurement

**Formula**:
```python
chars_per_minute = (total_keystrokes / time_span) * 60
wpm = chars_per_minute / 5  # Average word = 5 characters
```

**Interpretation**:
- `< 20 WPM`: Very slow (reading/thinking)
- `20-40 WPM`: Below average
- `40-60 WPM`: Average typing
- `60-80 WPM`: Good typing
- `> 80 WPM`: Excellent typing

---

#### 2. **Raw WPM**

**Definition**: Typing speed without error correction

**Note**: Currently same as WPM (system doesn't track errors)

**Future Enhancement**: Would subtract errors/corrections

---

#### 3. **Accuracy Score** (0-100)

**Definition**: Quality of typing based on pause patterns

**Formula**:
```python
accuracy_score = 100 - (pause_frequency / 2) - (keystroke_variance * 100)
accuracy_score = clamp(0, 100)
```

**Factors**:
- Fewer pauses = higher accuracy
- Lower variance = more consistent = higher accuracy

**Interpretation**:
- `90-100`: Excellent accuracy
- `70-89`: Good accuracy
- `50-69`: Moderate accuracy
- `< 50`: Poor accuracy (many hesitations)

---

#### 4. **Rhythm Consistency** (0-100)

**Definition**: How steady your typing rhythm is

**Formula**:
```python
intervals = [time between consecutive keystrokes]
variance = variance(intervals)
max_variance = 0.5  # 500ms expected max

rhythm_consistency = max(0, 100 - (variance / max_variance) * 100)
```

**Interpretation**:
- `80-100`: Very consistent (in "flow" state)
- `60-79`: Good consistency
- `40-59`: Moderate consistency
- `< 40`: Irregular (distracted/uncertain)

**Use Case**: Detect when you're "in the zone" vs. struggling

---

#### 5. **Fatigue Score** (0-100)

**Definition**: Composite indicator of typing tiredness

**Formula**:
```python
baseline_wpm = 40  # Configurable
wpm_factor = max(0, (baseline - actual_wpm) / baseline) * 100
variance_factor = min(100, (keystroke_variance / 0.5) * 100)

fatigue_score = (wpm_factor + variance_factor + pause_frequency) / 3
```

**Components**:
1. **Speed degradation**: How much slower than baseline
2. **Rhythm irregularity**: Increased variance
3. **Pause frequency**: More thinking/hesitation

**Interpretation**:
- `0-30`: Fresh and alert
- `31-50`: Mild fatigue
- `51-70`: Moderate fatigue (consider break)
- `> 70`: High fatigue (break recommended)

---

#### 6. **Health Score** (0-100)

**Definition**: Overall typing wellness indicator

**Formula**:
```python
health_score = 100 - fatigue_score + (rhythm_consistency - 50) / 2
health_score = clamp(0, 100)
```

**Interpretation**:
- `80-100`: Healthy typing patterns
- `60-79`: Acceptable
- `40-59`: Warning zone
- `< 40`: Unhealthy patterns (risk of RSI)

---

#### 7. **Average Keystroke Interval** (seconds)

**Definition**: Mean time between consecutive keystrokes

**Formula**:
```python
intervals = [t[i+1] - t[i] for all keystrokes]
avg_interval = mean(intervals)
```

**Typical Values**:
- `0.1-0.2s`: Fast typing (60-120 WPM)
- `0.3-0.5s`: Normal typing (40-60 WPM)
- `> 1.0s`: Slow/thoughtful typing

---

#### 8. **Keystroke Variance** (seconds²)

**Definition**: Variability in typing rhythm

**Formula**:
```python
variance = variance(keystroke_intervals)
```

**Interpretation**:
- `< 0.1`: Very consistent
- `0.1-0.3`: Normal variation
- `> 0.5`: Highly irregular (distracted/tired)

---

#### 9. **Pause Frequency** (%)

**Definition**: Percentage of long gaps in typing

**Formula**:
```python
pauses = count(intervals > 2.0 seconds)
pause_frequency = (pauses / total_intervals) * 100
```

**Interpretation**:
- `< 10%`: Continuous flow
- `10-20%`: Normal thinking pauses
- `20-40%`: Frequent breaks in thought
- `> 40%`: Highly fragmented (multitasking?)

---

#### 10. **Typing Bursts**

**Definition**: Number of rapid typing sequences

**Formula**:
```python
burst_threshold = 0.1  # 100ms between keys
consecutive_fast = 0
bursts = 0

for interval in intervals:
    if interval < burst_threshold:
        consecutive_fast += 1
    else:
        if consecutive_fast >= 3:  # At least 3 fast keys
            bursts += 1
        consecutive_fast = 0
```

**Interpretation**:
- `0-2`: Slow, methodical typing
- `3-10`: Normal bursts
- `> 10`: High-speed typing with flow states

---

### Mouse Metrics (7 Parameters)

#### 1. **Total Distance** (pixels)

**Definition**: Cumulative mouse movement

**Formula**:
```python
distance = 0
for i in range(1, len(mouse_positions)):
    dx = positions[i].x - positions[i-1].x
    dy = positions[i].y - positions[i-1].y
    distance += sqrt(dx² + dy²)  # Euclidean distance
```

**Typical Values**:
- `< 500px`: Minimal movement (focused work)
- `500-2000px`: Normal usage
- `> 5000px`: High activity (design work, browsing)

---

#### 2. **Average Speed** (pixels/second)

**Definition**: Mean mouse movement velocity

**Formula**:
```python
avg_speed = total_distance / time_span
```

**Interpretation**:
- `< 50 px/s`: Slow, precise movements
- `50-150 px/s`: Normal usage
- `> 150 px/s`: Fast, possibly erratic

---

#### 3. **Click Frequency** (clicks/minute)

**Definition**: Rate of mouse clicks

**Formula**:
```python
clicks = count(click_events)
click_frequency = (clicks / analysis_window) * 60
```

**Typical Values**:
- `< 5/min`: Reading/viewing
- `5-20/min`: Normal work
- `> 30/min`: Intense interaction (gaming, data entry)

---

#### 4. **Scroll Frequency** (scrolls/minute)

**Definition**: Rate of scrolling actions

**Formula**:
```python
scrolls = count(scroll_events)
scroll_frequency = (scrolls / analysis_window) * 60
```

**Use Case**: Distinguish reading (high scroll) vs. editing (low scroll)

---

#### 5. **Movement Smoothness** (0-100)

**Definition**: How fluid mouse movements are

**Formula**:
```python
# Calculate angle between consecutive movement vectors
for i in range(1, len(movements) - 1):
    vec1 = (dx1, dy1)
    vec2 = (dx2, dy2)
    
    cos_angle = dot_product(vec1, vec2) / (magnitude1 * magnitude2)
    
    if cos_angle < 0.5:  # > 60° direction change
        direction_changes += 1

smoothness = 100 - (direction_changes / movements) * 100
```

**Interpretation**:
- `80-100`: Smooth, confident movements
- `60-79`: Normal usage
- `40-59`: Jerky (fatigue or frustration)
- `< 40`: Erratic (possible tremor/stress)

**Health Indicator**: Sudden drops may indicate physical strain

---

#### 6. **Idle Periods**

**Definition**: Count of inactivity gaps > 5 seconds

**Formula**:
```python
idle_periods = 0
for i in range(1, len(mouse_events)):
    gap = events[i].timestamp - events[i-1].timestamp
    if gap > 5.0:
        idle_periods += 1
```

**Use Case**: Detect context switching, phone calls, meetings

---

#### 7. **Active Time Percentage** (%)

**Definition**: Proportion of time with mouse activity

**Formula**:
```python
idle_time = idle_periods * 5  # Approximate
active_time = time_span - idle_time
active_percentage = (active_time / time_span) * 100
```

**Interpretation**:
- `> 70%`: High engagement
- `50-70%`: Normal work pattern
- `30-50%`: Interrupted work
- `< 30%`: Mostly idle (meeting, reading)

---

## 🧮 Calculation Formulas

### Statistical Functions Used

#### Mean (Average)
```python
mean = sum(values) / count(values)
```

#### Variance
```python
variance = sum((x - mean)² for x in values) / count(values)
```

#### Standard Deviation
```python
std_dev = sqrt(variance)
```

#### Dot Product (for angle calculation)
```python
dot_product = (x1 * x2) + (y1 * y2)
```

#### Euclidean Distance
```python
distance = sqrt((x2 - x1)² + (y2 - y1)²)
```

---

## 🚨 Fatigue Detection

### Overall Fatigue Algorithm

**Formula**:
```python
typing_fatigue_score = typing_metrics.fatigue_score
mouse_inactivity = 100 - mouse_metrics.active_time_percentage

overall_fatigue = (typing_fatigue_score + mouse_inactivity) / 2
```

### Binary Indicators

#### Typing Fatigue Flags

```python
{
    'low_wpm': wpm < 30,
    'high_pause_frequency': pause_frequency > 20,
    'irregular_rhythm': rhythm_consistency < 50,
    'high_fatigue_score': fatigue_score > 70
}
```

#### Mouse Fatigue Flags

```python
{
    'low_activity': active_time_percentage < 30,
    'jerky_movements': movement_smoothness < 50,
    'excessive_idle': idle_periods > 5
}
```

### Fatigue Levels

| Level | Score | Recommendation |
|-------|-------|----------------|
| **Minimal** | 0-30 | Continue working |
| **Mild** | 31-50 | Consider break in 30 min |
| **Moderate** | 51-70 | Take 5-10 min break soon |
| **High** | 71-85 | Take break immediately |
| **Severe** | 86-100 | Stop work, rest required |

---

## 📖 Interpretation Guide

### Sample Session Analysis

```json
{
  "session_duration": 172.44,
  "typing_metrics": {
    "wpm": 2.15,
    "health_score": 0,
    "fatigue_score": 81.54,
    "rhythm_consistency": 0,
    "pause_frequency": 50.0
  },
  "mouse_metrics": {
    "total_distance": 1344.22,
    "avg_speed": 78.34,
    "movement_smoothness": 91.49,
    "active_time_percentage": 70.86
  }
}
```

### Interpretation

**Typing Behavior**:
- ❌ **Very Low WPM (2.15)**: Minimal typing activity
- ❌ **Zero Health Score**: Critical - indicates test/minimal usage
- ❌ **High Fatigue (81.54)**: Triggered by low activity
- ⚠️ **50% Pause Frequency**: Half the time spent waiting

**Mouse Behavior**:
- ✅ **Good Distance (1344px)**: Reasonable exploration
- ✅ **Smooth Movements (91.49)**: Confident, not jerky
- ✅ **Active Time (70.86%)**: Engaged with interface

**Conclusion**: This is a **test session** or **browsing activity** with minimal typing. Not indicative of actual work fatigue.

---

### Real-World Scenarios

#### Scenario 1: Productive Coding Session

```python
wpm: 45
health_score: 75
rhythm_consistency: 82
typing_bursts: 8
pause_frequency: 15
```

**Analysis**: Developer in flow state, consistent rhythm, healthy bursts of code writing.

---

#### Scenario 2: Fatigued Late-Night Work

```python
wpm: 22  # Down from usual 45
health_score: 35
rhythm_consistency: 48
pause_frequency: 38
mouse_smoothness: 52  # Down from usual 85
```

**Analysis**: Clear fatigue signs - slow, irregular typing, frequent pauses, jerky mouse. **Break recommended**.

---

#### Scenario 3: Reading/Research

```python
wpm: 5
scroll_frequency: 45
click_frequency: 8
active_time: 85%
typing_bursts: 0
```

**Analysis**: High engagement (mouse active), minimal typing, high scrolling. Not fatigued, just different task.

---

## 🔒 Privacy & Security

### What is NOT Stored

❌ **Actual keystrokes** (which keys pressed)  
❌ **Typed content** (passwords, documents, messages)  
❌ **Screenshots**  
❌ **Window titles** (in current implementation)  
❌ **Application-specific data**  

### What IS Stored

✅ **Keystroke timing** (when keys pressed)  
✅ **Key type** (letter/number/special/modifier)  
✅ **Mouse coordinates** (x, y positions)  
✅ **Event timestamps**  
✅ **Calculated metrics** (WPM, fatigue, etc.)  

### Data Retention

- **Default**: 1 hour rolling window
- **Maximum storage**: 10,000 keystrokes + 10,000 mouse events
- **Auto-cleanup**: Old data automatically purged
- **Export format**: JSON (no sensitive content)

### Privacy Best Practices

1. **Don't share raw JSON exports** (contains timing patterns)
2. **Run locally** (no network transmission)
3. **Use for personal analytics only**
4. **Review exported data** before sharing
5. **Comply with local laws** (some jurisdictions restrict monitoring)

---

## 💻 Installation & Usage

### Requirements

```bash
Python 3.7+
pynput >= 1.7.6
psutil >= 5.9.0
```

### Installation

```bash
# Clone/download the project
cd behavioral-monitor

# Install dependencies
pip install -r requirements.txt

# Test installation
python test_script.py
```

### Platform-Specific Setup

#### macOS
```bash
# Grant accessibility permissions
System Preferences → Security & Privacy → Accessibility
# Add Terminal or Python to allowed apps
```

#### Linux
```bash
# Install X11 libraries
sudo apt-get install python3-xlib  # Ubuntu/Debian
```

#### Windows
```bash
# Run as Administrator
# May need to add to antivirus exclusions
```

### Basic Usage

```python
from behavioral_monitor import BehavioralMonitor

# Create monitor instance
monitor = BehavioralMonitor(
    analysis_window=60,      # Analyze last 60 seconds
    inactivity_threshold=30, # 30s = inactive
    data_retention=3600      # Keep 1 hour of data
)

# Start monitoring
monitor.start_monitoring()

# Get current metrics
metrics = monitor.get_current_metrics()
print(f"WPM: {metrics['typing_metrics']['wpm']}")

# Check fatigue
fatigue = monitor.get_fatigue_indicators()
if fatigue['overall_fatigue_level'] > 70:
    print("High fatigue detected! Take a break.")

# Export data
monitor.export_data("session_data.json")

# Stop monitoring
monitor.stop_monitoring()
```

### Command Line

```bash
# Run with defaults
python behavioral_monitor.py

# Monitor will run until Ctrl+C
# Data exported automatically on exit
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. **No Events Recorded**

**Symptoms**: All metrics show 0

**Solutions**:
- Check accessibility permissions (macOS)
- Run with `sudo` (Linux/macOS)
- Run as Administrator (Windows)
- Disable antivirus temporarily
- Check if pynput installed correctly

---

#### 2. **Import Errors**

```python
ImportError: No module named 'pynput'
```

**Solution**:
```bash
pip install pynput psutil
# or
python -m pip install pynput psutil
```

---

#### 3. **Keyboard/Mouse Not Detected**

**macOS**:
- System Preferences → Security & Privacy → Accessibility
- Add Terminal/Python to allowed list
- Restart terminal after granting permissions

**Linux**:
- Install X11 development packages
- Use X11 session (not Wayland)
- Check: `echo $XDG_SESSION_TYPE` should show `x11`

**Windows**:
- Run as Administrator
- Check Windows Defender isn't blocking

---

#### 4. **High CPU Usage**

**Cause**: Too frequent analysis updates

**Solution**:
```python
# Reduce analysis frequency in _analysis_loop()
time.sleep(5)  # Instead of sleep(1)
```

---

#### 5. **Memory Growth**

**Cause**: Data retention too long

**Solution**:
```python
monitor = BehavioralMonitor(
    data_retention=1800  # 30 minutes instead of 1 hour
)
```

---

## ⚙️ Advanced Configuration

### Custom Baseline WPM

```python
def _calculate_typing_metrics(self):
    baseline_wpm = 60  # Change from default 40
    # ... rest of calculation
```

### Adjusting Fatigue Sensitivity

```python
# More sensitive (alerts earlier)
'high_fatigue_score': fatigue_score > 60  # Instead of 70

# Less sensitive
'high_fatigue_score': fatigue_score > 80
```

### Custom Analysis Window

```python
# Real-time (last 30s)
monitor = BehavioralMonitor(analysis_window=30)

# Long-term trends (last 5 minutes)
monitor = BehavioralMonitor(analysis_window=300)
```

### Integration with Other Tools

#### Export to CSV

```python
import json
import csv

with open('session_data.json', 'r') as f:
    data = json.load(f)

with open('metrics.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['timestamp', 'wpm', 'fatigue', 'health'])
    
    metrics = data['current_metrics']
    typing = metrics['typing_metrics']
    writer.writerow([
        metrics['timestamp'],
        typing['wpm'],
        typing['fatigue_score'],
        typing['health_score']
    ])
```

#### Webhook Alerts

```python
import requests

def check_fatigue_and_alert(monitor):
    fatigue = monitor.get_fatigue_indicators()
    if fatigue['overall_fatigue_level'] > 70:
        requests.post('https://your-webhook.com/alert', json={
            'message': 'High fatigue detected!',
            'level': fatigue['overall_fatigue_level']
        })
```

---

## 📚 Formulas Quick Reference

| Metric | Formula | Range |
|--------|---------|-------|
| WPM | `(keystrokes / time / 5) * 60` | 0-120+ |
| Fatigue | `(wpm_factor + variance + pauses) / 3` | 0-100 |
| Health | `100 - fatigue + rhythm_bonus` | 0-100 |
| Rhythm | `100 - (variance / 0.5) * 100` | 0-100 |
| Smoothness | `100 - (direction_changes / moves * 100)` | 0-100 |
| Active% | `(active_time / total) * 100` | 0-100 |

---

## 🎓 Best Practices

### For Personal Use

1. **Calibrate baseline**: Run normal work session to establish your personal WPM
2. **Set realistic thresholds**: Adjust fatigue alerts to your patterns
3. **Review weekly**: Export and analyze weekly trends
4. **Respect signals**: Take breaks when fatigue detected

### For Development

1. **Don't track sensitive apps**: Add exclusion list
2. **Aggregate metrics**: Store summaries, not raw events
3. **Respect privacy**: Never log actual content
4. **Be transpar