from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify  # We need jsonify to send the list back
from flask_login import login_required, current_user
from sqlalchemy import true
from .models import Post, User, Comment, Like, Follower, Notification,Category
import requests
from . import db
from werkzeug.utils import secure_filename
from prometheus_client import Counter
import os
import logging
import logging
from flask import request



# Import the registry from __init__.py
from . import registry

views = Blueprint("views", __name__)






@views.route("/")
@views.route("/home")
@login_required
def home():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    category_id = request.args.get('category_id')
    logger.debug(f"Received category_id: {category_id}")

    # Get following users
    following_ids = [follower.user_id for follower in current_user.following]
    following_ids.append(current_user.id)  # Include current user's posts
    logger.debug(f"Following IDs (including self): {following_ids}")

    # Build the query
    query = Post.query.filter(Post.author.in_(following_ids))

    # Apply category filter
    if category_id and category_id != "":
        try:
            category_id_int = int(category_id)
            query = query.filter(Post.category_id == category_id_int)
            logger.debug(f"Applied category filter for ID: {category_id_int}")
        except ValueError:
            logger.error(f"Invalid category_id: {category_id}")

    # Execute query
    posts = query.order_by(Post.date_created.desc()).all()
    logger.debug(f"Filtered posts count: {len(posts)}")
    for post in posts:
        logger.debug(f"Post - ID: {post.id}, Title: {post.title}, Category ID: {post.category_id}")

    # Get categories for the dropdown
    categories = Category.query.all()
    logger.debug(f"Categories available: {[category.name for category in categories]}")

    return render_template("home.html", user=current_user, posts=posts, categories=categories)


@login_required
@views.route("/create-post", methods=['GET', 'POST'])
def create_post():
    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('text')
        category_id = request.form.get('category_id')
        if not title:
            flash("Post title cannot be empty", category="error")
        elif not text:
            flash("Post content cannot be empty", category="error")
        else:
            post = Post(title=title, text=text, author=current_user.id)
            if category_id:
                post.category_id = int(category_id)
            db.session.add(post)
            db.session.commit()
            flash("Post created!", category='success')
            return redirect(url_for('views.home'))
    categories = Category.query.all()  # Query all categories
    return render_template("create_post.html", user=current_user, User=User, categories=categories)



@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    # Get post with specified id
    post = Post.query.filter_by(id=id).first()

    # Check if post exists
    if not post:
        flash("Post does not exist", category='error')
    else:
        # Delete post from the database
        db.session.delete(post)
        # Commit changes to the database
        db.session.commit()
        flash('Post deleted', category="success")

    # Redirect to home page
    return redirect(url_for('views.home'))

@views.route("/posts/<username>")
@login_required
def post(username):
    # Get the user with the specified username
    user = User.query.filter_by(username=username).first()
    # Check if the user exists
    if not user:
        flash("No user with that username exists", category="error")
        return redirect(url_for('views.home'))
    # Get all posts by the user
    posts = user.posts

    user_id = user.id

    # Check if the current user is following the user
    following = Follower.query.filter_by(
        user_id=user.id, follower_id=current_user.id).first()

    # Render the posts template and pass the current user, posts, username, User, following, user_id, and profile_user
    return render_template("posts.html", user=current_user, posts=posts, username=username, User=User, following=following, user_id=user_id, profile_user=user)

@views.route("/create-comment/<post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    text = request.form.get('text')
    if not text:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Comment cannot be empty'}), 400
        flash("Comment can not be empty", category="error")
    else:
        post = Post.query.filter_by(id=post_id).first()
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            if post.author != current_user.id:
                notification = Notification(
                    user_id=post.author,
                    message=f"{current_user.username} commented on your post."
                )
                db.session.add(notification)
            db.session.commit()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'comment': {
                        'id': comment.id,
                        'text': comment.text,
                        'username': comment.user.username,
                        'date': comment.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                        'can_delete': current_user.id == comment.author or current_user.id == post.author
                    }
                })
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Post does not exist'}), 404
            flash("Post does not exist", category="error")
    return redirect(url_for('views.home'))

@views.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    if not comment:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Comment does not exist'}), 404
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'You do not have permission to delete this comment'}), 403
        flash('You do not have permission to delete this comment.', category='error')
    else:
        db.session.delete(comment)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': true})
    return redirect(url_for('views.home'))

@views.route("/like-post/<post_id>", methods=["GET"])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(
        author=current_user.id, post_id=post_id).first()
    if not post:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Post does not exist'}), 404
        flash('Post does not exist', category='error')
        return redirect(url_for('views.home'))
    elif like:
        db.session.delete(like)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'liked': False, 'likes': len(post.likes)})
    else:
        like = Like(author=current_user.id, post_id=post_id)
        db.session.add(like)
        if post.author != current_user.id:
            notification = Notification(
                user_id=post.author,
                message=f"{current_user.username} liked your post."
            )
            db.session.add(notification)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'liked': True, 'likes': len(post.likes)})
    return redirect(url_for('views.home'))


