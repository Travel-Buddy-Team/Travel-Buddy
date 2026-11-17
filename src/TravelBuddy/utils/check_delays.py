from TravelBuddy.web.data import delay_profile, miss_probability

p = delay_profile("LAX-SFO")
print("flights:", p["flights"])
print("arrival p10 / p50 / p90:", p["arr"]["10"], p["arr"]["50"], p["arr"]["90"])
print()
for m in (30, 45, 55, 75, 90):
    print(f"{m:>3} min layover -> {miss_probability('LAX-SFO', m):.1%} miss")