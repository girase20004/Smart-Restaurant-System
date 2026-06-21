"""Authentication API routes."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from extensions import db
from models.user import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/login")
def login():
    """Authenticate admin, chef, or waiter users and return a JWT access token."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "").strip().lower()

    if not email or not password or role not in User.VALID_ROLES:
        return jsonify({"message": "email, password, and valid role are required"}), 400

    user = User.query.filter_by(email=email, role=role).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"access_token": token, "token_type": "Bearer", "user": user.to_dict()}), 200


@auth_bp.post("/users")
def create_user():
    """Create an initial user; useful for Phase 1 setup and local administration."""
    data = request.get_json(silent=True) or {}
    required = ["name", "email", "password", "role"]
    if any(not data.get(field) for field in required):
        return jsonify({"message": "name, email, password, and role are required"}), 400

    role = data["role"].strip().lower()
    if role not in User.VALID_ROLES:
        return jsonify({"message": "role must be admin, chef, or waiter"}), 400

    email = data["email"].strip().lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "email already exists"}), 409

    user = User(name=data["name"].strip(), email=email, role=role)
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "user created", "user": user.to_dict()}), 201