@views.route("/follow_unfollow/<username>", methods=["POST"])
@login_required
def follow_unfollow(username):
    # Get the user to follow/unfollow
    user_to_follow = User.query.filter_by(username=username).first()

    # Check if the user exists
    if not user_to_follow:
        flash("User does not exist", category="error")
        return redirect(url_for("views.home"))
    # Check if user tries to follow themselves
    if user_to_follow.id == current_user.id:
        flash("You cannot follow yourself", category="error")
        return redirect(url_for("views.home"))

    # Check if the current user is already following the user
    following = Follower.query.filter_by(
        user_id=user_to_follow.id, follower_id=current_user.id).first()

    try:
        if following:
            # If the current user is already following the user, unfollow them
            db.session.delete(following)
            db.session.commit()
            flash(
                f"You have unfollowed {user_to_follow.username}", category="success")
        else:
            # If the current user is not already following the user, follow them
            follow = Follower(user_id=user_to_follow.id,
                              follower_id=current_user.id)
            db.session.add(follow)
            # Create a notification for the user being followed
            if user_to_follow.id != current_user.id:
                notification = Notification(
                    user_id=user_to_follow.id,
                    message=f"{current_user.username} started following you."
                )
                db.session.add(notification)
            db.session.commit()
            flash(
                f"You are now following {user_to_follow.username}", category="success")
    except Exception as e:
        flash("An error occurred while following the user", category="error")
        # You may want to log the exception for debugging purposes
        raise e
    return redirect(url_for('views.post', username=username))

@views.route("/search", methods=["GET", "POST"])
@login_required
def search():
    if request.method == "POST":
        # Get the search query from the form
        query = request.form.get("query")

        # Search for users with a username that contains the query
        users = User.query.filter(User.username.like(f"%{query}%")).all()

        return render_template("search.html", user=current_user, users=users)
    else:
        # Render the search template when accessed via GET request
        return render_template("search.html", user=current_user)

@views.route("/search-autocomplete", methods=["GET"])
@login_required
def search_autocomplete():
    # Get what the user typed (e.g., "Col")
    query = request.args.get("query", "").strip()
    if query:  # If the user typed something
        # Find usernames that match (case-insensitive, e.g., "col" matches "ColinVIT")
        users = User.query.filter(User.username.ilike(f"%{query}%")).limit(5).all()
        # Make a list of matching usernames (e.g., ["ColinVIT"])
        suggestions = [user.username for user in users]
        # Send the list back as JSON (a format jQuery UI understands)
        return jsonify(suggestions)
    # If the user didn’t type anything, send an empty list
    return jsonify([])

@views.route("/upload-image", methods=['POST'])
@login_required
def upload_image():
    print("DEBUG: Entering upload-image route")  # Debug log
    if 'file' not in request.files:
        print("DEBUG: No file part in request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        print("DEBUG: No selected file")
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        uploads_dir = os.path.join('applicaton', 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, filename)
        print(f"DEBUG: Saving file to {file_path}")
        file.save(file_path)
        image_url = url_for('static', filename='uploads/' + filename)
        print(f"DEBUG: Returning image URL: {image_url}")
        return jsonify({'location': image_url})
    print("DEBUG: File upload failed")
    return jsonify({'error': 'File upload failed'}), 500

@views.route("/edit/<id>", methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get(id)
    if not post or current_user.id != post.author:
        flash("Post does not exist or you do not have permission to edit it",
              category="error")
        return redirect(url_for('views.home'))
    if request.method == "GET":
        return render_template("edit.html", user=current_user, post=post)
    if request.method == "POST":
        title = request.form.get('title')  # Get title
        text = request.form.get('text')
        if not title:
            flash("Post title cannot be empty", category="error")
        elif not text:
            flash("Post content cannot be empty", category="error")
        else:
            post.title = title  # Update title
            post.text = text
            db.session.commit()
            flash("Post updated!", category='success')
            return redirect(url_for('views.home'))

from prometheus_client import Counter

POST_SHARES_TOTAL = Counter('bloglite_post_shares_total', 'Total number of post shares', registry=registry)


@views.route("/share-post/<post_id>", methods=['POST'])
@login_required
def share_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post does not exist'}), 404

    data = request.get_json()
    username = data.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    recipient = User.query.filter_by(username=username).first()
    if not recipient:
        return jsonify({'error': 'User does not exist'}), 404
    if recipient.id == current_user.id:
        return jsonify({'error': 'You cannot share with yourself'}), 400

    # Increment the counter
    POST_SHARES_TOTAL.inc()

    notification = Notification(
        user_id=recipient.id,
        message=f"{current_user.username} shared a post with you: <a href='{url_for('views.view_post', id=post.id)}'>{post.title}</a>"
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'success': True})

@views.route("/notifications")
@login_required
def notifications():
    # Get the current user's notifications, ordered by most recent
    notifications = current_user.notifications.order_by(Notification.date_created.desc()).all()
    return render_template("notifications.html", user=current_user, notifications=notifications)

@views.route("/clear-notifications", methods=["POST"])
@login_required
def clear_notifications():
    # Delete all notifications for the current user
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("All notifications cleared!", category="success")
    return redirect(url_for('views.notifications'))

@views.route('/user_engagement/<int:user_id>')
def user_engagement(user_id):
    # Retrieve the user engagement data from the API
    user_engagement = requests.get(
        f'http://localhost:5000/api/user_engagement/{user_id}').json()
    nested_dict = user_engagement['user_engagement']
    # Render the user engagement template and pass the data to it
    return render_template('user_engagement.html', user_engagement=nested_dict, user=current_user)

@views.route("/post/<id>")
@login_required
def view_post(id):
    post = Post.query.get(id)
    if not post:
        flash("Post does not exist", category="error")
        return redirect(url_for('views.home'))
    return render_template("view_post.html", user=current_user, post=post, User=User)

