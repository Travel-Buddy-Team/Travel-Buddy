import json, pathlib
import pandas as pd
import airportsdata

CSV = "data/On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2026_7.csv"

OUT = pathlib.Path("web/fixtures/arcs.json")            ## BTS data TODO replace by an API later

MIN_FLIGHTS, TOP_N = 100, 120

df = pd.read_csv(CSV, low_memory=False)
df["route"] = df["Origin"] + "-" + df["Dest"]

stats = df.groupby("route").agg(
    flights=("ArrDel15", "size"),
    delayed=("ArrDel15", "sum"),
    diverted=("Diverted", "sum"),
    cancelled=("Cancelled", "sum"),
    median_delay=("ArrDelay", "median"),
)
stats["disruption_rate"] = (stats.delayed + stats.diverted + stats.cancelled) / stats.flights

top = (stats[stats.flights >= MIN_FLIGHTS]
       .sort_values("flights", ascending=False)
       .head(TOP_N)
       .reset_index())
top[["origin", "dest"]] = top.route.str.split("-", expand=True)

ap = airportsdata.load("IATA")

arcs, missing = [], set()
for r in top.itertuples():
    a, b = ap.get(r.origin), ap.get(r.dest)
    if not a or not b:
        missing.add(r.origin if not a else r.dest)
        continue
    arcs.append({
        "startLat": a["lat"], "startLng": a["lon"],
        "endLat":   b["lat"], "endLng":   b["lon"],
        "route": r.route,
        "flights": int(r.flights),
        "rate": round(float(r.disruption_rate), 3),
        "medianDelay": None if pd.isna(r.median_delay) else int(r.median_delay),
    })

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(arcs, indent=1))
print(f"wrote {len(arcs)} arcs -> {OUT}")
if missing:
    print("no coordinates for:", sorted(missing))