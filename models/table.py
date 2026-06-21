"""Restaurant table model."""

from extensions import db


class RestaurantTable(db.Model):
    """Physical restaurant table linked to a customer QR code."""

    __tablename__ = "restaurant_tables"

    id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    qr_code = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), nullable=False, default="available", index=True)

    orders = db.relationship("Order", back_populates="table", lazy=True)

    def to_dict(self) -> dict:
        """Serialize table fields for API responses."""
        return {
            "id": self.id,
            "table_number": self.table_number,
            "qr_code": self.qr_code,
            "status": self.status,
        }