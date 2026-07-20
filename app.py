import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from urllib.parse import quote_plus
from functools import wraps
from extensions import db, bcrypt

load_dotenv()

app = Flask(__name__)

db_user = os.getenv('DB_USER')
db_password = quote_plus(os.getenv('DB_PASSWORD'))
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT', '3306')
db_ssl_ca = os.getenv('DB_SSL_CA')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if db_ssl_ca:
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'connect_args': {'ssl_ca': db_ssl_ca}}
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db.init_app(app)
bcrypt.init_app(app)

from models import User   # safe now — models.py no longer imports app.py


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['role'] = user.role
            return {'success': True}
        else:
            return {'success': False, 'message': 'Invalid username or password'}

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


@app.route('/health')
def health():
    return {"status": "ok"}, 200

from models import Zone, Worker, Alert, SensorReading
from sqlalchemy import desc, case

from ml_risk import score_reading   # add near your other top-level imports

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    zones = Zone.query.all()
    zone_data = []

    severity_order = case(
        (Alert.severity == 'critical', 0),
        (Alert.severity == 'high', 1),
        (Alert.severity == 'medium', 2),
        (Alert.severity == 'low', 3),
    )

    for zone in zones:
        latest_reading = (
            SensorReading.query
            .filter_by(zone_id=zone.id)
            .order_by(desc(SensorReading.timestamp))
            .first()
        )
        workers_in_zone = Worker.query.filter_by(zone_id=zone.id).all()
        active_alerts = (
            Alert.query
            .filter_by(zone_id=zone.id, resolved=False)
            .order_by(severity_order, desc(Alert.timestamp))
            .all()
        )

        ml_result = score_reading(latest_reading) if latest_reading else None

        zone_data.append({
            'id': zone.id,
            'name': zone.name,
            'latest_reading': {
                'gas_level': float(latest_reading.gas_level),
                'temp': float(latest_reading.temp),
                'humidity': float(latest_reading.humidity),
                'timestamp': latest_reading.timestamp.strftime('%H:%M:%S')
            } if latest_reading else None,
            'workers': [{'id': w.id, 'name': w.name, 'status': w.status} for w in workers_in_zone],
            'active_alerts': [{
                'id': a.id,
                'severity': a.severity,
                'message': a.message,
                'timestamp': a.timestamp.strftime('%H:%M:%S')
            } for a in active_alerts],
            'ml': {
                'is_anomaly': ml_result['is_anomaly'],
                'score': ml_result['score']
            } if ml_result else None
        })

    return {'zones': zone_data}

@app.route('/dashboard')
@login_required
def dashboard():
    zones = Zone.query.all()
    return render_template('dashboard.html', title="Live Dashboard", zones=zones)

from worker_routes import worker_bp
app.register_blueprint(worker_bp)

from alert_routes import analytics_bp
app.register_blueprint(analytics_bp)

from user_routes import user_bp
app.register_blueprint(user_bp)

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)