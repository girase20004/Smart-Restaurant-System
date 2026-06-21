"""Application configuration for the Smart Restaurant Ordering & Management System."""

import os
from datetime import timedelta


class Config:
    """Base configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv("JWT_ACCESS_TOKEN_HOURS", "8")))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:admin123@localhost:5432/restaurant_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    QR_CODE_FOLDER = os.getenv("QR_CODE_FOLDER", "qr_codes")
    CUSTOMER_URL_BASE = os.getenv("CUSTOMER_URL_BASE", "http://localhost:5000")