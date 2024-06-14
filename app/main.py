from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
from flask import request, jsonify, current_app
from app.chat_rag import process_string, chat_llm
from .models import User, Report
from . import db, mail
from .rag import get_summary

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html') 
@main.route('/about_us', methods=['GET'])
def about_us():
    return render_template('about_us.html') 

@main.route('/talk_to_data')
@login_required
def talk_to_data():
    return render_template('talk_to_data.html')

@main.route('/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get('message')
    bot_response = chat_llm(user_message)
    # Implement your bot logic here. For now, we'll use a simple echo bot.
    # bot_response =  bot_response"
    # return bot_response
    return jsonify({'response': bot_response})

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!','info')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if not user.email_verified:
                flash('Please verify your email address before logging in.','warning')
                return redirect(url_for('main.login'))
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid credentials','danger')
    return render_template('login.html')



@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You are already logged in!",'info')
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if not email.endswith('@thehexaa.com'):
            flash("Please enter a valid @thehexaa.com email address!",'warning')
            return redirect(url_for('main.register')) 
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("User with this email already exists.",'danger')
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
        flash('Report submitted!', 'success')
    return render_template('add_report.html')

@main.route('/report', methods=['GET'])
@login_required
def report():
    return render_template('report.html')

@main.route('/all_report', methods=['GET'])
@login_required
def all_report():
    if not current_user.is_admin:
        flash("You are not an admin!",'danger')
        return redirect(url_for('main.add_report'))
    reports=Report.query.all()
    users = User.query.all()
    return render_template('all_reports.html', reports=reports, users=users)
    

@main.route('/api/reports/', methods=['GET','POST'])
def get_reports_by_email():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    reports = Report.query.filter_by(user_id=user.id).all()
    return jsonify([{
        'id': report.id,
        'author': {'email': report.author.email},
        'tasks_completed': report.tasks_completed,
        'challenges_faced': report.challenges_faced,
        'hours_worked': report.hours_worked,
        'date': report.date.strftime('%Y-%m-%d')
    } for report in reports])


@main.route('/summary', methods=['GET','POST'])
@login_required
def summary():
    if not current_user.is_admin:
        flash("You are not an admin!",'danger')
        return redirect(url_for('main.index'))
    if request.method=='POST':
        data = request.get_json()
        user_id = data.get('userId')
        user=User.query.get(user_id)
        reports = Report.query.filter_by(user_id=user.id).all()
        data_string = ""
        if not reports:
            flash("No reports are present!",'info')
            return render_template('summary.html')
        for report in reports:
            data_string += f"Date: {report.date}\n"
            data_string += f"- Tasks Completed: {report.tasks_completed}\n"
            data_string += f"- Challenges Faced: {report.challenges_faced}\n"
            data_string += f"- Hours Worked: {report.hours_worked}\n"
            data_string += f"- Additional Notes: {report.additional_notes}\n\n"
        summary=get_summary(user.email,data_string)
        return jsonify({'summary': summary}), 200
    users=User.query.all()
    return render_template('summary.html',users=users)


    