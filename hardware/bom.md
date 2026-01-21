# 📋 Danh Sách Linh Kiện (BOM)

> Danh sách đầy đủ linh kiện cho hệ thống Vaccine Cold Chain Monitor

---

## 🔷 Node Cảm Biến (mỗi đơn vị)

| # | Linh Kiện | Thông Số | SL | Giá Ước Tính |
|---|-----------|----------|------|--------------|
| 1 | ESP32 DevKit V1 | 30-pin, micro USB | 1 | 100-150k |
| 2 | DHT11 | Nhiệt độ/Độ ẩm | 1 | 20-40k |
| 3 | LED Đỏ 5mm | 20mA, 2V | 1 | 1k |
| 4 | LED Xanh 5mm | 20mA, 2V | 1 | 1k |
| 5 | LED Vàng 5mm | 20mA, 2V | 1 | 1k |
| 6 | Điện trở 220Ω | 1/4W | 3 | 500đ |
| 7 | Breadboard | 400 lỗ | 1 | 30-50k |
| 8 | Dây nối | M-M bộ | 1 bộ | 20-30k |
| 9 | Cáp USB | Micro USB | 1 | 20-30k |

**Tổng mỗi Node: ~200-300k**

---

## 🔷 Gateway (1 đơn vị)

| # | Linh Kiện | Thông Số | SL | Giá Ước Tính |
|---|-----------|----------|------|--------------|
| 1 | ESP32 DevKit V1 | 30-pin, micro USB | 1 | 100-150k |
| 2 | LED Xanh dương 5mm | 20mA, 2V | 1 | 1k |
| 3 | LED Vàng 5mm | 20mA, 2V | 1 | 1k |
| 4 | Điện trở 220Ω | 1/4W | 2 | 500đ |
| 5 | Cáp USB | Micro USB | 1 | 20-30k |
| 6 | Adapter nguồn | 5V 2A | 1 | 50-80k |

**Tổng Gateway: ~180-270k**

---

## 🔷 Server (1 đơn vị - tuỳ chọn)

| # | Linh Kiện | Thông Số | SL | Giá Ước Tính |
|---|-----------|----------|------|--------------|
| 1 | Raspberry Pi 4 | 4GB RAM | 1 | 1.5-2 triệu |
| 2 | Thẻ SD | 32GB Class 10 | 1 | 150-200k |
| 3 | Nguồn | 5V 3A USB-C | 1 | 150-200k |

**Hoặc sử dụng PC/Laptop/Cloud có sẵn**

---

## 📊 Tổng Chi Phí Dự Án

| Cấu Hình | Chi Phí Ước Tính |
|----------|------------------|
| Tối thiểu (1 Node + 1 Gateway) | ~400-600k |
| Tiêu chuẩn (3 Node + 1 Gateway) | ~800k-1.2 triệu |
| Có Server (+ RPi) | ~2.5-3.5 triệu |

---

## 🛒 Nơi Mua Linh Kiện

- **Điện tử Nshop** (nshop.com.vn): Giao nhanh, giá tốt
- **Điện tử IOT** (icdayroi.com): Chuyên IoT
- **Shopee/Lazada**: Giá rẻ, nhiều lựa chọn
- **Linh kiện Việt**: Giá buôn

---

## ⚠️ Lưu Ý

1. **Nâng cấp DHT22**: Để đo chính xác hơn, dùng DHT22 (+30-50k)
2. **Cảm biến chống nước**: Dùng DS18B20 cho môi trường khắc nghiệt
3. **Vỏ hộp**: Nên dùng hộp ABS hoặc in 3D để bảo vệ mạch
