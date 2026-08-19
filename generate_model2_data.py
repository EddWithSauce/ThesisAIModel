import numpy as np
import pandas as pd

np.random.seed(42)
num_batches = 2000

# Philippine Household Waste Feedstock Profiles based on DOST-FNRI Mass Data
feedstock_categories = [
    'Standard PH Household Waste (74% Rice, 11% Meat, 10% Veg)',
    'High-Vegetable / Market Scraps (40% Veg, 40% Rice, 20% Fruit)',
    'High-Protein / Meat Scraps (40% Meat, 45% Rice, 15% Veg)',
    'Pure Carbohydrate / Grain Waste (90%+ Rice/Bread)',
]

sampled_feedstocks = np.random.choice(
    feedstock_categories, size=num_batches, p=[0.55, 0.20, 0.15, 0.10]
)

initial_mass_kg = np.random.uniform(1.0, 5.0, size=num_batches)

# Moisture & Motor Load simulation tailored to PH starch-heavy waste
initial_moisture_pct = []
initial_motor_load_a = []
npk_profiles = []

for fs in sampled_feedstocks:
  if 'Standard PH Household' in fs:
    moisture = np.random.uniform(72.0, 82.0)  # High due to rice + sauces/sabaw
    load = np.random.uniform(1.6, 2.3)  # Viscous gelled starch slurry
    npk = 'Balanced Organic (High C / Moderate K)'
  elif 'High-Vegetable' in fs:
    moisture = np.random.uniform(78.0, 88.0)
    load = np.random.uniform(1.2, 1.7)
    npk = 'High Nitrogen & Fiber (N-Rich)'
  elif 'High-Protein' in fs:
    moisture = np.random.uniform(65.0, 76.0)
    load = np.random.uniform(1.8, 2.6)
    npk = 'High Phosphorus & Nitrogen (P-N Rich)'
  else:  # Pure Carbs
    moisture = np.random.uniform(68.0, 78.0)
    load = np.random.uniform(1.9, 2.8)  # Thick starch resistance
    npk = 'Organic Soil Conditioner (High Carbon)'

  initial_moisture_pct.append(round(moisture, 2))
  initial_motor_load_a.append(round(load, 2))
  npk_profiles.append(npk)

initial_moisture_pct = np.array(initial_moisture_pct)

# Drying Physics: Bound water in rice requires higher latent heat of vaporization
water_mass_kg = initial_mass_kg * (initial_moisture_pct / 100.0)
batch_time_min = 85.0 + (water_mass_kg * 48.0) + np.random.normal(0, 3.0)

# Final Mass Yield at 30% target moisture
dry_matter_kg = initial_mass_kg - water_mass_kg
final_mass_kg = dry_matter_kg + (dry_matter_kg * (0.30 / 0.70)) + np.random.normal(0, 0.03)

df_ph_model2 = pd.DataFrame({
    'Feedstock_Type': sampled_feedstocks,
    'Initial_Mass_kg': np.round(initial_mass_kg, 2),
    'Initial_Moisture_Pct': initial_moisture_pct,
    'Initial_Motor_Load_A': initial_motor_load_a,
    'Target_Batch_Time_Min': np.round(batch_time_min, 1),
    'Target_Final_Mass_kg': np.round(final_mass_kg, 2),
    'Projected_NPK_Profile': npk_profiles,
})

df_ph_model2.to_csv('model2_synthetic_batch_dataset.csv', index=False)
print('Philippine-calibrated Model 2 dataset generated successfully!')
print(df_ph_model2.head())