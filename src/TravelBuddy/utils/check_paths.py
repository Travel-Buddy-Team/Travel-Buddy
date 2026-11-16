## deviation check

import json
from TravelBuddy.utils.paths import PATHS
for p in json.loads(PATHS.read_text()):
    print(f"{p['route']:>9}  {p['deviationPct']*100:5.1f}%  {len(p['points']):4d} pts")
