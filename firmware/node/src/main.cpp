/**
 * Vaccine Cold Chain Monitoring - ESP32 Node (Smart Sensor)
 * 
 * Main entry point - Integrates all modules
 * 
 * Project Structure:
 * ├── include/
 * │   ├── config.h          - Configuration & data structures
 * │   ├── sensor.h          - DHT11 sensor with Median Filter
 * │   ├── espnow_comm.h     - ESP-NOW communication
 * │   ├── alarm.h           - Alarm & Cooler control (Edge Logic)
 * │   └── led_status.h      - Status LED indicator
 * └── src/
 *     ├── main.cpp          - This file
 *     ├── sensor.cpp
 *     ├── espnow_comm.cpp
 *     ├── alarm.cpp
 *     └── led_status.cpp
 */

#include <Arduino.h>
#include "config.h"
#include "sensor.h"
#include "espnow_comm.h"
#include "alarm.h"
#include "led_status.h"

// ==================== TIMING VARIABLES ====================
unsigned long lastTempRead = 0;

// ==================== SENSOR DATA ====================
SensorData_t sensorData;

// ==================== COMMAND HANDLER ====================
void onCommandReceived(CommandData_t* cmd) {
    String command = String(cmd->command);
    command.trim();
    command.toUpperCase();
    
    Serial.printf("[CMD] Processing: %s\n", command.c_str());
    
    if (command == "TURN_ON_BACKUP_COOLER" || command == "CMD:TURN_ON_BACKUP_COOLER") {
        nodeAlarm.activateCooler();
        
        // Send status feedback
        sensorData.coolerState = nodeAlarm.getCoolerState();
        espNow.send(&sensorData);
        Serial.println("[CMD] Sent: STAT:COOLER_ON");
    }
    else if (command == "TURN_OFF_BACKUP_COOLER" || command == "CMD:TURN_OFF_BACKUP_COOLER") {
        nodeAlarm.deactivateCooler();
        
        sensorData.coolerState = nodeAlarm.getCoolerState();
        espNow.send(&sensorData);
        Serial.println("[CMD] Sent: STAT:COOLER_OFF");
    }
    else if (command == "RESET_ALARM" || command == "CMD:RESET_ALARM") {
        nodeAlarm.deactivateAlarm();
        
        sensorData.alarmState = nodeAlarm.getAlarmState();
        espNow.send(&sensorData);
        Serial.println("[CMD] Sent: STAT:ALARM_OFF");
    }
    else {
        Serial.printf("[CMD] Unknown: %s\n", command.c_str());
    }
}

// ==================== READ AND SEND TEMPERATURE ====================
void readAndSendTemperature() {
    float rawTemp, humidity;
    
    if (!sensor.read(&rawTemp, &humidity)) {
        return;
    }
    
    float filteredTemp = sensor.getFilteredTemperature();
    
    Serial.printf("[SENSOR] Raw: %.1f°C, Filtered: %.1f°C, Humidity: %.1f%%\n",
        rawTemp, filteredTemp, humidity);
    
    // Check timeout
    espNow.checkTimeout();
    
    // Edge Logic: Check alarm condition
    nodeAlarm.checkCondition(filteredTemp, espNow.isConnected());
    
    // Prepare sensor data
    strcpy(sensorData.nodeId, NODE_ID_STR);
    sensorData.deviceId = DEVICE_ID;
    sensorData.temperature = filteredTemp;
    sensorData.humidity = humidity;
    sensorData.alarmState = nodeAlarm.getAlarmState();
    sensorData.coolerState = nodeAlarm.getCoolerState();
    sensorData.timestamp = millis();
    
    // Send via ESP-NOW
    if (!espNow.send(&sensorData)) {
        Serial.println("[ESP-NOW] Send error!");
    }
}

// ==================== LED TEST ====================
void testLeds() {
    Serial.println("[SETUP] Testing LEDs...");
    
    digitalWrite(LED_ALARM, HIGH);
    delay(200);
    digitalWrite(LED_ALARM, LOW);
    
    digitalWrite(LED_COOLER, HIGH);
    delay(200);
    digitalWrite(LED_COOLER, LOW);
    
    digitalWrite(LED_STATUS, HIGH);
    delay(200);
    digitalWrite(LED_STATUS, LOW);
    
    Serial.println("[SETUP] LED test complete");
}

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println();
    Serial.println("╔════════════════════════════════════════════════╗");
    Serial.println("║  VACCINE COLD CHAIN - NODE (Smart Sensor)      ║");
    Serial.println("║  Modular Structure v2.0                        ║");
    Serial.println("╚════════════════════════════════════════════════╝");
    
    // Initialize modules
    nodeAlarm.init();
    statusLed.init();
    sensor.init();
    
    // Test LEDs
    testLeds();
    
    // Initialize ESP-NOW with command callback
    espNow.init();
    setCommandCallback(onCommandReceived);
    
    Serial.println();
    Serial.println("[SETUP] Complete! Starting monitoring...");
    Serial.println("════════════════════════════════════════════════");
}

// ==================== LOOP ====================
void loop() {
    unsigned long now = millis();
    
    // Read and send temperature periodically
    if (now - lastTempRead >= TEMP_READ_INTERVAL) {
        lastTempRead = now;
        readAndSendTemperature();
    }
    
    // Update status LED
    statusLed.update(espNow.isConnected());
    
    // Update alarm LED (blink if active)
    nodeAlarm.updateAlarmLed();
    
    delay(10);
}
