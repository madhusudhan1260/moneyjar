from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.transaction import DEFAULT_EXPENSE_CATEGORIES, EXPENSE, INCOME, Transaction

bp = Blueprint("transactions", __name__, url_prefix="/transactions")


@bp.route("/")
@login_required
def history():
    entries = (
        Transaction.query.filter_by(user_id=current_user.id)
        .order_by(Transaction.date.desc())
        .all()
    )
    return render_template("transactions.html", entries=entries)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        type_ = request.form.get("type")
        category = request.form.get("category", "Other").strip() or "Other"
        description = request.form.get("description", "").strip()
        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        if type_ not in (INCOME, EXPENSE) or amount <= 0:
            flash("Enter a valid type and a positive amount.", "error")
            return render_template("transaction_new.html", categories=DEFAULT_EXPENSE_CATEGORIES)

        db.session.add(
            Transaction(
                user_id=current_user.id,
                type=type_,
                category=category if type_ == EXPENSE else "Income",
                amount=amount,
                description=description,
            )
        )
        db.session.commit()
        return redirect(url_for("dashboard.index"))

    return render_template("transaction_new.html", categories=DEFAULT_EXPENSE_CATEGORIES)
