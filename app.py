"""SROMS Flask application entry point."""

from flask import Flask, jsonify

from config import Config
from extensions import db, jwt

from routes.auth_routes import auth_bp
from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.table_routes import table_bp
from routes.customer_routes import customer_bp


def create_app(config_class=Config):
    """Create and configure the Flask application."""

    app = Flask(__name__)
    app.config.from_object(config_class)

    # extensions init
    db.init_app(app)
    jwt.init_app(app)

    # blueprints register
    app.register_blueprint(auth_bp)
    app.register_blueprint(table_bp)
    app.register_blueprint(menu_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(customer_bp)

    # ✅ HOME ROUTE FIX (IMPORTANT)
    @app.route("/")
    def home():
        return "Smart Restaurant System Running 🚀"

    # health check
    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "SROMS"}), 200

    # CLI: init DB
    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        print("Database tables created.")

    # CLI: seed data
    @app.cli.command("seed-sample")
    def seed_sample_command():
        from models.menu import Menu
        from models.table import RestaurantTable
        from models.user import User

        if not User.query.filter_by(email="admin@sroms.test").first():
            admin = User(
                name="Admin User",
                email="admin@sroms.test",
                role="admin"
            )
            admin.set_password("StrongPass123!")
            db.session.add(admin)

        for table_number in ("T1", "T2", "T3"):
            if not RestaurantTable.query.filter_by(table_number=table_number).first():
                db.session.add(
                    RestaurantTable(table_number=table_number, status="available")
                )

        sample_items = [
            {
                "dish_name": "Butter Chicken",
                "price": 320,
                "category": "Main Course",
                "image": "https://images.unsplash.com/photo-1603894584373-5ac82b2ae398",
                "ingredients": "Chicken, tomato gravy, butter, cream",
                "prep_time": 25,
                "veg_nonveg": "non-veg",
                "best_seller": True,
                "todays_special": True,
                "spice_level": "Medium",
                "allergens": "Dairy"
            },
            {
                "dish_name": "Butter Naan",
                "price": 120,
                "category": "Breads",
                "image": "https://images.unsplash.com/photo-1596797038530-2c107229654b",
                "ingredients": "Flour, butter, yogurt",
                "prep_time": 10,
                "veg_nonveg": "veg",
                "best_seller": True,
                "spice_level": "Mild",
                "allergens": "Gluten, dairy"
            },
            {
                "dish_name": "Cold Drink",
                "price": 80,
                "category": "Beverages",
                "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e",
                "ingredients": "Carbonated soft drink",
                "prep_time": 2,
                "veg_nonveg": "veg",
                "todays_special": True,
                "spice_level": "None",
                "allergens": "None"
            },
        ]

        for item in sample_items:
            if not Menu.query.filter_by(dish_name=item["dish_name"]).first():
                db.session.add(Menu(**item))

        db.session.commit()
        print("Sample data inserted.")


    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)