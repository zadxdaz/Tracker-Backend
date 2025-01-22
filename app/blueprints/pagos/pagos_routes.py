from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Pago, Servicio

pagos_bp = Blueprint('pagos', __name__)

# Crear un nuevo pago
@pagos_bp.route('/pagos', methods=['POST'])
@login_required
def crear_pago():
    data = request.json

    # Validar los datos requeridos
    if not data.get('servicio_id') or not data.get('monto'):
        return jsonify({"mensaje": "El servicio_id y el monto son obligatorios"}), 400

    # Verificar que el servicio pertenece al usuario autenticado
    servicio = Servicio.query.get_or_404(data['servicio_id'])
    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado: no puedes agregar pagos a este servicio"}), 403

    # Crear el nuevo pago
    nuevo_pago = Pago(
        servicio_id=servicio.id,
        monto=data['monto'],
        estado=data.get('estado', 'pendiente'),  # Estado por defecto
        fecha_pago=data.get('fecha_pago')  # Puede ser None o un valor válido
    )
    db.session.add(nuevo_pago)
    db.session.commit()

    return jsonify({"mensaje": "Pago creado exitosamente", "pago": {
        "id": nuevo_pago.id,
        "servicio_id": nuevo_pago.servicio_id,
        "monto": nuevo_pago.monto,
        "estado": nuevo_pago.estado,
        "fecha_pago": nuevo_pago.fecha_pago
    }}), 201

# Listar todos los pagos de un servicio
@pagos_bp.route('/pagos/<int:servicio_id>', methods=['GET'])
@login_required
def listar_pagos(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    pagos = Pago.query.filter_by(servicio_id=servicio_id).all()
    return jsonify([{
        "id": pago.id,
        "monto": pago.monto,
        "estado": pago.estado,
        "fecha_pago": pago.fecha_pago
    } for pago in pagos])

# Obtener un pago específico
@pagos_bp.route('/pagos/detalle/<int:id>', methods=['GET'])
@login_required
def obtener_pago(id):
    pago = Pago.query.get_or_404(id)
    servicio = Servicio.query.get_or_404(pago.servicio_id)

    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    return jsonify({
        "id": pago.id,
        "servicio_id": pago.servicio_id,
        "monto": pago.monto,
        "estado": pago.estado,
        "fecha_pago": pago.fecha_pago
    })

# Actualizar un pago existente
@pagos_bp.route('/pagos/<int:id>', methods=['PUT'])
@login_required
def actualizar_pago(id):
    pago = Pago.query.get_or_404(id)
    servicio = Servicio.query.get_or_404(pago.servicio_id)

    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    data = request.json
    pago.monto = data.get('monto', pago.monto)
    pago.estado = data.get('estado', pago.estado)
    pago.fecha_pago = data.get('fecha_pago', pago.fecha_pago)
    db.session.commit()

    return jsonify({"mensaje": "Pago actualizado exitosamente", "pago": {
        "id": pago.id,
        "servicio_id": pago.servicio_id,
        "monto": pago.monto,
        "estado": pago.estado,
        "fecha_pago": pago.fecha_pago
    }})

# Eliminar un pago
@pagos_bp.route('/pagos/<int:id>', methods=['DELETE'])
@login_required
def eliminar_pago(id):
    pago = Pago.query.get_or_404(id)
    servicio = Servicio.query.get_or_404(pago.servicio_id)

    if servicio.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403

    db.session.delete(pago)
    db.session.commit()
    return jsonify({"mensaje": "Pago eliminado exitosamente"})
