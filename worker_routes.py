from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from extensions import db
from models import Worker, Zone

worker_bp = Blueprint('workers', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@worker_bp.route('/workers')
def list_workers():
    return render_template('workers.html', workers=Worker.query.all())

@worker_bp.route('/workers/add', methods=['GET', 'POST'])
@admin_required
def add_worker():
    zones = Zone.query.all()
    if request.method == 'POST':
        worker = Worker(name=request.form['name'], zone_id=request.form['zone_id'], status='safe')
        db.session.add(worker)
        db.session.commit()
        flash(f"{worker.name} added")
        return redirect(url_for('workers.list_workers'))
    return render_template('worker_form.html', zones=zones, worker=None)

@worker_bp.route('/workers/<int:worker_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    zones = Zone.query.all()
    if request.method == 'POST':
        worker.name = request.form['name']
        worker.zone_id = request.form['zone_id']
        if request.form.get('offline'):
            worker.status = 'offline'
        elif worker.status == 'offline':
            worker.status = 'safe'  # back online; next reading re-derives real status
        db.session.commit()
        flash(f"{worker.name} updated")
        return redirect(url_for('workers.list_workers'))
    return render_template('worker_form.html', zones=zones, worker=worker)

@worker_bp.route('/workers/<int:worker_id>/delete', methods=['POST'])
@admin_required
def delete_worker(worker_id):
    worker = Worker.query.get_or_404(worker_id)
    db.session.delete(worker)
    db.session.commit()
    flash(f"{worker.name} removed")
    return redirect(url_for('workers.list_workers'))