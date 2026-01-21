#include "alarm.h"

// Global instance
AlarmHandler nodeAlarm;

// ==================== ALARM HANDLER IMPLEMENTATION ====================

AlarmHandler::AlarmHandler() {
    alarmActive = false;
    coolerActive = false;
    lastAlarmBlink = 0;
    alarmLedState = false;
}

void AlarmHandler::init() {
    pinMode(LED_ALARM, OUTPUT);
    pinMode(LED_COOLER, OUTPUT);
    
    digitalWrite(LED_ALARM, LOW);
    digitalWrite(LED_COOLER, LOW);
    
    Serial.println("[ALARM] Initialized");
}

// ==================== ALARM CONTROL ====================

void AlarmHandler::activateAlarm() {
    if (!alarmActive) {
        alarmActive = true;
        digitalWrite(LED_ALARM, HIGH);
        Serial.println("⚠️ [ALARM] ACTIVATED - Overheat + No connection!");
    }
}

void AlarmHandler::deactivateAlarm() {
    alarmActive = false;
    alarmLedState = false;
    digitalWrite(LED_ALARM, LOW);
    Serial.println("[ALARM] Deactivated");
}

bool AlarmHandler::isAlarmActive() {
    return alarmActive;
}

void AlarmHandler::updateAlarmLed() {
    if (!alarmActive) return;
    
    // Blink fast when alarm is active
    if (millis() - lastAlarmBlink >= 100) {
        lastAlarmBlink = millis();
        alarmLedState = !alarmLedState;
        digitalWrite(LED_ALARM, alarmLedState ? HIGH : LOW);
    }
}

// ==================== COOLER CONTROL ====================

void AlarmHandler::activateCooler() {
    coolerActive = true;
    digitalWrite(LED_COOLER, HIGH);
    Serial.println("[COOLER] Activated - Backup cooler ON");
}

void AlarmHandler::deactivateCooler() {
    coolerActive = false;
    digitalWrite(LED_COOLER, LOW);
    Serial.println("[COOLER] Deactivated - Backup cooler OFF");
}

bool AlarmHandler::isCoolerActive() {
    return coolerActive;
}

// ==================== EDGE LOGIC ====================

void AlarmHandler::checkCondition(float temperature, bool gatewayConnected) {
    // EDGE LOGIC: Activate alarm when:
    // 1. Temperature > TEMP_MAX (8°C)
    // 2. AND gateway is disconnected
    
    if (temperature > TEMP_MAX && !gatewayConnected) {
        activateAlarm();
    }
    
    // Note: Alarm is NOT auto-deactivated
    // It requires RESET_ALARM command from server
}

bool AlarmHandler::getAlarmState() {
    return alarmActive;
}

bool AlarmHandler::getCoolerState() {
    return coolerActive;
}
