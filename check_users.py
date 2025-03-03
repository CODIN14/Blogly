from applicaton import create_app, db
from applicaton.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    if users:
        print("Users still exist:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}, Username: {user.username}")
    else:
        print("No users found in the database.")