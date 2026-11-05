import json

for a in sorted(json.load(open("web/fixtures/arcs.json")), key=lambda x: -x["rate"])[:15]:
    m = "  ".join(f"{k[-2:]}:{v*100:.0f}" for k, v in sorted(a["byMonth"].items()))
    print(f"{a['route']:>9} {a['rate']*100:5.1f}%   {m}")