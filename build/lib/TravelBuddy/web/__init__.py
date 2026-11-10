from pathlib import Path

from flask import Flask
from TravelBuddy.web.api import api
from TravelBuddy.web.home import home


def create_app() -> Flask:
    """
    :return: The configured Flask application.
    """

    root_dir = Path(__file__).resolve().parent
    template_dir = root_dir / "templates"
    static_dir = root_dir / "static"

    print(static_dir)

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    app.register_blueprint(home)
    app.register_blueprint(api)

    return app
