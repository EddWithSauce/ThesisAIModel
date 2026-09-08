import pandas as pd
import joblib
import warnings

def load_model3_pipeline():
    """Loads the preprocessor and ag engine for Model 3."""
    print("Loading Model 3 Artifacts...")
    try:
        preprocessor = joblib.load('model3_preprocessor.joblib')
        ag_engine = joblib.load('model3_ag_engine.joblib')
        return preprocessor, ag_engine
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        exit()

def get_agronomic_recommendation(preprocessor, ag_engine, crop, soil, npk_profile):
    """Simulates the Mini-PC generating a crop dosing schedule."""
    
    input_data = pd.DataFrame({
        'Target_Crop': [crop],
        'Soil_Type': [soil],
        'Batch_NPK_Profile': [npk_profile]
    })
    
    print("\n" + "="*50)
    print("  EAT SYSTEM: AGRONOMIC RECOMMENDATION  ")
    print("="*50)
    print(f"Target Crop:  {crop}")
    print(f"Soil Type:    {soil}")
    print(f"Batch NPK:    {npk_profile}")
    print("-" * 50)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        processed_features = preprocessor.transform(input_data)
        predictions = ag_engine.predict(processed_features)[0]
    
    # Extract outputs
    rec_dose_g = predictions[0]
    interval_days = predictions[1]
    match_score = predictions[2]
    
    print(" APPLICATION PROTOCOL:")
    print(f" >> Crop Compatibility Match: {match_score:.1f}%")
    print(f" >> Recommended Dosage:       {rec_dose_g:.1f} grams per 10kg pot")
    print(f" >> Application Interval:     Every {interval_days:.0f} Days")
    print("="*50 + "\n")

if __name__ == "__main__":
    prep, ag_engine = load_model3_pipeline()
    
    # --- TEST SCENARIO 1: Pechay in Clay Loam ---
    # Using the exact output from our Model 2 test!
    get_agronomic_recommendation(
        prep, ag_engine,
        crop='Pechay',
        soil='Clay Loam',
        npk_profile='High Nitrogen & Fiber (N-Rich)' 
    )
    
    # --- TEST SCENARIO 2: Talong in Volcanic Soil ---
    get_agronomic_recommendation(
        prep, ag_engine,
        crop='Talong (Eggplant)',
        soil='Volcanic / Silt Loam',
        npk_profile='High Phosphorus & Nitrogen (P-N Rich)'
    )