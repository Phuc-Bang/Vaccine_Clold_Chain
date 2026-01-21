# 🚀 Kế hoạch Nâng cấp VaccineColdChain

**Ngày tạo**: 22 Tháng 1, 2026  
**Phiên bản hiện tại**: v1.0 (Basic Capstone)  
**Status**: Planning Phase

---

## 📊 Tổng quan

Hệ thống VaccineColdChain v1.0 đã thực hiện 4 tầng kiến thức cơ bản. Kế hoạch nâng cấp tập trung vào:

- ✅ Tính năng mới (Multi-site, Sensors)
- ✅ Giao diện UX/UI hiện đại
- ✅ Bảo mật & Xác thực
- ✅ Hiệu năng & Scale
- ✅ DevOps & Monitoring
- ✅ Redundancy & HA

---

## 🎯 Phase 1: v1.1 - Enhanced Monitoring (Q1 2026)

### Mục tiêu

Cải thiện độ chính xác đo lường và thêm tính năng giám sát cơ bản.

### Tính năng

#### 1.1.1 Thêm cảm biến độ ẩm (Humidity)

- **Thiết bị**: DHT22 (Temp + Humidity)
- **File thay đổi**:
  - `firmware/node/include/sensor.h` - Thêm struct humidity
  - `firmware/node/src/sensor.cpp` - Hàm đọc DHT22
  - `backend/database.py` - Bảng telemetry thêm column `humidity`
  - `frontend/src/js/chart.js` - Hiển thị 2 biểu đồ

#### 1.1.2 Cảnh báo nhiều mức (Alert Levels)

```cpp
enum AlertLevel {
    NORMAL,      // 2-8°C
    WARNING,     // 8-10°C (Alert mềm)
    CRITICAL     // >10°C (Local alarm + MQTT)
};
```

#### 1.1.3 Data validation & Filtering

- Implement **Kalman Filter** (nâng cấp từ Median Filter)
- Reject anomaly: Nhảy nhiệt độ > 5°C trong 1 giây

#### 1.1.4 Status LED Dashboard

- **Red LED**: Critical alarm
- **Yellow LED**: Warning
- **Green LED**: Normal
- Thay `static/index.html` - Real-time LED status

**Timeline**: 2-3 tuần  
**Priority**: 🔴 High  
**Assignee**: TBD

---

## 🎯 Phase 2: v1.2 - Multi-Site Support (Q1 2026)

### Mục tiêu

Hỗ trợ giám sát nhiều kho lạnh đồng thời.

### Tính năng

#### 2.1 Device Registration UI

- Web form để đăng ký kho mới (Kho A, Kho B, Kho C...)
- Mỗi kho có Device ID + API Key riêng
- **File mới**:
  - `backend/api/devices.py` - CRUD devices
  - `frontend/src/pages/DeviceManager.html`

#### 2.2 Multi-Tenant Dashboard

- Filter theo Device/Kho
- Sidebar hiển thị danh sách devices
- `frontend/src/js/app.js` - Switch device context

#### 2.3 Database Schema Update

```sql
CREATE TABLE devices (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(200),
    api_key VARCHAR(255),
    created_at TIMESTAMP
);

-- Foreign key
ALTER TABLE telemetry ADD device_id VARCHAR(50);
ALTER TABLE alarms ADD device_id VARCHAR(50);
```

#### 2.4 API Endpoint Refactor

```
OLD: POST /api/telemetry
NEW: POST /api/devices/{device_id}/telemetry
```

**Timeline**: 2-3 tuần  
**Priority**: 🔴 High  
**Assignee**: TBD

---

## 🎯 Phase 3: v2.0 - Security & Authentication (Q2 2026)

### Mục tiêu

Thêm xác thực người dùng và bảo mật toàn hệ thống.

### Tính năng

#### 3.1 User Authentication

- **Backend**:
  - JWT token authentication
  - `backend/api/auth.py` - Login/Register
  - `backend/middleware/auth.py` - Token validation
  - Hash password: bcrypt
- **Frontend**:
  - Login page: `frontend/src/pages/Login.html`
  - Session management: `frontend/src/js/auth.js`

#### 3.2 Role-Based Access Control (RBAC)

```python
ROLES = {
    "admin": ["create_device", "delete_device", "view_reports"],
    "operator": ["view_dashboard", "acknowledge_alarm"],
    "viewer": ["view_dashboard"]
}
```

