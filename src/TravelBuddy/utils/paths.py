##### !!!!!!!!!!!!! if the tree moves, this is the only file to change!!!!!!!!!!!!!!!!!!!!!!
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent          # src/TravelBuddy
REPO = PKG.parent.parent                              # repo root

DATA = REPO / "data"
CACHE = DATA / "opensky_cache"
FIXTURES = PKG / "web" / "static" / "globe" / "fixtures"

ARCS = FIXTURES / "arcs.json"
PATHS = FIXTURES / "paths.json"
ROUTES = FIXTURES / "routes.txt"

BTS_GLOB = str(DATA / "On_Time_Reporting_Carrier*.csv")