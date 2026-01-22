#ifndef LED_STATUS_H
#define LED_STATUS_H

#include <Arduino.h>
#include "config.h"

// ==================== STATUS LED MODULE ====================

class StatusLed {
private:
    bool ledState;
    unsigned long lastBlink;
    
public:
    StatusLed();
    
    void init();
    void update(bool gatewayConnected);
    void on();
    void off();
    void toggle();
};

// Global instance
extern StatusLed statusLed;

#endif // LED_STATUS_H
