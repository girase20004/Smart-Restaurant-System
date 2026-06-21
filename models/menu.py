"""Menu item model."""

from extensions import db


class Menu(db.Model):
    """Dish that customers can browse and order from the QR menu."""

    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(160), nullable=False, index=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    image = db.Column(db.String(255), nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    prep_time = db.Column(db.Integer, nullable=True)
    veg_nonveg = db.Column(db.String(20), nullable=False)
    availability = db.Column(db.Boolean, nullable=False, default=True, index=True)
    best_seller = db.Column(db.Boolean, nullable=False, default=False, index=True)
    todays_special = db.Column(db.Boolean, nullable=False, default=False, index=True)
    spice_level = db.Column(db.String(30), nullable=True)
    allergens = db.Column(db.String(255), nullable=True)

    order_items = db.relationship("OrderItem", back_populates="menu_item", lazy=True)

    def to_dict(self) -> dict:
        """Serialize menu item fields for API responses and templates."""
        return {
            "id": self.id,
            "dish_name": self.dish_name,
            "price": float(self.price),
            "category": self.category,
            "image": self.image,
            "ingredients": self.ingredients,
            "prep_time": self.prep_time,
            "veg_nonveg": self.veg_nonveg,
            "availability": self.availability,
            "best_seller": self.best_seller,
            "todays_special": self.todays_special,
            "spice_level": self.spice_level,
            "allergens": self.allergens,
        }