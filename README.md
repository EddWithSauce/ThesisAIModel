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

### Operating Constraints
* **Thermophilic Temperature Target**: $50^\circ\text{C} - 70^\circ\text{C}$ active thermal regulation for pathogen destruction (*E. coli*, *Salmonella* compliance with PNS/BAFS 40:2013 organic fertilizer standards).
* **Final Moisture Target**: $\approx 30\%$ moisture floor.

---

## 2. Machine Learning Architecture Overview

| Model | Deployment Target | Inputs | Outputs | Performance Metrics |
| :--- | :--- | :--- | :--- | :--- |
| **Model 1**<br>*(Process Controller)* | **ESP32 Microcontroller**<br>(Pure C++ `model1_controller.h`) | - Chamber Temp (°C)<br>- Moisture (%)<br>- Motor Load Current (A) | - Target Heater PWM (%)<br>- Target Aeration Fan PWM (%) | - **Heater PWM**: MAE 0.47% \| $R^2 = 0.9132$<br>- **Fan PWM**: MAE 0.43% \| $R^2 = 0.9950$ |
| **Model 2**<br>*(Batch Dynamics Estimator)* | **Mini-PC / Local Host**<br>(Python / `scikit-learn`) | - Feedstock Profile Category<br>- Initial Mass (kg)<br>- Cold-Start Moisture (%)<br>- Initial Motor Current (A) | - Total Processing Time (mins)<br>- Expected Final Yield Mass (kg)<br>- Projected NPK Category | - **Time**: MAE 0.67 mins \| $R^2 = 0.9995$<br>- **Yield Mass**: MAE 0.011 kg \| $R^2 = 0.9983$<br>- **NPK Class**: Accuracy 100.0% |
| **Model 3**<br>*(Contextual Ag Engine)* | **Mini-PC / Local Host**<br>(Python / `scikit-learn`) | - Target Crop (*Pechay, Kangkong, Talong, Kamatis, Sili*)<br>- Local Soil Type (*Clay Loam, Volcanic/Silt, Sandy*)<br>- Batch NPK Profile | - Recommended Dose (g/10kg pot)<br>- Application Interval (Days)<br>- Crop Compatibility Match Score (%) | - **Dosage**: MAE 0.66 g/pot \| $R^2 = 0.9927$<br>- **Interval**: MAE 0.00 days \| $R^2 = 1.0000$<br>- **Match Score**: MAE 3.54% \| $R^2 = 0.8424$ |

---

## 3. Repository File Structure

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
```

---

## 4. Quickstart Guide

### Step 1: Prerequisites & Environment Setup
Clone the repository and install required Python packages:

```bash
git clone https://github.com/your-username/eat-system-ml.git
cd eat-system-ml
pip install -r requirements.txt
```

*Required Dependencies*: `numpy`, `pandas`, `scikit-learn`, `joblib`, `m2cgen`, `matplotlib`, `seaborn`

### Step 2: Regenerate Datasets & Train Models Sequentially

**Model 1 (Embedded Controller):**
```bash
python generate_model1_data.py
python train_model1.py
python export_model1.py
```

**Model 2 (Batch Estimator):**
```bash
python generate_model2_data.py
python train_model2.py
```

**Model 3 (Contextual Ag Engine):**
```bash
python generate_model3_data.py
python train_model3.py
```

### Step 3: Run the End-to-End Master Pipeline
```bash
python eat_system_pipeline.py
```

---

## 5. Next Steps & Implementation Roadmap

* **Phase 1: ESP32 Firmware Integration (`.ino`)**
  * Include `model1_controller.h` in an Arduino sketch for the ESP32.
  * Wire physical hardware pins: DS18B20/Thermocouple (Chamber Temperature), Soil/Resistive Moisture Sensor, ACS712 Current Sensor (Motor Load), and SSR/MOSFET PWM outputs for the Heating Element and Aeration Fan.
  * Implement the 1-second execution loop calling `score(inputs, outputs)`.

* **Phase 2: Serial Communication Bridge**
  * Develop a Python `pyserial` daemon on the Mini-PC to communicate over USB Serial (UART) with the ESP32.
  * Transmit batch targets from Model 2 down to the ESP32 and continuously stream real-time hardware telemetry back to the Mini-PC.

* **Phase 3: Mini-PC Web Application (User Interface)**
  * Build a Streamlit or Flask web dashboard running on the Mini-PC.
  * Display real-time process monitoring graphs (temperature, moisture, PWM duty cycles).
  * Provide input forms for selecting target local crops (*Talong*, *Pechay*, *Kamatis*) and displaying the generated agronomic batch report.

* **Phase 4: Bench-Scale Physical Validation**
  * Execute physical test runs using real household food waste mixtures to log actual thermal curves and validate physical sensor inputs against synthetic model expectations.
