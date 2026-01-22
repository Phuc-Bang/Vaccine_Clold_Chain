const API_URL = "http://localhost:8000/api/v1";
const DEVICE_ID = "NODE_01";

let myChart = null;

function initChart() {
  const ctx = document.getElementById("mainChart");
  myChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Nhiệt độ (°C)",
          data: [],
          borderColor: "#1f5eff",
          backgroundColor: "rgba(31, 94, 255, 0.12)",
          tension: 0.35,
          fill: true,
          pointRadius: 3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          suggestedMin: 0,
          suggestedMax: 12,
          ticks: { stepSize: 2 },
        },
      },
      plugins: {
        legend: { display: false },
      },
    },
  });
}

function medianFilter(values, windowSize = 3) {
  // Lọc nhiễu kiểu median để bỏ spike đơn lẻ
  if (values.length < windowSize) {
    return values;
  }

  const half = Math.floor(windowSize / 2);
  return values.map((_, index) => {
    const start = Math.max(0, index - half);
    const end = Math.min(values.length, index + half + 1);
    const slice = values.slice(start, end).sort((a, b) => a - b);
    return slice[Math.floor(slice.length / 2)];
  });
}

function updateChart(data) {
  const labels = data.map((item) => item.time.split(" ")[1] || item.time);
  const rawValues = data.map((item) => Number(item.value));
  const filteredValues = medianFilter(rawValues, 3);

  myChart.data.labels = labels;
  myChart.data.datasets[0].data = filteredValues;
  myChart.update();
}

function updateKPI(latestTemp, latestTime) {
  const tempEl = document.getElementById("temp-value");
  const lastUpdatedEl = document.getElementById("last-updated");

  tempEl.classList.remove("temp-normal", "temp-warn", "temp-danger", "blink");

  if (latestTemp >= 10) {
    tempEl.classList.add("temp-danger", "blink");
  } else if (latestTemp >= 8) {
    tempEl.classList.add("temp-warn");
  } else {
    tempEl.classList.add("temp-normal");
  }

  tempEl.textContent = `${latestTemp.toFixed(2)} °C`;
  lastUpdatedEl.textContent = latestTime;
}

function updateDeviceUI(status) {
  const statusEl = document.getElementById("device-status");
  const iconEl = document.getElementById("device-icon");

  if (status === "ON") {
    statusEl.textContent = "ON";
    iconEl.className = "fa-solid fa-fan fa-2x text-success";
    iconEl.classList.add("fa-spin");
  } else if (status === "OFF") {
    statusEl.textContent = "OFF";
    iconEl.className = "fa-solid fa-power-off fa-2x text-danger";
  } else if (status === "PENDING") {
    statusEl.textContent = "ĐANG CHUYỂN";
    iconEl.className = "fa-solid fa-spinner fa-2x text-warning fa-spin";
  } else if (status === "DISCONNECTED") {
    statusEl.textContent = "DISCONNECTED";
    iconEl.className = "fa-solid fa-plug-circle-xmark fa-2x text-secondary";
  } else {
    statusEl.textContent = "UNKNOWN";
    iconEl.className = "fa-solid fa-circle-question fa-2x text-muted";
  }
}

function setControlsEnabled(isEnabled) {
  ["btn-on", "btn-off"].forEach((id) => {
    const btn = document.getElementById(id);
    btn.disabled = !isEnabled;
  });
}

function setLoadingState(btn, isLoading) {
  if (!btn) return;
  btn.disabled = isLoading;
  btn.classList.toggle("btn-loading", isLoading);
}

function showToast(message, type) {
  const colors = {
    success: "#1db477",
    error: "#e23b3b",
    warning: "#f5b400",
  };

  Toastify({
    text: message,
    duration: 2500,
    gravity: "top",
    position: "right",
    close: true,
    style: {
      background: colors[type] || colors.warning,
    },
  }).showToast();
}

function parseTimestamp(timeString) {
  if (!timeString) return null;
  const safe = timeString.replace(" ", "T");
  const parsed = new Date(safe);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

async function fetchHistoryData() {
  try {
    const res = await fetch(`${API_URL}/history/${DEVICE_ID}?limit=20`);
    const data = await res.json();

    if (!data.length) {
      return;
    }

    updateChart(data);

    const latest = data[data.length - 1];
    updateKPI(Number(latest.value), latest.time);

    const latestTs = parseTimestamp(latest.time);
    const overlay = document.getElementById("offline-overlay");

    if (latestTs && Date.now() - latestTs.getTime() > 10000) {
      // Mất tín hiệu > 10s
      overlay.classList.remove("d-none");
      updateDeviceUI("DISCONNECTED");
      setControlsEnabled(false);
    } else {
      overlay.classList.add("d-none");
      setControlsEnabled(true);
    }
  } catch (error) {
    console.error("Fetch history error:", error);
  }
}

async function waitForStatus(targetStatus, timeoutMs = 8000) {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    await new Promise((resolve) => setTimeout(resolve, 1000));
    try {
      const res = await fetch(`${API_URL}/device/${DEVICE_ID}/status`);
      const data = await res.json();
      if (data.status === targetStatus) {
        return true;
      }
    } catch (error) {
      console.log("Wait status error:", error);
    }
  }

  return false;
}

async function controlDevice(action) {
  const btnId = action === "ON" ? "btn-on" : "btn-off";
  const btn = document.getElementById(btnId);
  const overlay = document.getElementById("offline-overlay");

  if (!overlay.classList.contains("d-none")) {
    showToast("Mất tín hiệu, không thể gửi lệnh.", "error");
    return;
  }

  setLoadingState(btn, true);

  try {
    const payload = {
      device_id: DEVICE_ID,
      command: action,
      param: 100,
    };

    const response = await fetch(`${API_URL}/control/device`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Server Error");

    showToast(`Đã gửi lệnh ${action} thành công!`, "success");
    updateDeviceUI("PENDING");

    const confirmed = await waitForStatus(action, 8000);
    if (confirmed) {
      showToast("Máy lạnh đã hoạt động", "success");
      updateDeviceUI(action);
    } else {
      showToast("Thiết bị chưa phản hồi, vui lòng kiểm tra", "error");
    }
  } catch (error) {
    console.error(error);
    showToast(`Gửi lệnh thất bại: ${error.message}`, "error");
  } finally {
    setLoadingState(btn, false);
  }
}

async function syncDeviceStatus() {
  try {
    const res = await fetch(`${API_URL}/device/${DEVICE_ID}/status`);
    const data = await res.json();
    if (data.status && data.status !== "UNKNOWN") {
      updateDeviceUI(data.status);
    }
  } catch (error) {
    console.log("Sync error:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  initChart();
  fetchHistoryData();
  setInterval(fetchHistoryData, 3000);

  syncDeviceStatus();
  setInterval(syncDeviceStatus, 2000);
});