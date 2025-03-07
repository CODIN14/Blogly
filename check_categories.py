from applicaton import create_app, db
from applicaton.models import Category, Post

app = create_app()
with app.app_context():
    categories = Category.query.all()
    if categories:
        print("Categories and their posts:")
        for category in categories:
            posts = Post.query.filter_by(category_id=category.id).all()
            print(f"Category: {category.name} (ID: {category.id}), Posts: {[p.title for p in posts]}")
    else:
        print("No categories found.")