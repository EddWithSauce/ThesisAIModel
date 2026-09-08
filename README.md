# EAT System — Embedded Machine Learning Core

This repository contains the complete 3-tier machine learning pipeline for the **Embedded Automated Thermophilic (EAT)** Bio-Fertilizer System.

The system automates domestic food waste conversion into nutrient-rich organic bio-fertilizer by combining embedded closed-loop control on an ESP32 microcontroller with batch state estimation and contextual agricultural recommendation engines running on a local host (Mini-PC).

---

## 1. Philippine Household Waste Baseline Calibration

All synthetic datasets and model training pipelines in this repository are calibrated directly against empirical **DOST-FNRI National Nutrition Survey (ENNS)** mass-based plate waste data:

* **Rice & Cereals**: **74.1%** by mass (49.6g/day average per household)
* **Fish, Meat & Poultry**: **11.2%** by mass (7.5g/day)
* **Vegetables**: **10.0%** by mass (6.7g/day)
* **Others**: **4.7%** by mass (3.1g/day)

### Operating Constraints & Biological Framework
* **Thermophilic Temperature Target**: $50^\circ\text{C} - 70^\circ\text{C}$ active thermal regulation for pathogen destruction (*E. coli*, *Salmonella* compliance with PNS/BAFS 40:2013 organic fertilizer standards).
* **Final Moisture Target**: $\approx 30\%$ moisture floor.
* **Methane Prevention (Aerobic Integrity):** The system strictly enforces aerobic conditions. Model 1 utilizes active fan aeration to prevent anaerobic sludge formation, eliminating methane generation without the need for additional ML models. A hardware MQ-4 Methane sensor is integrated as a hardcoded C++ fallback interrupt.
* **Microbial Inoculation Strategy:** The system utilizes a continuous **10-15% back-mixing** protocol, retaining a portion of finished compost to inoculate subsequent batches. Initial Day-1 setups require a basic starter (vermicast/garden soil) paired with a structural bulking agent (*ipa*/cocopeat) for aeration.

---

## 2. Machine Learning Architecture Overview

**Algorithm Rationale:** The architecture strictly utilizes **Random Forest Regressors and Classifiers** (Decision Trees). Alternative models (CNNs, DNNs, or Multiple Linear Regression) were explicitly rejected to handle the non-linear physics of composting and to enforce strict, immediate safety guardrails (e.g., an instant 0% heater drop during thermal runaway).

| Model | Deployment Target | Inputs | Outputs | Performance Metrics |
| :--- | :--- | :--- | :--- | :--- |
| **Model 1**<br>*(Process Controller)* | **ESP32 Microcontroller**<br>(Pure C++ `model1_controller.h`) | - Chamber Temp (°C)<br>- Moisture (%)<br>- Motor Load Current (A) | - Target Heater PWM (%)<br>- Target Aeration Fan PWM (%) | - **Heater PWM**: MAE 0.47% \| $R^2 = 0.9132$<br>- **Fan PWM**: MAE 0.43% \| $R^2 = 0.9950$ |
| **Model 2**<br>*(Batch Estimator)* | **Mini-PC / Local Host**<br>(Python / `scikit-learn`) | - Feedstock Profile Category<br>- Initial Mass (kg)<br>- Cold-Start Moisture (%)<br>- Initial Motor Current (A) | - Total Processing Time (mins)<br>- Expected Final Yield Mass (kg)<br>- Projected NPK Category | - **Time**: MAE 0.67 mins \| $R^2 = 0.9995$<br>- **Yield Mass**: MAE 0.011 kg \| $R^2 = 0.9983$<br>- **NPK Class**: Accuracy 100.0% |
| **Model 3**<br>*(Ag Engine)* | **Mini-PC / Local Host**<br>(Python / `scikit-learn`) | - Target Crop (*Pechay, Kangkong, Talong, Kamatis, Sili*)<br>- Local Soil Type (*Clay Loam, Volcanic/Silt, Sandy*)<br>- Batch NPK Profile | - Recommended Dose (g/10kg pot)<br>- Application Interval (Days)<br>- Crop Compatibility Match Score (%) | - **Dosage**: MAE 0.66 g/pot \| $R^2 = 0.9927$<br>- **Interval**: MAE 0.00 days \| $R^2 = 1.0000$<br>- **Match Score**: MAE 3.54% \| $R^2 = 0.8424$ |

---

## 3. Hardware Architecture & Edge Topography

To ensure the embedded ML runs accurately on physical hardware, the prototype requires the following specific mechanical and electrical configurations:

* **Motor & Transmission:** Comminution is driven by a **NEMA 17 Stepper Motor**. Because direct-drive steppers lack the torque ($\approx 0.5$ Nm) to process dense sludge, the system requires a **Planetary Gearbox** (e.g., 5:1 ratio) to achieve the necessary mechanical advantage.
* **Motor Driver:** The NEMA 17 is controlled via a **TB6600 Stepper Motor Driver**.
* **Current Sensing Topology:** Because the TB6600 outputs a constant, flat current (e.g., 1.5A) regardless of physical load, the **ACS712 Current Sensor must be wired in series to the main DC power line** (pre-TB6600). This allows the sensor to detect wattage/back-EMF fluctuations, feeding accurate `initial_motor_load_a` data into the AI models.
* **ESP32 Pin Routing:** Critical analog sensors (Moisture, ACS712) must route to **ADC1 pins (GPIO 32, 33)** to preserve ADC2, ensuring the system can deploy Wi-Fi for the web dashboard in Phase 3 without disabling the analog telemetry.

---

## 4. Repository File Structure

```text
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
└── README.md                     # Repository documentation
