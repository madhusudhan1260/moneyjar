from datetime import datetime

from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from models import db
from models.jar import Jar
from models.transaction import EXPENSE, INCOME, Transaction

bp = Blueprint("dashboard", __name__)

# strftime filtering below is SQLite-specific; swap to extract() if moving to Postgres.


def _sum(user_id, type_, month=None, year=None):
    query = db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0)).filter_by(
        user_id=user_id, type=type_
    )
    if month and year:
        query = query.filter(
            func.strftime("%m", Transaction.date) == f"{month:02d}",
            func.strftime("%Y", Transaction.date) == str(year),
        )
    return query.scalar() or 0.0


def _spending_insight(user_id):
    now = datetime.utcnow()
    prev_month = now.month - 1 or 12
    prev_year = now.year if now.month > 1 else now.year - 1

    rows = (
        db.session.query(
            Transaction.category, func.coalesce(func.sum(Transaction.amount), 0.0)
        )
        .filter_by(user_id=user_id, type=EXPENSE)
        .filter(
            func.strftime("%m", Transaction.date) == f"{now.month:02d}",
            func.strftime("%Y", Transaction.date) == str(now.year),
        )
        .group_by(Transaction.category)
        .all()
    )
    if not rows:
        return None

    top_category, top_amount = max(rows, key=lambda r: r[1])

    prev_amount = (
        db.session.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter_by(user_id=user_id, type=EXPENSE, category=top_category)
        .filter(
            func.strftime("%m", Transaction.date) == f"{prev_month:02d}",
            func.strftime("%Y", Transaction.date) == str(prev_year),
        )
        .scalar()
        or 0.0
    )

    if prev_amount <= 0:
        return f"You spent ₹{top_amount:,.0f} on {top_category} this month."

    change_pct = round((top_amount - prev_amount) / prev_amount * 100)
    if change_pct > 5:
        return (
            f"You spent ₹{top_amount:,.0f} on {top_category} this month, "
            f"{change_pct}% higher than last month."
        )
    if change_pct < -5:
        return (
            f"You spent ₹{top_amount:,.0f} on {top_category} this month, "
            f"{abs(change_pct)}% lower than last month. Nice work."
        )
    return f"Your {top_category} spending is steady at ₹{top_amount:,.0f} this month."


@bp.route("/")
@login_required
def index():
    if not current_user.onboarded:
        return redirect(url_for("profile.setup"))

    now = datetime.utcnow()
    all_income = _sum(current_user.id, INCOME)
    all_expense = _sum(current_user.id, EXPENSE)
    month_spent = _sum(current_user.id, EXPENSE, month=now.month, year=now.year)

    jars = Jar.query.filter_by(user_id=current_user.id).order_by(Jar.created_at.desc()).all()
    saved_in_jars = sum(jar.saved_amount for jar in jars)
    total_balance = all_income - all_expense - saved_in_jars

    category_rows = (
        db.session.query(Transaction.category, func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter_by(user_id=current_user.id, type=EXPENSE)
        .filter(
            func.strftime("%m", Transaction.date) == f"{now.month:02d}",
            func.strftime("%Y", Transaction.date) == str(now.year),
        )
        .group_by(Transaction.category)
        .all()
    )

    return render_template(
        "dashboard.html",
        total_balance=total_balance,
        month_spent=month_spent,
        saved_in_jars=saved_in_jars,
        all_income=all_income,
        jars=jars,
        insight=_spending_insight(current_user.id),
        chart_labels=[row[0] for row in category_rows],
        chart_values=[row[1] for row in category_rows],
    )
