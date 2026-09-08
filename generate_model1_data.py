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
# Simulate shifting Philippine day/night temperatures (~23°C to ~33°C)
  dynamic_ambient = 28.0 + (np.sin(i / 400.0) * 5.0) 
  
  # --- 1 & 2. Comprehensive Control Logic ---
  if curr_temp > 72.0:
    # TEST 1 FIX: Emergency Thermal Purge
    base_heater = 0.0
    base_fan = 100.0
  elif curr_temp < 50.0:
    # TEST 2 FIX: Aggressive Cold/Soggy Start
    base_heater = 100.0  # Max heat to reach thermophilic target
    base_fan = 30.0 + max(0.0, (curr_moisture - 60.0) * 2.0) # Boost fan if extremely wet
  else:
    # GOLDILOCKS ZONE: Smooth Maintenance (50°C - 72°C)
    temp_error = target_temp - curr_temp
    if curr_temp <= 65.0:
      base_heater = 30.0 + (temp_error * 3.0)  
    else:
      base_heater = max(0.0, 30.0 - (curr_temp - 65.0) * 6.0)
      
    base_fan = 15.0 + max(0.0, (curr_moisture - 30.0) * 0.95)
    if curr_temp > 62.0:
      base_fan += (curr_temp - 62.0) * 4.0 

  # Hardware Clipping Limits
  p_heat = float(np.clip(base_heater, 0.0, 100.0))
  p_fan = float(np.clip(base_fan, 10.0, 100.0))

  # Add hardware noise
  actual_heater_pwm = float(np.clip(p_heat + np.random.normal(0, 0.5), 0.0, 100.0))
  actual_fan_pwm = float(np.clip(p_fan + np.random.normal(0, 0.5), 0.0, 100.0))

  # --- 3. Dynamic Physics & Environment Engine ---
  temp_gain = (
      (actual_heater_pwm * 0.04)
      - ((curr_temp - dynamic_ambient) * 0.008)
      - (actual_fan_pwm * 0.006)
  )
  curr_temp += temp_gain + np.random.normal(0, 0.02)
  
  moisture_loss = (curr_temp * 0.0004) + (actual_fan_pwm * 0.00025)
  curr_moisture = max(10.0, curr_moisture - moisture_loss)
  
  # Load mapping: wetter/colder = heavier sludge = higher amps
  curr_load = 1.2 + (curr_moisture * 0.02) + np.random.normal(0, 0.05)

  # --- 4. Chaos Injector (The Extrapolation Fix) ---
  if i % 600 == 0 and i > 0:
      # Inject Thermal Runaway (Trains the AI for Test 1)
      curr_temp = np.random.uniform(80.0, 95.0)
      curr_moisture = np.random.uniform(20.0, 45.0)
      curr_load = np.random.uniform(0.5, 1.5)
  elif i % 600 == 300 and i > 0:
      # Inject Extreme Soggy Start (Trains the AI for Test 2)
      curr_temp = np.random.uniform(20.0, 30.0)
      curr_moisture = np.random.uniform(75.0, 95.0)
      curr_load = np.random.uniform(3.0, 4.5)  # Forces the AI to learn how to handle heavy 3.50A+ loads!

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