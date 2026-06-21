"""Order line-item model for customer QR ordering."""

from extensions import db


class OrderItem(db.Model):
    """A menu item, quantity, notes, and amount merged into a table order."""

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, index=True)
    menu_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    line_total = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    order = db.relationship("Order", back_populates="items")
    menu_item = db.relationship("Menu", back_populates="order_items")

    def to_dict(self) -> dict:
        """Serialize order line-item fields for running bill responses."""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "menu_id": self.menu_id,
            "dish_name": self.menu_item.dish_name if self.menu_item else None,
            "unit_price": float(self.menu_item.price) if self.menu_item else 0,
            "quantity": self.quantity,
            "notes": self.notes,
            "line_total": float(self.line_total),
        }