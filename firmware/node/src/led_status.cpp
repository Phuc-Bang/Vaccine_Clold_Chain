#include "led_status.h"

// Global instance
StatusLed statusLed;

// ==================== STATUS LED IMPLEMENTATION ====================

StatusLed::StatusLed() {
    ledState = false;
    lastBlink = 0;
}

void StatusLed::init() {
    pinMode(LED_STATUS, OUTPUT);
    digitalWrite(LED_STATUS, LOW);
    Serial.println("[LED] Status LED initialized");
}

void StatusLed::update(bool gatewayConnected) {
    int blinkInterval;
    
    if (gatewayConnected) {
        blinkInterval = 1000;  // Slow blink when connected
    } else {
        blinkInterval = 200;   // Fast blink when disconnected
    }
    
    if (millis() - lastBlink >= blinkInterval) {
        lastBlink = millis();
        toggle();
    }
}

void StatusLed::on() {
    ledState = true;
    digitalWrite(LED_STATUS, HIGH);
}

void StatusLed::off() {
    ledState = false;
    digitalWrite(LED_STATUS, LOW);
}

void StatusLed::toggle() {
    ledState = !ledState;
    digitalWrite(LED_STATUS, ledState ? HIGH : LOW);
}
