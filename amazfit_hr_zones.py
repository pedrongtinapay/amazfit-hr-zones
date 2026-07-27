import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import xml.etree.ElementTree as ET
import os
from collections import defaultdict
from datetime import datetime

try:
    import fitparse
    HAS_FITPARSE = True
except ImportError:
    HAS_FITPARSE = False

class HeartRateZoneAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Amazfit Heart Rate Zone Estimator")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.files = []
        self.all_hr_data = []
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title = ttk.Label(main_frame, text="Amazfit Heart Rate Zone Estimator", 
                          font=("Arial", 16, "bold"))
        title.grid(row=0, column=0, columnspan=3, pady=10)
        
        # File upload section
        ttk.Label(main_frame, text="GPX Files:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        
        # File listbox
        self.file_listbox = tk.Listbox(main_frame, height=6)
        self.file_listbox.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S), padx=(5, 0))
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=5)
        
        ttk.Button(btn_frame, text="Add GPX Files", command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_files).pack(side=tk.LEFT, padx=5)
        
        # Analysis button
        ttk.Button(main_frame, text="Analyze Heart Rate Zones", 
                   command=self.analyze).grid(row=4, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Results section
        ttk.Label(main_frame, text="Heart Rate Zones:", 
                  font=("Arial", 12, "bold")).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(15, 5))
        
        # Results frame with scrollbar
        results_frame = ttk.Frame(main_frame)
        results_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.results_text = tk.Text(results_frame, height=15, width=100, wrap=tk.WORD)
        self.results_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=results_scrollbar.set)
        
        # Configure tags for styling
        self.results_text.tag_config("header", font=("Arial", 11, "bold"))
        self.results_text.tag_config("zone_name", font=("Arial", 10, "bold"), foreground="blue")
        self.results_text.tag_config("info", font=("Arial", 9))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
    
    def add_files(self):
        files = filedialog.askopenfilenames(
            title="Select workout files",
            filetypes=[("GPX and FIT files", "*.gpx;*.fit"), ("GPX files", "*.gpx"), ("FIT files", "*.fit"), ("All files", "*.*")]
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
    
    def parse_gpx(self, filepath):
        """Extract heart rate and timestamp data from GPX file"""
        hr_data = []
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            # GPX namespace
            ns = {'gpx': 'http://www.topografix.com/GPX/1/1',
                  'gpxtpx': 'http://www.garmin.com/xmlschemas/TrackPointExtension/v2'}
            
            # Find all track points with heart rate data
            for trkpt in root.findall('.//gpx:trkpt', ns):
                try:
                    # Try to find extensions with heart rate
                    extensions = trkpt.find('.//gpxtpx:TrackPointExtension', ns)
                    if extensions is not None:
                        hr_elem = extensions.find('gpxtpx:hr', ns)
                        if hr_elem is not None:
                            hr = int(hr_elem.text)
                            hr_data.append(hr)
                except (ValueError, AttributeError):
                    pass
        except Exception as e:
            messagebox.showerror("Parse Error", f"Error parsing {filepath}: {str(e)}")
        
        return hr_data
    
    def parse_fit(self, filepath):
        """Extract heart rate data from FIT file"""
        if not HAS_FITPARSE:
            messagebox.showerror("Missing Dependency", "fitparse library is required for FIT files.\nInstall with: pip install fitparse")
            return []
        
        hr_data = []
        try:
            fit_file = fitparse.FitFile(filepath)
            
            # Iterate through records in the FIT file
            for record in fit_file.messages:
                if record.name == 'record':
                    for field in record.fields:
                        if field.name == 'heart_rate' and field.value is not None:
                            try:
                                hr = int(field.value)
                                if hr > 0:  # Filter out invalid readings
                                    hr_data.append(hr)
                            except (ValueError, TypeError):
                                pass
        except Exception as e:
            messagebox.showerror("Parse Error", f"Error parsing {filepath}: {str(e)}")
        
        return hr_data
    
    def estimate_zones(self, all_hr_data):
        """
        Estimate heart rate zones using statistical analysis
        Common zone calculation: based on max HR and percentages
        """
        if not all_hr_data:
            return None
        
        min_hr = min(all_hr_data)
        max_hr = max(all_hr_data)
        avg_hr = sum(all_hr_data) / len(all_hr_data)
        
        # Calculate resting HR (lower quartile)
        sorted_hr = sorted(all_hr_data)
        resting_hr = sorted_hr[len(sorted_hr) // 4]
        
        # Calculate heart rate reserve (HRR)
        hrr = max_hr - resting_hr
        
        # Define zones using standard zone system (5 zones based on HRR)
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
        
        # Count HR readings in each zone
        zone_counts = defaultdict(int)
        for zone_name in zones:
            zone_counts[zone_name] = sum(1 for hr in all_hr_data 
                                        if zones[zone_name]['min'] <= hr <= zones[zone_name]['max'])
        
        return {
            'zones': zones,
            'zone_counts': zone_counts,
            'stats': {
                'min_hr': min_hr,
                'max_hr': max_hr,
                'avg_hr': avg_hr,
                'resting_hr': resting_hr,
                'total_readings': len(all_hr_data)
            }
        }
    
    def analyze(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please select at least one workout file")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.all_hr_data = []
        
        # Parse all files
        self.results_text.insert(tk.END, "Parsing workout files...\n\n")
        self.root.update()
        
        file_count = 0
        for filepath in self.files:
            # Determine file type and parse accordingly
            if filepath.lower().endswith('.fit'):
                hr_data = self.parse_fit(filepath)
            else:  # Default to GPX
                hr_data = self.parse_gpx(filepath)
            
            if hr_data:
                file_count += 1
                self.all_hr_data.extend(hr_data)
                self.results_text.insert(tk.END, f"✓ {os.path.basename(filepath)}: {len(hr_data)} HR readings\n")
            else:
                self.results_text.insert(tk.END, f"✗ {os.path.basename(filepath)}: No HR data found\n")
        
        if not self.all_hr_data:
            messagebox.showerror("No Data", "No heart rate data found in any files")
            return
        
        # Estimate zones
        result = self.estimate_zones(self.all_hr_data)
        
        # Display results
        self.results_text.delete(1.0, tk.END)
        
        self.results_text.insert(tk.END, "ANALYSIS SUMMARY\n", "header")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        stats = result['stats']
        self.results_text.insert(tk.END, f"Files Processed: {file_count}\n")
        self.results_text.insert(tk.END, f"Total HR Readings: {stats['total_readings']:,}\n")
        self.results_text.insert(tk.END, f"Resting HR: {stats['resting_hr']} bpm\n")
        self.results_text.insert(tk.END, f"Average HR: {stats['avg_hr']:.1f} bpm\n")
        self.results_text.insert(tk.END, f"Max HR: {stats['max_hr']} bpm\n\n")
        
        self.results_text.insert(tk.END, "HEART RATE ZONES\n", "header")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        
        for zone_name in result['zones']:
            zone = result['zones'][zone_name]
            count = result['zone_counts'][zone_name]
            percentage = (count / stats['total_readings'] * 100) if stats['total_readings'] > 0 else 0
            
            self.results_text.insert(tk.END, f"{zone_name}\n", "zone_name")
            self.results_text.insert(tk.END, f"  Range: {zone['min']} - {zone['max']} bpm\n", "info")
            self.results_text.insert(tk.END, f"  Description: {zone['description']}\n", "info")
            self.results_text.insert(tk.END, f"  Time in Zone: {count:,} readings ({percentage:.1f}%)\n", "info")
            
            # Visual bar
            bar_length = int(percentage / 5)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            self.results_text.insert(tk.END, f"  {bar}\n", "info")
            self.results_text.insert(tk.END, "\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = HeartRateZoneAnalyzer(root)
    root.mainloop()
