import pandas as pd
from app import app
from extensions import db

with app.app_context():
    query = "SELECT * FROM sensor_readings ORDER BY zone_id, timestamp"
    df = pd.read_sql(query, db.engine)

# print(df.shape)
# print(df.head())
# print(df.describe())
# print(df['zone_id'].value_counts())


df['gas_change'] = df.groupby('zone_id')['gas_level'].diff()
df['temp_change'] = df.groupby('zone_id')['temp'].diff()

df['gas_rolling_avg'] = df.groupby('zone_id')['gas_level'].rolling(window=5).mean().reset_index(level=0, drop=True)

df = df.dropna()

print(df.shape)
print(df.head(10))