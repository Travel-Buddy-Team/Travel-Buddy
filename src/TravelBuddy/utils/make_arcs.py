import glob, json, pathlib
import pandas as pd
import airportsdata

OUT = pathlib.Path("web/fixtures/arcs.json")
MIN_FLIGHTS, TOP_N = 200, 120

COLS = ["FlightDate", "Origin", "Dest", "ArrDel15", "Diverted", "Cancelled", "ArrDelay"]

frames = []
for f in sorted(glob.glob("data/On_Time_Reporting_Carrier*.csv")):
    d = pd.read_csv(f, low_memory=False, usecols=COLS)
    print(f"  {pathlib.Path(f).name[-16:]}  {len(d):,} rows")
    frames.append(d)

if not frames:
    raise SystemExit("no BTS files found in data/ . run src/fetch_data.py first")

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
        }
    )

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(arcs, indent=1))
print(f"wrote {len(arcs)} arcs -> {OUT}")
if missing:
    print("no coords for:", sorted(missing))

routes = sorted({a["route"] for a in arcs})
pathlib.Path("web/fixtures/routes.txt").write_text("\n".join(routes))
print(len(routes), "routes")
