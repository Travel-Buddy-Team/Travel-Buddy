#### loads computed data fixture for API. pls refer to docs/endpoints.md
import json
from functools import lru_cache

from TravelBuddy.utils.paths import ARCS, PATHS

MIN_FLIGHTS = 200


@lru_cache(maxsize=1)
def _arcs():
    return json.loads(ARCS.read_text())


@lru_cache(maxsize=1)
def _paths():
    return json.loads(PATHS.read_text())


def all_routes():
    ### every route w/ stats. GET /api/routes
    return _arcs()


def route(code):
    ### 1 route in detail, or None. GET /api/routes/<route>
    for a in _arcs():
        if a["route"] == code.upper():
            return a | {"belowThreshold": a["flights"] < MIN_FLIGHTS}
    return None


def flight_paths():
    ### validated flight tracks. GET /api/paths
    return _paths()