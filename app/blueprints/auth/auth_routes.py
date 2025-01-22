from flask import Blueprint, redirect, url_for, request, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
import os
from app.models import db, Usuario

auth_bp = Blueprint('auth', __name__)

# Configuración de Google OAuth
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = os.getenv('GOOGLE_DISCOVERY_URL')

# Cliente de OAuth
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Configurar Flask-Login
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

@auth_bp.route('/login')
def login():
    # Obtener la URL de redireccionamiento desde el frontend
    next_url = request.args.get('next_url', '/')  # Redirige a '/' por defecto si no se proporciona


    # Almacenar la URL de redirección en la sesión
    session['next_url'] = next_url


    # Descubrir la URL de autorización de Google
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Construir la URL de autorización
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=url_for('auth.callback', _external=True),
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@auth_bp.route('/auth/callback')
def callback():
    # Obtener el código de autorización de Google
    code = request.args.get("code")

    

    # Obtener la URL de token de Google
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Preparar la solicitud para obtener el token
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parsear el token de acceso
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Obtener información del usuario
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]

        # Verificar si el usuario ya existe en la base de datos
        user = Usuario.query.filter_by(email=users_email).first()
        if not user:
            # Crear un nuevo usuario si no existe
            user = Usuario(
                nombre=users_name,
                email=users_email
            )
            db.session.add(user)
            db.session.commit()

        # Iniciar sesión del usuario
        login_user(user)
        session['user_id'] = user.id
        next_url = session.pop('next_url', '/')  # Elimina `next_url` de la sesión después de usarlo
        return redirect(next_url)
    else:
        return "Error al autenticar con Google", 400
