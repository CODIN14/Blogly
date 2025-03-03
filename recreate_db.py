from applicaton import create_app, db

app = create_app()
with app.app_context():
    db.drop_all()  # Drop tables (just in case)
    db.create_all()
print("Database recreated with Notification model!")