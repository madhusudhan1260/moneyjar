from datetime import datetime, timedelta

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.transaction import DEFAULT_EXPENSE_CATEGORIES, EXPENSE, INCOME, Transaction
from services.statement_import import categorize, parse_statement

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


@bp.route("/import", methods=["GET", "POST"])
@login_required
def import_statement():
    if request.method == "POST":
        file = request.files.get("statement")
        if not file or not file.filename:
            flash("Choose a statement file to upload.", "error")
            return render_template("transaction_import.html")

        rows, errors = parse_statement(file)

        imported = 0
        duplicates = 0
        for row in rows:
            day_start = datetime.combine(row["date"], datetime.min.time())
            day_end = day_start + timedelta(days=1)

            exists = Transaction.query.filter_by(
                user_id=current_user.id,
                type=row["type"],
                amount=row["amount"],
                description=row["description"],
            ).filter(
                Transaction.date >= day_start, Transaction.date < day_end
            ).first()
            if exists:
                duplicates += 1
                continue

            db.session.add(
                Transaction(
                    user_id=current_user.id,
                    type=row["type"],
                    category=categorize(row["description"]) if row["type"] == EXPENSE else "Income",
                    amount=row["amount"],
                    description=row["description"],
                    date=day_start,
                )
            )
            imported += 1

        db.session.commit()

        if imported:
            flash(f"Imported {imported} transaction(s).", "success")
        if duplicates:
            flash(f"Skipped {duplicates} duplicate(s) already in your history.", "success")
        for error in errors:
            flash(error, "error")
        if not imported and not duplicates and not errors:
            flash("No transactions found in that file.", "error")

        return redirect(url_for("transactions.history"))

    return render_template("transaction_import.html")
