function showBarChart(element, label, labels, data) {
    new Chart(element, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function showBubbleChart(element, label, data) {
    new Chart(element, {
        type: 'bubble',
        data: {
            datasets: [{
                label: label,
                data: data.map(row2bubble)
            }]
        },
        options: {
            plugins: {
                tooltip: {
                    enabled: false
                }
            },
            scales: {
                x: {
                    min: 2018,
                    ticks: {
                        stepSize: 1
                    }
                },
                y: {
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function row2bubble(row) {
    return {
        x: row[0],
        y: row[1],
        r: row[3] * 0.2
    };
}