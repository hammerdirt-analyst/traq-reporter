import {el, svgEl} from "./dom.js";
import {riskClass} from "./reporter-data.js";

const width = 760;
const height = 420;
const pad = 34;

export function coordinateLayout(trees) {
  const lats = trees.map((tree) => tree.latitude).filter(Number.isFinite);
  const lons = trees.map((tree) => tree.longitude).filter(Number.isFinite);
  if (!lats.length || !lons.length) return [];

  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const lonSpan = maxLon - minLon || 0.001;
  const latSpan = maxLat - minLat || 0.001;

  return trees
    .filter((tree) => Number.isFinite(tree.latitude) && Number.isFinite(tree.longitude))
    .map((tree) => ({
      tree,
      x: pad + ((tree.longitude - minLon) / lonSpan) * (width - pad * 2),
      y: height - pad - ((tree.latitude - minLat) / latSpan) * (height - pad * 2)
    }));
}

export function renderMap(trees, selectedId, onSelect) {
  if (!trees.length) return el("div", {class: "empty-state"}, "No trees match the current filters.");

  const points = coordinateLayout(trees);
  if (!points.length) return el("div", {class: "empty-state"}, "No mapped coordinates are available for these trees.");

  const svg = svgEl("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": "Tree coordinate map",
    class: "coordinate-map"
  }, [
    svgEl("rect", {x: 0, y: 0, width, height, class: "map-bg"}),
    ...points.map(({tree, x, y}) => svgEl("circle", {
      cx: x,
      cy: y,
      r: selectedId === tree.id ? 10 : 7,
      tabindex: "0",
      class: `map-point ${riskClass(tree.overall_risk)}${selectedId === tree.id ? " is-selected" : ""}`,
      onclick: () => onSelect(tree.id)
    }))
  ]);

  return el("div", {class: "map-panel"}, [
    el("div", {class: "map-caption"}, `${trees.length} filtered tree${trees.length === 1 ? "" : "s"}`),
    svg
  ]);
}
