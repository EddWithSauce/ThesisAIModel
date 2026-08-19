import joblib
import m2cgen as m2c

# 1. Load trained Model 1
print("Loading trained Model 1...")
model = joblib.load('model1_controller.joblib')

# 2. Transpile the Scikit-Learn Random Forest model into native C++ code
print("Transpiling Model 1 into pure C++ code...")
code = m2c.export_to_c(model)

# 3. Save as a C++ header file for the ESP32 / Arduino IDE
header_filename = 'model1_controller.h'
with open(header_filename, 'w') as f:
  f.write('// Auto-generated C++ code for EAT Model 1 Controller\n\n')
  f.write(code)

print(
    f"Successfully exported C++ controller to '{header_filename}'! Ready for"
    ' ESP32 deployment.'
)