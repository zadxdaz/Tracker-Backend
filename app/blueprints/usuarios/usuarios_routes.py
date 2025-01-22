from flask import Blueprint, request, jsonify
from app.models import db, Usuario

usuarios_bp = Blueprint('usuarios', __name__)

@usuarios_bp.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    nuevo_usuario = Usuario(
        nombre=data['nombre'],
        email=data['email'],
        contraseña=data['contraseña']
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario creado exitosamente"}), 201

from flask_login import login_required, current_user

@usuarios_bp.route('/usuarios/me', methods=['GET'])
@login_required
def obtener_usuario():
    """Devuelve la información del usuario autenticado."""
    return jsonify({
        "id": current_user.id,
        "nombre": current_user.nombre,
        "email": current_user.email,
        "fecha_creacion": current_user.fecha_creacion
    })


