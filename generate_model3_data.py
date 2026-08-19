import numpy as np
import pandas as pd

np.random.seed(42)
num_samples = 3000

# Philippine Target Crops & Local Soil Profiles
crops = [
    'Pechay',
    'Kangkong',
    'Talong (Eggplant)',
    'Kamatis (Tomato)',
    'Sili (Chili Pepper)',
]
soil_types = ['Clay Loam', 'Volcanic / Silt Loam', 'Sandy Loam']
npk_profiles = [
    'Balanced Organic (High C / Moderate K)',
    'High Nitrogen & Fiber (N-Rich)',
    'High Phosphorus & Nitrogen (P-N Rich)',
    'Organic Soil Conditioner (High Carbon)',
]

sample_crops = np.random.choice(crops, size=num_samples)
sample_soils = np.random.choice(soil_types, size=num_samples)
sample_npks = np.random.choice(npk_profiles, size=num_samples)

doses = []
freqs = []
scores = []

for crop, soil, npk in zip(sample_crops, sample_soils, sample_npks):
  # Base application rates (grams per 10kg pot / plant)
  if crop in ['Pechay', 'Kangkong']:  # Fast-growing leafy greens
    base = 20.0 if 'N-Rich' in npk else 35.0
    freq = 7
  elif crop in [
      'Talong (Eggplant)',
      'Kamatis (Tomato)',
  ]:  # Heavy-feeding fruiting crops
    base = 25.0 if 'P-N Rich' in npk or 'High C / Moderate K' in npk else 40.0
    freq = 14
  else:  # Sili
    base = 22.0
    freq = 10

  # Local soil nutrient retention adjustments
  if soil == 'Sandy Loam':
    base *= 1.25  # Increased dosage due to higher water leaching
  elif soil == 'Clay Loam':
    base *= 0.85  # Decreased dosage due to high nutrient retention

  # Compatibility match score
  if (
      (crop in ['Pechay', 'Kangkong'] and 'N-Rich' in npk)
      or (
          crop in ['Talong (Eggplant)', 'Kamatis (Tomato)']
          and 'P-N Rich' in npk
      )
      or ('Balanced Organic' in npk)
  ):
    score = np.random.uniform(88.0, 99.0)
  else:
    score = np.random.uniform(65.0, 82.0)

  doses.append(round(base + np.random.normal(0, 0.8), 1))
  freqs.append(freq)
  scores.append(round(score, 1))

df_model3 = pd.DataFrame({
    'Target_Crop': sample_crops,
    'Soil_Type': sample_soils,
    'Batch_NPK_Profile': sample_npks,
    'Rec_Dose_g_per_pot': doses,
    'Apply_Freq_Days': freqs,
    'Compatibility_Score': scores,
})

df_model3.to_csv('model3_contextual_ag_dataset.csv', index=False)
print('Model 3 dataset created successfully!')
print(df_model3.head())