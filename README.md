# Amazfit Heart Rate Zone Estimator

A lightweight desktop application for analyzing heart rate zones from Amazfit GPX workout exports.

## Features

- ✅ **Multi-file upload** - Load multiple GPX files at once
- ✅ **Heart rate parsing** - Extracts HR data from GPX track points
- ✅ **5-zone estimation** - Recovery, Aerobic, Tempo, Threshold, VO2Max
- ✅ **Statistical analysis** - Calculates resting HR, max HR, and averages
- ✅ **Visual progress bars** - Shows time spent in each zone with percentages
- ✅ **No dependencies** - Uses only Python's built-in libraries

## Heart Rate Zones

The app uses the Heart Rate Reserve (HRR) method to calculate personalized zones:

- **Zone 1 - Recovery** (50-60% HRR): Light recovery, warm-up, cool-down
- **Zone 2 - Aerobic** (60% HRR): Easy pace, conversation possible
- **Zone 3 - Tempo** (60-70% HRR): Moderate effort, building endurance
- **Zone 4 - Threshold** (70-85% HRR): Hard effort, lactate threshold training
- **Zone 5 - VO2Max** (85%+ HRR): Maximum intensity, high-intensity intervals

## Installation

No installation needed! Just requires Python 3.6+.

## Usage

```bash
python amazfit_hr_zones.py
```

Then:
1. Click **"Add GPX Files"** to select your Amazfit exports (select multiple files)
2. Click **"Analyze Heart Rate Zones"** to see your breakdown
3. View the results with zone ranges, time spent, and visual bars

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)

## How It Works

1. **Parses GPX files** - Reads TrackPoint extensions with heart rate data
2. **Calculates statistics** - Determines resting HR, max HR, and heart rate reserve
3. **Estimates zones** - Divides reserve into 5 zones based on standard training intensity levels
4. **Analyzes distribution** - Counts readings in each zone and calculates percentages

## Example Output

```
Files Processed: 3
Total HR Readings: 15,234
Resting HR: 58 bpm
Average HR: 142.5 bpm
Max HR: 178 bpm

Zone 1 - Recovery
  Range: 58 - 118 bpm
  Time in Zone: 2,543 readings (16.7%)
  
Zone 2 - Aerobic
  Range: 118 - 124 bpm
  Time in Zone: 1,890 readings (12.4%)
  ...
```

## License

MIT
