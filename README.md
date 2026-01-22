# ColdChain Dashboard – Vaccine Cold Room SCADA

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)

**Web dashboard giám sát & điều khiển kho lạnh vắc-xin** dựa trên FastAPI, MQTT, Chart.js với khả năng:

- ✅ Giám sát nhiệt độ realtime với biểu đồ
- ✅ Điều khiển thiết bị từ xa (ON/OFF máy lạnh)
- ✅ Cảnh báo ngưỡng nhiệt độ tự động
- ✅ Phát hiện mất tín hiệu (dead link detection)
- ✅ Lọc nhiễu dữ liệu (median filter)
- ✅ Đồng bộ trạng thái giữa nhiều tab

---

## 🏗️ Kiến trúc hệ thống (Architecture)

```
┌─────────────┐      MQTT      ┌──────────────┐      HTTP      ┌──────────────┐
│  Simulator  │ ─────────────> │ MQTT Worker  │ ─────────────> │   Backend    │
│  (ESP32)    │                │              │                │   FastAPI    │
└─────────────┘                └──────────────┘                └──────────────┘
                                       │                               │
                                       │                               │
                                       ▼                               ▼
                                ┌──────────────┐                ┌──────────────┐
                                │   Database   │ <───────────── │   Frontend   │
                                │   SQLite     │      HTTP      │   HTML/JS    │
                                └──────────────┘                └──────────────┘
```

### Luồng dữ liệu:

1. **Simulator/ESP32** → Gửi dữ liệu nhiệt độ qua MQTT topic `coldchain/sensor/NODE_01/data`
2. **MQTT Worker** → Subscribe MQTT, lưu vào SQLite, cập nhật status qua Backend API
3. **Frontend** → Polling Backend API mỗi 3 giây để lấy dữ liệu mới và vẽ chart
4. **Điều khiển**: Frontend → Backend → MQTT → Simulator → Phản hồi status → Worker → Backend → Frontend

---

## 📁 Cấu trúc thư mục

```
coldchain-dashboard/
├── backend/               # FastAPI backend
│   └── main.py           # API endpoints
├── worker/               # MQTT worker
│   └── mqtt_worker.py    # Subscribe MQTT, ghi DB
├── frontend/             # Web dashboard
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── simulator/            # Giả lập thiết bị IoT
│   └── vaccine_sim.py
├── database/             # SQLite database
│   ├── schema.sql
│   └── iot_industrial.db
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
└── README.md
```

---

## 🚀 Cài đặt & Chạy

### Bước 1: Cài đặt dependencies

```bash
# Clone repo
git clone <your-repo-url>
cd coldchain-dashboard

# Tạo virtual environment (khuyến nghị)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt packages
pip install -r requirements.txt
```

### Bước 2: Khởi tạo database

```bash
cd database
sqlite3 iot_industrial.db < schema.sql
cd ..
```

### Bước 3: Chạy MQTT Broker

**Option A: Sử dụng Mosquitto (local)**

```bash
# Cài đặt Mosquitto
sudo apt-get install mosquitto mosquitto-clients  # Ubuntu/Debian
brew install mosquitto                            # macOS

# Chạy broker
mosquitto -v
```

**Option B: Sử dụng public broker**

Thay đổi `MQTT_BROKER` trong code thành `broker.hivemq.com` hoặc `test.mosquitto.org`

### Bước 4: Chạy các service

**Terminal 1: Backend**

```bash
cd backend
python main.py

# Hoặc dùng uvicorn trực tiếp
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2: MQTT Worker**

```bash
cd worker
python mqtt_worker.py
```

**Terminal 3: Simulator (giả lập thiết bị)**

```bash
cd simulator
python vaccine_sim.py
```

**Terminal 4: Frontend**

```bash
cd frontend

# Cách 1: Dùng Live Server (VS Code extension)
# Click chuột phải vào index.html > Open with Live Server

