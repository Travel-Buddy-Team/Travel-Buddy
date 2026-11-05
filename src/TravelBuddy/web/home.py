"""
Main entry point for the application
"""

from flask import Blueprint, render_template
import logging

logger = logging.getLogger(__name__)

home = Blueprint("home", __name__, url_prefix="/")

@home.route("/")
def index():
    return render_template("core/index.html")


@home.route("/route")
def route():
    return render_template("core/route.html")


@home.route("/globe")
def globe():
    return render_template("globe/globe.html")

