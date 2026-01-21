#ifndef ALARM_H
#define ALARM_H

#include <Arduino.h>
#include "config.h"

// ==================== ALARM MODULE (Edge Logic) ====================

class AlarmHandler {
private:
    bool alarmActive;
    bool coolerActive;
    unsigned long lastAlarmBlink;
    bool alarmLedState;
    
public:
    AlarmHandler();
    
    void init();
    
    // Alarm control
    void activateAlarm();
    void deactivateAlarm();
    bool isAlarmActive();
    void updateAlarmLed();
    
    // Cooler control
    void activateCooler();
    void deactivateCooler();
    bool isCoolerActive();
    
    // Edge Logic: Check if alarm should trigger
    void checkCondition(float temperature, bool gatewayConnected);
    
    // Get states
    bool getAlarmState();
    bool getCoolerState();
};

// Global instance
extern AlarmHandler nodeAlarm;

#endif // ALARM_H
