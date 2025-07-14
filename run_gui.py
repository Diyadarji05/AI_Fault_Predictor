import tkinter as tk
from tkinter import messagebox
import pandas as pd
import joblib
import os
import time
import threading
import platform
from sensor_simulator import generate_sensor_data
import matplotlib.pyplot as plt

model = joblib.load("model.pkl")
LOG_FILE = "fault_log.csv"
monitoring = False
last_fault = False

# 🔊 Play Beep Sound
def play_beep():
    if platform.system() == "Windows":
        import winsound
        winsound.Beep(1000, 500)
    else:
        print('\a')

# 📝 Log sensor data
def log_data(data, prediction):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.read_csv(LOG_FILE) if os.path.exists(LOG_FILE) else pd.DataFrame(columns=["Vibration", "Temperature", "Current", "Fault", "Timestamp"])
    df.loc[len(df)] = list(data) + [prediction, timestamp]
    df.tail(500).to_csv(LOG_FILE, index=False)

# 🖼️ Show Graph
def show_graph():
    if not os.path.exists(LOG_FILE):
        messagebox.showerror("Error", "Log file not found!")
        return
    df = pd.read_csv(LOG_FILE)
    plt.figure(figsize=(8,4))
    plt.plot(df["Fault"], marker='o')
    plt.title("Fault History")
    plt.ylabel("Fault (1 = Detected)")
    plt.xlabel("Samples")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 📂 Open Log Preview
def open_log():
    if not os.path.exists(LOG_FILE):
        messagebox.showerror("Error", "Log file not found!")
        return
    df = pd.read_csv(LOG_FILE)
    preview = df.tail(10).to_string(index=False)
    messagebox.showinfo("Log Preview", preview)

# 🔁 Monitor Loop (in background)
def monitor_loop():
    global monitoring, last_fault

    while monitoring:
        status_label.config(text="🔄 Fetching details...", fg="orange")
        root.update_idletasks()
        time.sleep(1)

        data = generate_sensor_data()
        prediction = model.predict([data])[0]
        last_fault = bool(prediction)

        status = "❌ FAULT DETECTED!" if prediction else "✅ All Good"
        color = "red" if prediction else "green"

        status_label.config(text=status, fg=color)
        sensor_label.config(text=f"V={data[0]:.2f}g, T={data[1]:.1f}°C, C={data[2]:.2f}A")
        root.update_idletasks()

        log_data(data, prediction)

        status_label.config(text="✅ Fetching done. You can stop monitoring.", fg="green")
        time.sleep(2)

# ▶️ Start Button Click
def start_monitoring():
    global monitoring
    monitoring = True
    threading.Thread(target=monitor_loop, daemon=True).start()

# ⏹ Stop Button Click
def stop_monitoring():
    global monitoring
    monitoring = False
    if last_fault:
        play_beep()
        messagebox.showerror("Fault Detected", "❌ Fault was detected during monitoring!")
    else:
        messagebox.showinfo("No Fault", "✅ No faults found. You can start a new session.")

# 🧱 GUI Setup
root = tk.Tk()
root.title("🛡️ AI Fault Monitoring System")
root.geometry("400x400")

tk.Label(root, text="AI Fault Detection Dashboard", font=("Helvetica", 16, "bold")).pack(pady=10)

status_label = tk.Label(root, text="Status: Not Started", font=("Arial", 12))
status_label.pack(pady=5)

sensor_label = tk.Label(root, text="Sensor Data: --", font=("Arial", 10))
sensor_label.pack(pady=5)

tk.Button(root, text="▶️ Start Monitoring", width=20, command=start_monitoring).pack(pady=10)
tk.Button(root, text="⏹ Stop Monitoring", width=20, command=stop_monitoring).pack()

# 📊 Graph & Logs Section
tk.Label(root, text="\n📊 Graph and Logs", font=("Arial", 12, "bold")).pack()

tk.Button(root, text="Show Fault Graph", command=show_graph).pack(pady=5)
tk.Button(root, text="Open Log CSV", command=open_log).pack(pady=5)

root.mainloop()
