from app import app
from models import SensorReading
from risk_logic import evaluate_reading

with app.app_context():
    readings = SensorReading.query.order_by(SensorReading.id.desc()).limit(10).all()
    for r in readings:
        alert = evaluate_reading(r)
        if alert:
            print(f"ALERT: {alert.message} (severity: {alert.severity})")
        else:
            print(f"Reading {r.id} — safe, no alert")