import glob, json, pathlib
import pandas as pd
import airportsdata
from TravelBuddy.utils.paths import ARCS as OUT, ROUTES, DATA
from TravelBuddy.utils.paths import ARCS as OUT, BTS_GLOB, ROUTES

MIN_FLIGHTS, TOP_N = 200, 120

CAUSES = [
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "SecurityDelay",
    "LateAircraftDelay",
]
COLS = [
    "FlightDate",
    "Origin",
    "Dest",
    "ArrDel15",
    "Diverted",
    "Cancelled",
    "ArrDelay",
] + CAUSES

frames = []
for f in sorted(glob.glob(BTS_GLOB)):
    d = pd.read_csv(f, low_memory=False, usecols=COLS)
    print(f"  {pathlib.Path(f).name[-16:]}  {len(d):,} rows")
    frames.append(d)

if not frames:
    raise SystemExit("no BTS files found in data/ - run utils/data_fetch.py first")

df = pd.concat(frames, ignore_index=True)
df["route"] = df.Origin + "-" + df.Dest
df["period"] = pd.to_datetime(df.FlightDate).dt.strftime("%Y-%m")
print(f"total {len(df):,} rows across {df.period.nunique()} months")


def rates(g):
    out = g.agg(
        flights=("ArrDel15", "size"),
        delayed=("ArrDel15", "sum"),
        diverted=("Diverted", "sum"),
        cancelled=("Cancelled", "sum"),
        median_delay=("ArrDelay", "median"),
    )
    out["rate"] = (out.delayed + out.diverted + out.cancelled) / out.flights
    return out


overall = rates(df.groupby("route"))
by_month = rates(df.groupby(["route", "period"]))
causes = df.groupby("route")[CAUSES].sum()

top = (
    overall[overall.flights >= MIN_FLIGHTS]
    .sort_values("flights", ascending=False)
    .head(TOP_N)
    .reset_index()
)
top[["origin", "dest"]] = top.route.str.split("-", expand=True)

AP = airportsdata.load("IATA")

arcs, missing = [], set()
for r in top.itertuples():
    a, b = AP.get(r.origin), AP.get(r.dest)
    if not a or not b:
        missing.add(r.origin if not a else r.dest)
        continue
    months = by_month.loc[r.route]
    c = causes.loc[r.route]
    arcs.append(
        {
            "startLat": a["lat"],
            "startLng": a["lon"],
            "endLat": b["lat"],
            "endLng": b["lon"],
            "route": r.route,
            "flights": int(r.flights),
            "rate": round(float(r.rate), 3),
            "medianDelay": None if pd.isna(r.median_delay) else int(r.median_delay),
            "byMonth": {p: round(float(v), 3) for p, v in months.rate.items()},
            "causes": {
                "carrier": int(c.CarrierDelay),
                "weather": int(c.WeatherDelay),
                "nas": int(c.NASDelay),
                "security": int(c.SecurityDelay),
                "lateAircraft": int(c.LateAircraftDelay),
            },
        }
    )

OUT.write_text(json.dumps(arcs, indent=1))
print(f"wrote {len(arcs)} arcs -> {OUT}")
if missing:
    print("no coords for:", sorted(missing))

routes = sorted({a["route"] for a in arcs})
ROUTES.write_text("\n".join(routes))
print(len(routes), "routes")
