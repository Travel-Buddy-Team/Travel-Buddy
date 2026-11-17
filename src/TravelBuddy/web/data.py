#### loads computed data fixture for API. pls refer to docs/endpoints.md
import json
from functools import lru_cache

from TravelBuddy.utils.paths import ARCS, DELAYS, PATHS

MIN_FLIGHTS = 200

@lru_cache(maxsize=1)
def _arcs():
    return json.loads(ARCS.read_text())


@lru_cache(maxsize=1)
def _paths():
    return json.loads(PATHS.read_text())

@lru_cache(maxsize=1)
def _delays():
    return json.loads(DELAYS.read_text())

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

def delay_profile(code):
    ## arrival + depart delay quantiles in mins. none if unknown
    return _delays().get(code.upper())

def _percentile_at(points, x):
    ## given sorted (val, percent) pairs, the percent at which x sits
    if x <= points[0][0]:
        return points[0][1] / 100
    if x >= points[-1][0]:
        return points[-1][1] / 100
    for (v1, p1), (v2, p2) in zip(points, points[1:]):
        if v1 <= x <= v2:
            if v2 == v1:
                return p2 / 100
            return (p1 + (p2 - p1) * (x - v1) / (v2 - v1)) / 100
    return points[-1][1] / 100

def miss_probability(code, layover_minutes):
   ## chance inbound leg arrive too late to make connection this long
    prof = delay_profile(code)
    if not prof:
        return None
    pts = sorted((float(v), int(p)) for p, v in prof["arr"].items())
    return round(1 - _percentile_at(pts, layover_minutes), 3)