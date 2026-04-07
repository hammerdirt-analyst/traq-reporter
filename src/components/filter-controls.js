import {el} from "./dom.js";
import {riskLabel, riskOrder, speciesOptions} from "./reporter-data.js";

export function renderFilters(trees, state, onChange) {
  const speciesSelect = el("select", {onchange: (event) => onChange({species: event.target.value})}, [
    el("option", {value: "all"}, "All species"),
    ...speciesOptions(trees).map((name) => el("option", {value: name}, name))
  ]);
  speciesSelect.value = state.species;

  const riskSelect = el("select", {onchange: (event) => onChange({risk: event.target.value})}, [
    el("option", {value: "all"}, "All risks"),
    ...riskOrder.map((risk) => el("option", {value: risk}, riskLabel(risk)))
  ]);
  riskSelect.value = state.risk;

  return el("div", {class: "filter-bar-inner"}, [
    el("label", {}, ["Species", speciesSelect]),
    el("label", {}, ["Risk", riskSelect]),
    el("button", {type: "button", onclick: () => onChange({species: "all", risk: "all", selectedId: null})}, "Reset filters")
  ]);
}