#### 3.3 API Key Rotation

- Auto-rotate API keys mỗi 90 ngày
- `backend/models/ApiKey.py` - Quản lý rotation

#### 3.4 Data Encryption

- MQTT over TLS (Port 8883)
- Backend DB password hashed
- Sensitive fields in `.env`

#### 3.5 Audit Log

```sql
CREATE TABLE audit_logs (
    id INT PRIMARY KEY,
    user_id VARCHAR(50),
    action VARCHAR(200),
    timestamp TIMESTAMP,
    ip_address VARCHAR(50)
);
```

**Timeline**: 3-4 tuần  
**Priority**: 🔴 Critical  
**Assignee**: TBD

---

## 🎯 Phase 4: v2.0 - Modern Frontend (Q2 2026)

### Mục tiêu

Nâng cấp giao diện từ vanilla JS → **Next.js + React** (SSR + Modern Stack).

### Tech Stack

```json
{
  "framework": "Next.js 14+ (App Router)",
  "library": "React 18+",
  "styling": "Tailwind CSS",
  "components": "shadcn/ui",
  "charts": "Recharts",
  "realtime": "Socket.io-client",
  "state": "Zustand",
  "http": "SWR + Axios",
  "language": "TypeScript",
  "testing": "Vitest + React Testing Library",
  "deploy": "Vercel"
}
```

### Tính năng

#### 4.1 Project Setup & Structure

```bash
npx create-next-app@latest vaccine-frontend \
  --typescript \
  --tailwind \
  --app \
  --eslint

npm install \
  socket.io-client \
  recharts \
  axios \
  zustand \
  swr \
  @radix-ui/react-* \
  class-variance-authority \
  clsx \
  tailwind-merge
```

**Project Structure**:

```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Dashboard home
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── devices/
│   │   ├── page.tsx             # Device list
│   │   └── [id]/
│   │       ├── page.tsx         # Device detail
│   │       └── chart.tsx        # Live chart
│   ├── alerts/
│   │   ├── page.tsx             # Alerts dashboard
│   │   └── history/page.tsx
│   ├── reports/page.tsx         # Historical reports
│   ├── settings/
│   │   ├── page.tsx             # User settings
│   │   └── admin/page.tsx
│   └── api/                     # Backend routes
│       ├── auth/route.ts
│       ├── devices/route.ts
│       ├── telemetry/route.ts
│       └── alerts/route.ts
├── components/
│   ├── Dashboard/
│   │   ├── index.tsx
│   │   ├── TemperatureChart.tsx
│   │   ├── AlertPanel.tsx
│   │   └── StatusGrid.tsx
│   ├── Device/
│   │   ├── DeviceCard.tsx
│   │   ├── DeviceList.tsx
│   │   └── DeviceDetail.tsx
│   ├── Common/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Navbar.tsx
│   ├── Charts/
│   │   ├── TemperatureChart.tsx   # Recharts
│   │   ├── HumidityChart.tsx
│   │   └── AlertTimeline.tsx
│   └── UI/
│       ├── Button.tsx             # shadcn/ui
│       ├── Card.tsx
│       ├── Dialog.tsx
│       ├── Badge.tsx
│       └── ...
├── hooks/
│   ├── useRealtimeData.ts         # Socket.io hook
│   ├── useDevices.ts              # SWR data fetching
│   ├── useAlerts.ts
│   ├── useDarkMode.ts
│   └── useAuth.ts
├── lib/
│   ├── axios.ts                   # Axios instance
│   ├── socket.ts                  # Socket.io setup
│   ├── utils.ts
│   ├── constants.ts
│   └── types.ts
├── store/
│   ├── authStore.ts               # Zustand stores
│   ├── deviceStore.ts
│   └── alertStore.ts
├── styles/
│   └── globals.css                # Tailwind styles
├── public/
│   ├── logo.svg
│   └── icons/
├── middleware.ts                  # Next.js middleware (Auth)
├── tailwind.config.ts
├── tsconfig.json
├── next.config.js
└── package.json
```

#### 4.2 Core Components

