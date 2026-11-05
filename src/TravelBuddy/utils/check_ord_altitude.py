import json, glob, math
import airportsdata

AP = airportsdata.load("IATA")
O = (AP["ORD"]["lat"], AP["ORD"]["lon"])
D = (AP["SFO"]["lat"], AP["SFO"]["lon"])

def km(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * 6371 * math.asin(math.sqrt(h))

f = glob.glob("data/opensky_cache/trk_a43e5b_*.json")[0]
path = json.load(open(f))["path"]

hits = [p for p in path
        if p[3] is not None and p[3] < 3000
        and km((p[1], p[2]), O) > 200 and km((p[1], p[2]), D) > 200]

if hits:
    print(len(hits), "low points away from both airports - likely a stitched multi-leg")
    print("example:", hits[0][1], hits[0][2], hits[0][3], "m")
else:
    alts = [p[3] for p in path if p[3] is not None]
    print("single continuous flight - cruise altitude held, max", max(alts), "m")