import random
import sys
import time
from datetime import datetime, timedelta
from app import app
from extensions import db
from models import SensorReading, Zone
from risk_logic import evaluate_reading, update_worker_statuses

BASELINE_GAS = 15.0
BASELINE_TEMP = 26.0
BASELINE_HUMIDITY = 55.0

def generate_reading(prev_gas, prev_temp, prev_humidity, spike=False):
    gas = prev_gas + (BASELINE_GAS - prev_gas) * 0.15 + random.uniform(-2, 2)
    temp = prev_temp + (BASELINE_TEMP - prev_temp) * 0.15 + random.uniform(-0.5, 0.5)
    humidity = prev_humidity + (BASELINE_HUMIDITY - prev_humidity) * 0.1 + random.uniform(-1, 1)

    if spike:
        gas += random.uniform(30, 60)
        temp += random.uniform(5, 10)

    gas = max(0, min(gas, 100))
    temp = max(15, min(temp, 50))
    humidity = max(20, min(humidity, 90))

    return round(gas, 2), round(temp, 2), round(humidity, 2)


def simulate_batch(num_readings_per_zone=500, hazard_probability=0.05):
    with app.app_context():
        zones = Zone.query.all()
        if not zones:
            print("No zones found — add zones to the DB first.")
            return

        base_time = datetime.now() - timedelta(minutes=num_readings_per_zone)

        for zone in zones:
            gas, temp, humidity = BASELINE_GAS, BASELINE_TEMP, BASELINE_HUMIDITY
            for i in range(num_readings_per_zone):
                spike = random.random() < hazard_probability
                gas, temp, humidity = generate_reading(gas, temp, humidity, spike=spike)
                reading = SensorReading(
                    zone_id=zone.id, gas_level=gas, temp=temp, humidity=humidity,
                    timestamp=base_time + timedelta(minutes=i)
                )
                db.session.add(reading)
            print(f"Zone {zone.id} done — {num_readings_per_zone} readings generated.")

        db.session.commit()
        print(f"Inserted {num_readings_per_zone} readings for {len(zones)} zones.")


def simulate_live(interval_seconds=12, hazard_probability=0.05):
    with app.app_context():
        zones = Zone.query.all()
        if not zones:
            print("No zones found — add zones to the DB first.")
            return

        last_values = {}
        for zone in zones:
            last_reading = (
                SensorReading.query
                .filter_by(zone_id=zone.id)
                .order_by(SensorReading.timestamp.desc())
                .first()
            )
            if last_reading:
                last_values[zone.id] = (float(last_reading.gas_level), float(last_reading.temp), float(last_reading.humidity))
            else:
                last_values[zone.id] = (BASELINE_GAS, BASELINE_TEMP, BASELINE_HUMIDITY)

        print(f"Live simulation started — one reading per zone every {interval_seconds}s. Ctrl+C to stop.")

        try:
            while True:
                for zone in zones:
                    gas, temp, humidity = last_values[zone.id]
                    spike = random.random() < hazard_probability
                    gas, temp, humidity = generate_reading(gas, temp, humidity, spike=spike)
                    last_values[zone.id] = (gas, temp, humidity)

                    reading = SensorReading(
                        zone_id=zone.id, gas_level=gas, temp=temp, humidity=humidity,
                        timestamp=datetime.now()
                    )
                    db.session.add(reading)
                    db.session.commit()

                    alert = evaluate_reading(reading)
                    update_worker_statuses(zone.id)

                    tag = f" ⚠ {alert.severity}" if alert else ""
                    print(f"Zone {zone.id} — gas={gas}, temp={temp}{tag}")

                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nLive simulation stopped.")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--live':
        simulate_live()
    else:
        simulate_batch(num_readings_per_zone=500, hazard_probability=0.05)