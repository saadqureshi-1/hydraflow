from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime
from .models import User, Report
from . import db, mail
from flask_mail import Message

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html') 
@main.route('/about_us', methods=['GET'])
def about_us():
    return render_template('about_us.html') 

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.email_verified:
                flash('Please verify your email address before logging in.')
                return redirect(url_for('main.login'))
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials')
    return render_template('login.html')



@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        logout_user()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email.endswith('@thehexaa.com'):
            flash("Please enter a valid @thehexaa.com email address!")
            return redirect(url_for('main.register')) 
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User with this email already exists.")
            return redirect(url_for('main.register')) 
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        send_verification_email(user)
        flash('A confirmation email has been sent to your email address.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

def send_verification_email(user):
    token = user.generate_verification_token()
    verification_link = url_for('main.confirm_email', token=token, _external=True)
    msg = Message('Confirm Your Email Address', sender=current_app.config['MAIL_USERNAME'], recipients=[user.email])
    msg.body = f'Please click the following link to verify your email address: {verification_link}'
    mail.send(msg)

@main.route('/confirm_email/<token>')
def confirm_email(token):
    user = User.verify_verification_token(token)
    if user is None:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main.login'))
    user.email_verified = True
    db.session.commit()
    flash('Your email has been verified!', 'success')
    return redirect(url_for('main.login'))

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/add_report', methods=['GET', 'POST'])
@login_required
def add_report():
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
    return render_template('add_report.html')

@main.route('/report', methods=['GET'])
@login_required
def report():
    return render_template('report.html')

@main.route('/all_report', methods=['GET'])
@login_required
def all_report():
    if not current_user.is_admin:
        flash("You are not an admin!")
        return redirect(url_for('main.add_report'))
    reports=Report.query.all()
    users = User.query.all()
    return render_template('all_reports.html', reports=reports, users=users)
    
    