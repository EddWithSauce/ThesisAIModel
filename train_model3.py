import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# 1. Load Model 3 dataset
print("Loading Model 3 dataset...")
df = pd.read_csv('model3_contextual_ag_dataset.csv')

# 2. Features and Targets
X = df[['Target_Crop', 'Soil_Type', 'Batch_NPK_Profile']]
y = df[['Rec_Dose_g_per_pot', 'Apply_Freq_Days', 'Compatibility_Score']]

# 3. Categorical Pipeline (One-Hot Encoding)
preprocessor = ColumnTransformer(
    transformers=[(
        'cat',
        OneHotEncoder(handle_unknown='ignore'),
        ['Target_Crop', 'Soil_Type', 'Batch_NPK_Profile'],
    )]
)

X_processed = preprocessor.fit_transform(X)

# 4. Train-Test Split (80% Train, 20% Test)
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y, test_size=0.2, random_state=42
)

# 5. Train Multi-Output Random Forest Regressor
print("Training Model 3 Contextual Ag Engine...")
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# 6. Evaluate Model Metrics
y_pred = model.predict(X_test)

mae_dose = mean_absolute_error(y_test['Rec_Dose_g_per_pot'], y_pred[:, 0])
r2_dose = r2_score(y_test['Rec_Dose_g_per_pot'], y_pred[:, 0])

mae_freq = mean_absolute_error(y_test['Apply_Freq_Days'], y_pred[:, 1])
r2_freq = r2_score(y_test['Apply_Freq_Days'], y_pred[:, 1])

mae_score = mean_absolute_error(y_test['Compatibility_Score'], y_pred[:, 2])
r2_score_val = r2_score(y_test['Compatibility_Score'], y_pred[:, 2])

print("\n================ MODEL 3 EVALUATION ================")
print(
    f"Recommended Dosage   - MAE: {mae_dose:.2f} g/pot | R² Score:"
    f" {r2_dose:.4f}"
)
print(
    f"Application Interval - MAE: {mae_freq:.2f} days  | R² Score:"
    f" {r2_freq:.4f}"
)
print(
    f"Compatibility Score  - MAE: {mae_score:.2f}%     | R² Score:"
    f" {r2_score_val:.4f}"
)
print("====================================================")

# 7. Export Model Artifacts
joblib.dump(preprocessor, 'model3_preprocessor.joblib')
joblib.dump(model, 'model3_ag_engine.joblib')
print("\nModel 3 preprocessor and model saved successfully!")