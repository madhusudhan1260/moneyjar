from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User  # noqa: E402,F401
from .transaction import Transaction  # noqa: E402,F401
from .jar import Jar, JarTransaction  # noqa: E402,F401
