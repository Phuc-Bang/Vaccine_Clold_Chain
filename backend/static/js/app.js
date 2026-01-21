/**
 * Vaccine Cold Chain Monitoring - Main Application
 * Modern UI with premium effects
 */

// ==================== GLOBAL CONFIG ====================
const CONFIG = {
    GATEWAY_ID: 1,
    TEMP_MIN: 20.0,
    TEMP_MAX: 30.0,
    TEMP_ALARM: 35.0,
    MAX_LOG_ENTRIES: 100
};

// ==================== GLOBAL STATE ====================
let coolerOn = false;
let wsClient = null;
let tempChart = null;
let api = null;

// ==================== UI ELEMENTS ====================
const elements = {
    connectionStatus: () => document.getElementById('connectionStatus'),
    currentTemp: () => document.getElementById('currentTemp'),
    currentHumidity: () => document.getElementById('currentHumidity'),
    alarmStatus: () => document.getElementById('alarmStatus'),
    coolerStatus: () => document.getElementById('coolerStatus'),
    btnCooler: () => document.getElementById('btnCooler'),
    btnAlarm: () => document.getElementById('btnAlarm'),
    controlFeedback: () => document.getElementById('controlFeedback'),
    logContainer: () => document.getElementById('logContainer'),
    alertList: () => document.getElementById('alertList')
};

// ==================== UI UPDATE FUNCTIONS ====================

function updateConnectionStatus(connected) {
    const el = elements.connectionStatus();
    if (connected) {
        el.className = 'status-badge connected';
        el.innerHTML = '<div class="status-dot"></div><span>Đã kết nối</span>';
    } else {
        el.className = 'status-badge disconnected';
        el.innerHTML = '<div class="status-dot"></div><span>Mất kết nối</span>';
    }
}

function updateTemperature(temp, humidity) {
    const tempEl = elements.currentTemp();
    tempEl.textContent = `${temp.toFixed(1)}°C`;
    
    // Update class based on temperature
    tempEl.className = 'temp-value ';
    if (temp > CONFIG.TEMP_MAX || temp < CONFIG.TEMP_MIN) {
        if (temp > CONFIG.TEMP_ALARM) {
            tempEl.className += 'danger';
        } else {
            tempEl.className += 'warning';
        }
    } else {
        tempEl.className += 'normal';
    }
    
    elements.currentHumidity().textContent = `${humidity.toFixed(1)}%`;
}

function updateAlarmStatus(isOn) {
    const el = elements.alarmStatus();
    if (isOn) {
        el.className = 'status-item alarm-on';
        el.innerHTML = `
            <div class="status-icon">🔔</div>
            <div class="status-text">Còi Hú: BẬT</div>
        `;
    } else {
        el.className = 'status-item alarm-off';
        el.innerHTML = `
            <div class="status-icon">🔕</div>
            <div class="status-text">Còi Hú: TẮT</div>
        `;
    }
}

function updateCoolerStatus(isOn) {
    const el = elements.coolerStatus();
    const btn = elements.btnCooler();
    coolerOn = isOn;
    
    if (isOn) {
        el.className = 'status-item cooler-on';
        el.innerHTML = `
            <div class="status-icon">❄️</div>
            <div class="status-text">Máy Lạnh: BẬT</div>
        `;
        btn.innerHTML = '🔥 Tắt Máy Lạnh Dự Phòng';
        btn.className = 'btn btn-cooler active';
    } else {
        el.className = 'status-item cooler-off';
        el.innerHTML = `
            <div class="status-icon">⬜</div>
            <div class="status-text">Máy Lạnh: TẮT</div>
        `;
        btn.innerHTML = '❄️ Bật Máy Lạnh Dự Phòng';
        btn.className = 'btn btn-cooler';
    }
}

function setFeedback(message, type = 'info') {
    const el = elements.controlFeedback();
    el.textContent = message;
    
    // Add visual feedback
    el.style.color = type === 'success' ? '#34d399' : 
                     type === 'error' ? '#f87171' : 
                     '#94a3b8';
}

// ==================== LOGGING ====================

