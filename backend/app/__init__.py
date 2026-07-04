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
    
    # Create DB tables automatically on boot if DB is connected
    with app.app_context():
        try:
            db.create_all()
            print("Database tables verified/created successfully.")
        except Exception as e:
            print(f"Database connection error or table creation skipped: {str(e)}")
            print("Please ensure your MySQL server is running and configured correctly in .env.")
            
    return app
