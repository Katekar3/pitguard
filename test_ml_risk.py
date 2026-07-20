from app import app
from models import SensorReading
from ml_risk import score_reading

with app.app_context():
    readings = SensorReading.query.order_by(SensorReading.id.desc()).limit(15).all()
    readings = list(reversed(readings))

    for r in readings:
        result = score_reading(r)
        if result is None:
            print(f"Reading {r.id} (zone {r.zone_id}) — not enough history yet")
        else:
            flag = "🚨 ANOMALY" if result['is_anomaly'] else "safe"
            print(f"Reading {r.id} (zone {r.zone_id}) — gas={r.gas_level}, temp={r.temp} — {flag} (score={result['score']:.4f})")