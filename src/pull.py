import json, math, pathlib
from datetime import datetime, timezone, timedelta

import airportsdata
import requests
from opensky_auth import headers

API = "https://opensky-network.org/api"
CACHE = pathlib.Path("data/opensky_cache")
CACHE.mkdir(parents=True, exist_ok=True)
OUT = pathlib.Path("web/fixtures/paths.json")

DEST = "SFO"        # ONE airport covers EVERY route landing there
MAX_TRACKS = 8

AP = airportsdata.load("IATA")
ICAO2IATA = {v["icao"]: k for k, v in AP.items() if v.get("icao")}
WANT = set(pathlib.Path("web/fixtures/routes.txt").read_text().split())

MIN_CREDITS = 500
remaining = None

def get(name, path, params):
    global remaining
    f = CACHE / f"{name}.json"
    if f.exists():
        return json.loads(f.read_text())
    if remaining is not None and remaining < MIN_CREDITS:
        raise SystemExit(f"stopping: only {remaining} credits left")
    r = requests.get(f"{API}{path}", params=params, headers=headers(), timeout=90)
    remaining = int(r.headers.get("X-Rate-Limit-Remaining", 0))
    print(f"  {r.status_code}  left={remaining}")
    r.raise_for_status()
    f.write_text(json.dumps(r.json()))
    return r.json()


def km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * 6371 * math.asin(math.sqrt(h))


end = (datetime.now(timezone.utc) - timedelta(days=2)).replace(
    hour=0, minute=0, second=0, microsecond=0)
begin = end - timedelta(days=1)
b, e = int(begin.timestamp()), int(end.timestamp())

print(f"arrivals into {DEST}")
arrivals = get(f"arr_{DEST}_{b}", "/flights/arrival",
               {"airport": AP[DEST]["icao"], "begin": b, "end": e})
print(f"  {len(arrivals)} arrivals")

picked, seen = [], set()
for f in arrivals:
    origin = ICAO2IATA.get(f.get("estDepartureAirport") or "")
    route = f"{origin}-{DEST}"
    if origin and route in WANT and route not in seen:
        seen.add(route)
        picked.append((route, f))
    if len(picked) >= MAX_TRACKS:
        break
print(f"matched {len(picked)} routes: {[r for r, _ in picked]}")

paths = []
for route, f in picked:
    print(f"track {route} ({f['icao24']})")
    tr = get(f"trk_{f['icao24']}_{f['firstSeen']}", "/tracks/all",
            {"icao24": f["icao24"], "time": f["firstSeen"]})
    pts = [[p[1], p[2]] for p in tr.get("path", []) if p[1] and p[2]]
    if len(pts) < 10:
        print("  too few points, skipping")
        continue
    actual = sum(km(pts[i], pts[i+1]) for i in range(len(pts)-1))
    direct = km(pts[0], pts[-1])
    paths.append({
        "route": route,
        "callsign": (f.get("callsign") or "").strip(),
        "icao24": f["icao24"],
        "date": datetime.fromtimestamp(f["firstSeen"], timezone.utc).strftime("%Y-%m-%d"),
        "points": [[round(a, 4), round(o, 4)] for a, o in pts],
        "greatCircleKm": round(direct, 1),
        "actualTrackKm": round(actual, 1),
        "deviationPct": round((actual - direct) / direct, 3) if direct else None,
    })

OUT.write_text(json.dumps(paths, indent=1))
print(f"\nwrote {len(paths)} paths -> {OUT}  ({remaining} credits left)")