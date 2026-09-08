#include "model1_controller.h"

// --- Pin Definitions ---
const int MOISTURE_PIN = 32;
const int CURRENT_PIN = 33;
const int TEMP_PIN = 4;
const int HEATER_PIN = 18;
const int FAN_PIN = 19;

// Array to hold the 3 inputs for the AI (Temp, Moisture, Load)
double ai_inputs[3]; 

// Array to hold the 2 outputs from the AI (Heater PWM, Fan PWM)
double ai_outputs[2];

void setup() {
  Serial.begin(115200);
  
  // Configure Output Pins
  pinMode(HEATER_PIN, OUTPUT);
  pinMode(FAN_PIN, OUTPUT);
  
  // Note: We will add the actual sensor setup (like DS18B20 initialization) here later
  
  Serial.println("EAT System: ESP32 Edge Controller Booting...");
  Serial.println("AI Model Loaded.");
}

void loop() {
  // 1. Read Physical Sensors (Mock values for now until sensors are wired)
  double current_temp = read_temperature(); 
  double current_moisture = read_moisture();
  double current_load = read_motor_load();

  // 2. Package data for the Machine Learning Model
  ai_inputs[0] = current_temp;
  ai_inputs[1] = current_moisture;
  ai_inputs[2] = current_load;

  // 3. Run the Random Forest AI! (This calls the function from model1_controller.h)
  score(ai_inputs, ai_outputs); 
  
  double heater_pwm_pct = ai_outputs[0];
  double fan_pwm_pct = ai_outputs[1];

  // 4. Convert AI Percentage (0-100%) to ESP32 PWM (0-255)
  int esp_heater_pwm = map(heater_pwm_pct, 0, 100, 0, 255);
  int esp_fan_pwm = map(fan_pwm_pct, 0, 100, 0, 255);

  // 5. Execute Hardware Commands
  analogWrite(HEATER_PIN, esp_heater_pwm);
  analogWrite(FAN_PIN, esp_fan_pwm);

  // Print to Serial Monitor for debugging
  Serial.print("Temp: "); Serial.print(current_temp);
  Serial.print("C | Moist: "); Serial.print(current_moisture);
  Serial.print("% | Load: "); Serial.print(current_load);
  Serial.print("A || AI Heater: "); Serial.print(heater_pwm_pct);
  Serial.print("% | AI Fan: "); Serial.println(fan_pwm_pct);

  delay(2000); // Run inference every 2 seconds
}

// --- Dummy Sensor Functions (To be replaced with real libraries) ---
double read_temperature() { return 35.0; } 
double read_moisture() { return 78.0; }
double read_motor_load() { return 2.1; }