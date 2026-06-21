"""Menu API routes."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models.menu import Menu


menu_bp = Blueprint("menu", __name__, url_prefix="/api/menu")


@menu_bp.post("")
@jwt_required()
def add_menu_item():
    """Add a dish to the restaurant menu."""
    data = request.get_json(silent=True) or {}
    required = ["dish_name", "price", "category", "veg_nonveg"]
    if any(data.get(field) in (None, "") for field in required):
        return jsonify({"message": "dish_name, price, category, and veg_nonveg are required"}), 400

    item = Menu(
        dish_name=data["dish_name"].strip(),
        price=data["price"],
        category=data["category"].strip(),
        image=data.get("image"),
        ingredients=data.get("ingredients"),
        prep_time=data.get("prep_time"),
        veg_nonveg=data["veg_nonveg"].strip().lower(),
        availability=bool(data.get("availability", True)),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"message": "menu item added", "menu_item": item.to_dict()}), 201


@menu_bp.get("")
def get_menu():
    """Return menu items, optionally filtered by category and availability."""
    query = Menu.query
    category = request.args.get("category")
    available = request.args.get("available")
    if category:
        query = query.filter(Menu.category.ilike(category))
    if available is not None:
        query = query.filter_by(availability=available.lower() == "true")
    items = query.order_by(Menu.category.asc(), Menu.dish_name.asc()).all()
    return jsonify({"menu": [item.to_dict() for item in items]}), 200