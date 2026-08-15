import calendar
from datetime import datetime

from . import db

DEPOSIT = "deposit"
WITHDRAW = "withdraw"

JAR_EMOJIS = ["🏠", "🎓", "📱", "✈️", "🆘", "💻", "🚗", "💍", "🎉", "🐷"]


class Jar(db.Model):
    __tablename__ = "jars"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    emoji = db.Column(db.String(8), default="🫙")
    target_amount = db.Column(db.Float, nullable=False)
    saved_amount = db.Column(db.Float, nullable=False, default=0)
    monthly_target = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship(
        "JarTransaction", backref="jar", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def progress_pct(self):
        if self.target_amount <= 0:
            return 100
        return min(100, round(self.saved_amount / self.target_amount * 100, 1))

    @property
    def remaining(self):
        return max(0, self.target_amount - self.saved_amount)

    @property
    def estimated_completion(self):
        if self.monthly_target <= 0 or self.remaining <= 0:
            return None
        months_left = self.remaining / self.monthly_target
        month = datetime.utcnow().month - 1 + round(months_left)
        year = datetime.utcnow().year + month // 12
        month = month % 12 + 1
        return f"{calendar.month_name[month]} {year}"


class JarTransaction(db.Model):
    __tablename__ = "jar_transactions"

    id = db.Column(db.Integer, primary_key=True)
    jar_id = db.Column(db.Integer, db.ForeignKey("jars.id"), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # deposit | withdraw
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
