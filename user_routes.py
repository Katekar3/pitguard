from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models import User
from worker_routes import admin_required

user_bp = Blueprint('users', __name__)

@user_bp.route('/admin/users')
@admin_required
def list_users():
    return render_template('users.html', users=User.query.all())

@user_bp.route('/admin/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('user_form.html')

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f"{username} created")
        return redirect(url_for('users.list_users'))

    return render_template('user_form.html')

@user_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash("You can't delete your own account")
        return redirect(url_for('users.list_users'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"{user.username} removed")
    return redirect(url_for('users.list_users'))