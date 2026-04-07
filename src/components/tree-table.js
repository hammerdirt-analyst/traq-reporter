import {el} from "./dom.js";
import {fmt, fmtNumber, riskClass, riskLabel} from "./reporter-data.js";

export function renderTable(trees, selectedId, onSelect) {
  const table = el("table", {class: "tree-table"}, [
    el("thead", {}, el("tr", {}, ["Job", "Species", "Risk", "DBH", "Height", "Targets"].map((label) => el("th", {}, label)))),
    el("tbody", {}, trees.map((tree) => el("tr", {
      class: selectedId === tree.id ? "is-selected" : "",
      onclick: () => onSelect(tree.id)
    }, [
      el("td", {}, tree.job_number),
      el("td", {}, fmt(tree.species)),
      el("td", {class: `risk-cell ${riskClass(tree.overall_risk)}`}, riskLabel(tree.overall_risk)),
      el("td", {}, fmtNumber(tree.dbh, " in")),
      el("td", {}, fmtNumber(tree.height, " ft")),
      el("td", {}, tree.targets.map((target) => target.label).filter(Boolean).join(", ") || "Not recorded")
    ])))
  ]);
  return el("div", {}, [
    el("div", {class: "table-caption"}, `${trees.length} tree${trees.length === 1 ? "" : "s"} in table`),
    table
  ]);
}
