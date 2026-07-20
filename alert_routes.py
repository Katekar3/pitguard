from flask import Blueprint, render_template, jsonify, session
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func
from extensions import db
from models import Alert, Zone
from risk_logic import resolve_alert

analytics_bp = Blueprint('analytics', __name__)

def login_required_json(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return f(*args, **kwargs)
    return decorated

@analytics_bp.route('/api/alerts/<int:alert_id>/resolve', methods=['POST'])
@login_required_json
def resolve_alert_route(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    resolve_alert(alert.id)
    return jsonify({'success': True})

@analytics_bp.route('/alerts/history')
def alert_history():
    return render_template('alert_history.html')

@analytics_bp.route('/api/alert-trends')
def alert_trends():
    since = datetime.utcnow() - timedelta(days=7)

    rows = db.session.query(
        func.date(Alert.timestamp).label('day'),
        Alert.severity,
        func.count(Alert.id).label('count')
    ).filter(Alert.timestamp >= since) \
     .group_by(func.date(Alert.timestamp), Alert.severity) \
     .all()

    days = [(since + timedelta(days=i)).date().isoformat() for i in range(8)]
    severities = ['low', 'medium', 'high', 'critical']

    data = {day: {sev: 0 for sev in severities} for day in days}
    for row in rows:
        day_str = row.day.isoformat() if hasattr(row.day, 'isoformat') else str(row.day)
        if day_str in data:
            data[day_str][row.severity] = row.count

    return jsonify({
        'days': days,
        'series': {sev: [data[day][sev] for day in days] for sev in severities}
    })

@analytics_bp.route('/api/alert-by-zone')
def alert_by_zone():
    rows = db.session.query(
        Zone.name, func.count(Alert.id)
    ).join(Alert, Alert.zone_id == Zone.id) \
     .group_by(Zone.name) \
     .all()

    return jsonify({'zones': [r[0] for r in rows], 'counts': [r[1] for r in rows]})