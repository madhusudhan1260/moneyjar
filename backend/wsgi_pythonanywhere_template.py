import sys

path = "/home/YOUR_USERNAME/moneyjar/backend"
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application  # noqa: E402
