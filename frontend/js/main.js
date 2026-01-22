/**
 * ColdChain Dashboard - Main JavaScript
 * File: frontend/js/main.js
 */

// === CONFIGURATION ===

const API_URL = "http://localhost:8000/api/v1";  // TÙY CHỈNH địa chỉ backend
const NODE_ID = "NODE_01";  // TÙY CHỈNH device ID
const REFRESH_INTERVAL = 3000;  // 3 giây
const STATUS_SYNC_INTERVAL = 2000;  // 2 giây
const DEAD_LINK_THRESHOLD = 10000;  // 10 giây

// Ngưỡng nhiệt độ
const TEMP_THRESHOLDS = {
    NORMAL_MIN: 2,
    NORMAL_MAX: 8,
    WARN_MAX: 10
};

// === GLOBAL VARIABLES ===

let myChart = null;
let lastDataTimestamp = null;

// === CHART INITIALIZATION ===

function initChart() {
    const ctx = document.getElementById('mainChart').getContext('2d');
    
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Nhiệt độ (°C)',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                tension: 0.4,  // Đường cong mượt
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }, {
                // Đường ngưỡng an toàn trên (8°C)
                label: 'Ngưỡng trên (8°C)',
                data: [],
                borderColor: '#ffc107',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0
            }, {
                // Đường ngưỡng nguy hiểm (10°C)
                label: 'Ngưỡng nguy hiểm (10°C)',
                data: [],
                borderColor: '#dc3545',
                borderWidth: 2,
                borderDash: [5, 5],
                fill: false,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Thời gian'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Nhiệt độ (°C)'
                    },
                    suggestedMin: 0,
                    suggestedMax: 15
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
    
    console.log("✅ Chart initialized");
}

// === DATA FILTERING (Lọc nhiễu) ===

function applyMedianFilter(values, windowSize = 3) {
    /**
     * Áp dụng median filter để loại bỏ spike/nhiễu
     * windowSize: kích thước cửa sổ (nên là số lẻ)
     */
    const filtered = [];
    const halfWindow = Math.floor(windowSize / 2);
    
    for (let i = 0; i < values.length; i++) {
        const window = [];
        
        // Lấy các giá trị xung quanh
        for (let j = Math.max(0, i - halfWindow); j <= Math.min(values.length - 1, i + halfWindow); j++) {
            window.push(values[j]);
        }
        
        // Sắp xếp và lấy median
        window.sort((a, b) => a - b);
        const median = window[Math.floor(window.length / 2)];
        filtered.push(median);
    }
    
    return filtered;
}

function applyMovingAverage(values, windowSize = 3) {
    /**
     * Áp dụng moving average để làm mượt dữ liệu
     */
    const smoothed = [];
    
    for (let i = 0; i < values.length; i++) {
        let sum = 0;
        let count = 0;
        
        for (let j = Math.max(0, i - windowSize + 1); j <= i; j++) {
            sum += values[j];
            count++;
        }
        
        smoothed.push(sum / count);
    }
    
    return smoothed;
}

// === CHART UPDATE ===

function updateChart(data) {
    /**
     * Cập nhật chart với dữ liệu mới
     * data: array of {value, time}
     */
    if (!myChart || !data || data.length === 0) {
        console.warn("⚠️ No data to update chart");
        return;
    }
    
    // Tách labels và values
    const labels = data.map(item => {
        // Format: "HH:MM:SS"
        const timeParts = item.time.split(' ');
        return timeParts.length > 1 ? timeParts[1] : item.time;
    });
    
    const rawValues = data.map(item => parseFloat(item.value));
    
    // Áp dụng filter để loại bỏ nhiễu
    const filteredValues = applyMedianFilter(rawValues, 3);
    const smoothedValues = applyMovingAverage(filteredValues, 2);
    
    // Tạo mảng ngưỡng cố định
    const upperThreshold = new Array(labels.length).fill(TEMP_THRESHOLDS.NORMAL_MAX);
    const dangerThreshold = new Array(labels.length).fill(TEMP_THRESHOLDS.WARN_MAX);
    
    // Cập nhật chart
    myChart.data.labels = labels;
    myChart.data.datasets[0].data = smoothedValues;
    myChart.data.datasets[1].data = upperThreshold;
    myChart.data.datasets[2].data = dangerThreshold;
    
    myChart.update('none');  // Update không animation để mượt hơn
    
    console.log(`📊 Chart updated with ${data.length} points`);
}

// === KPI UPDATE ===

