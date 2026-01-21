const ctx = document.getElementById('tempChart').getContext('2d');

// Create Gradient
const gradient = ctx.createLinearGradient(0, 0, 0, 400);
gradient.addColorStop(0, 'rgba(0, 243, 255, 0.5)'); // Neon Blue High
gradient.addColorStop(1, 'rgba(0, 243, 255, 0.0)'); // Transparent Low

const tempChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: [], // Time labels
        datasets: [{
            label: 'Nhiệt độ (°C)',
            data: [],
            borderColor: '#00f3ff', // Neon Blue Border
            backgroundColor: gradient,
            borderWidth: 2,
            pointBackgroundColor: '#ffffff',
            pointBorderColor: '#00f3ff',
            pointRadius: 4,
            pointHoverRadius: 6,
            fill: true,
            tension: 0.4 // Smooth curve
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                labels: {
                    color: '#8b9bb4', // Muted Text
                    font: {
                        family: 'Outfit'
                    }
                }
            }
        },
        scales: {
            x: {
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                },
                ticks: {
                    color: '#8b9bb4'
                }
            },
            y: {
                beginAtZero: false,
                grid: {
                    color: 'rgba(255, 255, 255, 0.05)'
                },
                ticks: {
                    color: '#8b9bb4'
                },
                suggestedMin: 0,
                suggestedMax: 15
            }
        },
        interaction: {
            mode: 'index',
            intersect: false,
        }
    }
});

function updateChart(timestamp, temperature) {
    const timeLabel = new Date(timestamp * 1000).toLocaleTimeString();

    // Add new data
    tempChart.data.labels.push(timeLabel);
    tempChart.data.datasets[0].data.push(temperature);

    // Keep only last 20 points
    if (tempChart.data.labels.length > 20) {
        tempChart.data.labels.shift();
        tempChart.data.datasets[0].data.shift();
    }

    tempChart.update();
}