```tsx
// hooks/useRealtimeData.ts
import { useEffect, useState } from "react";
import { io } from "socket.io-client";

export function useRealtimeData(deviceId: string) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState("disconnected");

  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_API_URL);

    socket.on("connect", () => setStatus("connected"));
    socket.on(`telemetry:${deviceId}`, (payload) => {
      setData(payload);
    });
    socket.on("disconnect", () => setStatus("disconnected"));

    return () => socket.disconnect();
  }, [deviceId]);

  return { data, status };
}
```

```tsx
// components/Dashboard/TemperatureChart.tsx
"use client";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { useRealtimeData } from "@/hooks/useRealtimeData";

export function TemperatureChart({ deviceId }: { deviceId: string }) {
  const { data } = useRealtimeData(deviceId);

  return (
    <LineChart width={800} height={400} data={data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="timestamp" />
      <YAxis />
      <Tooltip />
      <Line type="monotone" dataKey="temperature" stroke="#8884d8" />
    </LineChart>
  );
}
```

#### 4.3 Real-time Updates (Socket.io)

- WebSocket connection to backend
- Automatic reconnect with exponential backoff
- Event-based data streaming
- Latency: < 100ms

```ts
// lib/socket.ts
import { io } from "socket.io-client";

export const socket = io(process.env.NEXT_PUBLIC_API_URL, {
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  reconnectionAttempts: 5,
});
```

#### 4.4 Authentication Middleware

```ts
// middleware.ts
import { NextRequest, NextResponse } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("token")?.value;

  if (!token && !request.nextUrl.pathname.startsWith("/login")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/devices/:path*", "/alerts/:path*", "/reports/:path*"],
};
```

#### 4.5 Performance Optimization

- Image optimization (next/image)
- Code splitting (automatic with Next.js)
- Data caching (SWR with stale-while-revalidate)
- CDN-ready (Static export for Vercel)

#### 4.6 Features

- ✅ Dark mode toggle (CSS variables)
- ✅ Export CSV/PDF reports (html2pdf library)
- ✅ Alarm history with infinite scroll
- ✅ Temperature graph with zoom/pan
- ✅ Multi-language support (i18n)
- ✅ Responsive design (Mobile/Tablet/Desktop)
- ✅ Performance optimized (Code splitting, Image optimization)
- ✅ SEO ready (Server-side rendering)
- ✅ Accessibility (WCAG 2.1 AA)

**Timeline**: 4 tuần  
**Priority**: 🔴 High  
**Assignee**: TBD

---

## 🎯 Phase 5: v2.1 - DevOps & Containerization (Q2 2026)

### Mục tiêu

Hoàn chỉnh deployment pipeline và monitoring.

### Tính năng

#### 5.1 Complete Docker Setup

```yaml
# docker-compose.yml
services:
  backend:
    build: ./backend
    ports: ["5000:5000"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  db:
    image: postgres:14
    volumes: ["./data:/var/lib/postgresql/data"]
  mqtt:
    image: eclipse-mosquitto:latest
    ports: ["1883:1883", "8883:8883"]
```

#### 5.2 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npm test
      - run: python -m pytest backend/
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t vaccine-coldchain .
      - run: docker push registry/vaccine-coldchain
```

#### 5.3 Monitoring & Logging

- **Prometheus** - Metrics collection
- **Grafana** - Dashboard visualization
- **ELK Stack** - Centralized logging
- Metrics: CPU, Memory, Request latency, MQTT publish rate

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: "backend"
    static_configs:
      - targets: ["localhost:5000"]
```

#### 5.4 Health Check Endpoints

```python
@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "db": check_db(),
        "mqtt": check_mqtt(),
        "timestamp": datetime.now()
    }
```

**Timeline**: 3 tuần  
**Priority**: 🔴 High  
**Assignee**: TBD

---

## 🎯 Phase 6: v2.2 - High Availability (Q3 2026)

### Mục tiêu

Đảm bảo hệ thống không bị downtime.

### Tính năng

#### 6.1 Gateway Redundancy

- **Active-Passive**: 2 Gateway, 1 chủ động, 1 chờ
- Heartbeat mechanism (2 giây)
- Failover tự động

```cpp
// gateway/src/redundancy.cpp
void checkPrimaryGateway() {
    if (millis() - lastHeartbeat > 6000) {
        // Primary dead, backup takes over
        PRIMARY_MODE = false;
        reconnectMQTT();
    }
}
```

#### 6.2 Database Replication

- PostgreSQL Master-Slave replication
- Automatic failover with pg_auto_failover

