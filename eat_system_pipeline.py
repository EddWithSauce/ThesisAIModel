import joblib
import pandas as pd
import time
import warnings

class EATSystemPipeline:

  def __init__(self):
    print("Initializing EAT System AI Core...")

    # Load Model 1 Artifact (Added!)
    self.m1_ctrl = joblib.load("model1_controller.joblib")

    # Load Model 2 Artifacts
    self.m2_prep = joblib.load("model2_preprocessor.joblib")
    self.m2_reg = joblib.load("model2_regressor.joblib")
    self.m2_cls = joblib.load("model2_classifier.joblib")

    # Load Model 3 Artifacts
    self.m3_prep = joblib.load("model3_preprocessor.joblib")
    self.m3_ag = joblib.load("model3_ag_engine.joblib")

  def process_new_batch(
      self,
      feedstock_type: str,
      initial_mass_kg: float,
      initial_moisture_pct: float,
      initial_load_a: float,
      target_crop: str,
      soil_type: str,
  ) -> dict:

    with warnings.catch_warnings():
      warnings.simplefilter("ignore")

      # ==========================================
      # 1. Execute Model 2: Batch Dynamics Estimator
      # ==========================================
      df_m2 = pd.DataFrame([{
          "Feedstock_Type": feedstock_type,
          "Initial_Mass_kg": initial_mass_kg,
          "Initial_Moisture_Pct": initial_moisture_pct,
          "Initial_Motor_Load_A": initial_load_a,
      }])

      m2_features = self.m2_prep.transform(df_m2)
      m2_reg_output = self.m2_reg.predict(m2_features)[0]

      est_time_min = round(m2_reg_output[0], 1)
      est_mass_kg = round(m2_reg_output[1], 2)
      npk_profile = self.m2_cls.predict(m2_features)[0]

      # ==========================================
      # 1.5. Execute Model 1: Digital Twin Simulation
      # ==========================================
      print("\n[SYSTEM] Handing off to ESP32 Edge Controller...")
      print(f"[ESP32] Target Time: {est_time_min} mins. Engaging Thermophilic Loop (Previewing 5 steps)")
      
      curr_temp = 32.0 # Baras ambient temp
      curr_moist = initial_moisture_pct
      curr_load = initial_load_a
      
      print(f"{'Step':<5} | {'Temp (°C)':<10} | {'Moist (%)':<10} | {'Heater PWM':<12} | {'Fan PWM':<10}")
      print("-" * 65)
      
      for step in range(1, 6):
          m1_preds = self.m1_ctrl.predict([[curr_temp, curr_moist, curr_load]])
          h_pwm = m1_preds[0][0] if m1_preds.ndim == 2 else m1_preds[0]
          f_pwm = m1_preds[0][1] if m1_preds.ndim == 2 else m1_preds[1]
          
          print(f"{step:<5} | {curr_temp:<10.1f} | {curr_moist:<10.1f} | {h_pwm:<12.1f} | {f_pwm:<10.1f}")
          
          # Basic physics progression
          curr_temp += (h_pwm * 0.05) - (f_pwm * 0.01)
          curr_moist -= (h_pwm * 0.01) + (f_pwm * 0.02)
          time.sleep(0.5)

      print("[ESP32] ... Fast-forwarding to batch completion ...\n")
      time.sleep(1)

      # ==========================================
      # 2. Execute Model 3: Contextual Agriculture Engine
      # ==========================================
      df_m3 = pd.DataFrame([{
          "Target_Crop": target_crop,
          "Soil_Type": soil_type,
          "Batch_NPK_Profile": npk_profile,
      }])

      m3_features = self.m3_prep.transform(df_m3)
      m3_output = self.m3_ag.predict(m3_features)[0]

      rec_dose_g = round(m3_output[0], 1)
      apply_freq_days = int(round(m3_output[1]))
      compat_score = round(m3_output[2], 1)

    return {
        "Est_Batch_Time_Min": est_time_min,
        "Est_Final_Mass_kg": est_mass_kg,
        "NPK_Profile": npk_profile,
        "Rec_Dose_g": rec_dose_g,
        "Apply_Freq_Days": apply_freq_days,
        "Compatibility_Score": compat_score,
    }


# Test Run Simulation
if __name__ == "__main__":
  pipeline = EATSystemPipeline()

  # Simulated Philippine household batch run
  batch_results = pipeline.process_new_batch(
      feedstock_type="Standard PH Household Waste (74% Rice, 11% Meat, 10% Veg)",
      initial_mass_kg=2.5,
      initial_moisture_pct=76.0,
      initial_load_a=2.1,
      target_crop="Talong (Eggplant)",
      soil_type="Clay Loam",
  )

  print("\n================ EAT SYSTEM BATCH REPORT ================")
  print("Input Batch Mass    : 2.50 kg")
  print("Feedstock Type      : Standard PH Household Waste")
  print("Target Crop / Soil  : Talong (Eggplant) / Clay Loam")
  print("---------------------------------------------------------")
  print(f"Estimated Time      : {batch_results['Est_Batch_Time_Min']} mins")
  print(f"Expected Final Yield: {batch_results['Est_Final_Mass_kg']} kg")
  print(f"Bio-Fertilizer Type : {batch_results['NPK_Profile']}")
  print("---------------------------------------------------------")
  print(f"Recommended Dosage  : {batch_results['Rec_Dose_g']} g per pot (10kg pot)")
  print(f"Application Schedule: Every {batch_results['Apply_Freq_Days']} days")
  print(f"Crop Match Score    : {batch_results['Compatibility_Score']}%")
  print("=========================================================")