"""SROMS Flask application entry point."""

from flask import Flask, jsonify

from config import Config
from extensions import db, jwt

from routes.auth_routes import auth_bp
from routes.menu_routes import menu_bp
from routes.order_routes import order_bp
from routes.table_routes import table_bp
from routes.customer_routes import customer_bp
from routes.chef_routes import chef_bp   # <-- ADD THIS


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
    app.register_blueprint(chef_bp)   # <-- ADD THIS

    # HOME ROUTE
    @app.route("/")
    def home():
        return "Smart Restaurant System Running 🚀"

    # Health Check
    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "SROMS"}), 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)