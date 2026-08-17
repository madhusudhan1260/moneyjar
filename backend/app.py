import os

from flask import Flask, render_template
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from sqlalchemy import inspect, text

from config import Config
from models import db
from models.user import User

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")

login_manager = LoginManager()
login_manager.login_view = "auth.login"
csrf = CSRFProtect()

# users table predates the onboarding fields on some deployments; add them in place
# instead of requiring a separate migration step on every deploy.
_NEW_USER_COLUMNS = {
    "onboarded": "BOOLEAN DEFAULT 0",
    "monthly_income": "FLOAT DEFAULT 0",
    "pocket_money": "FLOAT DEFAULT 0",
    "money_to_give": "FLOAT DEFAULT 0",
    "current_savings": "FLOAT DEFAULT 0",
}


def _add_missing_columns():
    inspector = inspect(db.engine)
    existing = {col["name"] for col in inspector.get_columns("users")}
    for name, ddl in _NEW_USER_COLUMNS.items():
        if name not in existing:
            db.session.execute(text(f"ALTER TABLE users ADD COLUMN {name} {ddl}"))
    db.session.commit()


def create_app():
    app = Flask(
        __name__,
        template_folder=os.path.join(FRONTEND_DIR, "templates"),
        static_folder=os.path.join(FRONTEND_DIR, "static"),
    )
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from routes.auth import bp as auth_bp
    from routes.dashboard import bp as dashboard_bp
    from routes.jars import bp as jars_bp
    from routes.profile import bp as profile_bp
    from routes.transactions import bp as transactions_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(jars_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(transactions_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, message="Page not found"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("error.html", code=500, message="Something went wrong"), 500

    with app.app_context():
        db.create_all()
        _add_missing_columns()

    return app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5050)