#### 6.3 Load Balancer

- HAProxy hoặc Nginx
- Route traffic: API requests → multiple backends
- Health check: /health endpoint

```nginx
# nginx.conf
upstream backend {
    server backend1:5000;
    server backend2:5000;
    keepalive 32;
}
```

#### 6.4 Message Queue (RabbitMQ/Kafka)

- Decouple API from database
- Ensure no message loss
- Worker processes: `backend/workers/telemetry_worker.py`

**Timeline**: 4 tuần  
**Priority**: 🟡 Medium  
**Assignee**: TBD

---

## 🎯 Phase 7: v3.0 - Advanced Features (Q3 2026)

### Mục tiêu

Thêm tính năng thông minh và phân tích nâng cao.

### Tính năng

#### 7.1 Predictive Maintenance

- Machine Learning: Predict failure 48h trước
- Dùng ARIMA hoặc Prophet để forecast temperature
- Alert: "Dự kiến quá nhiệt vào ngày mai 10:00"

```python
# backend/ml/forecasting.py
from prophet import Prophet

def predict_temperature(device_id):
    data = fetch_historical_data(device_id)
    model = Prophet()
    model.fit(data)
    forecast = model.make_future_dataframe(periods=48)  # 48 hours
    return model.predict(forecast)
```

#### 7.2 Anomaly Detection

- Isolation Forest algorithm
- Real-time anomaly scoring
- Alert nếu anomaly score > 0.8

#### 7.3 Geographic Map

- Hiển thị vị trí từng kho trên map
- Color-code: Green (Normal), Yellow (Warning), Red (Critical)
- `frontend/src/components/GeoMap.jsx` + Google Maps API

#### 7.4 SMS/Email Notifications

- **Twilio** - SMS alerts
- **SendGrid** - Email reports
- Configurable thresholds
- Daily digest report

```python
# backend/notifications/alert_service.py
def send_critical_alert(device_id, message):
    send_sms(admin_phone, f"CRITICAL: {message}")
    send_email(admin_email, f"Critical Alert - {device_id}")
```

#### 7.5 Third-party Integration

- Slack channel integration
- Telegram bot for alerts
- Webhook support for external systems

**Timeline**: 5 tuần  
**Priority**: 🟡 Medium  
**Assignee**: TBD

---

## 🎯 Phase 8: v3.1 - Mobile App (Q4 2026)

### Mục tiêu

Ứng dụng di động để giám sát khi không có máy tính.

### Tính năng

#### 8.1 React Native App

```bash
npx react-native init VaccineApp
# Shared components với web frontend
```

#### 8.2 Features

- Real-time dashboard
- Push notifications (Firebase Cloud Messaging)
- Offline mode: Sync when online
- Camera: Chụp hình kho (evidence photo)
- Biometric login (Face ID, Fingerprint)

#### 8.3 Deployment

- iOS: App Store
- Android: Google Play

**Timeline**: 6 tuần  
**Priority**: 🟢 Low  
**Assignee**: TBD

---

## 🎯 Phase 9: v4.0 - Cloud Deployment (Q4 2026)

### Mục tiêu

Deploy lên cloud để scale globally.

### Tính năng

#### 9.1 AWS Deployment

```
- EC2: Backend servers
- RDS: PostgreSQL managed database
- S3: Backup & logs storage
- CloudFront: CDN for frontend
- Route53: DNS management
```

#### 9.2 Infrastructure as Code (Terraform)

```hcl
# infra/terraform/main.tf
resource "aws_ec2_instance" "backend" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"
  count         = 2
}
```

#### 9.3 Auto-scaling

- Scale up/down dựa trên CPU/Memory
- ASG (Auto Scaling Group) policy

#### 9.4 CDN & Caching

- CloudFront for static assets
- Redis for API caching

**Timeline**: 5 tuần  
**Priority**: 🟡 Medium  
**Assignee**: TBD

---

## 📋 Dependency & Prerequisites

| Phase          | Depends On       | Notes               |
| -------------- | ---------------- | ------------------- |
| 1.1            | -                | Standalone          |
| 1.2            | 1.1              | Need updated schema |
| 2.0            | 1.2              | RBAC + multi-tenant |
| 2.0 (Frontend) | 1.2              | React setup         |
| 5.0            | 2.0              | Docker + CI/CD      |
| 6.0            | 5.0              | HA needs monitoring |
| 7.0            | 2.0 (Multi-site) | ML on multi devices |
| 8.0            | 2.0 (API stable) | Mobile clients      |
| 9.0            | 5.0              | Terraform ready     |

