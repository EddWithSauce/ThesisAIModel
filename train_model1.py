import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

# Set plot style
sns.set_theme(style="whitegrid")

# 1. Load the generated synthetic dataset
print("Loading dataset...")
df = pd.read_csv('model1_synthetic_control_dataset.csv')

# 2. Separate Features (Inputs) and Targets (Outputs)
X = df[['Chamber_Temp_C', 'Moisture_Percent', 'Motor_Load_A']]
y = df[['Target_Heater_PWM', 'Target_Fan_PWM']]

# 3. Split into 80% Training set and 20% Testing set
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Train the Multi-Output Random Forest Regressor
print("Training Model 1 Controller...")
model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# 5. Evaluate Model Metrics
y_pred = model.predict(X_test)

mae_heater = mean_absolute_error(y_test['Target_Heater_PWM'], y_pred[:, 0])
mae_fan = mean_absolute_error(y_test['Target_Fan_PWM'], y_pred[:, 1])

r2_heater = r2_score(y_test['Target_Heater_PWM'], y_pred[:, 0])
r2_fan = r2_score(y_test['Target_Fan_PWM'], y_pred[:, 1])

print("\n--- Model Evaluation Results ---")
print(
    f"Heater PWM Control - MAE: {mae_heater:.2f}% | R² Score: {r2_heater:.4f}"
)
print(f"Fan PWM Control    - MAE: {mae_fan:.2f}% | R² Score: {r2_fan:.4f}")

# 6. Save Model to Disk
model_filename = 'model1_controller.joblib'
joblib.dump(model, model_filename)
print(f"\nTrained model successfully saved to '{model_filename}'!")

# 7. Visualization: Predicted vs Actual Actuator Duty Cycles
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Heater PWM plot
ax1.scatter(
    y_test['Target_Heater_PWM'],
    y_pred[:, 0],
    color='tab:red',
    alpha=0.3,
    s=15,
)
ax1.plot([0, 100], [0, 100], 'k--', lw=2)
ax1.set_title('Heater PWM: Actual vs Predicted')
ax1.set_xlabel('Actual PWM (%)')
ax1.set_ylabel('Predicted PWM (%)')

# Fan PWM plot
ax2.scatter(
    y_test['Target_Fan_PWM'], y_pred[:, 1], color='tab:blue', alpha=0.3, s=15
)
ax2.plot([0, 100], [0, 100], 'k--', lw=2)
ax2.set_title('Fan PWM: Actual vs Predicted')
ax2.set_xlabel('Actual PWM (%)')
ax2.set_ylabel('Predicted PWM (%)')

plt.tight_layout()
plt.savefig('model1_prediction_accuracy.png')
print("Evaluation plot saved as 'model1_prediction_accuracy.png'.")