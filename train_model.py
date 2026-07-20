import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from app import app
from extensions import db

with app.app_context():
    query = "SELECT * FROM sensor_readings ORDER BY zone_id, timestamp"
    df = pd.read_sql(query, db.engine)

df['gas_change'] = df.groupby('zone_id')['gas_level'].diff()
df['temp_change'] = df.groupby('zone_id')['temp'].diff()
df['gas_rolling_avg'] = df.groupby('zone_id')['gas_level'].rolling(window=5).mean().reset_index(level=0, drop=True)
df = df.dropna()

features = ['gas_level', 'temp', 'humidity', 'gas_change', 'temp_change', 'gas_rolling_avg']
X = df[features]

model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

df['anomaly'] = model.predict(X)  # -1 = anomaly, 1 = normal
df['anomaly_score'] = model.decision_function(X)  # lower = more anomalous

joblib.dump(model, 'isolation_forest_model.pkl')
print("Model trained and saved.")

print(df['anomaly'].value_counts())
print(df[df['anomaly'] == -1][['zone_id', 'gas_level', 'temp', 'gas_change', 'anomaly_score']].head(20))