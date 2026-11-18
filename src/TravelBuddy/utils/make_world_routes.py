### builds world_routes.json for the faint grey background on the globe
# this data is from World Air Network. We don't have disruption, delays, cancellation, etc.
# for these routes. So these arcs will be drawn grey + unlabeled on purpose

# !!!!!!!! run AFTER make_arcs.py (it reads arcs.json to avoid doubling up on routes we already measured)

import csv
import io
import json

import requests

from TravelBuddy.utils.paths import ARCS, WORLD_ROUTES, OPENFLIGHTS

BASE = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/"

# max arc to draw... full set is like 18k pairs which will render but
# may lag on a laptop... we can raise depending on hardware
# None for all of them

MAX_ARCS = 2000

# a pair need at least THIS many arlines flying it to count as a route
# worth drawing. filters out one-off charter + seasonals

MIN_AIRLINES = 2

def fetch(name):
    # dl one openflight .dat + cache under data/openflights/.
    cached = OPENFLIGHTS / name
    if cached.exists():
        print(f"{name}: using cached copy")
        return cached.read_text(encoding="utf-8")

    print(f"{name}: downloading")
    r = requests.get(BASE + name, timeout=120)
    r.raise_for_status()
    text = r.text
    if len(text) < 100000:
        raise SystemExit(f"{name}: only {len(text)} chars. bad download")

    OPENFLIGHTS.mkdir(parents=True, exist_ok=True)
    cached.write_text(text, encoding="utf-8")
    return text

# bts considers territories as domestic but OpenFlights
# lists each as its own coutnry. w/o this JFK-SJU would be considered
# international when bts haS data for it
US_COUNTRIES = {
    "United States",
    "Puerto Rico",
    "Virgin Islands",
    "Guam",
    "Northern Mariana Islands",
    "American Samoa",
}

def airports():
    # IATA code -> (lat, lng, is_us)
    # skip rows w/ no IATA or bad cords
    out = {}
    for row in csv.reader(io.StringIO(fetch("airports.dat"))):
        if len(row) < 8:
            continue
        code = row[4]
        if not code or code == "\\N" or len(code) != 3:
            continue
        try:
            out[code] = (float(row[6]), float(row[7]), row[3] in US_COUNTRIES)
        except ValueError:
            continue
    us = sum(1 for v in out.values() if v[2])
    print(f"{len(out)} airports with IATA + coords ({us} in US/territories)")
    return out

def pairs(coords):
    # undirected airport pair -> number of airlines flying it
    counts = {}
    rows = unresolved = domestic = 0
    for row in csv.reader(io.StringIO(fetch("routes.dat"))):
        if len(row) < 5:
            continue
        rows += 1
        origin, dest = row[2], row[4]
        if origin == dest or origin not in coords or dest not in coords:
            unresolved += 1
            continue
        # skip US domestic pairs. bts already cover it
        # if we drew them grey, grey would mean two diff things on the same globe
        if coords[origin][2] and coords[dest][2]:
            domestic += 1
            continue
        key = tuple(sorted((origin, dest)))
        counts[key] = counts.get(key, 0) + 1
    print(
        f"{rows} route rows -> {len(counts)} international pairs "
        f"({domestic} US domestic skipped, {unresolved} unresolvable)"
    )
    return counts

def main():
    coords = airports()
    counts = pairs(coords)

    # nothing US domestic should survive the filter above,
    # but if arcs.json ever grows an international rte this still w\orks
    measured = set()
    if ARCS.exists():
        for a in json.loads(ARCS.read_text()):
            measured.add(tuple(sorted(a["route"].split("-"))))
        print(f"excluding {len(measured)} routes we measure ourselves")
    else:
        print("WARNING: no arcs.json. run make_arcs.py first")

    keep = [
        (pair, n)
        for pair, n in counts.items()
        if n >= MIN_AIRLINES and pair not in measured
    ]
    keep.sort(key=lambda kv: -kv[1])
    if MAX_ARCS:
        dropped = max(0, len(keep) - MAX_ARCS)
        keep = keep[:MAX_ARCS]
        if dropped:
            print(f"capped at MAX_ARCS={MAX_ARCS} ({dropped} thinner routes dropped)")

    out = []
    for (a, b), n in keep:
        lat1, lng1, _ = coords[a]
        lat2, lng2, _ = coords[b]
        # 4dec, ~11m on ground. far past what a px
        # on a globe can show, and it keeps the file 1/3 the size
        out.append(
            {
                "startLat": round(lat1, 4),
                "startLng": round(lng1, 4),
                "endLat": round(lat2, 4),
                "endLng": round(lng2, 4),
                "pair": f"{a}-{b}",
                "airlines": n,
            }
        )

    WORLD_ROUTES.write_text(json.dumps(out))
    print(f"wrote {len(out)} world routes -> {WORLD_ROUTES}")

if __name__ == "__main__":
    main()