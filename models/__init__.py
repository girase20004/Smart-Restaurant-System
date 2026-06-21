"""Database models package."""

from extensions import db

from models.user import User
from models.table import RestaurantTable
from models.menu import Menu
from models.order import Order
from models.order_item import OrderItem

# Chef Order Workflow Status
ORDER_STATUSES = [
    "NEW",
    "ACCEPTED",
    "COOKING",
    "READY",
    "SERVED"
]

__all__ = [
    "db",
    "User",
    "RestaurantTable",
    "Menu",
    "Order",
    "OrderItem",
    "ORDER_STATUSES"
]