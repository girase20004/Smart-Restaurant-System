from datetime import datetime
import logging

from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from models import ORDER_STATUSES, Order, OrderItem, db

chef_bp = Blueprint("chef", __name__)
logger = logging.getLogger(__name__)

ACTIVE_ORDER_STATUSES = ("NEW", "ACCEPTED", "COOKING", "READY")
STATUS_TRANSITIONS = {
    "NEW": "ACCEPTED",
    "ACCEPTED": "COOKING",
    "COOKING": "READY",
    "READY": "SERVED",
}
STATUS_BUTTON_LABELS = {
    "NEW": "Accept Order",
    "ACCEPTED": "Start Cooking",
    "COOKING": "Mark Ready",
    "READY": "Mark Served",
}


def _order_query():
    return (
        Order.query.options(
            joinedload(Order.table),
            joinedload(Order.items).joinedload(OrderItem.menu_item),
        )
        .order_by(Order.created_at.asc(), Order.id.asc())
    )


def _normalise_status(status):
    return (status or "").strip().upper()


def _request_status_payload():
    payload = request.get_json(silent=True) or {}
    order_id = payload.get("order_id") or request.form.get("order_id")
    status = _normalise_status(payload.get("status") or request.form.get("status"))
    return order_id, status


def _set_order_status(order, new_status):
    if new_status not in ORDER_STATUSES:
        return {"error": "Invalid status", "allowed_statuses": list(ORDER_STATUSES)}, 400

    current_status = order.status
    expected_next = STATUS_TRANSITIONS.get(current_status)

    if new_status == current_status:
        return {"order": order.to_chef_dict(), "message": "Order already has this status"}, 200

    if new_status != expected_next and new_status != "CANCELLED":
        return {
            "error": "Invalid status transition",
            "current_status": current_status,
            "expected_next_status": expected_next,
        }, 409

    order.status = new_status
    order.updated_at = datetime.utcnow()
    db.session.commit()
    logger.info("Kitchen notification: order %s moved from %s to %s", order.id, current_status, new_status)
    return {"order": order.to_chef_dict(), "message": "Order status updated"}, 200


@chef_bp.get("/chef/dashboard")
def dashboard():
    orders = _order_query().filter(Order.status.in_(ACTIVE_ORDER_STATUSES)).all()
    return render_template(
        "chef/dashboard.html",
        orders=orders,
        status_transitions=STATUS_TRANSITIONS,
        status_button_labels=STATUS_BUTTON_LABELS,
    )


@chef_bp.get("/chef/orders")
def orders_page():
    selected_status = _normalise_status(request.args.get("status", "ALL")) or "ALL"
    query = _order_query().filter(Order.status.in_(ACTIVE_ORDER_STATUSES))

    if selected_status != "ALL":
        if selected_status not in ACTIVE_ORDER_STATUSES:
            return render_template(
                "chef/orders.html",
                orders=[],
                selected_status=selected_status,
                statuses=ACTIVE_ORDER_STATUSES,
                status_transitions=STATUS_TRANSITIONS,
                status_button_labels=STATUS_BUTTON_LABELS,
                error="Invalid active status filter.",
            ), 400
        query = query.filter(Order.status == selected_status)

    return render_template(
        "chef/orders.html",
        orders=query.all(),
        selected_status=selected_status,
        statuses=ACTIVE_ORDER_STATUSES,
        status_transitions=STATUS_TRANSITIONS,
        status_button_labels=STATUS_BUTTON_LABELS,
    )


@chef_bp.post("/chef/update_order_status")
def update_order_status_page():
    order_id, new_status = _request_status_payload()
    order = db.session.get(Order, int(order_id)) if str(order_id or "").isdigit() else None
    if order is None:
        if request.is_json:
            return jsonify({"error": "Order not found"}), 404
        return redirect(url_for("chef.orders_page"))

    body, status_code = _set_order_status(order, new_status)
    if request.is_json:
        return jsonify(body), status_code
    return redirect(request.referrer or url_for("chef.orders_page"))


@chef_bp.get("/api/chef/orders")
def api_orders():
    status = _normalise_status(request.args.get("status", "ACTIVE")) or "ACTIVE"
    query = _order_query()

    if status == "ACTIVE":
        query = query.filter(Order.status.in_(ACTIVE_ORDER_STATUSES))
    elif status != "ALL":
        if status not in ORDER_STATUSES:
            return jsonify({"error": "Invalid status filter", "allowed_statuses": list(ORDER_STATUSES)}), 400
        query = query.filter(Order.status == status)

    return jsonify({"orders": [order.to_chef_dict() for order in query.all()]})


@chef_bp.post("/api/chef/order/<int:order_id>/status")
def api_update_order_status(order_id):
    payload = request.get_json(silent=True) or {}
    new_status = _normalise_status(payload.get("status"))
    order = db.session.get(Order, order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    body, status_code = _set_order_status(order, new_status)
    return jsonify(body), status_code
