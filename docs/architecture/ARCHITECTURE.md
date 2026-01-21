# 🏗️ Kiến Trúc Hệ Thống

> Vaccine Cold Chain Monitor - Kiến trúc IoT 4 tầng

---

## Tổng Quan

```mermaid
graph TB
    subgraph "Tầng 1: Cảm Biến"
        N1[ESP32 Node 1]
        N2[ESP32 Node 2]
        N3[ESP32 Node N]
    end
    
    subgraph "Tầng 2: Biên"
        GW[ESP32 Gateway]
        BUF[(Bộ Đệm Local)]
    end
    
    subgraph "Tầng 3: Server"
        MQTT[MQTT Broker]
        API[FastAPI Server]
        DB[(SQLite)]
    end
    
    subgraph "Tầng 4: Người Dùng"
        DASH[Dashboard Web]
        ALERT[Hệ Thống Cảnh Báo]
    end
    
    N1 -->|ESP-NOW| GW
    N2 -->|ESP-NOW| GW
    N3 -->|ESP-NOW| GW
    GW -->|WiFi/MQTT| MQTT
    GW -.->|Offline| BUF
    MQTT <--> API
    API <--> DB
    API -->|WebSocket| DASH
    API --> ALERT
```

---

## Chi Tiết Từng Tầng

### Tầng 1: Node Cảm Biến
| Thành Phần | Mô Tả |
|------------|-------|
| **Vi xử lý** | ESP32 DevKit V1 |
| **Cảm biến** | DHT11/DHT22 |
| **Giao thức** | ESP-NOW (tầm xa 250m) |
| **Nguồn** | Pin/USB |

### Tầng 2: Gateway Biên
| Tính Năng | Cách Thực Hiện |
|-----------|----------------|
| **Tổng hợp dữ liệu** | Thu thập từ nhiều node |
| **Store & Forward** | Lưu đệm khi mất kết nối |
| **Edge Logic** | Cảnh báo cục bộ |

### Tầng 3: Server
| Dịch Vụ | Công Nghệ |
|---------|-----------|
| **API** | FastAPI (Python) |
| **Message Broker** | Mosquitto MQTT |
| **CSDL** | SQLite |

### Tầng 4: Giao Diện Người Dùng
| Tính Năng | Mô Tả |
|-----------|-------|
| **Dashboard** | Biểu đồ thời gian thực |
| **Cảnh báo** | Thông báo vi phạm nhiệt độ |
| **Điều khiển** | Gửi lệnh từ xa |

---

## Luồng Dữ Liệu

```
Cảm biến → [ESP-NOW] → Gateway → [MQTT] → Server → [WebSocket] → Dashboard
                          ↓
                    [Chế độ Buffer]
                    (khi mất mạng)
```

---

## Mô Hình Bảo Mật

- 🔐 ESP-NOW: Ghép cặp theo địa chỉ MAC
- 🔐 MQTT: Mã hóa TLS (production)
- 🔐 API: Xác thực token (dự kiến)
