import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import xml.etree.ElementTree as ET
import os
import csv
from collections import defaultdict
from datetime import datetime
import math

try:
    import fitparse
    HAS_FITPARSE = True
except ImportError:
    HAS_FITPARSE = False

class HeartRateZoneAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazfit Heart Rate Zone Estimator with Pace")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        self.files = []
        self.all_hr_data = []
        self.all_distance_data = []
        self.db_file = "hr_zone_data.csv"
        self.cumulative_stats = self.load_cumulative_stats()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Analysis
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        self.setup_analysis_tab(analysis_frame)
        
        # Tab 2: History
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="History & Cumulative")
        self.setup_history_tab(history_frame)
    
    def setup_analysis_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Current Session Analysis", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # File upload section
        ttk.Label(main_frame, text="FIT Files:").pack(anchor=tk.W, pady=(10, 0))
        
        # File listbox
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=tk.BOTH, expand=False, pady=5, padx=0)
        list_frame.config(height=120)
        
        self.file_listbox = tk.Listbox(list_frame, height=6)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Add FIT Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # Analysis button
        ttk.Button(main_frame, text="Analyze & Save to Database", 
                   command=self.analyze).pack(pady=10, fill=tk.X)
        
        # Results section
        ttk.Label(main_frame, text="Heart Rate Zones with Pace:", 
                  font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.results_text = tk.Text(results_frame, height=20, wrap=tk.WORD)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        # Configure tags
        self.results_text.tag_config("header", font=("Arial", 11, "bold"))
        self.results_text.tag_config("zone_name", font=("Arial", 10, "bold"), foreground="blue")
        self.results_text.tag_config("info", font=("Arial", 9))
    
    def setup_history_tab(self, parent):
        main_frame = ttk.Frame(parent, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Cumulative Statistics & History", font=("Arial", 14, "bold"))
        title.pack(pady=10)
        
        # Cumulative stats section
        ttk.Label(main_frame, text="Cumulative Running Values:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.cumulative_text = tk.Text(main_frame, height=7, wrap=tk.WORD)
        self.cumulative_text.pack(fill=tk.X, pady=5)
        
        # History table
        ttk.Label(main_frame, text="Session History:", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(15, 5))
        
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_text = tk.Text(table_frame, height=20, font=("Courier", 8))
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
        
        # Refresh button
        ttk.Button(main_frame, text="Refresh History", command=self.refresh_history_tab).pack(pady=10)
        
        self.refresh_history_tab()
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select FIT files",
            filetypes=[("FIT files", "*.fit"), ("All files", "*.*")]
        )
        for file in files:
            if file not in self.files:
                self.files.append(file)
        self.update_file_list()
    
    def remove_file(self):
        selection = self.file_listbox.curselection()
        if selection:
            self.files.pop(selection[0])
            self.update_file_list()
    
    def clear_files(self):
        self.files = []
        self.update_file_list()
    
    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def parse_fit(self, filepath):
        """Extract heart rate and distance data from FIT file"""
        if not HAS_FITPARSE:
            messagebox.showerror("Missing Dependency", "fitparse library is required.\nInstall with: pip install fitparse")
            return [], []
        
        hr_data = []
        distance_data = []
        
        try:
            fit_file = fitparse.FitFile(filepath)
            
            cumulative_distance = 0
            
            for record in fit_file.messages:
                if record.name == 'record':
                    for field in record.fields:
                        if field.name == 'heart_rate' and field.value is not None:
                            try:
                                hr = int(field.value)
                                if hr > 0:
                                    hr_data.append(hr)
                            except (ValueError, TypeError):
                                pass
                        elif field.name == 'distance' and field.value is not None:
                            try:
                                dist = float(field.value) / 1000  # Convert meters to km
                                if dist >= 0:
                                    cumulative_distance = dist
                            except (ValueError, TypeError):
                                pass
            
            # Estimate distance based on record count if not available
            if cumulative_distance == 0 and len(hr_data) > 0:
                cumulative_distance = len(hr_data) / 60  # Rough estimate: ~1km per minute
            
            distance_data = [cumulative_distance] * len(hr_data)
        
        except Exception as e:
            messagebox.showerror("Parse Error", f"Error parsing {filepath}: {str(e)}")
        
        return hr_data, distance_data
    
    def pace_to_string(self, pace_min_per_km):
        """Convert pace (min/km) to MM:SS format"""
        if pace_min_per_km == 0 or pace_min_per_km < 0:
            return "N/A"
        minutes = int(pace_min_per_km)
        seconds = int((pace_min_per_km - minutes) * 60)
        return f"{minutes}:{seconds:02d}"
    
    def estimate_zones(self, all_hr_data, all_distance_data):
        """Estimate heart rate zones with pace calculations"""
        if not all_hr_data:
            return None
        
        min_hr = min(all_hr_data)
        max_hr = max(all_hr_data)
        avg_hr = sum(all_hr_data) / len(all_hr_data)
        
        sorted_hr = sorted(all_hr_data)
        resting_hr = sorted_hr[len(sorted_hr) // 4]
        
        hrr = max_hr - resting_hr
        
        zones = {
            'Zone 1 - Recovery': {
                'min': resting_hr,
                'max': int(resting_hr + (hrr * 0.50)),
                'description': 'Light recovery, warm-up, cool-down'
            },
            'Zone 2 - Aerobic': {
                'min': int(resting_hr + (hrr * 0.50)),
                'max': int(resting_hr + (hrr * 0.60)),
                'description': 'Easy pace, conversation possible'
            },
            'Zone 3 - Tempo': {
                'min': int(resting_hr + (hrr * 0.60)),
                'max': int(resting_hr + (hrr * 0.70)),
                'description': 'Moderate effort, building endurance'
            },
            'Zone 4 - Threshold': {
                'min': int(resting_hr + (hrr * 0.70)),
                'max': int(resting_hr + (hrr * 0.85)),
                'description': 'Hard effort, lactate threshold training'
            },
            'Zone 5 - VO2Max': {
                'min': int(resting_hr + (hrr * 0.85)),
                'max': max_hr,
                'description': 'Maximum intensity, high-intensity intervals'
            }
        }
        
        # Calculate zone statistics
        zone_counts = defaultdict(int)
        zone_distances = defaultdict(float)
        zone_paces = defaultdict(list)
        
        for i, hr in enumerate(all_hr_data):
            distance = all_distance_data[i] if i < len(all_distance_data) else 0
            
            for zone_name in zones:
                zone = zones[zone_name]
                if zone['min'] <= hr <= zone['max']:
                    zone_counts[zone_name] += 1
                    zone_distances[zone_name] += distance / len(all_hr_data)
                    
                    # Estimate pace for this zone
                    if distance > 0:
                        time_minutes = len(all_hr_data) / 60
                        pace = time_minutes / max(distance, 0.001)
                        zone_paces[zone_name].append(pace)
        
        return {
            'zones': zones,
            'zone_counts': zone_counts,
            'zone_distances': zone_distances,
            'zone_paces': zone_paces,
            'stats': {
                'min_hr': min_hr,
                'max_hr': max_hr,
                'avg_hr': avg_hr,
                'resting_hr': resting_hr,
                'total_readings': len(all_hr_data),
                'total_distance': sum(all_distance_data) if all_distance_data else 0
            }
        }
    
    def analyze(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please select at least one FIT file")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.all_hr_data = []
        self.all_distance_data = []
        
        self.results_text.insert(tk.END, "Parsing FIT files...\n\n")
        self.root.update()
        
        file_count = 0
        for filepath in self.files:
            hr_data, distance_data = self.parse_fit(filepath)
            if hr_data:
                file_count += 1
                self.all_hr_data.extend(hr_data)
                self.all_distance_data.extend(distance_data)
                self.results_text.insert(tk.END, f"✓ {os.path.basename(filepath)}: {len(hr_data)} HR readings\n")
            else:
                self.results_text.insert(tk.END, f"✗ {os.path.basename(filepath)}: No HR data found\n")
        
        if not self.all_hr_data:
            messagebox.showerror("No Data", "No heart rate data found in any files")
            return
        
        result = self.estimate_zones(self.all_hr_data, self.all_distance_data)
        
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, "ANALYSIS SUMMARY\n", "header")
        self.results_text.insert(tk.END, "=" * 70 + "\n\n")
        
        stats = result['stats']
        self.results_text.insert(tk.END, f"Files Processed: {file_count}\n")
        self.results_text.insert(tk.END, f"Total HR Readings: {stats['total_readings']:,}\n")
        self.results_text.insert(tk.END, f"Total Distance: {stats['total_distance']:.2f} km\n")
        self.results_text.insert(tk.END, f"Resting HR: {stats['resting_hr']} bpm\n")
        self.results_text.insert(tk.END, f"Average HR: {stats['avg_hr']:.1f} bpm\n")
        self.results_text.insert(tk.END, f"Max HR: {stats['max_hr']} bpm\n\n")
        
        self.results_text.insert(tk.END, "HEART RATE ZONES WITH PACE\n", "header")
        self.results_text.insert(tk.END, "=" * 70 + "\n\n")
        
        for zone_name in result['zones']:
            zone = result['zones'][zone_name]
            count = result['zone_counts'][zone_name]
            percentage = (count / stats['total_readings'] * 100) if stats['total_readings'] > 0 else 0
            
            zone_paces = result['zone_paces'][zone_name]
            avg_pace = sum(zone_paces) / len(zone_paces) if zone_paces else 0
            
            self.results_text.insert(tk.END, f"{zone_name}\n", "zone_name")
            self.results_text.insert(tk.END, f"  HR Range: {zone['min']} - {zone['max']} bpm\n", "info")
            self.results_text.insert(tk.END, f"  Description: {zone['description']}\n", "info")
            self.results_text.insert(tk.END, f"  Time in Zone: {count:,} readings ({percentage:.1f}%)\n", "info")
            self.results_text.insert(tk.END, f"  Average Pace: {self.pace_to_string(avg_pace)} min/km\n", "info")
            
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            self.results_text.insert(tk.END, f"  {bar}\n", "info")
            self.results_text.insert(tk.END, "\n")
        
        # Save to database
        self.save_to_database(result, file_count)
        
        self.results_text.insert(tk.END, "\n✓ Data saved to database: hr_zone_data.csv\n", "header")
    
    def save_to_database(self, result, file_count):
        """Save analysis results to CSV database"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        stats = result['stats']
        
        file_exists = os.path.exists(self.db_file)
        
        with open(self.db_file, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                # Write header
                writer.writerow([
                    'Timestamp', 'Files Analyzed', 'Total HR Readings', 'Total Distance (km)',
                    'Resting HR', 'Average HR', 'Max HR',
                    'Zone 1 Count', 'Zone 1 %', 'Zone 1 Avg Pace',
                    'Zone 2 Count', 'Zone 2 %', 'Zone 2 Avg Pace',
                    'Zone 3 Count', 'Zone 3 %', 'Zone 3 Avg Pace',
                    'Zone 4 Count', 'Zone 4 %', 'Zone 4 Avg Pace',
                    'Zone 5 Count', 'Zone 5 %', 'Zone 5 Avg Pace'
                ])
            
            row = [timestamp, file_count, stats['total_readings'], f"{stats['total_distance']:.2f}",
                   stats['resting_hr'], f"{stats['avg_hr']:.1f}", stats['max_hr']]
            
            for zone_name in ['Zone 1 - Recovery', 'Zone 2 - Aerobic', 'Zone 3 - Tempo', 
                             'Zone 4 - Threshold', 'Zone 5 - VO2Max']:
                count = result['zone_counts'][zone_name]
                percentage = (count / stats['total_readings'] * 100) if stats['total_readings'] > 0 else 0
                
                zone_paces = result['zone_paces'][zone_name]
                avg_pace = sum(zone_paces) / len(zone_paces) if zone_paces else 0
                
                row.extend([count, f"{percentage:.1f}", self.pace_to_string(avg_pace)])
            
            writer.writerow(row)
        
        # Update cumulative stats
        self.cumulative_stats = self.load_cumulative_stats()
        self.refresh_history_tab()
    
    def load_cumulative_stats(self):
        """Load and calculate cumulative statistics from database"""
        if not os.path.exists(self.db_file):
            return None
        
        cumulative = {
            'sessions': 0,
            'total_readings': 0,
            'total_distance': 0,
            'avg_hr': 0,
            'max_hr': 0
        }
        
        try:
            with open(self.db_file, 'r') as f:
                reader = csv.DictReader(f)
                readings = []
                max_hrs = []
                total_dist = 0
                session_count = 0
                
                for row in reader:
                    session_count += 1
                    total_readings = int(row['Total HR Readings'])
                    cumulative['total_readings'] += total_readings
                    total_dist += float(row['Total Distance (km)'])
                    max_hrs.append(int(row['Max HR']))
                    
                    # Collect avg HR weighted by readings
                    readings.append((float(row['Average HR']), total_readings))
                
                cumulative['sessions'] = session_count
                cumulative['total_distance'] = total_dist
                cumulative['max_hr'] = max(max_hrs) if max_hrs else 0
                
                # Calculate weighted average HR
                if readings:
                    total_weighted = sum(hr * count for hr, count in readings)
                    cumulative['avg_hr'] = total_weighted / cumulative['total_readings']
        
        except Exception as e:
            print(f"Error loading stats: {e}")
        
        return cumulative
    
    def refresh_history_tab(self):
        """Refresh the history tab with cumulative stats and database contents"""
        self.cumulative_text.delete(1.0, tk.END)
        self.history_text.delete(1.0, tk.END)
        
        # Show cumulative stats
        if self.cumulative_stats and self.cumulative_stats['sessions'] > 0:
            self.cumulative_text.insert(tk.END, f"Total Sessions: {self.cumulative_stats['sessions']} | ")
            self.cumulative_text.insert(tk.END, f"Total HR Readings: {self.cumulative_stats['total_readings']:,} | ")
            self.cumulative_text.insert(tk.END, f"Total Distance: {self.cumulative_stats['total_distance']:.2f} km | ")
            self.cumulative_text.insert(tk.END, f"Avg HR (weighted): {self.cumulative_stats['avg_hr']:.1f} bpm | ")
            self.cumulative_text.insert(tk.END, f"Overall Max HR: {self.cumulative_stats['max_hr']} bpm")
        else:
            self.cumulative_text.insert(tk.END, "No data yet. Analyze some FIT files to populate this section.")
        
        # Show history table
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    content = f.read()
                    self.history_text.insert(tk.END, content)
            except Exception as e:
                self.history_text.insert(tk.END, f"Error reading database: {e}\n")
        else:
            self.history_text.insert(tk.END, "Database file not found yet.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartRateZoneAnalyzer(root)
    root.mainloop()
