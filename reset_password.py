from applicaton import create_app, db
from applicaton.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Query all users to find your account
    users = User.query.all()
    for user in users:
        print(f"ID: {user.id}, Email: {user.email}, Username: {user.username}, Password (hashed): {user.password}")

    # Reset password for a specific user (replace 'your.email@example.com' with your email)
    user = User.query.filter_by(email='colinpaul.ebby2022@vitstudent.ac.in').first()
    if user:
        new_password = 'coolME@1412'  # Replace with your desired new password
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        print(f"Password for {user.email} has been reset to: {new_password}")
    else:
        print("User not found")