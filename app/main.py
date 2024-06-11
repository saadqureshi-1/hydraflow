from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .models import User, Report
from . import db

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        date_str = request.form['date']
        tasks_completed = request.form['tasks_completed']
        challenges_faced = request.form.get('challenges_faced', '')
        hours_worked = request.form['hours_worked']
        additional_notes = request.form.get('additional_notes', '')

        # Convert date string to date object
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        report = Report(
            date=date,
            tasks_completed=tasks_completed,
            challenges_faced=challenges_faced,
            hours_worked=hours_worked,
            additional_notes=additional_notes,
            user_id=current_user.id
        )
        db.session.add(report)
        db.session.commit()
        flash('Report submitted!')
    return render_template('index.html')
