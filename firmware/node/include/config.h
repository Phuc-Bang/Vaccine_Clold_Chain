#ifndef CONFIG_H
#define CONFIG_H

// ==================== DEVICE INFO ====================
#define NODE_ID_STR         "NODE_01"
#define DEVICE_ID           1

// ==================== HARDWARE PINS ====================
#define DHT_PIN             4       // DHT11 data pin
#define DHT_TYPE            DHT11

#define LED_ALARM           25      // LED Đỏ - Còi hú quá nhiệt
#define LED_COOLER          26      // LED Xanh - Máy lạnh dự phòng
#define LED_STATUS          27      // LED Vàng - Trạng thái kết nối

// ==================== TEMPERATURE THRESHOLDS ====================
// Ngưỡng nhiệt độ phòng thực tế
#define TEMP_MIN            20.0    // Minimum comfortable (°C)
#define TEMP_MAX            30.0    // Maximum comfortable (°C)
#define TEMP_ALARM          35.0    // Alarm threshold (°C)

// ==================== ESP-NOW CONFIG ====================
// Gateway MAC: 30:ED:A0:BD:1D:2C
#define GATEWAY_MAC         {0x30, 0xED, 0xA0, 0xBD, 0x1D, 0x2C}

// ==================== TIMING CONFIG ====================
#define TEMP_READ_INTERVAL  5000    // Read temperature every 5 seconds
#define GATEWAY_TIMEOUT     15000   // 15 seconds timeout

// ==================== FILTER CONFIG ====================
#define MEDIAN_FILTER_SIZE  5

// ==================== DATA STRUCTURES ====================

// Sensor data sent from Node -> Gateway
typedef struct {
    char nodeId[16];
    int deviceId;
    float temperature;
    float humidity;
    bool alarmState;
    bool coolerState;
    unsigned long timestamp;
} SensorData_t;

// Command received from Gateway -> Node
typedef struct {
    char command[32];
    int targetDeviceId;
} CommandData_t;

#endif // CONFIG_H
