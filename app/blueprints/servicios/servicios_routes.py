from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Servicio

servicios_bp = Blueprint('servicios', __name__)

@servicios_bp.route('/servicios', methods=['OPTIONS'])
def handle_options():
    if request.method == "OPTIONS":
        return 'ok',200
    
# Crear un nuevo servicio
@servicios_bp.route('/servicios/crear', methods=['POST'])
@login_required
def crear_servicio():
    data = request.json

    

    # Validar los datos requeridos
    if not data.get('nombre') or not data.get('costo_mensual'):
        return jsonify({"mensaje": "El nombre y el costo mensual son obligatorios"}), 400

    # Crear el nuevo servicio
    nuevo_servicio = Servicio(
        usuario_id=current_user.id,
        nombre=data.get('nombre'),
        frecuencia=data.get('frecuencia', 'mensual')  # Valor por defecto
    )
    db.session.add(nuevo_servicio)
    db.session.commit()

    return jsonify({"mensaje": "Servicio creado exitosamente", "servicio": {
        "id": nuevo_servicio.id,
        "nombre": nuevo_servicio.nombre,
        "frecuencia": nuevo_servicio.frecuencia,
        "fecha_creacion": nuevo_servicio.fecha_creacion
    }}), 201

# Listar todos los servicios del usuario
@servicios_bp.route('/servicios', methods=['GET'])
@login_required
def listar_servicios():
    servicios = Servicio.query.filter_by(usuario_id=current_user.id).all()
    return jsonify([{
        "id": servicio.id,
        "nombre": servicio.nombre,
        "frecuencia": servicio.frecuencia,
        "fecha_creacion": servicio.fecha_creacion
    } for servicio in servicios])

# Obtener un servicio específico
@servicios_bp.route('/servicios/<int:id>', methods=['GET'])
@login_required
def obtener_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    return jsonify({
        "id": servicio.id,
        "nombre": servicio.nombre,
        "frecuencia": servicio.frecuencia,
        "fecha_creacion": servicio.fecha_creacion
    })

# Actualizar un servicio existente
@servicios_bp.route('/servicios/<int:id>', methods=['PUT'])
@login_required
def actualizar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    data = request.json

    # Actualizar campos
    servicio.nombre = data.get('nombre', servicio.nombre)
    servicio.frecuencia = data.get('frecuencia', servicio.frecuencia)
    db.session.commit()

    return jsonify({"mensaje": "Servicio actualizado exitosamente", "servicio": {
        "id": servicio.id,
        "nombre": servicio.nombre,
        "frecuencia": servicio.frecuencia,
        "fecha_creacion": servicio.fecha_creacion
    }})

# Eliminar un servicio
@servicios_bp.route('/servicios/<int:id>', methods=['DELETE'])
@login_required
def eliminar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    db.session.delete(servicio)
    db.session.commit()
    return jsonify({"mensaje": "Servicio eliminado exitosamente"})
