"""
Main entry point for the application
"""

from flask import Flask, render_template
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("core/index.html")


@app.route("/route")
def route():
    return render_template("core/route.html")


if __name__ == "__main__":
    app.run()
