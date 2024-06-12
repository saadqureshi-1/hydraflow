from app import  db
from app.models import User

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
