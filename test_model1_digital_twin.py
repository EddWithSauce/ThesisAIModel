import time
import random
import pandas as pd
import joblib  # Uncomment this to load your actual trained Model 1
import warnings

print("Loading model1_controller.joblib...")
try:
    model1 = joblib.load('model1_controller.joblib')
except FileNotFoundError:
    print("Error: Ensure 'model1_controller.joblib' is in the same folder as this script.")
    exit()

class DigitalChamber:
    def __init__(self):
        # Initial cold-start conditions
        self.temperature = 25.0  # °C
        self.moisture = 65.0     # %
        self.motor_load = 1.5    # A
        
    def update_physics(self, heater_pwm, fan_pwm):
        """Simulates how the chamber reacts to the ESP32's PWM signals."""
        # Heater increases temp; Fan cools it down
        temp_delta = (heater_pwm * 0.05) - (fan_pwm * 0.02) - 0.1 # Natural heat loss
        self.temperature += temp_delta
        
        # Heat and airflow reduce moisture
        moisture_delta = (heater_pwm * 0.01) + (fan_pwm * 0.03)
        self.moisture -= moisture_delta
        
        # Motor load fluctuates slightly based on moisture (drier = less sticky)
        self.motor_load = max(0.5, 1.5 + (self.moisture - 30) * 0.01 + random.uniform(-0.1, 0.1))
        
        # Clamp values to realistic bounds
        self.temperature = max(20.0, min(self.temperature, 100.0))
        self.moisture = max(10.0, min(self.moisture, 90.0))

def get_model1_predictions(temp, moisture, load):
    """
    Passes virtual sensor telemetry directly into your trained Random Forest model.
    """
    # Scikit-learn expects a 2D array for predictions: [[feature1, feature2, feature3]]
    # We use warnings to suppress the annoying feature-name mismatch warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        predictions = model1.predict([[temp, moisture, load]])
    
    # A multi-output regressor typically returns an array like [[heater_pwm, fan_pwm]]
    if predictions.ndim == 2:
        heater_pwm = predictions[0][0]
        fan_pwm = predictions[0][1]
    else:
        # Just in case it returns a flat array [heater_pwm, fan_pwm]
        heater_pwm = predictions[0]
        fan_pwm = predictions[1]
        
    return heater_pwm, fan_pwm

def run_simulation(steps=20):
    chamber = DigitalChamber()
    log = []
    
    print("Starting Model 1 Digital Twin Simulation...\n")
    print(f"{'Step':<5} | {'Temp (°C)':<10} | {'Moist (%)':<10} | {'Load (A)':<10} || {'Heater PWM':<12} | {'Fan PWM':<10}")
    print("-" * 75)
    
    for step in range(1, steps + 1):
        # 1. Read virtual sensors
        t, m, l = chamber.temperature, chamber.moisture, chamber.motor_load
        
        # 2. AI Model calculates control signals
        heater_pwm, fan_pwm = get_model1_predictions(t, m, l)
        
        # 3. Log data
        log.append({'Step': step, 'Temp': t, 'Moisture': m, 'Heater_PWM': heater_pwm, 'Fan_PWM': fan_pwm})
        print(f"{step:<5} | {t:<10.1f} | {m:<10.1f} | {l:<10.2f} || {heater_pwm:<12.1f} | {fan_pwm:<10.1f}")
        
        # 4. Apply outputs to the physical chamber twin
        chamber.update_physics(heater_pwm, fan_pwm)
        time.sleep(0.1) # Fast-forwarded time
        
    print("\nSimulation Complete!")

if __name__ == "__main__":
    run_simulation(steps=15)