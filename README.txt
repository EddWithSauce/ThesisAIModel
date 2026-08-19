# EAT System — Embedded Machine Learning Core

This repository contains the complete 3-tier machine learning pipeline for the Embedded Automated Thermophilic (EAT) Bio-Fertilizer System.

The system automates domestic food waste conversion into nutrient-rich organic bio-fertilizer by combining embedded closed-loop control on an ESP32 microcontroller with batch state estimation and contextual agricultural recommendation engines running on a local host (Mini-PC).

================================================================================
1. PHILIPPINE HOUSEHOLD WASTE BASELINE CALIBRATION
================================================================================

All synthetic datasets and model training pipelines in this repository are calibrated directly against empirical DOST-FNRI National Nutrition Survey (ENNS) mass-based plate waste data:

- Rice & Cereals: 74.1% by mass (49.6g/day average per household)
- Fish, Meat & Poultry: 11.2% by mass (7.5g/day)
- Vegetables: 10.0% by mass (6.7g/day)
- Others: 4.7% by mass (3.1g/day)

Operating Constraints:
- Thermophilic Temperature Target: 50°C - 70°C active thermal regulation for pathogen destruction (E. coli, Salmonella compliance with PNS/BAFS 40:2013 organic fertilizer standards).
- Final Moisture Target: ~30% moisture floor.

================================================================================
2. MACHINE LEARNING ARCHITECTURE OVERVIEW
================================================================================

MODEL 1: Process Controller
- Deployment Target: ESP32 Microcontroller (Pure C++ `model1_controller.h`)
- Inputs: Chamber Temp (°C), Moisture (%), Motor Load Current (A)
- Outputs: Target Heater PWM (%), Target Aeration Fan PWM (%)
- Metrics: 
  * Heater PWM: MAE 0.47% | R² = 0.9132
  * Fan PWM: MAE 0.43% | R² = 0.9950

MODEL 2: Batch Dynamics Estimator
- Deployment Target: Mini-PC / Local Host (Python / scikit-learn)
- Inputs: Feedstock Profile Category, Initial Mass (kg), Cold-Start Moisture (%), Initial Motor Current (A)
- Outputs: Total Processing Time (mins), Expected Final Yield Mass (kg), Projected NPK Category
- Metrics:
  * Processing Time: MAE 0.67 mins | R² = 0.9995
  * Yield Mass: MAE 0.011 kg | R² = 0.9983
  * NPK Profile Class: Accuracy 100.0%

MODEL 3: Contextual Ag Engine
- Deployment Target: Mini-PC / Local Host (Python / scikit-learn)
- Inputs: Target Crop (Pechay, Kangkong, Talong, Kamatis, Sili), Local Soil Type (Clay Loam, Volcanic/Silt, Sandy), Batch NPK Profile
- Outputs: Recommended Dose (g/10kg pot), Application Interval (Days), Crop Compatibility Match Score (%)
- Metrics:
  * Recommended Dosage: MAE 0.66 g/pot | R² = 0.9927
  * Application Interval: MAE 0.00 days | R² = 1.0000
  * Compatibility Match Score: MAE 3.54% | R² = 0.8424

================================================================================
3. REPOSITORY FILE STRUCTURE
================================================================================

.
├── generate_model1_data.py       # Simulates closed-loop thermal & moisture control telemetry
├── train_model1.py               # Trains Model 1 Random Forest Regressor
├── export_model1.py              # Transpiles Model 1 into pure C++ code via m2cgen
├── model1_controller.h           # Auto-generated C++ header file for ESP32 deployment
│
├── generate_model2_data.py       # Simulates batch runs calibrated to PH FNRI waste profiles
├── train_model2.py               # Trains Model 2 Regressor & NPK Classifier
├── model2_preprocessor.joblib    # Feature transformer for Model 2
├── model2_regressor.joblib       # Model 2 Batch Time & Mass Regressor
├── model2_classifier.joblib      # Model 2 NPK Profile Classifier
│
├── generate_model3_data.py       # Simulates agronomic datasets for PH crops & soils
├── train_model3.py               # Trains Model 3 Contextual Ag Engine Regressor
├── model3_preprocessor.joblib    # Feature transformer for Model 3
├── model3_ag_engine.joblib       # Model 3 Ag Engine artifact
│
├── eat_system_pipeline.py        # Master pipeline orchestrator script
├── requirements.txt              # Project Python dependencies
└── README.txt                    # Repository documentation

================================================================================
4. QUICKSTART GUIDE
================================================================================

Step 1: Prerequisites & Environment Setup
Clone the repository and install required Python packages:
  git clone https://github.com/your-username/eat-system-ml.git
  cd eat-system-ml
  pip install -r requirements.txt

Required Dependencies: numpy, pandas, scikit-learn, joblib, m2cgen, matplotlib, seaborn

Step 2: Regenerate Datasets & Train Models Sequentially
Model 1 (Embedded Controller):
  python generate_model1_data.py
  python train_model1.py
  python export_model1.py

Model 2 (Batch Estimator):
  python generate_model2_data.py
  python train_model2.py

Model 3 (Contextual Ag Engine):
  python generate_model3_data.py
  python train_model3.py

Step 3: Run the End-to-End Master Pipeline
  python eat_system_pipeline.py

================================================================================
5. NEXT STEPS & IMPLEMENTATION ROADMAP
================================================================================

Phase 1: ESP32 Firmware Integration (.ino)
- Include model1_controller.h in an Arduino sketch for the ESP32.
- Wire physical hardware pins: DS18B20/Thermocouple (Chamber Temperature), Soil/Resistive Moisture Sensor, ACS712 Current Sensor (Motor Load), and SSR/MOSFET PWM outputs for the Heating Element and Aeration Fan.
- Implement the 1-second execution loop calling score(inputs, outputs).

Phase 2: Serial Communication Bridge
- Develop a Python pyserial daemon on the Mini-PC to communicate over USB Serial (UART) with the ESP32.
- Transmit batch targets from Model 2 down to the ESP32 and continuously stream real-time hardware telemetry back to the Mini-PC.

Phase 3: Mini-PC Web Application (User Interface)
- Build a Streamlit or Flask web dashboard running on the Mini-PC.
- Display real-time process monitoring graphs (temperature, moisture, PWM duty cycles).
- Provide input forms for selecting target local crops (Talong, Pechay, Kamatis) and displaying the generated agronomic batch report.

Phase 4: Bench-Scale Physical Validation
- Execute physical test runs using real household food waste mixtures to log actual thermal curves and validate physical sensor inputs against synthetic model expectations.
