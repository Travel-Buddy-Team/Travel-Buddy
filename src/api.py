from flask import Blueprint, request

api = Blueprint("api", __name__, url_prefix="/api/v1/")


@api.route("/checkFlight", methods=["POST"])
def check_flight():
    raise NotImplementedError("Cannot check flights currently")

