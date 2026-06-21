"""Customer-facing QR ordering routes and APIs."""

from decimal import Decimal

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import func

from extensions import db
from models.menu import Menu
from models.order import Order
from models.order_item import OrderItem
from models.table import RestaurantTable


customer_bp = Blueprint("customer", __name__, url_prefix="/customer")
GST_RATE = Decimal("0.05")


def _get_table_or_404(table_number: str) -> RestaurantTable:
    """Return a table from a QR table number or raise Flask's 404 response."""
    return RestaurantTable.query.filter_by(table_number=table_number).first_or_404()


def _active_order_for_table(table_id: int) -> Order | None:
    """Return the latest open order for a table so new items merge into the bill."""
    return (
        Order.query.filter(Order.table_id == table_id, Order.status.in_(["pending", "preparing", "served"]))
        .order_by(Order.created_at.desc())
        .first()
    )


def _running_bill(order: Order | None) -> dict:
    """Build subtotal, GST, and total amounts for the customer's running bill."""
    if not order:
        return {"items": [], "subtotal": 0, "gst": 0, "total": 0}

    subtotal = sum((Decimal(item.line_total) for item in order.items), Decimal("0"))
    gst = (subtotal * GST_RATE).quantize(Decimal("0.01"))
    total = (subtotal + gst).quantize(Decimal("0.01"))
    return {
        "items": [item.to_dict() for item in order.items],
        "subtotal": float(subtotal),
        "gst": float(gst),
        "total": float(total),
    }


@customer_bp.get("/<table_number>")
def home(table_number: str):
    """Render the no-login customer home page after scanning a table QR code."""
    table = _get_table_or_404(table_number)
    categories = [row[0] for row in db.session.query(Menu.category).filter_by(availability=True).distinct().all()]
    specials = Menu.query.filter_by(availability=True, todays_special=True).limit(6).all()
    best_sellers = Menu.query.filter_by(availability=True, best_seller=True).limit(6).all()
    return render_template(
        "customer/home.html",
        table=table,
        categories=categories,
        specials=specials,
        best_sellers=best_sellers,
    )


@customer_bp.get("/<table_number>/menu")
def menu(table_number: str):
    """Render the customer menu with search/category filtering support."""
    table = _get_table_or_404(table_number)
    search = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    query = Menu.query
    if search:
        query = query.filter(Menu.dish_name.ilike(f"%{search}%"))
    if category:
        query = query.filter(func.lower(Menu.category) == category.lower())
    items = query.order_by(Menu.category.asc(), Menu.dish_name.asc()).all()
    categories = [row[0] for row in db.session.query(Menu.category).distinct().all()]
    return render_template("customer/menu.html", table=table, menu_items=items, categories=categories, search=search, category=category)


@customer_bp.get("/<table_number>/dish/<int:menu_id>")
def dish_details(table_number: str, menu_id: int):
    """Render detailed dish information and an add-to-cart action."""
    table = _get_table_or_404(table_number)
    item = Menu.query.get_or_404(menu_id)
    return render_template("customer/dish_details.html", table=table, item=item)


@customer_bp.get("/<table_number>/cart")
def cart(table_number: str):
    """Render the browser-side cart page for quantity and note editing."""
    table = _get_table_or_404(table_number)
    return render_template("customer/cart.html", table=table)


@customer_bp.get("/<table_number>/bill")
def get_running_bill(table_number: str):
    """Return the current running bill for a table."""
    table = _get_table_or_404(table_number)
    order = _active_order_for_table(table.id)
    return jsonify({"table_number": table.table_number, "bill": _running_bill(order)}), 200


@customer_bp.post("/place_order")
def place_order():
    """Create or merge customer cart items into the table's current running bill."""
    data = request.get_json(silent=True) or {}
    table_number = str(data.get("table_number", "")).strip()
    items = data.get("items") or []
    if not table_number or not items:
        return jsonify({"message": "table_number and items are required"}), 400

    table = _get_table_or_404(table_number)
    order = _active_order_for_table(table.id)
    if not order:
        order = Order(table_id=table.id, status="pending", total=0)
        db.session.add(order)
        db.session.flush()

    for item_payload in items:
        menu_id = item_payload.get("menu_id")
        quantity = int(item_payload.get("quantity", 1))
        if quantity < 1:
            return jsonify({"message": "quantity must be at least 1"}), 400
        menu_item = Menu.query.filter_by(id=menu_id, availability=True).first()
        if not menu_item:
            return jsonify({"message": f"menu item {menu_id} is unavailable"}), 400

        notes = (item_payload.get("notes") or "").strip()
        line_total = Decimal(str(menu_item.price)) * quantity
        existing = next((line for line in order.items if line.menu_id == menu_item.id and (line.notes or "") == notes), None)
        if existing:
            existing.quantity += quantity
            existing.line_total = Decimal(str(existing.line_total)) + line_total
        else:
            db.session.add(OrderItem(order_id=order.id, menu_id=menu_item.id, quantity=quantity, notes=notes, line_total=line_total))

    table.status = "occupied"
    db.session.flush()
    bill = _running_bill(order)
    order.total = Decimal(str(bill["total"]))
    db.session.commit()
    return jsonify({"message": "order placed", "order_id": order.id, "bill": bill}), 201