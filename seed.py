from app import  db
from app.models import User
import sqlite3
from faker import Faker
from datetime import datetime
import random

def seed_admin_user():
    # Create an admin user
    email="admin@thehexaa.com"
    password="admin"
    admin_user = User(
        email=email,
        is_admin=True,
        email_verified=True
    )
    admin_user.set_password(password)
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        print('Superuser already exists!')
        return
    
    db.session.add(admin_user)
    db.session.commit()

    print('Admin user seeded successfully!')


def insert_synthetic_data(db_path, num_users, num_reports):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    faker = Faker()
    
    # Check if the 'report' table is empty
    cursor.execute('SELECT COUNT(*) FROM report')
    report_count = cursor.fetchone()[0]
    if report_count > 0:
        print("Database tables already contain data. Skipping the seeding process.")
        conn.close()
        return
    # Generate synthetic data for 'user' table
    user_data = []
    for _ in range(num_users):
        email = faker.email()
        password_hash = faker.sha256()
        is_admin = faker.boolean()
        email_verified = faker.boolean()
        user_data.append((email, password_hash, is_admin, email_verified))
    
    cursor.executemany('''
        INSERT INTO user (email, password_hash, is_admin, email_verified)
        VALUES (?, ?, ?, ?)
    ''', user_data)
    
    # Generate synthetic data for 'report' table
    report_data = []
    for _ in range(num_reports):
        date = faker.date_this_decade()
        tasks_completed = faker.text()
        challenges_faced = faker.text() if faker.boolean() else None
        hours_worked = round(random.uniform(1, 12), 2)
        additional_notes = faker.text() if faker.boolean() else None
        timestamp = datetime.now()
        user_id = faker.random_int(min=1, max=num_users)  # Assuming user IDs start from 1
        report_data.append((date, tasks_completed, challenges_faced, hours_worked, additional_notes, timestamp, user_id))
    
    cursor.executemany('''
        INSERT INTO report (date, tasks_completed, challenges_faced, hours_worked, additional_notes, timestamp, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', report_data)
    
    # Commit and close the connection
    conn.commit()
    conn.close()
    print(f"Inserted {num_users} rows into 'user' table and {num_reports} rows into 'report' table.")

