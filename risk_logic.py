def classify_severity(gas_level, temp):
    gas_tier = None
    if gas_level >= 90:
        gas_tier = "critical"
    elif gas_level >= 70:
        gas_tier = "high"
    elif gas_level >= 50:
        gas_tier = "medium"
    elif gas_level >= 30:
        gas_tier = "low"

    temp_tier = None
    if temp >= 45:
        temp_tier = "critical"
    elif temp >= 40:
        temp_tier = "high"
    elif temp >= 36:
        temp_tier = "medium"
    elif temp >= 30:
        temp_tier = "low"

    rank_tier = {
        'low': 1, 'medium': 2, 'high': 3, 'critical': 4, None : 0
    }

    overall_severity = None
    if rank_tier[gas_tier] == rank_tier[temp_tier]:
        overall_severity = temp_tier
    elif rank_tier[gas_tier] > rank_tier[temp_tier]:
        overall_severity = gas_tier
    elif rank_tier[temp_tier] > rank_tier[gas_tier]:
        overall_severity = temp_tier

    return overall_severity

from extensions import db
from models import Alert

def evaluate_reading(reading):
    severity = classify_severity(float(reading.gas_level), float(reading.temp))
    alert = None

    if severity is not None:
        message = f"{severity.capitalize()} risk detected in zone {reading.zone_id} — gas: {reading.gas_level}, temp: {reading.temp}"
        alert = Alert(
            zone_id=reading.zone_id,
            reading_id=reading.id,
            severity=severity,
            message=message
        )
        db.session.add(alert)
        db.session.commit()
    else:
        # Reading is fully safe — auto-clear stale low/medium noise for this zone.
        # High/critical alerts are never touched here; those stay manual-resolve only.
        stale_alerts = Alert.query.filter_by(zone_id=reading.zone_id, resolved=False) \
            .filter(Alert.severity.in_(['low', 'medium'])).all()
        for a in stale_alerts:
            a.resolved = True
        if stale_alerts:
            db.session.commit()

    update_worker_statuses(reading.zone_id)

    return alert
from models import Worker

def update_worker_statuses(zone_id):
    active_alerts = Alert.query.filter_by(zone_id=zone_id, resolved=False).all()

    if not active_alerts:
        new_status = 'safe'
    else:
        severities = [a.severity for a in active_alerts]
        if any(s in ('high', 'critical') for s in severities):
            new_status = 'evacuated'
        else:
            new_status = 'alert'

    workers = Worker.query.filter_by(zone_id=zone_id).all()
    for w in workers:
        if w.status != 'offline':
            w.status = new_status

    db.session.commit()

def resolve_alert(alert_id):
    alert = Alert.query.get(alert_id)
    if alert and not alert.resolved:
        alert.resolved = True
        db.session.commit()
        update_worker_statuses(alert.zone_id)
    return alert
