import json
from TravelBuddy.utils.paths import ARCS

for a in sorted(json.loads(ARCS.read_text()), key=lambda x: -x["rate"])[:15]:
    m = "  ".join(f"{k[-2:]}:{v*100:.0f}" for k, v in sorted(a["byMonth"].items()))
    print(f"{a['route']:>9} {a['rate']*100:5.1f}%   {m}")
