This file is for ESP32 Integration there is a function within model1_controller.h named score(double inpute[3])

Please call it directly with this:

#include "model1_controller.h"

void loop() {
    // 1. Read ESP32 Sensor Hardware
    double sensor_inputs[3] = { readChamberTemp(), readMoistureSensor(), readMotorCurrent() };
    double predicted_outputs[2];

    // 2. Run Embedded AI Inference (0ms latency, pure C++)
    score(sensor_inputs, predicted_outputs);

    // 3. Actuate Physical Pins via PWM
    ledcWrite(HEATER_PWM_CHANNEL, predicted_outputs[0]); // Heater PWM
    ledcWrite(FAN_PWM_CHANNEL, predicted_outputs[1]);    // Fan PWM
    
    delay(1000); // Poll loop every 1 second
}