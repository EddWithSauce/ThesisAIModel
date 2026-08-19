import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# 1. Load the generated Model 2 synthetic dataset
print("Loading Model 2 batch dataset...")
df = pd.read_csv('model2_synthetic_batch_dataset.csv')

# 2. Define Features and Targets
X = df[['Feedstock_Type', 'Initial_Mass_kg', 'Initial_Moisture_Pct']]
y_reg = df[['Target_Batch_Time_Min', 'Target_Final_Mass_kg']]
y_cls = df['Projected_NPK_Profile']

# Setup One-Hot Encoding pipeline for categorical input 'Feedstock_Type'
preprocessor = ColumnTransformer(
    transformers=[
        (
            'cat',
            OneHotEncoder(handle_unknown='ignore'),
            ['Feedstock_Type'],
        )
    ],
    remainder='passthrough',
)

# Transform input features into numerical matrices
X_processed = preprocessor.fit_transform(X)

# 3. Train-Test Split (80% Train, 20% Test)
X_train, X_test, y_reg_train, y_reg_test, y_cls_train, y_cls_test = (
    train_test_split(X_processed, y_reg, y_cls, test_size=0.2, random_state=42)
)

# 4. Train Regressor (Time & Yield Mass)
print("Training Batch Dynamics Regressor...")
regressor = RandomForestRegressor(
    n_estimators=100, max_depth=10, random_state=42
)
regressor.fit(X_train, y_reg_train)

# 5. Train Classifier (NPK Category)
print("Training NPK Profile Classifier...")
classifier = RandomForestClassifier(n_estimators=50, random_state=42)
classifier.fit(X_train, y_cls_train)

# 6. Evaluate Regressor Metrics
y_reg_pred = regressor.predict(X_test)
mae_time = mean_absolute_error(y_reg_test['Target_Batch_Time_Min'], y_reg_pred[:, 0])
r2_time = r2_score(y_reg_test['Target_Batch_Time_Min'], y_reg_pred[:, 0])

mae_mass = mean_absolute_error(y_reg_test['Target_Final_Mass_kg'], y_reg_pred[:, 1])
r2_mass = r2_score(y_reg_test['Target_Final_Mass_kg'], y_reg_pred[:, 1])

# 7. Evaluate Classifier Metrics
y_cls_pred = classifier.predict(X_test)
acc_npk = accuracy_score(y_cls_test, y_cls_pred)

print("\n================ EVALUATION METRICS ================")
print(f"Batch Processing Time - MAE: {mae_time:.2f} mins | R²: {r2_time:.4f}")
print(f"Final Yield Mass      - MAE: {mae_mass:.3f} kg   | R²: {r2_mass:.4f}")
print(f"NPK Profile Class     - Accuracy: {acc_npk * 100:.2f}%")
print("====================================================")

# 8. Save Preprocessor, Regressor, and Classifier
joblib.dump(preprocessor, 'model2_preprocessor.joblib')
joblib.dump(regressor, 'model2_regressor.joblib')
joblib.dump(classifier, 'model2_classifier.joblib')

print("\nModel 2 artifacts successfully exported!")