---

## 📊 Timeline Overview

```
Q1 2026: v1.1 (Sensors) + v1.2 (Multi-Site)
Q2 2026: v2.0 (Security) + v2.0 (Frontend) + v2.1 (DevOps)
Q3 2026: v2.2 (HA) + v3.0 (Advanced Features)
Q4 2026: v3.1 (Mobile) + v4.0 (Cloud)
```

---

## 🎬 Getting Started

### Immediate Actions (Next Sprint)

- [ ] Assess current code quality
- [ ] Create dev/staging branches
- [ ] Setup issue tracker on GitHub
- [ ] Create task breakdown for Phase 1.1

### Tech Stack Decisions

#### ✅ DECIDED:

- **Frontend framework**: Next.js 14+ (React SSR)
  - Rationale: SSR, Built-in API routes, Image optimization, TypeScript native
  - Alternative considered: Vue 3 (rejected: less ecosystem for enterprise)
  - Alternative considered: Angular (rejected: overkill + learning curve)

- **UI Component Library**: shadcn/ui + Tailwind CSS
  - Rationale: Composable, Headless, Zero runtime, Copy-paste components
  - Alternative: Material-UI (heavier, less customizable)
  - Alternative: Bootstrap (outdated styling patterns)

- **Real-time Updates**: Socket.io
  - Rationale: Reliable, Auto-reconnect, Room support, Fallback protocols
  - Alternative: Raw WebSocket (no auto-reconnect)

- **Charts Library**: Recharts
  - Rationale: React-native, Declarative, Responsive by default
  - Alternative: Chart.js (requires wrapper, more boilerplate)

- **State Management**: Zustand
  - Rationale: Lightweight (~2kb), Simple API, No boilerplate
  - Alternative: Redux (overkill for this project)

- **HTTP Client**: SWR + Axios
  - Rationale: SWR for caching, Axios for request interceptors
  - Alternative: Fetch API (verbose, no caching)

- **Database**: PostgreSQL (relational)
  - Rationale: Time-series data (telemetry), ACID compliance
  - Alternative: MongoDB (NoSQL, less suitable for structured data)

#### 🔄 TBD:

- **Cloud provider**: AWS vs Azure vs GCP? → **Decision in Phase 9**

---

## 📝 Notes & Considerations

- **Security First**: Authentication từ Phase 2, không delay
- **Testing**: Unit + Integration tests cho mỗi phase (Jest + React Testing Library)
- **Documentation**: API docs, Storybook for UI components, deployment guide
- **Performance**:
  - Frontend: Image optimization, Code splitting, SWR caching
  - Backend: Database indexing, Query optimization từ sớm
  - Network: Gzip compression, CDN for static assets
- **Scalability**: Design for 1000+ devices từ v1.2
- **Browser Support**: Modern browsers (Chrome, Firefox, Safari, Edge) - last 2 versions
- **Mobile**: Responsive design for iPad + mobile (handled by Next.js + Tailwind)

---

## 👥 Team & Responsibilities

| Role          | Assigned To | Phases                   |
| ------------- | ----------- | ------------------------ |
| Backend Lead  | -           | 1.1, 1.2, 2.0, 5.0       |
| Frontend Lead | -           | 1.1, 2.0 (Frontend), 4.0 |
| DevOps        | -           | 5.0, 6.0, 9.0            |
| ML Engineer   | -           | 7.0                      |
| Mobile Dev    | -           | 8.0                      |

---

## 🔗 Related Documents

- [ARCHITECTURE.md](../architecture/ARCHITECTURE.md) - Current system design
- [TECH_STACK.md](../TECH_STACK.md) - Detailed tech stack decisions (coming soon)
- [API Documentation](../api/) - API endpoints
- [Guides](../guides/) - Development guides
- [FRONTEND_SETUP.md](../guides/FRONTEND_SETUP.md) - Next.js setup guide

---

**Last Updated**: 22 Tháng 1, 2026  
**Tech Stack Finalized**: 22 Tháng 1, 2026  
**Next Review**: 29 Tháng 1, 2026