function updateKPI(latestTemp, latestTime) {
    /**
     * Cập nhật KPI cards với dữ liệu mới nhất
     */
    const tempValue = parseFloat(latestTemp);
    const tempElement = document.getElementById('temp-value');
    const lastUpdatedElement = document.getElementById('last-updated');
    
    // Cập nhật giá trị nhiệt độ
    tempElement.textContent = `${tempValue.toFixed(1)}°C`;
    
    // Xóa tất cả class trạng thái cũ
    tempElement.classList.remove('temp-normal', 'temp-warn', 'temp-danger', 'blink');
    
    // Thêm class theo ngưỡng
    if (tempValue >= TEMP_THRESHOLDS.WARN_MAX) {
        // Nguy hiểm: >=10°C
        tempElement.classList.add('temp-danger', 'blink');
        showToast(`⚠️ CẢNH BÁO: Nhiệt độ quá cao (${tempValue.toFixed(1)}°C)!`, 'error');
    } else if (tempValue > TEMP_THRESHOLDS.NORMAL_MAX) {
        // Cảnh báo: 8-10°C
        tempElement.classList.add('temp-warn');
    } else if (tempValue >= TEMP_THRESHOLDS.NORMAL_MIN) {
        // Bình thường: 2-8°C
        tempElement.classList.add('temp-normal');
    } else {
        // Quá lạnh: <2°C (hiếm khi xảy ra)
        tempElement.classList.add('temp-warn');
    }
    
    // Cập nhật thời gian
    lastUpdatedElement.textContent = latestTime;
    
    // Lưu timestamp để kiểm tra dead link
    lastDataTimestamp = new Date();
}

// === DEVICE UI UPDATE ===

function updateDeviceUI(status) {
    /**
     * Cập nhật UI trạng thái thiết bị
     * status: "ON", "OFF", "PENDING", "UNKNOWN"
     */
    const statusElement = document.getElementById('device-status');
    const iconElement = document.getElementById('device-icon');
    const cardBody = iconElement.closest('.card-body');
    
    // Xóa class cũ
    cardBody.classList.remove('status-on', 'status-off', 'status-pending');
    
    switch(status) {
        case 'ON':
            statusElement.textContent = 'ĐANG HOẠT ĐỘNG';
            statusElement.className = 'text-success';
            iconElement.className = 'fas fa-fan fa-3x';  // Icon quạt
            cardBody.classList.add('status-on');
            break;
            
        case 'OFF':
            statusElement.textContent = 'TẮT';
            statusElement.className = 'text-danger';
            iconElement.className = 'fas fa-power-off fa-3x';
            cardBody.classList.add('status-off');
            break;
            
        case 'PENDING':
            statusElement.textContent = 'ĐANG XỬ LÝ...';
            statusElement.className = 'text-warning';
            iconElement.className = 'fas fa-spinner fa-3x';
            cardBody.classList.add('status-pending');
            break;
            
        default:
            statusElement.textContent = 'KHÔNG XÁC ĐỊNH';
            statusElement.className = 'text-secondary';
            iconElement.className = 'fas fa-question-circle fa-3x';
            break;
    }
}

// === FETCH HISTORY DATA ===

async function fetchHistoryData() {
    /**
     * Lấy dữ liệu lịch sử từ API
     */
    try {
        const response = await fetch(`${API_URL}/history/${NODE_ID}?limit=20`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data && data.length > 0) {
            // Cập nhật chart
            updateChart(data);
            
            // Cập nhật KPI với dữ liệu mới nhất
            const latest = data[data.length - 1];
            updateKPI(latest.value, latest.time);
            
            // Kiểm tra dead link
            checkDeadLink();
        } else {
            console.warn("⚠️ No data received from API");
        }
        
    } catch (error) {
        console.error("❌ Error fetching data:", error);
        showToast(`Lỗi kết nối API: ${error.message}`, 'error');
    }
}

// === DEVICE CONTROL ===

async function controlDevice(action) {
    /**
     * Gửi lệnh điều khiển thiết bị
     * action: "ON" hoặc "OFF"
     */
    const btnId = action === 'ON' ? 'btn-on' : 'btn-off';
    const btn = document.getElementById(btnId);
    
    // Hiển thị trạng thái loading
    setLoadingState(btn, true);
    
    try {
        const payload = {
            device_id: NODE_ID,
            command: action,
            param: 100
        };
        
        const response = await fetch(`${API_URL}/control/device`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`Server Error ${response.status}`);
        }
        
        const result = await response.json();
        console.log("✅ Control command sent:", result);
        
        showToast(`Đã gửi lệnh ${action} thành công!`, 'success');
        
        // Optimistic UI: hiển thị trạng thái PENDING
        updateDeviceUI('PENDING');
        
        // Chờ xác nhận từ thiết bị (timeout 8s)
        waitForStatus(action, 8000);
        
    } catch (error) {
        console.error("❌ Control error:", error);
        showToast(`Gửi lệnh thất bại: ${error.message}`, 'error');
    } finally {
        setLoadingState(btn, false);
    }
}

