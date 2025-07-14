import streamlit as st
import pandas as pd
import joblib
import time
import os
from sensor_simulator import generate_sensor_data

model = joblib.load("model.pkl")
LOG_FILE = "fault_log.csv"

# Load beep audio once
def play_alert_sound():
    st.markdown(
        """
        <audio id="myBeep" autoplay>
            <source src="alert.mp3" type="audio/mpeg">
        </audio>
        <script>
            document.getElementById("myBeep").play().catch(e => console.log(e));
        </script>
        """,
        unsafe_allow_html=True
    )

# Title
st.title("🛡️ AI Fault Detection Dashboard")

# State variables
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False
if "last_fault" not in st.session_state:
    st.session_state.last_fault = False

# Buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Start Monitoring"):
        st.session_state.monitoring = True
        st.success("System is now monitoring...")
with col2:
    if st.button("⏹️ Stop Monitoring"):
        st.session_state.monitoring = False
        if st.session_state.last_fault:
            play_alert_sound()
            st.error("❌ Fault detected during last monitoring.")
        else:
            st.info("✅ No fault detected. You can start a new monitoring.")

# UI placeholders
status_box = st.empty()
data_box = st.empty()

# Run monitoring
if st.session_state.monitoring:
    with st.spinner("🔄 Fetching sensor data and analyzing..."):
        data = generate_sensor_data()
        prediction = model.predict([data])[0]

        # Save fault result for STOP button to read
        st.session_state.last_fault = bool(prediction)

        # Update UI
        status = "❌ FAULT DETECTED!" if prediction else "✅ All Clear"
