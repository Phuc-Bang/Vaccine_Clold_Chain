# 🔌 Sơ Đồ Đấu Nối Phần Cứng

> Hướng dẫn kết nối chân cho ESP32 Sensor Node và Gateway

---

## 📍 Node Cảm Biến (ESP32 DevKit V1)

### Danh Sách Linh Kiện
| Linh Kiện | Model | Số Lượng |
|-----------|-------|----------|
| ESP32 | DevKit V1 | 1 |
| Cảm biến nhiệt độ | DHT11 hoặc DHT22 | 1 |
| LED Đỏ | 5mm | 1 |
| LED Xanh lá | 5mm | 1 |
| LED Vàng | 5mm | 1 |
| Điện trở | 220Ω | 3 |

### Sơ Đồ Kết Nối

```
┌─────────────────────────────────────────────┐
│                 ESP32 Node                   │
├─────────────────────────────────────────────┤
│                                             │
│   DHT11/22                                  │
│   ┌─────┐                                   │
│   │ VCC ├────────────── 3.3V                │
│   │ DATA├────────────── GPIO4               │
│   │ GND ├────────────── GND                 │
│   └─────┘                                   │
│                                             │
│   LED (với điện trở 220Ω)                   │
│   ┌─────┐                                   │
│   │ ĐỎ  ├────────────── GPIO25 (Báo động)   │
│   │XANH ├────────────── GPIO26 (Làm lạnh)   │
│   │VÀNG ├────────────── GPIO27 (Trạng thái) │
│   └─────┘                                   │
│                                             │
└─────────────────────────────────────────────┘
```

### Bảng Tổng Hợp Chân

| Chân | GPIO | Chức Năng | Mô Tả |
|------|------|-----------|-------|
| VCC | 3.3V | Nguồn | Cấp nguồn cảm biến |
| GND | GND | Mass | Mass chung |
| DATA | GPIO4 | Dữ liệu DHT | Nhiệt độ/Độ ẩm |
| LED_ALARM | GPIO25 | Đầu ra | Đỏ - Cảnh báo nhiệt độ |
| LED_COOLING | GPIO26 | Đầu ra | Xanh - Đang làm lạnh |
| LED_STATUS | GPIO27 | Đầu ra | Vàng - Trạng thái hệ thống |

---

## 📍 Gateway (ESP32 DevKit V1)

### Danh Sách Linh Kiện
| Linh Kiện | Model | Số Lượng |
|-----------|-------|----------|
| ESP32 | DevKit V1 | 1 |
| LED Xanh dương | 5mm | 1 |
| LED Vàng | 5mm | 1 |
| Điện trở | 220Ω | 2 |

### Sơ Đồ Kết Nối

```
┌─────────────────────────────────────────────┐
│                ESP32 Gateway                 │
├─────────────────────────────────────────────┤
│                                             │
│   LED (với điện trở 220Ω)                   │
│   ┌─────┐                                   │
│   │XANH ├────────────── GPIO2 (WiFi)        │
│   │VÀNG ├────────────── GPIO4 (Buffer Mode) │
│   └─────┘                                   │
│                                             │
│   Tích hợp: ESP-NOW radio cho mạng mesh    │
│   Tích hợp: WiFi cho kết nối MQTT          │
│                                             │
└─────────────────────────────────────────────┘
```

---

## ⚡ Yêu Cầu Nguồn Điện

| Thiết Bị | Điện Áp | Dòng TB | Dòng Đỉnh |
|----------|---------|---------|-----------|
| ESP32 Node | 5V USB | 80mA | 500mA |
| ESP32 Gateway | 5V USB | 100mA | 500mA |
| DHT11 | 3.3V | 0.5mA | 2.5mA |

---

## 🔧 Lưu Ý Lắp Ráp

1. **Điện trở kéo lên**: Cảm biến DHT có thể cần điện trở 10kΩ kéo lên trên đường DATA
2. **Hướng LED**: Chân dài = Anode (+), nối vào GPIO
3. **Mass chung**: Tất cả chân GND phải nối chung
4. **Cáp nguồn**: Dùng cáp USB chất lượng để hoạt động ổn định
