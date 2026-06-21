"""Order API routes."""

from flask import Blueprint, jsonify, request

from extensions import db
from models.order import Order
from models.table import RestaurantTable


order_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


@order_bp.post("")
def create_order():
    """Create a Phase 1 order with table and total information."""
    data = request.get_json(silent=True) or {}
    table_id = data.get("table_id")
    total = data.get("total", 0)
    if not table_id:
        return jsonify({"message": "table_id is required"}), 400

    table = RestaurantTable.query.get(table_id)
    if not table:
        return jsonify({"message": "table not found"}), 404

    order = Order(table_id=table.id, status=data.get("status", "pending"), total=total)
    table.status = "occupied"
    db.session.add(order)
    db.session.commit()
    return jsonify({"message": "order created", "order": order.to_dict()}), 201