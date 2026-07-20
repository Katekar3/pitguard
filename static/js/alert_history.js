async function loadTrendChart() {
    const res = await fetch('/api/alert-trends');
    const data = await res.json();

    new Chart(document.getElementById('trendChart'), {
        type: 'bar',
        data: {
            labels: data.days,
            datasets: [
                { label: 'Low',      data: data.series.low,      backgroundColor: '#14b8a6' },
                { label: 'Medium',   data: data.series.medium,   backgroundColor: '#f59e0b' },
                { label: 'High',     data: data.series.high,     backgroundColor: '#f97316' },
                { label: 'Critical', data: data.series.critical, backgroundColor: '#ef4444' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: { x: { stacked: true }, y: { stacked: true, beginAtZero: true } },
            plugins: {
                legend: { labels: { color: '#d1d5db' } },
                datalabels: {
                    color: '#0a0a0a',
                    font: { weight: 'bold', size: 10 },
                    formatter: (value) => value > 0 ? value : ''
                }
            }
        }
    });
}

async function loadZoneChart() {
    const res = await fetch('/api/alert-by-zone');
    const data = await res.json();

    new Chart(document.getElementById('zoneChart'), {
        type: 'bar',
        data: {
            labels: data.zones,
            datasets: [{ label: 'Total Alerts', data: data.counts, backgroundColor: '#f59e0b' }]
        },
        options: { responsive: true, plugins: { legend: { display: false } } }
    });
}


loadTrendChart();
loadZoneChart();