function log(message, type = 'info') {
    const container = elements.logContainer();
    const time = new Date().toLocaleTimeString('vi-VN');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${time}] ${message}`;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;

    // Keep only last N entries
    while (container.children.length > CONFIG.MAX_LOG_ENTRIES) {
        container.removeChild(container.firstChild);
    }
}

// ==================== ALERTS ====================

function addAlert(message) {
    const list = elements.alertList();
    
    // Remove "no alerts" message
    const noAlerts = list.querySelector('.no-alerts');
    if (noAlerts) noAlerts.remove();
    
    const time = new Date().toLocaleTimeString('vi-VN');
    const item = document.createElement('div');
    item.className = 'alert-item';
    item.innerHTML = `
        <div class="alert-icon">⚠️</div>
        <div class="alert-content">
            <div class="alert-message">${message}</div>
            <div class="alert-time">${time}</div>
        </div>
    `;
    list.insertBefore(item, list.firstChild);
}

// ==================== MESSAGE HANDLERS ====================

function handleMessage(data) {
    switch (data.type) {
        case 'telemetry':
            updateTemperature(data.temperature, data.humidity || 0);
            updateAlarmStatus(data.alarm_state);
            updateCoolerStatus(data.cooler_state);
            tempChart.addData(data.temperature);
            
            // Check for alerts
            if (data.temperature > CONFIG.TEMP_MAX) {
                addAlert(`Nhiệt độ cao: ${data.temperature.toFixed(1)}°C`);
            }
            
            log(`📊 ${data.temperature.toFixed(1)}°C | ${(data.humidity || 0).toFixed(1)}%`, 'info');
            break;
            
        case 'status':
            log(`✅ Node: ${data.status}`, 'success');
            setFeedback(`✅ ${data.status}`, 'success');
            
            if (data.status.includes('COOLER_ON')) {
                updateCoolerStatus(true);
            } else if (data.status.includes('COOLER_OFF')) {
                updateCoolerStatus(false);
            } else if (data.status.includes('ALARM_OFF')) {
                updateAlarmStatus(false);
            }
            break;
            
        case 'batch_received':
            log(`📦 Batch: ${data.count} mẫu từ Gateway ${data.gateway_id}`, 'info');
            break;
            
        case 'connected':
            log('🔌 Kết nối server thành công', 'success');
            break;
    }
}

// ==================== CONTROL FUNCTIONS ====================

async function toggleCooler() {
    const command = coolerOn ? 'TURN_OFF_BACKUP_COOLER' : 'TURN_ON_BACKUP_COOLER';
    setFeedback('⏳ Đang gửi lệnh...', 'info');
    
    const result = await api.sendCommand(CONFIG.GATEWAY_ID, command);
    
    if (result.ok) {
        log(`📤 Đã gửi: ${command}`, 'success');
        setFeedback('⏳ Đã gửi, chờ phản hồi...', 'info');
    } else {
        log(`❌ Lỗi: ${result.error}`, 'error');
        setFeedback('❌ ' + (result.error || 'Lỗi'), 'error');
    }
}

async function resetAlarm() {
    setFeedback('⏳ Đang gửi lệnh...', 'info');
    
    const result = await api.sendCommand(CONFIG.GATEWAY_ID, 'RESET_ALARM');
    
    if (result.ok) {
        log('📤 Đã gửi: RESET_ALARM', 'success');
        setFeedback('⏳ Đã gửi, chờ phản hồi...', 'info');
    } else {
        log(`❌ Lỗi: ${result.error}`, 'error');
        setFeedback('❌ ' + (result.error || 'Lỗi'), 'error');
    }
}

// ==================== INITIALIZATION ====================

function init() {
    // Initialize API client
    api = new ApiClient();
    
    // Initialize chart
    tempChart = new TemperatureChart('tempChart');
    
    // Initialize WebSocket
    wsClient = new WebSocketClient(null, {
        onMessage: handleMessage,
        onConnect: () => {
            updateConnectionStatus(true);
            log('🔌 WebSocket connected', 'success');
        },
        onDisconnect: () => {
            updateConnectionStatus(false);
            log('⚡ WebSocket disconnected', 'warning');
        }
    });
    wsClient.connect();
    
    // Bind button events
    elements.btnCooler().addEventListener('click', toggleCooler);
    elements.btnAlarm().addEventListener('click', resetAlarm);
    
    log('🚀 Dashboard khởi tạo thành công', 'success');
}

// Start when DOM ready
document.addEventListener('DOMContentLoaded', init);