// === WAIT FOR STATUS CONFIRMATION ===

async function waitForStatus(targetStatus, timeout = 8000) {
    /**
     * Polling để chờ thiết bị xác nhận trạng thái
     */
    const startTime = Date.now();
    const pollInterval = 1000;  // Poll mỗi 1 giây
    
    const pollStatus = async () => {
        try {
            const response = await fetch(`${API_URL}/device/${NODE_ID}/status`);
            const data = await response.json();
            
            if (data.status === targetStatus) {
                // Thành công!
                showToast(`✅ Thiết bị đã ${targetStatus === 'ON' ? 'bật' : 'tắt'} thành công!`, 'success');
                updateDeviceUI(targetStatus);
                return true;
            }
            
            // Chưa thành công, kiểm tra timeout
            if (Date.now() - startTime < timeout) {
                // Tiếp tục poll
                setTimeout(pollStatus, pollInterval);
            } else {
                // Timeout
                showToast('⚠️ Thiết bị chưa phản hồi, vui lòng kiểm tra!', 'error');
                syncDeviceStatus();  // Sync lại trạng thái thật
            }
            
        } catch (error) {
            console.error("Poll error:", error);
        }
    };
    
    // Bắt đầu poll
    setTimeout(pollStatus, pollInterval);
}

// === SYNC DEVICE STATUS ===

async function syncDeviceStatus() {
    /**
     * Đồng bộ trạng thái thiết bị từ backend
     */
    try {
        const response = await fetch(`${API_URL}/device/${NODE_ID}/status`);
        const data = await response.json();
        
        if (data.status && data.status !== "UNKNOWN") {
            updateDeviceUI(data.status);
        }
        
    } catch (error) {
        console.log("⚠️ Sync error:", error.message);
    }
}

// === DEAD LINK DETECTION ===

function checkDeadLink() {
    /**
     * Kiểm tra nếu không nhận dữ liệu mới > 10 giây
     */
    if (!lastDataTimestamp) return;
    
    const now = new Date();
    const timeDiff = now - lastDataTimestamp;
    
    const overlay = document.getElementById('offline-overlay');
    const connectionStatus = document.getElementById('connection-status');
    const btnOn = document.getElementById('btn-on');
    const btnOff = document.getElementById('btn-off');
    
    if (timeDiff > DEAD_LINK_THRESHOLD) {
        // Mất kết nối
        overlay.classList.remove('d-none');
        connectionStatus.innerHTML = '<i class="fas fa-times-circle"></i> Mất kết nối';
        connectionStatus.className = 'text-danger';
        
        // Disable nút điều khiển
        btnOn.disabled = true;
        btnOff.disabled = true;
        
    } else {
        // Kết nối tốt
        overlay.classList.add('d-none');
        connectionStatus.innerHTML = '<i class="fas fa-check-circle"></i> Đang kết nối';
        connectionStatus.className = 'text-success';
        
        // Enable nút điều khiển
        btnOn.disabled = false;
        btnOff.disabled = false;
    }
}

// === UI UTILITIES ===

function setLoadingState(button, isLoading) {
    /**
     * Hiển thị trạng thái loading cho button
     */
    if (isLoading) {
        button.classList.add('btn-loading');
        button.disabled = true;
    } else {
        button.classList.remove('btn-loading');
        button.disabled = false;
    }
}

function showToast(message, type = 'success') {
    /**
     * Hiển thị toast notification
     * type: 'success' hoặc 'error'
     */
    Toastify({
        text: message,
        duration: 3000,
        gravity: "top",
        position: "right",
        className: type,
        stopOnFocus: true
    }).showToast();
}

// === INITIALIZATION ===

document.addEventListener('DOMContentLoaded', () => {
    console.log("🚀 ColdChain Dashboard Starting...");
    
    // Khởi tạo chart
    initChart();
    
    // Lấy dữ liệu lần đầu
    fetchHistoryData();
    
    // Auto-refresh dữ liệu mỗi 3 giây
    setInterval(fetchHistoryData, REFRESH_INTERVAL);
    
    // Đồng bộ trạng thái thiết bị
    syncDeviceStatus();
    setInterval(syncDeviceStatus, STATUS_SYNC_INTERVAL);
    
    // Kiểm tra dead link mỗi 2 giây
    setInterval(checkDeadLink, 2000);
    
    console.log("✅ Dashboard initialized successfully!");
});