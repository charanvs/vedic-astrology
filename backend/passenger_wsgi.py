"""Entry point for cPanel "Setup Python App" (Phusion Passenger, WSGI).

FastAPI is an ASGI application, so it is wrapped with the a2wsgi adapter. Passenger may
pass the mount prefix (/astrology) either in SCRIPT_NAME or inside PATH_INFO; both work.
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from a2wsgi import ASGIMiddleware  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.main import app as asgi_app  # noqa: E402

BASE_PATH = get_settings().base_path.rstrip("/")
_wsgi_app = ASGIMiddleware(asgi_app)


def application(environ, start_response):
    path = environ.get("PATH_INFO") or "/"
    if BASE_PATH and (path == BASE_PATH or path.startswith(BASE_PATH + "/")):
        environ["PATH_INFO"] = path[len(BASE_PATH):] or "/"
        environ["SCRIPT_NAME"] = BASE_PATH
    return _wsgi_app(environ, start_response)
