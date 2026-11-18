const PERIODS = ["all", "2025-10", "2026-01", "2026-04", "2026-07"];
const LABELS = {
  all: "All seasons",
  "2025-10": "October 2025",
  "2026-01": "January 2026",
  "2026-04": "April 2026",
  "2026-07": "July 2026",
};

function urlFrom(id) {
  const el = document.getElementById(id);
  if (!el) {
    console.warn(`globe.js: no #${id} in the template -- skipping that layer`);
    return "";
  }
  return el.value;
}

const globe_im_url = urlFrom("globe-img-url");
const earth_topology_url = ""; // TODO
const fixtures_arcs_url = urlFrom("fixtures-arcs-url");
const fixtures_paths_url = urlFrom("fixtures-paths-url");
const fixtures_world_url = urlFrom("fixtures-world-url");

console.log(globe_im_url);

let periodIdx = 0,
  allArcs = [],
  paths = [],
  worldRoutes = [];
let showPaths = false,
  showAirports = false,
  showWorld = true;

const rateOf = (d) =>
  periodIdx === 0 ? d.rate : (d.byMonth[PERIODS[periodIdx]] ?? d.rate);
const hue = (r, a) =>
  `hsla(${210 - Math.min(r / 0.7, 1) * 210}, 85%, 60%, ${a})`;

// world routes are w/ OpenFlights + have no disruption
// data so we don't want to take a color
// grey mean 'connected but no stats'
const WORLD_COLOR = "rgba(150,162,178,0.45)";
// thin tube - setting this to null makes globe.gl draw plain lines which is cheaper if we raise MAX_ARCS in make_world_routes
const WORLD_STROKE = 0.05;
// how high grey arcs bow. globe.gl scales this by route length, so a transatlantic hop arcs high and a short one stays low
// returning null from arcAltitude is what hands control
const WORLD_BOW = 0.4;

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
  // null hand this arc over to arcAltitudeAutoScale below
  .arcAltitude((d) => (d.world ? null : 0.03 + rateOf(d) * 0.25))
  .arcAltitudeAutoScale((d) => (d.world ? WORLD_BOW : 0))
  .arcStroke((d) =>
    d.world ? WORLD_STROKE : 0.03 + Math.sqrt(d.flights) / 500,
  )
  .arcColor((d) =>
    d.world
      ? [WORLD_COLOR, WORLD_COLOR]
      : [hue(rateOf(d), 0.12), hue(rateOf(d), 0.65)],
  )
  .arcDashLength((d) => (d.world ? 1 : 0.25))
  .arcDashGap((d) => (d.world ? 0 : 1))
  .arcDashInitialGap((d) => (d.world ? 0 : Math.random()))
  .arcDashAnimateTime((d) => (d.world ? 0 : 4000))
  .arcsTransitionDuration(0)
  .arcLabel((d) =>
    d.world
      ? `${d.pair} — in the world network, not measured`
      : `${d.route} — ${(rateOf(d) * 100).toFixed(0)}% disrupted · ${d.flights} flights`,
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
  const measured = showPaths
    ? allArcs.filter((a) => routes.has(a.route))
    : allArcs;
  // world routes go first so measured arcs are drawn over the top
  const arcs = showWorld ? [...worldRoutes, ...measured] : [...measured];
  world.arcsData(arcs);
  world.pathsData(showPaths ? paths : []);
  world.htmlElementsData(showAirports ? airportsFrom(allArcs) : []);
  // globe_panel.html reuses this script w/o legend so neither of these elements is guaranteed to exist
  const period = document.getElementById("period");
  if (period) period.textContent = LABELS[PERIODS[periodIdx]];
  const worldRow = document.getElementById("world-row");
  if (worldRow) worldRow.classList.toggle("off", !showWorld);
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

function load(url, label, apply) {
  if (!url) return;
  fetch(url)
    .then((r) => {
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return r.json();
    })
    .then((d) => {
      apply(d);
      refresh();
    })
    .catch((e) => console.error(`${label} failed to load:`, e));
}

load(fixtures_arcs_url, "measured arcs", (d) => (allArcs = d));
load(fixtures_paths_url, "flight paths", (d) => (paths = d));
load(fixtures_world_url, "world routes", (d) => {
  worldRoutes = d.map((a) => ({ ...a, world: true }));
});

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
  if (k === "c") {
    showWorld = !showWorld;
    refresh();
  }
});
