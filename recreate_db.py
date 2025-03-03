from applicaton import create_app, db

app = create_app()
with app.app_context():
    db.drop_all()  # Drop all tables (just to be sure)
    db.create_all()
print("Database recreated successfully!")