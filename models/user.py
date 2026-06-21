"""User model with password hashing helpers."""

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class User(db.Model):
    """System user who can authenticate as an admin, chef, or waiter."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, index=True)

    VALID_ROLES = {"admin", "chef", "waiter"}

    def set_password(self, raw_password: str) -> None:
        """Hash and store a plaintext password."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Return True when the supplied password matches the stored hash."""
        return check_password_hash(self.password, raw_password)

    def to_dict(self) -> dict:
        """Serialize public user fields."""
        return {"id": self.id, "name": self.name, "email": self.email, "role": self.role}