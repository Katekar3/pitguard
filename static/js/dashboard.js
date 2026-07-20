function severityColor(severity) {
    const colors = {
        low: 'text-yellow-400',
        medium: 'text-orange-400',
        high: 'text-red-400 severity-glow',
        critical: 'text-red-500 font-bold severity-glow'
    };
    return colors[severity] || 'text-gray-400';
}

function statusColor(status) {
    const colors = {
        safe: 'text-green-400',
        alert: 'text-orange-400',
        evacuated: 'text-red-400',
        offline: 'text-gray-500'
    };
    return colors[status] || 'text-gray-400';
}

function statusDotColor(zone) {
    if (zone.active_alerts.some(a => a.severity === 'critical')) return 'bg-red-500 dot-glow-red';
    if (zone.active_alerts.some(a => a.severity === 'high')) return 'bg-red-400 dot-glow-red';
    if (zone.active_alerts.length > 0) return 'bg-orange-400 dot-glow-amber';
    return 'bg-green-500';
}

async function updateDashboard() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();

        data.zones.forEach(zone => {
            const card = document.getElementById(`zone-${zone.id}`);
            if (!card) return;

            const dot = card.querySelector('.zone-status-dot');
            dot.className = `zone-status-dot w-2.5 h-2.5 rounded-full ${statusDotColor(zone)}`;

            renderMlBadge(card, zone.ml);

            const readingDiv = card.querySelector('.reading-data');
                if (zone.latest_reading) {
                    const r = zone.latest_reading;
                    const prevGas = readingDiv.dataset.gas;
                    const changed = prevGas !== undefined && prevGas !== String(r.gas_level);

                    readingDiv.innerHTML = `
                        <div class="grid grid-cols-3 gap-2 text-center">
                            <div>
                                <p class="text-2xl font-bold ${changed ? 'value-flash' : ''}">${r.gas_level}</p>
                                <p class="text-xs text-gray-600">Gas</p>
                            </div>
                            <div>
                                <p class="text-2xl font-bold">${r.temp}°</p>
                                <p class="text-xs text-gray-600">Temp</p>
                            </div>
                            <div>
                                <p class="text-2xl font-bold">${r.humidity}%</p>
                                <p class="text-xs text-gray-600">Humidity</p>
                            </div>
                        </div>
                        <p class="text-center text-xs text-gray-700 mt-2">Updated ${r.timestamp}</p>
                    `;
                    readingDiv.dataset.gas = r.gas_level;
                } else {
                    readingDiv.innerHTML = '<p class="text-center text-gray-600 text-sm py-4">No readings yet</p>';
                }
            const workersDiv = card.querySelector('.workers-list');
            workersDiv.innerHTML = zone.workers.length
                ? zone.workers.map(w => `<div class="${statusColor(w.status)}">${w.name} <span class="text-gray-600">— ${w.status}</span></div>`).join('')
                : '<p class="text-gray-700">No workers assigned</p>';

            const alertsDiv = card.querySelector('.alerts-list');
            alertsDiv.innerHTML = zone.active_alerts.length
                ? zone.active_alerts.map(a => `
                    <div class="flex items-center justify-between ${severityColor(a.severity)}">
                        <span>⚠ ${a.message} <span class="text-xs text-gray-600">(${a.timestamp})</span></span>
                        <button onclick="resolveAlert(${a.id})" class="text-xs text-gray-500 hover:text-teal-400 ml-2 underline">Resolve</button>
                    </div>
                `).join('')
                : '<p class="text-green-600">All clear</p>';
        });
    } catch (err) {
        console.error('Failed to update dashboard:', err);
    }
}
async function resolveAlert(alertId) {
    try {
        const res = await fetch(`/api/alerts/${alertId}/resolve`, { method: 'POST' });
        const data = await res.json();
        if (data.success) updateDashboard();
    } catch (err) {
        console.error('Failed to resolve alert:', err);
    }
}
function renderMlBadge(zoneCard, ml) {
    const badge = zoneCard.querySelector('.ml-badge');
    const scoreEl = zoneCard.querySelector('.ml-score');
    const explainerEl = zoneCard.querySelector('.ml-explainer');

    if (!ml) {
        badge.textContent = 'ML: Gathering data…';
        badge.className = 'ml-badge text-xs px-2 py-1 rounded bg-gray-700 text-gray-400';
        scoreEl.textContent = '';
        explainerEl.textContent = 'Needs a few more readings before pattern analysis kicks in.';
        return;
    }

    if (ml.is_anomaly) {
        badge.textContent = '⚠ Anomaly Detected';
        badge.className = 'ml-badge text-xs px-2 py-1 rounded bg-red-900 text-red-300';
        explainerEl.textContent = 'Sensor pattern deviates from normal zone behavior — may precede a threshold breach.';
    } else {
        badge.textContent = 'ML: Normal Pattern';
        badge.className = 'ml-badge text-xs px-2 py-1 rounded bg-teal-900 text-teal-300';
        explainerEl.textContent = 'Readings consistent with typical zone behavior.';
    }
    scoreEl.textContent = `score: ${ml.score.toFixed(3)}`;
}
updateDashboard();
setInterval(updateDashboard, 5000);