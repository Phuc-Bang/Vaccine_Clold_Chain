/**
 * Vaccine Cold Chain Monitoring - ESP32 Gateway
 * 
 * Main entry point - Integrates all modules
 * 
 * Project Structure:
 * ├── include/
 * │   ├── config.h          - Configuration & data structures
 * │   ├── buffer.h          - Circular buffer (Store & Forward)
 * │   ├── espnow_handler.h  - ESP-NOW communication
 * │   ├── mqtt_handler.h    - MQTT client
 * │   └── wifi_handler.h    - WiFi Manager
 * └── src/
 *     ├── main.cpp          - This file
 *     ├── buffer.cpp
 *     ├── espnow_handler.cpp
 *     ├── mqtt_handler.cpp
 *     └── wifi_handler.cpp
 */

#include <Arduino.h>
#include "config.h"
#include "buffer.h"
#include "wifi_handler.h"
#include "espnow_handler.h"
#include "mqtt_handler.h"

// ==================== TIMING VARIABLES ====================
unsigned long lastBatchSend = 0;
unsigned long lastStatusPrint = 0;
bool ledState = false;
unsigned long lastLedBlink = 0;

// Reset button
unsigned long buttonPressStart = 0;
bool buttonPressed = false;
const unsigned long RESET_HOLD_TIME = 3000;  // 3 seconds to reset

// Forward declaration
void checkResetButton();

// ==================== CALLBACKS ====================

// Called when sensor data received from Node via ESP-NOW
void onSensorDataReceived(SensorData_t* data, const uint8_t* mac) {
    Serial.println();
    Serial.println("╔═══════════════════════════════════════╗");
    Serial.println("║    DATA FROM NODE                     ║");
    Serial.println("╠═══════════════════════════════════════╣");
    Serial.printf("║ Node ID: %s\n", data->nodeId);
    Serial.printf("║ Device ID: %d\n", data->deviceId);
    Serial.printf("║ Temperature: %.1f°C\n", data->temperature);
    Serial.printf("║ Humidity: %.1f%%\n", data->humidity);
    Serial.printf("║ Alarm: %s\n", data->alarmState ? "ON" : "OFF");
    Serial.printf("║ Cooler: %s\n", data->coolerState ? "ON" : "OFF");
    Serial.println("╚═══════════════════════════════════════╝");
    
    // Store in buffer
    dataBuffer.push(data);
    
    // If MQTT connected, send immediately
    if (mqtt.isConnected()) {
        mqtt.publishTelemetry(data);
    }
}

// Called when command received from Server via MQTT
void onCommandReceived(CommandData_t* cmd) {
    Serial.printf("[CMD] Forwarding: %s\n", cmd->command);
    
    // Send to all registered nodes
    espNow.sendToAllNodes(cmd);
    
    // Also broadcast
    espNow.broadcast(cmd);
}

// ==================== STATUS LED ====================
void updateStatusLed() {
    int interval;
    
    if (wifi.isConnected() && mqtt.isConnected()) {
        interval = 1000;  // Slow - All OK
    } else if (wifi.isConnected()) {
        interval = 500;   // Medium - WiFi only
    } else {
        interval = 100;   // Fast - No connection
    }
    
    if (millis() - lastLedBlink >= interval) {
        lastLedBlink = millis();
        ledState = !ledState;
        digitalWrite(LED_STATUS, ledState);
    }
}

// ==================== PRINT STATUS ====================
void printStatus() {
    Serial.println();
    Serial.println("╔═══════════════════════════════════════╗");
    Serial.println("║         GATEWAY STATUS                ║");
    Serial.println("╠═══════════════════════════════════════╣");
    Serial.printf("║ WiFi:   %s\n", wifi.isConnected() ? "✓ Connected" : "✗ Disconnected");
    Serial.printf("║ MQTT:   %s\n", mqtt.isConnected() ? "✓ Connected" : "✗ Disconnected");
    Serial.printf("║ Buffer: %d / %d records\n", dataBuffer.getCount(), BUFFER_SIZE);
    Serial.printf("║ Nodes:  %d registered\n", espNow.getNodeCount());
    Serial.printf("║ Broker: %s\n", mqtt.getBroker());
    Serial.println("╚═══════════════════════════════════════╝");
}

// ==================== SETUP ====================
void setup() {
    Serial.begin(115200);
    delay(1000);
    
    Serial.println();
    Serial.println("╔════════════════════════════════════════════════╗");
    Serial.println("║  VACCINE COLD CHAIN - GATEWAY                  ║");
    Serial.println("║  Modular Structure v2.0                        ║");
    Serial.println("╚════════════════════════════════════════════════╝");
    
    // Initialize LED and Button
    pinMode(LED_STATUS, OUTPUT);
    digitalWrite(LED_STATUS, LOW);
    
    pinMode(RESET_BUTTON, INPUT_PULLUP);
    Serial.println("[INFO] Hold BOOT button 3s to reset WiFi");
    
    // Setup WiFi (with WiFiManager portal)
    wifi.setup();
    
    // Setup ESP-NOW
    espNow.init();
    setDataReceivedCallback(onSensorDataReceived);
    
    // Setup MQTT
    mqtt.setBroker(wifi.getMQTTBroker());
    setCommandReceivedCallback(onCommandReceived);
    
    if (wifi.isConnected()) {
        mqtt.connect();
    }
    
    Serial.println();
    Serial.println("[SETUP] Complete! Waiting for data...");
    Serial.println("════════════════════════════════════════════════");
    
    printStatus();
}

// ==================== LOOP ====================
void loop() {
    // Check reset button (hold 3s to reset WiFi)
    checkResetButton();
    
    // Check WiFi status
    wifi.checkConnection();
    
    // Handle MQTT
    if (wifi.isConnected()) {
        if (!mqtt.isConnected()) {
            mqtt.connect();
        }
        mqtt.loop();
    }
    
    // Check if need to send batch
    if (mqtt.isConnected() && dataBuffer.getCount() >= BATCH_SIZE) {
        if (millis() - lastBatchSend >= BATCH_SEND_INTERVAL) {
            lastBatchSend = millis();
            
            BufferedData_t batch[BATCH_SIZE];
            int count = dataBuffer.popBatch(batch, BATCH_SIZE);
            mqtt.publishBatch(batch, count);
        }
    }
    
    // Update LED
    updateStatusLed();
    
    // Print status periodically
    if (millis() - lastStatusPrint >= STATUS_PRINT_INTERVAL) {
        lastStatusPrint = millis();
        printStatus();
    }
    
    delay(10);
}

// ==================== CHECK RESET BUTTON ====================
void checkResetButton() {
    if (digitalRead(RESET_BUTTON) == LOW) {  // Button pressed (active low)
        if (!buttonPressed) {
            buttonPressed = true;
            buttonPressStart = millis();
            Serial.println("[BUTTON] Pressed - Hold 3s to reset");
        } else {
            // Check if held long enough
            if (millis() - buttonPressStart >= RESET_HOLD_TIME) {
                Serial.println("[BUTTON] Resetting WiFi...");
                wifi.resetSettings();
            }
        }
    } else {
        buttonPressed = false;
    }
}
