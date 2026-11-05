from flask import Blueprint, request, send_file

api = Blueprint("api", __name__, url_prefix="/api/")

