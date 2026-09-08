import pandas as pd
import joblib
import warnings

def load_model2_pipeline():
    """Loads the preprocessor, regressor, and classifier for Model 2."""
    print("Loading Model 2 Artifacts...")
    try:
        preprocessor = joblib.load('model2_preprocessor.joblib')
        regressor = joblib.load('model2_regressor.joblib')
        classifier = joblib.load('model2_classifier.joblib')
        return preprocessor, regressor, classifier
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        exit()

def estimate_batch(preprocessor, regressor, classifier, feedstock, mass, moisture, load):
    """Simulates the Mini-PC predicting the batch outcomes."""
    
    # 1. Format the raw telemetry exactly how the preprocessor expects it
    input_data = pd.DataFrame({
        'Feedstock_Type': [feedstock],
        'Initial_Mass_kg': [mass],
        'Initial_Moisture_Pct': [moisture],
        'Initial_Motor_Load_A': [load]
    })
    
    print("\n" + "="*50)
    print(" 🌿 EAT SYSTEM: NEW BATCH INITIALIZATION 🌿 ")
    print("="*50)
    print(f"Input Type:   {feedstock}")
    print(f"Initial Mass: {mass} kg")
    print(f"Moisture:     {moisture}%")
    print(f"Motor Load:   {load} A")
    print("-" * 50)
    
    # 2. Preprocess the data (One-Hot Encoding the strings, scaling the numbers)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        processed_features = preprocessor.transform(input_data)
        
        # 3. Run predictions
        reg_preds = regressor.predict(processed_features)[0] 
        npk_class = classifier.predict(processed_features)[0]
    
    # Extract regression targets
    est_time_min = reg_preds[0]
    est_yield_kg = reg_preds[1]
    
    # Convert minutes to hours for easier reading
    est_time_hours = est_time_min / 60.0
    
    print(" 📊 ESTIMATION RESULTS:")
    print(f" >> Projected Processing Time: {est_time_hours:.1f} Hours ({est_time_min:.0f} mins)")
    print(f" >> Expected Final Yield:      {est_yield_kg:.2f} kg of Bio-Fertilizer")
    print(f" >> Predicted NPK Profile:     {npk_class}")
    print("="*50 + "\n")

if __name__ == "__main__":
    prep, reg, clf = load_model2_pipeline()
    
    # --- TEST SCENARIO 1: A Standard Filipino Dinner Cleanup ---
    # Imagine a household in Baras dumping in leftover rice, sabaw, and some fish bones.
    estimate_batch(
        prep, reg, clf,
        feedstock='Standard PH Household Waste (74% Rice, 11% Meat, 10% Veg)',
        mass=1.5,       # 1.5 kg of food waste
        moisture=78.0,  # Very wet from the soup/sauce
        load=2.8        # Heavy, sticky load on the comminution blades
    )
    
    # --- TEST SCENARIO 2: Vegetable Scraps from the Palengke ---
    # Mostly pechay and kangkong stalks, lighter and slightly drier.
    estimate_batch(
        prep, reg, clf,
        feedstock='High-Vegetable / Market Scraps (40% Veg, 40% Rice, 20% Fruit)',
        mass=0.8,       
        moisture=82.0,  
        load=1.4        # Very low motor resistance
    )