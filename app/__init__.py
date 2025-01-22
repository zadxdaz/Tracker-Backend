from flask import Flask
from app.models import db
from app.blueprints.usuarios import usuarios_bp
from app.blueprints.servicios import servicios_bp
from app.blueprints.pagos import pagos_bp
from app.blueprints.gastos import gastos_bp
from flask_login import LoginManager
from app.blueprints.auth.auth_routes import auth_bp
from app.models import db, Usuario
from flask_login import LoginManager
from flask_cors import CORS
login_manager = LoginManager()
import os
from dotenv import load_dotenv
load_dotenv()
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = "clave_secreta"

    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_DISCOVERY_URL'] = os.getenv('GOOGLE_DISCOVERY_URL')

    db.init_app(app)
    login_manager.init_app(app)

    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(usuarios_bp, url_prefix='/api')
    app.register_blueprint(servicios_bp, url_prefix='/api')
    app.register_blueprint(pagos_bp, url_prefix='/api')
    app.register_blueprint(gastos_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

    return app
