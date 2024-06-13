import sqlite3
from faker import Faker
from datetime import datetime
import random

def insert_synthetic_data(db_path, num_users, num_reports):
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    faker = Faker()
    
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

# Specify the path to the SQLite database and the number of rows to insert
db_path = 'instance/db.sqlite3'  # Adjusted path
num_users = 100
num_reports = 100

insert_synthetic_data(db_path, num_users, num_reports)
