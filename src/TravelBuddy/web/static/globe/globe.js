const PERIODS = ["all", "2025-10", "2026-01", "2026-04", "2026-07"];
const LABELS = {
  all: "All seasons",
  "2025-10": "October 2025",
  "2026-01": "January 2026",
  "2026-04": "April 2026",
  "2026-07": "July 2026",
};

const globe_im_url = document.getElementById("globe-img-url").value;
const earth_topology_url = ""; // TODO: CLARIFY;
const fixtures_arcs_url = document.getElementById("fixtures-arcs-url").value;
const fixtures_paths_url = document.getElementById("fixtures-paths-url").value;

console.log(globe_im_url);

let periodIdx = 0,
  allArcs = [],
  paths = [];
let showPaths = false,
  showAirports = false;

const rateOf = (d) =>
  periodIdx === 0 ? d.rate : (d.byMonth[PERIODS[periodIdx]] ?? d.rate);
const hue = (r, a) =>
  `hsla(${210 - Math.min(r / 0.7, 1) * 210}, 85%, 60%, ${a})`;

const world = Globe()(document.getElementById("globe"))
  .globeImageUrl(globe_im_url)
  .bumpImageUrl(earth_topology_url)
  .backgroundColor("#000")
  .showAtmosphere(true)
  .atmosphereColor("#6cc5ff")
  .atmosphereAltitude(0.18);

world.globeMaterial().bumpScale = 2;
world.globeMaterial().shininess = 12;
world.controls().zoomSpeed = 2.5;

world
  .arcAltitude((d) => 0.03 + rateOf(d) * 0.25)
  .arcStroke((d) => 0.03 + Math.sqrt(d.flights) / 500)
  .arcColor((d) => [hue(rateOf(d), 0.12), hue(rateOf(d), 0.65)])
  .arcDashLength(0.25)
  .arcDashGap(1)
  .arcDashInitialGap(() => Math.random())
  .arcDashAnimateTime(4000)
  .arcsTransitionDuration(0)
  .arcLabel(
    (d) =>
      `${d.route} — ${(rateOf(d) * 100).toFixed(0)}% disrupted · ${d.flights} flights`,
  );

world
  .pathPoints("points")
  .pathPointLat((p) => p[0])
  .pathPointLng((p) => p[1])
  .pathPointAlt(0.02)
  .pathColor(() => ["rgba(108,197,255,0.85)", "rgba(255,209,102,0.95)"])
  .pathStroke(2.5)
  .pathDashLength(0.08)
  .pathDashGap(0.012)
  .pathDashAnimateTime(9000)
  .pathTransitionDuration(0)
  .pathLabel(
    (d) =>
      `${d.route} · ${d.callsign} · ${(d.deviationPct * 100).toFixed(1)}% longer than direct`,
  );

world
  .htmlElement((d) => {
    const el = document.createElement("div");
    el.className = "apm";
    el.innerHTML = `<div class="dot"></div><div class="code">${d.code}</div>`;
    return el;
  })
  .htmlElementVisibilityModifier((el, isVisible) => {
    el.style.opacity = isVisible ? 1 : 0;
  });

function airportsFrom(arcs) {
  const seen = {};
  arcs.forEach((a) => {
    const [o, d] = a.route.split("-");
    (seen[o] ??= { code: o, lat: a.startLat, lng: a.startLng, n: 0 }).n++;
    (seen[d] ??= { code: d, lat: a.endLat, lng: a.endLng, n: 0 }).n++;
  });
  return Object.values(seen)
    .sort((x, y) => y.n - x.n)
    .slice(0, 16);
}

function refresh() {
  const routes = new Set(paths.map((p) => p.route));
  const arcs = showPaths ? allArcs.filter((a) => routes.has(a.route)) : allArcs;
  world.arcsData([...arcs]);
  world.pathsData(showPaths ? paths : []);
  world.htmlElementsData(showAirports ? airportsFrom(allArcs) : []);
  document.getElementById("period").textContent = LABELS[PERIODS[periodIdx]];
}

const VIEWS = {
  us: { lat: 39, lng: -98, altitude: 1.1 },
  west: { lat: 37, lng: -115, altitude: 0.6 },
  globe: { lat: 20, lng: -60, altitude: 2.5 },
};
function view(n) {
  world.pointOfView(VIEWS[n], 1000);
}
function zoom(f) {
  const p = world.pointOfView();
  world.pointOfView(
    { ...p, altitude: Math.min(4, Math.max(0.25, p.altitude * f)) },
    300,
  );
}

fetch(fixtures_arcs_url)
  .then((r) => r.json())
  .then((d) => {
    allArcs = d;
    refresh();
  })
  .catch((e) => console.error("arcs failed to load:", e));

fetch(fixtures_paths_url)
  .then((r) => r.json())
  .then((d) => {
    paths = d;
  })
  .catch((e) => console.error("paths failed to load:", e));

document.addEventListener("keydown", (e) => {
  const k = e.key.toLowerCase();
  if (k === "p") {
    showPaths = !showPaths;
    refresh();
    if (showPaths) view("west");
  }
  if (k === "m") {
    periodIdx = (periodIdx + 1) % PERIODS.length;
    refresh();
  }
  if (k === "a") {
    showAirports = !showAirports;
    refresh();
  }
});