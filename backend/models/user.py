from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    onboarded = db.Column(db.Boolean, default=False, nullable=False)
    monthly_income = db.Column(db.Float, default=0, nullable=False)
    pocket_money = db.Column(db.Float, default=0, nullable=False)
    money_to_give = db.Column(db.Float, default=0, nullable=False)
    current_savings = db.Column(db.Float, default=0, nullable=False)

    transactions = db.relationship(
        "Transaction", backref="user", lazy=True, cascade="all, delete-orphan"
    )
    jars = db.relationship("Jar", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
