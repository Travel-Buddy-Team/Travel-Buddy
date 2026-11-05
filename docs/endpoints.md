# What the backend sends to the front end

The below example responses work. I already put files in `web/fixtures/` so front end can work against those today and switch to live endpoints with no code changes.

## Conventions
- Field names `camelCase`
- Rates decimals between 0 to 1, NOT percentages!!!! `0.557` NOT `55.7`!!!
- Airport codes IATA (3 letters: `SFO`). Routes are `ORIGIN-DEST` (`LAX-SFO`)
- Months are `YYYY-MM`. Dates are `YYYY-MM-DD`
- Distances are kilometres (km). Times are minutes
- Cords are `[latitude, longitude]`

## GET /api/routes

Every route we have data for. This will power globe and search screen.

Fixture: `web/fixtures/arcs.json` **ready now**

```json
[
  {
    "route": "LAX-SFO",
    "startLat": 33.9425, "startLng": -118.4081,
    "endLat": 37.6189,   "endLng": -122.3750,
    "flights": 4312,
    "rate": 0.421,
    "medianDelay": 20,
    "byMonth": {
      "2025-10": 0.35, "2026-01": 0.19,
      "2026-04": 0.52, "2026-07": 0.56
    }
  }
]
```

- `rate` share of flights disrupted across all four months
- `byMonth` same rate per month for season toggle
- `medianDelay` med arrival delay in mins, including early arrivals as negatives
- **Disrupted** means arrived 15+ mins late, diverted, or cancelled (how BTS defines)

## GET /api/routes/{route}

One route in detail. Powers route detail screen.

**Not built yet** the cause breakdown isn't handled in code. Everything above `causes` is available today.

```json
{
  "route": "LAX-SFO",
  "flights": 4312,
  "rate": 0.421,
  "delayedRate": 0.415,
  "divertedRate": 0.002,
  "cancelledRate": 0.004,
  "medianDelay": 20,
  "byMonth": { "2026-07": 0.56 },
  "causes": {
    "nas": 207720,
    "lateAircraft": 109456,
    "carrier": 89393,
    "weather": 13556,
    "security": 130
  }
}
```

- `causes` vals are **total delay minutes** attributed to each cause NOT the rates!!
- `nas` = National Airspace System: air traffic control, airport capacity, non-severe weather that reduces capacity. Don't label it "weather" in the UI... It's the biggest cause at SFO and you can see that from data.

**Errors**
- Unknown route -> `404` with `{"error": "unknown route"}`
- Route below the min. sample threshold (200 flights) -> `200` with `"belowThreshold": true` and no `rate`. The UI shows the not enough data state over a number we don't trust (sub-200)

## GET /api/paths

Real recorded flight tracks for actual drawing routes against direct line.

Fixture: `web/fixtures/paths.json` **ready now, 6 tracks**

```json
[
  {
    "route": "ORD-SFO",
    "callsign": "UAL2158",
    "icao24": "a4493a",
    "date": "2026-10-26",
    "points": [[41.9534, -87.8996], [41.4853, -88.1448]],
    "greatCircleKm": 2963.4,
    "actualTrackKm": 3102.8,
    "deviationPct": 0.047
  }
]
```

- `points` is flown track, in order `[lat, lng]`
- `deviationPct` is how much further the flight actually flies than the direct great circle route
- I checked every track against BTS. The callsign and route must match a real scheduled service, which filters out diversions

## GET /api/connection

Whether a connection is likely to hold. Powers screen 04.

**Not built yet.** I need arrival-delay distributions computed per route.

Request:

`GET /api/connection?legs=LAX-DEN,DEN-JFK&date=2026-12-18&layover=55`

Response:

```json
{
  "legs": [
    {
      "route": "LAX-DEN",
      "schedDep": "09:20", "depP10": "09:15", "depP90": "10:05",
      "schedArr": "10:40", "arrP10": "10:05", "arrP90": "11:55"
    }
  ],
  "connection": {
    "airport": "DEN",
    "scheduledMinutes": 55,
    "missProbability": 0.15
  }
}
```

### Whisker caps calculation

The three marks, per the UI revision w/ BT, are: early cap, scheduled time, late cap. Scheduled comes from our timetable. Two caps come from history.

We can't use min. and max. A flight that was six hours late would stretch our whisker so it tells us nothing. Instead we use the 10th and 90th percentiles.

Take every flight on that route, sort them by how late they arrived:

    2,000 LAX-DEN flights, sorted by arrival delay:

      -18 min, -15, -12, ... , +4, +7, ... , +52, +68, ... , +340
                     ^                             ^
               the 200th value              the 1,800th value
                   = p10                         = p90

`p10` is the value 10% of flights beat. `p90` is the value 90% of flights beat. So 80% of our flights land between them and that span is what our whisker draws. Extremes still exist in the data, they just don't set our scale.

Worked through example: if `p10` is -35 minutes and `p90` is +75 minutes against 10:40 scheduled arrival, the whisker reads

    top cap    10:05
    box        10:40   (scheduled)
    bottom cap 11:55

`missProbability` is a separate (and simpler number) but not percentile. If we count how many of those 2,000 flights arrived more than 55 minutes late, if 300 did, that is 0.15, and our screen will says we miss our connection about 15% of the time.

**Note** 5/95 would give wider, more urgent whisker. 25/75 narrower one. I picked 10 90 because it captures normal variation without letting rare disasters define what it looks like.