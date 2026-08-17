from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db

bp = Blueprint("profile", __name__)


def _parse_amount(raw):
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return 0.0
    return value if value > 0 else 0.0


@bp.route("/setup", methods=["GET", "POST"])
@login_required
def setup():
    if request.method == "POST":
        if request.form.get("skip"):
            current_user.onboarded = True
            db.session.commit()
            return redirect(url_for("dashboard.index"))

        current_user.monthly_income = _parse_amount(request.form.get("monthly_income"))
        current_user.pocket_money = _parse_amount(request.form.get("pocket_money"))
        current_user.money_to_give = _parse_amount(request.form.get("money_to_give"))
        current_user.current_savings = _parse_amount(request.form.get("current_savings"))
        current_user.onboarded = True
        db.session.commit()
        flash("Your financial snapshot is saved.", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("setup.html")
