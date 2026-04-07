import L from "../../_node/leaflet@1.9.4/index.e6e42d4c.js";
import {el} from "./dom.d2c937d2.js";
import {boundsFromProject, treeLatLngs} from "./map-bounds.b4997607.js";
import {riskKey} from "./reporter-data.243ef50a.js";

const riskColors = {
  low: "#16833a",
  moderate: "#c89b00",
  high: "#c92a1f",
  extreme: "#c92a1f",
  none: "#777777",
  unknown: "#777777"
};

export function boundsFromTrees(trees) {
  const points = treeLatLngs(trees);
  return points.length ? L.latLngBounds(points) : null;
}

export function renderLeafletMap(trees, selectedId, onSelect, project) {
  if (!trees.length) return el("div", {class: "empty-state"}, "No trees match the current filters.");

  const mappedTrees = trees.filter((tree) => Number.isFinite(tree.latitude) && Number.isFinite(tree.longitude));
  if (!mappedTrees.length) return el("div", {class: "empty-state"}, "No mapped coordinates are available for these trees.");

  const container = el("div", {class: "map-panel"}, [
    el("div", {class: "map-caption"}, `${trees.length} filtered tree${trees.length === 1 ? "" : "s"}`),
    el("div", {class: "leaflet-map"})
  ]);
  const mapNode = container.querySelector(".leaflet-map");

  requestAnimationFrame(() => {
    const map = L.map(mapNode, {scrollWheelZoom: false});
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    for (const tree of mappedTrees) {
      const risk = riskKey(tree.overall_risk);
      L.circleMarker([tree.latitude, tree.longitude], {
        radius: selectedId === tree.id ? 9 : 7,
        color: selectedId === tree.id ? "#111111" : "#ffffff",
        weight: selectedId === tree.id ? 3 : 2,
        fillColor: riskColors[risk] ?? riskColors.unknown,
        fillOpacity: 0.95
      })
        .addTo(map)
        .bindTooltip(`${tree.job_number}: ${tree.species}`)
        .on("click", () => onSelect(tree.id));
    }

    const bounds = boundsFromProject(project) ?? boundsFromTrees(mappedTrees);
    if (bounds) map.fitBounds(bounds, {padding: [24, 24], maxZoom: 18});
    else map.setView([mappedTrees[0].latitude, mappedTrees[0].longitude], 17);
  });

  return container;
}
