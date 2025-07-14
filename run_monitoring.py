import time
import threading
from sensor_simulator import generate_sensor_data
import joblib
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
import webbrowser
import tkinter as tk
from tkinter import ttk
import winsound  # Windows only


# Config
LOG_FILE = "fault_log.csv"
MAX_LOG_ENTRIES = 500
MODEL_FILE = "model.pkl"

# Load model
model = joblib.load(MODEL_FILE)

# Make log file if needed
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Vibration", "Temperature", "Current", "Fault", "Timestamp"])

# Log function
def log_data(sensor_data, prediction):
    try:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        row = sensor_data + [prediction, timestamp]

        df = pd.read_csv(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=["Vibration", "Temperature", "Current", "Fault", "Timestamp"])
        df.loc[len(df)] = row

        if len(df) > MAX_LOG_ENTRIES:
            df = df.tail(MAX_LOG_ENTRIES)

        df.to_csv(LOG_FILE, index=False)
    except PermissionError:
        print("⚠️ fault_log.csv is open. Please close it and try again.")

# Plot graph
def plot_fault_graph():
    try:
        df = pd.read_csv(LOG_FILE)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df['Minute'] = df['Timestamp'].dt.strftime('%H:%M')
        fault_counts = df.groupby('Minute')['Fault'].sum()

        plt.figure(figsize=(12, 6))
        plt.plot(fault_counts.index, fault_counts.values, marker='o', color='blue', label='Line Graph')
        plt.bar(fault_counts.index, fault_counts.values, alpha=0.4, color='red', label='Bar Graph')
        plt.title("Faults Per Minute")
        plt.xlabel("Time (Minute)")
        plt.ylabel("Number of Faults")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"⚠️ Could not show graphs: {e}")

# GUI Class
class FaultMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Fault Monitor GUI")
        self.running = False

        self.status_label = ttk.Label(root, text="Status: Stopped", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.sensor_label = ttk.Label(root, text="Sensor Data: --", font=("Arial", 12))
        self.sensor_label.pack(pady=5)

        self.start_btn = ttk.Button(root, text="Start Monitoring", command=self.start_monitoring)
        self.start_btn.pack(pady=5)

        self.stop_btn = ttk.Button(root, text="Stop Monitoring", command=self.stop_monitoring)
        self.stop_btn.pack(pady=5)

        self.graph_btn = ttk.Button(root, text="Show Fault Graph", command=plot_fault_graph)
        self.graph_btn.pack(pady=5)

        self.open_csv_btn = ttk.Button(root, text="Open Log CSV", command=self.open_csv_file)
        self.open_csv_btn.pack(pady=5)

    def open_csv_file(self):
        try:
            webbrowser.open(os.path.abspath(LOG_FILE))
        except:
            print("⚠️ Could not open log file.")
    
    def monitor_loop(self):
        while self.running:
         data = generate_sensor_data()
        prediction = model.predict([data])[0]

        log_data(data, prediction)

        status = "FAULT DETECTED!" if prediction == 1 else "All Good"
        color = "red" if prediction == 1 else "green"

        if prediction == 1:
            winsound.Beep(1000, 500)

        self.status_label.config(text=f"Status: {status}", foreground=color)
        self.sensor_label.config(text=f"Sensor Data: V={data[0]}g, T={data[1]}°C, C={data[2]}A")

        self.root.update_idletasks()  # ✅ Force GUI to refresh labels

        time.sleep(2)

    def start_monitoring(self):
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self.monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def stop_monitoring(self):
        self.running = False
        self.status_label.config(text="Status: Stopped", foreground="black")
        self.sensor_label.config(text="Sensor Data: --")

# Run GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = FaultMonitorApp(root)
    root.mainloop()
