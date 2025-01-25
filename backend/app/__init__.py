import warnings
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate
from config import Config
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

# Initialize extensions globally, to be used inside create_app()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()  # Initialize Migrate
warnings.filterwarnings("ignore", category=UserWarning)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Initialize extensions 
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Initialize migrate with app and db

    # Import and register blueprints (routes) here to avoid circular import
    from .dashboard import dashboard_routes
    app.register_blueprint(dashboard_routes, url_prefix='/')

    # Register authentication routes 
    from .authentication import bp as auth_bp, main
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main, url_prefix='/')

    from .record import record_bp
    app.register_blueprint(record_bp, url_prefix='/record')

    from .account import account_bp
    app.register_blueprint(account_bp, url_prefix='/account')

    # Register the categories blueprint
    from .categories import categories_bp
    app.register_blueprint(categories_bp)

    from .budget import budgets_bp
    app.register_blueprint(budgets_bp)

    app.config['DEBUG'] = True  # Enable debug mode

    return app
