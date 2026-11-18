# sanity check the globe data
# run from repo root
import csv, json
from TravelBuddy.utils.paths import ARCS, PATHS, WORLD_ROUTES, OPENFLIGHTS

US = {"United States", "Puerto Rico", "Virgin Islands", "Guam", "Northern Mariana Islands", "American Samoa"}
us = set()
for r in csv.reader((OPENFLIGHTS / "airports.dat").read_text(encoding="utf-8").splitlines()):
    if len(r) > 8 and r[4] not in ("", "\\N") and r[3] in US:
        us.add(r[4])

w = json.loads(WORLD_ROUTES.read_text())
a = json.loads(ARCS.read_text())
p = json.loads(PATHS.read_text())

dom = [x for x in w if all(c in us for c in x["pair"].split("-"))]
gate = [x for x in w if any(c in us for c in x["pair"].split("-"))]
measured = {tuple(sorted(x["route"].split("-"))) for x in a}
clash = [x for x in w if tuple(sorted(x["pair"].split("-"))) in measured]

print(f"world routes      : {len(w)}")
print(f"  US-domestic     : {len(dom)}   (must be 0)")
print(f"  US gateways     : {len(gate)}")
print(f"  clash with BTS  : {len(clash)}   (must be 0)")
print(f"BTS arcs          : {len(a)} directed / {len(measured)} pairs")
print(f"OpenSky tracks    : {len(p)}  all on BTS routes: "
      f"{ {x['route'] for x in p} <= {x['route'] for x in a} }")

ok = not dom and not clash and len(w) and len(a)
print("\n" + ("PASS" if ok else "FAIL"))