import pandas as pd
import joblib
from extensions import db
from models import SensorReading

model = joblib.load('isolation_forest_model.pkl')

FEATURES = ['gas_level', 'temp', 'humidity', 'gas_change', 'temp_change', 'gas_rolling_avg']

def score_reading(reading):
    # Fetch recent history for this zone, including the new reading, ordered by time
    recent = (
    SensorReading.query
    .filter_by(zone_id=reading.zone_id)
    .filter(SensorReading.timestamp <= reading.timestamp)
    .order_by(SensorReading.timestamp.desc())
    .limit(5)
    .all()
)
    recent = list(reversed(recent))  # put back in chronological order

    df = pd.DataFrame([{
        'gas_level': float(r.gas_level),
        'temp': float(r.temp),
        'humidity': float(r.humidity)
    } for r in recent])

    df['gas_change'] = df['gas_level'].diff()
    df['temp_change'] = df['temp'].diff()
    df['gas_rolling_avg'] = df['gas_level'].rolling(window=5).mean()

    latest = df.iloc[[-1]][FEATURES]  # just the newest row's features

    if latest.isnull().any().any():
        return None  # not enough history yet to score this reading

    anomaly = model.predict(latest)[0]
    score = model.decision_function(latest)[0]

    return {'is_anomaly': bool(anomaly == -1), 'score': float(score)}


from models import Zone, SensorReading

def get_zone_ml_scores():
    """Latest ML anomaly assessment per zone, for dashboard display."""
    scores = {}
    for zone in Zone.query.all():
        latest = SensorReading.query.filter_by(zone_id=zone.id) \
            .order_by(SensorReading.timestamp.desc()).first()
        scores[zone.id] = score_reading(latest) if latest else None
    return scores