# Cách 2: Dùng Python HTTP server
python -m http.server 8080
# Truy cập: http://localhost:8080
```

---

## 🎯 Sử dụng

### Dashboard Features:

1. **KPI Cards**: Hiển thị nhiệt độ hiện tại, trạng thái máy lạnh, thời gian cập nhật
2. **Biểu đồ lịch sử**: 20 mẫu gần nhất với các đường ngưỡng
3. **Điều khiển**: Bật/tắt máy lạnh bằng nút ON/OFF
4. **Cảnh báo thông minh**:
   - 🟢 Xanh (2-8°C): An toàn
   - 🟡 Vàng (8-10°C): Cảnh báo
   - 🔴 Đỏ + nhấp nháy (>10°C): Nguy hiểm
5. **Dead Link Detection**: Cảnh báo khi mất tín hiệu >10 giây

### MQTT Topics:

- `coldchain/sensor/NODE_01/data` - Dữ liệu nhiệt độ
- `coldchain/device/NODE_01/cmd` - Lệnh điều khiển
- `coldchain/device/NODE_01/stat` - Trạng thái thiết bị

---

## 🔧 Tùy chỉnh

### Thay đổi Device ID:

File cần sửa:

- `backend/main.py` → `device_states`
- `worker/mqtt_worker.py` → `TOPIC_DATA`, `TOPIC_STATUS`
- `simulator/vaccine_sim.py` → `DEVICE_ID`
- `frontend/js/main.js` → `NODE_ID`

### Thay đổi ngưỡng nhiệt độ:

File `frontend/js/main.js`:

```javascript
const TEMP_THRESHOLDS = {
  NORMAL_MIN: 2, // Sửa ở đây
  NORMAL_MAX: 8, // Sửa ở đây
  WARN_MAX: 10, // Sửa ở đây
};
```

### Kết nối ESP32 thật:

Thay simulator bằng code Arduino/ESP32:

```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

// Config
#define MQTT_BROKER "your-broker-ip"
#define TOPIC_DATA "coldchain/sensor/NODE_01/data"

// Gửi dữ liệu
String payload = "{\"temperature\":" + String(temp) + "}";
client.publish(TOPIC_DATA, payload.c_str());
```

---

## 📸 Screenshot

![Dashboard Screenshot](docs/dashboard-screenshot.png)

_(Thêm screenshot thật của bạn vào thư mục `docs/`)_

---

## 🛠️ Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Database**: SQLite
- **MQTT**: Paho MQTT
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Chart**: Chart.js 4.4
- **UI**: Bootstrap 5, Font Awesome
- **Notifications**: Toastify

---

## 📊 API Endpoints

| Method | Endpoint                     | Mô tả                    |
| ------ | ---------------------------- | ------------------------ |
| GET    | `/api/v1/history/{node_id}`  | Lấy lịch sử nhiệt độ     |
| POST   | `/api/v1/ingest`             | Nhận dữ liệu từ thiết bị |
| POST   | `/api/v1/control/device`     | Gửi lệnh điều khiển      |
| GET    | `/api/v1/device/{id}/status` | Lấy trạng thái thiết bị  |
| POST   | `/api/v1/device/{id}/status` | Cập nhật trạng thái      |

---

## 🐛 Troubleshooting

**Lỗi: "Connection refused" khi chạy worker**

- Kiểm tra MQTT broker đã chạy chưa
- Kiểm tra địa chỉ IP/port trong config

**Frontend không hiển thị dữ liệu**

- Kiểm tra CORS trong backend
- Kiểm tra backend đã chạy và truy cập được qua `http://localhost:8000`
- Mở Developer Console (F12) để xem lỗi

**Chart không cập nhật**

- Kiểm tra simulator đang gửi dữ liệu
- Kiểm tra worker đang ghi vào database
- Kiểm tra đường dẫn database trong backend

---

## 📝 TODO / Future Improvements

- [ ] Thêm authentication (JWT)
- [ ] Chuyển sang PostgreSQL/TimescaleDB cho production
- [ ] Thêm push notification (Email/Telegram) khi nhiệt độ vượt ngưỡng
- [ ] Hỗ trợ nhiều kho lạnh (multi-node)
- [ ] Export báo cáo PDF
- [ ] Mobile responsive cải thiện
- [ ] WebSocket thay vì polling
- [ ] Docker containerization

---

## 📄 License

MIT License - Sử dụng tự do cho mục đích học tập và thương mại.

---

## 👨‍💻 Author

Được phát triển bởi [Phuc Bang]

📧 Email: nguyenphucbang65@gmail.com
🔗 GitHub: https://github.com/Phuc-Bang

---

## 🙏 Acknowledgments

- Chart.js team
- FastAPI team
- Bootstrap team
- Paho MQTT project

---

**⭐ Nếu project hữu ích, hãy cho một star nhé!**
