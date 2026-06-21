"""Shared Flask extension instances for SROMS."""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Extensions are initialized in app.py to avoid circular imports.
db = SQLAlchemy()
jwt = JWTManager()