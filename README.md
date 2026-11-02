<h1 align="center">PitGuard</h1>

<p align="center">
  A live safety dashboard for underground mines.<br>
  Watches gas, air quality, temperature and humidity, and raises an alert before conditions turn dangerous.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white" alt="Flask">
  <img src="https://img.shields.io/badge/MySQL-4479A1?logo=mysql&logoColor=white" alt="MySQL">
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?logo=scikitlearn&logoColor=white" alt="scikit-learn">
  <img src="https://img.shields.io/badge/Tailwind-06B6D4?logo=tailwindcss&logoColor=white" alt="Tailwind">
</p>

<p align="center">
  <b><a href="YOUR-LIVE-LINK">Live demo</a></b>
</p>

<!-- Add a dashboard screenshot here:
<p align="center"><img src="docs/dashboard.png" width="760" alt="PitGuard dashboard"></p>
-->

---

## Why this exists

Underground mines are dangerous in ways you can't always see: a gas level creeps up, the air gets warm and thin, and by the time someone notices it's late. PitGuard is a learning project that explores how a monitoring system could catch this early, using two layers of checks: clear rules for known limits, and machine learning for readings that simply look wrong.

> Sensor data in this project is **simulated**. PitGuard is a portfolio project, not a certified safety system.

## What it does

- Tracks gas, air quality, temperature and humidity for each mine zone in real time.
- Classifies every reading with rule-based risk logic.
- Flags unusual patterns with an **Isolation Forest** anomaly detector, even when no single threshold is crossed.
- Raises alerts and keeps a history of them.
- Has user accounts, plus a cinematic drilling animation with sound on the login page.

## How the risk detection works

1. **Rules first.** `risk_logic.py` compares each reading against safe limits and labels it by risk level.
2. **Then anomaly detection.** I used Isolation Forest, an unsupervised model, rather than a supervised classifier. The only labels I could have trained on were the ones my own rules produce, so a supervised model would just have copied the rules. Isolation Forest finds readings that don't look like normal data without needing labels.

## Database

I designed the MySQL schema by hand:

| Table | Holds |
|---|---|
| `zones` | The mine areas being monitored |
| `workers` | People assigned to zones |
| `sensor_readings` | Every reading, per zone and time |
| `alerts` | Alerts raised from risk logic or anomaly detection |
| `users` | Dashboard accounts |

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy |
| Database | MySQL (Aiven, managed) |
| ML | scikit-learn (Isolation Forest) |
| Frontend | HTML, Tailwind CSS, vanilla JavaScript |
| Hosting | Render |

## Run it locally

```bash
git clone <YOUR-REPO-LINK>
cd <repo-folder>
pip install -r requirements.txt
```

Create a MySQL database, set your connection details as environment variables (see the config file), then:

```bash
flask run
```

## Known limitations

- Sensor data is simulated.
- The app is hosted on free tiers, so the first load can be slow while the server wakes up.

## Built by

**Yashmit Katekar**, as a solo project to learn Flask, MySQL and applied ML.
