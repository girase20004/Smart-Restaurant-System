"""Restaurant table and QR code API routes."""

import os

import qrcode
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.table import RestaurantTable


table_bp = Blueprint("tables", __name__, url_prefix="/api/tables")


def _generate_qr_for_table(table: RestaurantTable) -> str:
    """Generate a QR image for a table and return the saved relative path."""
    qr_folder = current_app.config["QR_CODE_FOLDER"]
    os.makedirs(qr_folder, exist_ok=True)
    customer_url = f"{current_app.config['CUSTOMER_URL_BASE']}/customer/{table.table_number}"
    filename = f"table_{table.table_number}.png"
    relative_path = os.path.join(qr_folder, filename)
    image = qrcode.make(customer_url)
    image.save(relative_path)
    return relative_path


@table_bp.post("")
@jwt_required()
def create_table():
    """Create a restaurant table and immediately generate its customer QR code."""
    data = request.get_json(silent=True) or {}
    table_number = str(data.get("table_number", "")).strip()
    if not table_number:
        return jsonify({"message": "table_number is required"}), 400

    if RestaurantTable.query.filter_by(table_number=table_number).first():
        return jsonify({"message": "table already exists"}), 409

    table = RestaurantTable(table_number=table_number, status=data.get("status", "available"))
    db.session.add(table)
    db.session.flush()
    table.qr_code = _generate_qr_for_table(table)
    db.session.commit()
    return jsonify({"message": "table created", "table": table.to_dict()}), 201


@table_bp.post("/<int:table_id>/qr")
@jwt_required()
def generate_qr(table_id: int):
    """Regenerate a QR image for an existing table."""
    table = RestaurantTable.query.get_or_404(table_id)
    table.qr_code = _generate_qr_for_table(table)
    db.session.commit()
    return jsonify({"message": "qr code generated", "table": table.to_dict()}), 200