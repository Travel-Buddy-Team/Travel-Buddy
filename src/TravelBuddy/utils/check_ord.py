import json, math
import airportsdata

AP = airportsdata.load("IATA")

def km(a, b):
    (la1, lo1), (la2, lo2) = a, b
    p1, p2 = math.radians(la1), math.radians(la2)
    dp, dl = p2 - p1, math.radians(lo2 - lo1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * 6371 * math.asin(math.sqrt(h))

paths = {p["route"]: p for p in json.load(open("web/fixtures/paths.json"))}
p = paths["ORD-SFO"]
pts = p["points"]

o = [AP["ORD"]["lat"], AP["ORD"]["lon"]]
d = [AP["SFO"]["lat"], AP["SFO"]["lon"]]

print("first point is", round(km(pts[0], o)), "km from ORD")
print("last point is ", round(km(pts[-1], d)), "km from SFO")
print("max offset from the direct line:",
      round(max(min(km(q, pts[0]), km(q, pts[-1])) for q in pts)), "km")
print("points:", len(pts))
for i in range(0, len(pts), len(pts)//8):
    print("  ", pts[i])