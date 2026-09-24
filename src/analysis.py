import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_csv("data/On_Time_Reporting_Carrier_On_Time_Performance_(1987_present)_2026_7.csv", low_memory=False)
df["route"] = df["Origin"] + "-" + df["Dest"]

stats = df.groupby("route").agg(
    flights=("ArrDel15", "size"),
    delayed=("ArrDel15", "sum"),
    diverted=("Diverted", "sum"),
    cancelled=("Cancelled", "sum"),
    median_delay=("ArrDelay", "median"),
)
stats["disruption_rate"] = (stats.delayed + stats.diverted + stats.cancelled) / stats.flights

print("month rows:", len(df))
print("overall delayed:", df.ArrDel15.mean())
print("overall cancelled:", df.Cancelled.mean())
print("overall diverted:", df.Diverted.mean())
print()
print(stats[stats.flights >= 100].disruption_rate.describe())
print()

print(stats[stats.flights >= 100].sort_values("disruption_rate", ascending=False).head(20))
print()

print(df[df.route == "CLD-SFO"][["FlightDate","CRSArrTime","ArrTime","ArrDelay","ArrDel15","WeatherDelay"]].head(20))

sfo = df[df.Dest == "SFO"]
print(sfo[["CarrierDelay","WeatherDelay","NASDelay","SecurityDelay","LateAircraftDelay"]].sum())