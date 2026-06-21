from datetime import datetime
from decimal import Decimal

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Enum


db = SQLAlchemy()

USER_ROLES = ("admin", "chef", "waiter")
TABLE_STATUSES = ("available", "occupied", "reserved", "inactive")
ORDER_STATUSES = ("NEW", "ACCEPTED", "COOKING", "READY", "SERVED", "CANCELLED")
VEG_NONVEG = ("veg", "nonveg", "egg")


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(Enum(*USER_ROLES, name="user_role"), nullable=False, default="waiter")

    def __repr__(self):
        return f"<User {self.email}>"


class RestaurantTable(db.Model):
    __tablename__ = "restaurant_tables"

    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    qr_code = db.Column(db.String(500), nullable=True)
    status = db.Column(Enum(*TABLE_STATUSES, name="table_status"), nullable=False, default="available")

    orders = db.relationship("Order", back_populates="table", lazy=True)

    def __repr__(self):
        return f"<RestaurantTable {self.table_number}>"


class Menu(db.Model):
    __tablename__ = "menu"

    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(160), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    image = db.Column(db.String(500), nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)
    veg_nonveg = db.Column(Enum(*VEG_NONVEG, name="veg_nonveg"), nullable=False, default="veg")
    availability = db.Column(db.Boolean, nullable=False, default=True, index=True)

    order_items = db.relationship("OrderItem", back_populates="menu", lazy=True)

    __table_args__ = (CheckConstraint("price >= 0", name="ck_menu_price_non_negative"),)

    def __repr__(self):
        return f"<Menu {self.dish_name}>"


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("restaurant_tables.id"), nullable=False, index=True)
    status = db.Column(Enum(*ORDER_STATUSES, name="order_status"), nullable=False, default="NEW", index=True)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    table = db.relationship("RestaurantTable", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy=True)

    __table_args__ = (CheckConstraint("total >= 0", name="ck_order_total_non_negative"),)

    def recalculate_total(self):
        self.total = sum((item.line_total for item in self.items), Decimal("0.00"))
        return self.total

    def to_chef_dict(self):
        return {
            "id": self.id,
            "table_id": self.table_id,
            "table_number": self.table.table_number if self.table else None,
            "status": self.status,
            "total": float(self.total or 0),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "items": [item.to_dict() for item in self.items],
        }

    def __repr__(self):
        return f"<Order {self.id} {self.status}>"


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)

    order = db.relationship("Order", back_populates="items")
    menu = db.relationship("Menu", back_populates="order_items")

    __table_args__ = (CheckConstraint("quantity > 0", name="ck_order_item_quantity_positive"),)

    @property
    def line_total(self):
        price = self.menu.price if self.menu else Decimal("0.00")
        return Decimal(price) * self.quantity

    def to_dict(self):
        return {
            "id": self.id,
            "menu_id": self.menu_id,
            "dish_name": self.menu.dish_name if self.menu else "Unknown item",
            "quantity": self.quantity,
            "notes": self.notes or "",
            "price": float(self.menu.price) if self.menu else 0,
            "line_total": float(self.line_total),
        }

    def __repr__(self):
        return f"<OrderItem order={self.order_id} menu={self.menu_id}>"