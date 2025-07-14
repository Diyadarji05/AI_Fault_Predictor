import random

def generate_sensor_data():
    # Fake sensor: vibration (g), temperature (°C), current (A)
    vibration = round(random.uniform(0.1, 3.5), 2)
    temperature = round(random.uniform(25, 90), 1)
    current = round(random.uniform(0.5, 15.0), 2)
    return [vibration, temperature, current]
