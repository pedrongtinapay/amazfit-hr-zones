# Amazfit Heart Rate Zone Estimator with CSV Database & Pace Tracking

A powerful desktop application for analyzing heart rate zones with pace calculations from Amazfit workout data exports (FIT format). Includes persistent CSV database with cumulative statistics.

## Features

- ✅ **Multi-file FIT upload** - Load multiple FIT files at once
- ✅ **Heart rate zone estimation** - 5 personalized zones based on HRR
- ✅ **Pace tracking** - Average pace for each HR zone
- ✅ **CSV database** - All results stored and persisted
- ✅ **Running cumulative stats** - Updates with each analysis:
  - Total sessions analyzed
  - Total HR readings
  - Total distance covered
  - Weighted average HR
  - Overall max HR
- ✅ **Session history** - View all past analyses in tabular format
- ✅ **No external dependencies** - Pure Python with tkinter

## Heart Rate Zones

The app uses the Heart Rate Reserve (HRR) method to calculate personalized zones:

- **Zone 1 - Recovery** (50-60% HRR): Light recovery, warm-up, cool-down
- **Zone 2 - Aerobic** (60% HRR): Easy pace, conversation possible
- **Zone 3 - Tempo** (60-70% HRR): Moderate effort, building endurance
- **Zone 4 - Threshold** (70-85% HRR): Hard effort, lactate threshold training
- **Zone 5 - VO2Max** (85%+ HRR): Maximum intensity, high-intensity intervals

## Installation

1. **Clone the repo:**
```bash
git clone https://github.com/pedrongtinapay/amazfit-hr-zones.git
cd amazfit-hr-zones
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Usage

```bash
python amazfit_hr_zones.py
```

### Tabs

**Analysis Tab:**
1. Click **"Add FIT Files"** to select your Amazfit exports
2. Click **"Analyze & Save to Database"** to process
3. View zone breakdown with heart rate ranges and pace

**History & Cumulative Tab:**
- **Cumulative stats** - Running totals updated with each analysis
- **Session history** - CSV view of all past analyses
- **Auto-refresh** - Click "Refresh History" to reload

## Database

Results are automatically saved to `hr_zone_data.csv` with:
- Timestamp of analysis
- Files analyzed
- HR statistics (resting, avg, max)
- Zone-by-zone breakdown:
  - Time in zone (readings & percentage)
  - Average pace per zone (min/km)

## Supported Formats

- **FIT** - Garmin/Amazfit native format (recommended)
- **GPX** - GPS exchange format (legacy)

## Requirements

- Python 3.6 or higher
- tkinter (usually included with Python)
- fitparse (installed via `pip install -r requirements.txt`)

## How It Works

1. **Parses FIT files** - Extracts heart rate and distance data from Amazfit exports
2. **Calculates statistics** - Determines resting HR, max HR, and heart rate reserve
3. **Estimates zones** - Divides reserve into 5 zones based on training intensity
4. **Calculates pace** - Average pace per zone from distance/time data
5. **Persists data** - Saves all results to CSV database
6. **Tracks cumulative** - Running totals update with each analysis

## Example Output

**Current Session:**
```
Zone 1 - Recovery
  HR Range: 58 - 118 bpm
  Time in Zone: 2,543 readings (16.7%)
  Average Pace: 6:45 min/km
  ████░░░░░░░░░░░░░░░░

Zone 5 - VO2Max
  HR Range: 148 - 178 bpm
  Time in Zone: 892 readings (5.8%)
  Average Pace: 4:12 min/km
  █░░░░░░░░░░░░░░░░░░
```

**Cumulative Stats (auto-updated):**
```
Total Sessions: 5
Total HR Readings: 75,234
Total Distance: 54.8 km
Avg HR (weighted): 142.3 bpm
Overall Max HR: 178 bpm
```

## License

MIT
