from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, bcrypt, jwt

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    # Enable CORS for frontend API calls
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    # Register blueprints with proper prefixes
    from app.routes.auth import auth_bp
    from app.routes.health import health_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(health_bp, url_prefix='/api')
    
    # Register members blueprint
    from app.routes.members import members_bp
    app.register_blueprint(members_bp, url_prefix='/api/members')
    
    # Register membership plans blueprint
    from app.routes.membership_plans import membership_plans_bp
    app.register_blueprint(membership_plans_bp, url_prefix='/api/membership-plans')
    
    # Register payments blueprint
    from app.routes.payments import payments_bp
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    
    # Register attendance blueprint
    from app.routes.attendance import attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    
    # Register analytics blueprint
    from app.routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # Register gym owner reports blueprint
    from app.routes.reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    
    # Register gym logo blueprint
    from app.routes.gym_logo import gym_logo_bp
    app.register_blueprint(gym_logo_bp, url_prefix='/api/gym/logo')
    
    # Register gym settings blueprint
    from app.routes.gym_settings import gym_settings_bp
    app.register_blueprint(gym_settings_bp, url_prefix='/api/gym')
    
    # Register gym QR blueprint
    from app.routes.gym_qr import gym_qr_bp
    app.register_blueprint(gym_qr_bp, url_prefix='/api/gym/qr')
    
    # Register admin blueprint (Super Admin functionality)
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    # Create DB tables automatically on boot if DB is connected
    with app.app_context():
        try:
            db.create_all()
            print("Database tables verified/created successfully.")
        except Exception as e:
            print(f"Database connection error or table creation skipped: {str(e)}")
            print("Please ensure your MySQL server is running and configured correctly in .env.")
            
    return app
