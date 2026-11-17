from TravelBuddy.web.data import all_routes, route, flight_paths
from flask import Blueprint, request, jsonify

api = Blueprint("api", __name__, url_prefix="/api/")

@api.route("routes")
def api_routes():
    return jsonify(all_routes()), 200


@api.route("route/<route_name>")
def api_route(route_name: str):
    routes_data = route(route_name)

    if not routes_data:
        return jsonify({}), 404

    return jsonify(routes_data), 200


@api.route("paths")
def api_paths():
    return jsonify(flight_paths())