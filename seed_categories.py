from applicaton import create_app, db
from applicaton.models import Category

app = create_app()
with app.app_context():
    categories = [
        Category(name="Technology"),
        Category(name="Lifestyle"),
        Category(name="Travel"),
        Category(name="Food"),
    ]
    db.session.add_all(categories)
    db.session.commit()
    print("Categories added!")