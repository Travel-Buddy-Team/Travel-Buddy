## deviation check

import json

for p in json.load(open("web/fixtures/paths.json")):
    print(f"{p['route']:>9}  {p['deviationPct']*100:5.1f}%  {len(p['points']):4d} pts")