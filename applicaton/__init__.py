# Import necessary modules and libraries
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
from os import path, getenv
from flask_login import LoginManager
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry, REGISTRY
import time

# Create a SQLAlchemy object for database management
db = SQLAlchemy()

# Define Prometheus metrics globally
registry = CollectorRegistry()
HTTP_REQUESTS_TOTAL = Counter('http_requests_total', 'Total HTTP requests', ['endpoint'], registry=registry)
HTTP_REQUEST_DURATION_SECONDS = Histogram('http_request_duration_seconds', 'HTTP request duration', ['endpoint'], registry=registry)
APP_INFO = Counter('app_info', 'Application info', ['version'], registry=registry)
APP_INFO.labels(version='1.0.0').inc()

def create_app():
    # Create a Flask app instance
    app = Flask(__name__)

    # Middleware to track requests
    @app.before_request
    def before_request():
        request.start_time = time.time()
        endpoint = request.endpoint if request.endpoint else 'unknown'
        HTTP_REQUESTS_TOTAL.labels(endpoint=endpoint).inc()

    @app.after_request
    def after_request(response):
        endpoint = request.endpoint if request.endpoint else 'unknown'
        duration = time.time() - request.start_time
        HTTP_REQUEST_DURATION_SECONDS.labels(endpoint=endpoint).observe(duration)
        return response

    # Expose metrics endpoint
    @app.route('/prometheus/metrics')
    def metrics():
        return Response(generate_latest(registry), mimetype='text/plain')

    # Set the secret key for the app
    app.config['SECRET_KEY'] = "perfetch"
    app.config['SQLALCHEMY_DATABASE_URI'] = getenv('DATABASE_URL', 'sqlite:///database.db').replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the SQLAlchemy object with the app
    db.init_app(app)

    # Import and initialize the API module
    from .resources import api
    api.init_app(app)

    # Import and register the views blueprint
    from .views import views
    app.register_blueprint(views, url_prefix="/")

    # Import and register the authentication blueprint
    from .authentication import authentication
    app.register_blueprint(authentication, url_prefix="/")

    # Import the models
    from .models import User, Post, Comment, Like, Follower

    # Create the database if it does not exist
    with app.app_context():
        if not path.exists("database.db"):
            db.create_all()
            print("Created database!")

    # Initialize the LoginManager
    login_manager = LoginManager()
    login_manager.login_view = "authentication.log_in"
    login_manager.init_app(app)

    # Define a user loader function for the LoginManager
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # Return the app instance
    return app