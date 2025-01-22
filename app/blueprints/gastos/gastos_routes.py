from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, Gasto
from datetime import datetime

gastos_bp = Blueprint('gastos', __name__)

# Crear un nuevo gasto

@gastos_bp.route('/gastos', methods=['OPTIONS'])
def handle_options():
    if request.method == "OPTIONS":
        return 'ok',200
    


@gastos_bp.route('/gastos', methods=['POST'])
@login_required
def crear_gasto():
    data = request.json

    # Validar y convertir fecha
    fecha_gasto = data.get('fecha_gasto')
    if fecha_gasto:
        try:
            # Convertir la fecha recibida a un objeto datetime
            fecha_gasto = datetime.strptime(fecha_gasto, '%Y-%m-%d')
        except ValueError:
            return jsonify({"mensaje": "Formato de fecha inválido. Use 'YYYY-MM-DD'"}), 400

    # Crear el nuevo gasto
    nuevo_gasto = Gasto(
        usuario_id=current_user.id,
        nombre=data.get('nombre'),
        monto=data.get('monto'),
        categoria=data.get('categoria'),
        fecha_gasto=fecha_gasto  # Ahora es un objeto datetime
    )
    db.session.add(nuevo_gasto)
    db.session.commit()

    return jsonify({
        "mensaje": "Gasto creado exitosamente",
        "gasto": {
            "id": nuevo_gasto.id,
            "nombre": nuevo_gasto.nombre,
            "monto": nuevo_gasto.monto,
            "categoria": nuevo_gasto.categoria,
            "fecha_gasto": nuevo_gasto.fecha_gasto
        }
    }), 201


# Listar todos los gastos del usuario
@gastos_bp.route('/gastos', methods=['GET'])
@login_required
def listar_gastos():
    gastos = Gasto.query.filter_by(usuario_id=current_user.id).all()
    return jsonify([{
        "id": gasto.id,
        "nombre": gasto.nombre,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
        "fecha_gasto": gasto.fecha_gasto
    } for gasto in gastos])

# Obtener un gasto específico
@gastos_bp.route('/gastos/<int:id>', methods=['GET'])
@login_required
def obtener_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    if gasto.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    return jsonify({
        "id": gasto.id,
        "nombre": gasto.nombre,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
        "fecha_gasto": gasto.fecha_gasto
    })

# Actualizar un gasto existente
@gastos_bp.route('/gastos/<int:id>', methods=['PUT'])
@login_required
def actualizar_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    if gasto.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    data = request.json
    gasto.nombre = data.get('nombre', gasto.nombre)
    gasto.monto = data.get('monto', gasto.monto)
    gasto.categoria = data.get('categoria', gasto.categoria)
    gasto.fecha_gasto = data.get('fecha_gasto', gasto.fecha_gasto)
    db.session.commit()
    return jsonify({"mensaje": "Gasto actualizado exitosamente", "gasto": {
        "id": gasto.id,
        "nombre": gasto.nombre,
        "monto": gasto.monto,
        "categoria": gasto.categoria,
        "fecha_gasto": gasto.fecha_gasto
    }})

# Eliminar un gasto
@gastos_bp.route('/gastos/<int:id>', methods=['DELETE'])
@login_required
def eliminar_gasto(id):
    gasto = Gasto.query.get_or_404(id)
    if gasto.usuario_id != current_user.id:
        return jsonify({"mensaje": "Acceso denegado"}), 403
    db.session.delete(gasto)
    db.session.commit()
    return jsonify({"mensaje": "Gasto eliminado exitosamente"})
