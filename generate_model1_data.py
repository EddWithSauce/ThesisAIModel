import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Set plot style for clean visualization
sns.set_theme(style="whitegrid")

# Set random seed for reproducibility
np.random.seed(42)

# Generate 5,000 simulated sensor readings (1-second intervals)
time_steps = 5000
ambient_temp = 28.0  # Ambient temperature in °C
target_temp = 60.0  # Midpoint of the 50°C - 70°C thermophilic pasteurization target

chamber_temp = []
moisture_content = []
motor_load_amps = []
heater_pwm = []
fan_pwm = []

curr_temp = ambient_temp
curr_moisture = 75.0  # Starting moisture %

for i in range(time_steps):
  # 1. Smooth Continuous Control Logic for Heater PWM
  temp_error = target_temp - curr_temp

  # Smooth proportional heater curve with saturation limits [0%, 100%]
  if curr_temp < 50.0:
    base_heater = 80.0 + (50.0 - curr_temp) * 0.82  # Ramp up rapidly from cold
  elif 50.0 <= curr_temp <= 65.0:
    base_heater = 30.0 + (temp_error * 3.0)  # Fine balance inside thermophilic zone
  else:
    base_heater = max(0.0, 30.0 - (curr_temp - 65.0) * 6.0)  # Cut heat on overshoot

  p_heat = float(np.clip(base_heater, 0.0, 100.0))

  # 2. Smooth Control Logic for Aeration Fan PWM
  # Higher fan speed when moisture is high or when temperature overshoots
  base_fan = 15.0 + (curr_moisture - 30.0) * 0.95
  if curr_temp > 62.0:
    base_fan += (curr_temp - 62.0) * 4.0  # Boost fan for thermal management

  p_fan = float(np.clip(base_fan, 10.0, 100.0))

  # Add realistic sensor & environmental micro-jitter (noise sd = 0.5)
  actual_heater_pwm = float(
      np.clip(p_heat + np.random.normal(0, 0.5), 0.0, 100.0)
  )
  actual_fan_pwm = float(
      np.clip(p_fan + np.random.normal(0, 0.5), 0.0, 100.0)
  )

  # 3. Dynamic Physics Equations
  temp_gain = (
      (actual_heater_pwm * 0.04)
      - ((curr_temp - ambient_temp) * 0.008)
      - (actual_fan_pwm * 0.006)
  )
  curr_temp += temp_gain + np.random.normal(0, 0.02)

  # Moisture evaporation rate based on heat and airflow
  moisture_loss = (curr_temp * 0.0004) + (actual_fan_pwm * 0.00025)
  curr_moisture = max(30.0, curr_moisture - moisture_loss)

  # Motor load impedance based on slurry moisture content
  curr_load = 1.2 + (curr_moisture * 0.018) + np.random.normal(0, 0.01)

  chamber_temp.append(round(curr_temp, 2))
  moisture_content.append(round(curr_moisture, 2))
  motor_load_amps.append(round(curr_load, 2))
  heater_pwm.append(round(actual_heater_pwm, 2))
  fan_pwm.append(round(actual_fan_pwm, 2))

# Create DataFrame
df_model1 = pd.DataFrame({
    'Chamber_Temp_C': chamber_temp,
    'Moisture_Percent': moisture_content,
    'Motor_Load_A': motor_load_amps,
    'Target_Heater_PWM': heater_pwm,
    'Target_Fan_PWM': fan_pwm,
})

# Save to CSV
df_model1.to_csv('model1_synthetic_control_dataset.csv', index=False)
print('Smoothed dataset generated successfully!')
print(df_model1.head())

# Save Plot
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.set_xlabel('Time Steps (s)')
ax1.set_ylabel('Chamber Temp (°C)', color='tab:red')
ax1.plot(df_model1['Chamber_Temp_C'], color='tab:red', alpha=0.8)

ax2 = ax1.twinx()
ax2.set_ylabel('Moisture Content (%)', color='tab:blue')
ax2.plot(df_model1['Moisture_Percent'], color='tab:blue', alpha=0.8)

plt.title('EAT Chamber Thermal & Moisture Profile (Smoothed Model 1 Dataset)')
fig.tight_layout()
plt.savefig('chamber_simulation_profile.png')