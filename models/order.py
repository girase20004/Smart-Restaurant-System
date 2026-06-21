"""Order model."""

from datetime import datetime, timezone

from extensions import db


class Order(db.Model):
    """Customer order associated with a restaurant table and running bill."""

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    table_id = db.Column(db.Integer, db.ForeignKey("restaurant_tables.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="pending", index=True)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    table = db.relationship("RestaurantTable", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan", lazy=True)

    def to_dict(self, include_items: bool = False) -> dict:
        """Serialize order fields for API responses."""
        data = {
            "id": self.id,
            "table_id": self.table_id,
            "status": self.status,
            "total": float(self.total),
            "created_at": self.created_at.isoformat(),
        }
        if include_items:
            data["items"] = [item.to_dict() for item in self.items]
        return data