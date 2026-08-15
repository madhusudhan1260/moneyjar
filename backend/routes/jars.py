from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from models import db
from models.jar import DEPOSIT, WITHDRAW, JAR_EMOJIS, Jar, JarTransaction

bp = Blueprint("jars", __name__, url_prefix="/jars")


def _get_owned_jar(jar_id):
    jar = Jar.query.get_or_404(jar_id)
    if jar.user_id != current_user.id:
        abort(404)
    return jar


@bp.route("/new", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        emoji = request.form.get("emoji") or "🫙"
        try:
            target_amount = float(request.form.get("target_amount", 0))
            monthly_target = float(request.form.get("monthly_target", 0) or 0)
        except ValueError:
            flash("Enter valid numbers for amounts.", "error")
            return render_template("jar_new.html", emojis=JAR_EMOJIS)

        if not name or target_amount <= 0:
            flash("Jar name and a positive target amount are required.", "error")
            return render_template("jar_new.html", emojis=JAR_EMOJIS)

        jar = Jar(
            user_id=current_user.id,
            name=name,
            emoji=emoji,
            target_amount=target_amount,
            monthly_target=monthly_target,
        )
        db.session.add(jar)
        db.session.commit()
        return redirect(url_for("dashboard.index"))

    return render_template("jar_new.html", emojis=JAR_EMOJIS)


@bp.route("/<int:jar_id>")
@login_required
def detail(jar_id):
    jar = _get_owned_jar(jar_id)
    entries = JarTransaction.query.filter_by(jar_id=jar.id).order_by(JarTransaction.date.desc()).all()
    return render_template("jar_detail.html", jar=jar, entries=entries)


@bp.route("/<int:jar_id>/deposit", methods=["POST"])
@login_required
def deposit(jar_id):
    jar = _get_owned_jar(jar_id)
    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0

    if amount <= 0:
        flash("Enter a positive amount to add.", "error")
        return redirect(url_for("jars.detail", jar_id=jar.id))

    jar.saved_amount += amount
    db.session.add(JarTransaction(jar_id=jar.id, type=DEPOSIT, amount=amount))
    db.session.commit()
    return redirect(url_for("jars.detail", jar_id=jar.id))


@bp.route("/<int:jar_id>/withdraw", methods=["POST"])
@login_required
def withdraw(jar_id):
    jar = _get_owned_jar(jar_id)
    try:
        amount = float(request.form.get("amount", 0))
    except ValueError:
        amount = 0

    if amount <= 0 or amount > jar.saved_amount:
        flash("Enter an amount up to what's saved in this jar.", "error")
        return redirect(url_for("jars.detail", jar_id=jar.id))

    jar.saved_amount -= amount
    db.session.add(JarTransaction(jar_id=jar.id, type=WITHDRAW, amount=amount))
    db.session.commit()
    return redirect(url_for("jars.detail", jar_id=jar.id))


@bp.route("/<int:jar_id>/delete", methods=["POST"])
@login_required
def delete(jar_id):
    jar = _get_owned_jar(jar_id)
    db.session.delete(jar)
    db.session.commit()
    return redirect(url_for("dashboard.index"))
