from datetime import datetime

from . import db

INCOME = "income"
EXPENSE = "expense"

DEFAULT_EXPENSE_CATEGORIES = [
    "Food", "Transport", "Rent", "Bills", "Shopping", "Entertainment", "Health", "Other",
]


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # income | expense
    category = db.Column(db.String(60), nullable=False, default="Other")
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255))
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
