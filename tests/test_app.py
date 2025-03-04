def test_create_post_with_category(self):
    # Sign up a user
    self.client.post('/sign-up', data={
        'email': 'colinpaul.ebby2022@vitstudent.ac.in',
        'username': 'ColinVIT',
        'password': 'coolME@1412',
        'confirm_password': 'coolME@1412'
    }, follow_redirects=True)
    self.client.post('/login', data={
        'email': 'colinpaul.ebby2022@vitstudent.ac.in',
        'password': 'coolME@1412'
    }, follow_redirects=True)
    # Add a category
    with self.app.app_context():
        category = Category(name="TestCategory")
        db.session.add(category)
        db.session.commit()
        category_id = category.id
    # Create a post with a category
    response = self.client.post('/create-post', data={
        'text': 'Test post with category',
        'category_id': category_id
    }, follow_redirects=True)
    self.assertEqual(response.status_code, 200)
    with self.app.app_context():
        post = Post.query.filter_by(text='Test post with category').first()
        self.assertIsNotNone(post)
        self.assertEqual(post.category.name, "TestCategory")

def test_filter_posts_by_category(self):
    # Sign up a user
    self.client.post('/sign-up', data={
        'email': 'colinpaul.ebby2022@vitstudent.ac.in',
        'username': 'ColinVIT',
        'password': 'coolME@1412',
        'confirm_password': 'coolME@1412'
    }, follow_redirects=True)
    self.client.post('/login', data={
        'email': 'colinpaul.ebby2022@vitstudent.ac.in',
        'password': 'coolME@1412'
    }, follow_redirects=True)
    # Add a category and a post
    with self.app.app_context():
        category = Category(name="TestCategory")
        db.session.add(category)
        db.session.commit()
        post = Post(text="Test post", author=current_user.id, category_id=category.id)
        db.session.add(post)
        db.session.commit()
        category_id = category.id
    # Filter posts by category
    response = self.client.get(f'/home?category_id={category_id}')
    self.assertEqual(response.status_code, 200)
    self.assertIn(b"Test post", response.data)