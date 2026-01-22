#include "wifi_handler.h"

// Global instance
WiFiHandler wifi;

// ==================== WIFI HANDLER IMPLEMENTATION ====================

WiFiHandler::WiFiHandler() {
    connected = false;
    strcpy(mqttBroker, "192.168.1.100");
}

bool WiFiHandler::setup() {
    // Load saved MQTT broker
    loadMQTTBroker();
    
    WiFiManager wm;
    
    // Custom parameter for MQTT server
    WiFiManagerParameter mqttParam("mqtt", "MQTT Server", mqttBroker, 64);
    wm.addParameter(&mqttParam);
    
    // Portal timeout
    wm.setConfigPortalTimeout(WIFI_PORTAL_TIMEOUT);
    
    Serial.println("[WiFi] Starting WiFiManager...");
    Serial.printf("[WiFi] Connect to AP: %s / %s\n", WIFI_AP_SSID, WIFI_AP_PASSWORD);
    
    bool result = wm.autoConnect(WIFI_AP_SSID, WIFI_AP_PASSWORD);
    
    if (result) {
        connected = true;
        Serial.println("[WiFi] Connected!");
        Serial.printf("[WiFi] IP: %s\n", WiFi.localIP().toString().c_str());
        
        // Save MQTT broker from portal
        strcpy(mqttBroker, mqttParam.getValue());
        saveMQTTBroker(mqttBroker);
        
    } else {
        connected = false;
        Serial.println("[WiFi] Failed to connect!");
    }
    
    return connected;
}

bool WiFiHandler::isConnected() {
    return WiFi.status() == WL_CONNECTED;
}

void WiFiHandler::checkConnection() {
    connected = (WiFi.status() == WL_CONNECTED);
}

const char* WiFiHandler::getMQTTBroker() {
    return mqttBroker;
}

void WiFiHandler::saveMQTTBroker(const char* broker) {
    strcpy(mqttBroker, broker);
    
    prefs.begin("vaccine", false);
    prefs.putString("mqtt_broker", broker);
    prefs.end();
    
    Serial.printf("[WiFi] MQTT broker saved: %s\n", broker);
}

void WiFiHandler::loadMQTTBroker() {
    prefs.begin("vaccine", true);
    String saved = prefs.getString("mqtt_broker", "192.168.1.100");
    saved.toCharArray(mqttBroker, sizeof(mqttBroker));
    prefs.end();
    
    Serial.printf("[WiFi] MQTT broker loaded: %s\n", mqttBroker);
}

String WiFiHandler::getLocalIP() {
    return WiFi.localIP().toString();
}

String WiFiHandler::getMacAddress() {
    return WiFi.macAddress();
}

void WiFiHandler::resetSettings() {
    Serial.println("[WiFi] Resetting all settings...");
    
    // Clear Preferences
    prefs.begin("vaccine", false);
    prefs.clear();
    prefs.end();
    
    // Clear WiFiManager saved credentials
    WiFiManager wm;
    wm.resetSettings();
    
    Serial.println("[WiFi] Settings cleared! Restarting...");
    delay(1000);
    ESP.restart();
}
