import {el} from "./dom.js";
import {fmt, riskLabel, riskOrder} from "./reporter-data.js";

export function stat(label, value) {
  return el("div", {class: "stat-card"}, [
    el("div", {class: "stat-value"}, value),
    el("div", {class: "stat-label"}, label)
  ]);
}

export function riskPills(counts) {
  return el("div", {class: "risk-pills"}, riskOrder
    .filter((risk) => counts?.[risk])
    .map((risk) => el("span", {class: `risk-pill risk-${risk}`}, `${riskLabel(risk)} ${counts[risk]}`)));
}

export function keyValues(values) {
  return el("dl", {class: "key-values"}, Object.entries(values).flatMap(([key, value]) => [
    el("dt", {}, key),
    el("dd", {}, fmt(value))
  ]));
}

export function detailSection(title, content, open = false) {
  return el("details", {open: open ? "" : null, class: "detail-section"}, [
    el("summary", {}, title),
    content
  ]);
}

export function renderObjectList(items) {
  if (!items?.length) return el("p", {class: "muted"}, "Not recorded.");
  return el("div", {class: "object-list"}, items.map((item) => keyValues(item)));
}
