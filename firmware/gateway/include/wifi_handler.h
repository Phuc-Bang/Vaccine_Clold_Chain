#ifndef WIFI_HANDLER_H
#define WIFI_HANDLER_H

#include <Arduino.h>
#include <WiFiManager.h>
#include <Preferences.h>
#include "config.h"

// ==================== WIFI MODULE ====================

class WiFiHandler {
private:
    Preferences prefs;
    bool connected;
    char mqttBroker[64];
    
public:
    WiFiHandler();
    
    bool setup();
    bool isConnected();
    void checkConnection();
    
    const char* getMQTTBroker();
    void saveMQTTBroker(const char* broker);
    void loadMQTTBroker();
    
    String getLocalIP();
    String getMacAddress();
    void resetSettings();
};

// Global instance
extern WiFiHandler wifi;

#endif // WIFI_HANDLER_H
