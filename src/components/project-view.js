import {el} from "./dom.js";
import {renderFilters} from "./filter-controls.js";
import {renderLeafletMap} from "./leaflet-map.js";
import {createInitialProjectState, createProjectModel, projectSlugFromLocation, projectViewModel} from "./project-state.js";
import {renderTreeModal} from "./tree-modal.js";
import {renderTable} from "./tree-table.js";

export function renderProject(data, locationObject = location) {
  const slug = projectSlugFromLocation(locationObject, data.projects[0]?.slug);
  const {project, trees} = createProjectModel(data, slug);
  const state = createInitialProjectState();
  const root = el("div", {class: "project-view"});
  const controls = el("div", {class: "filter-bar"});
  const map = el("div", {class: "tree-map"});
  const table = el("div", {class: "tree-table-wrap"});
  const modalLayer = el("div", {class: "modal-layer"});

  function update(patch) {
    Object.assign(state, patch);
    rerender();
  }

  function rerender() {
    const view = projectViewModel(trees, state);
    state.selectedId = view.selectedId;
    controls.replaceChildren(renderFilters(trees, state, update));
    map.replaceChildren(renderLeafletMap(view.filtered, view.selectedId, (selectedId) => update({selectedId}), project));
    table.replaceChildren(renderTable(view.filtered, view.selectedId, (selectedId) => update({selectedId})));
    const modal = renderTreeModal(view.selectedTree, () => update({selectedId: null}));
    modalLayer.replaceChildren(...(modal ? [modal] : []));
    document.body.classList.toggle("tree-modal-open", Boolean(view.selectedId));
    modalLayer.querySelector(".tree-modal")?.focus();
  }

  function onKeydown(event) {
    if (event.key === "Escape" && state.selectedId) update({selectedId: null});
  }

  document.addEventListener("keydown", onKeydown);

  root.append(
    el("section", {class: "project-header"}, [
      el("a", {href: "./", class: "back-link"}, "Back to all projects"),
      el("h1", {}, project?.name ?? "Project"),
      project?.description ? el("p", {class: "lede"}, project.description) : null,
      project?.image ? el("img", {class: "project-hero-image", src: project.image, alt: ""}) : null
    ]),
    !trees.length ? el("section", {class: "panel empty-state"}, [
      el("h2", {}, "No staged tree jobs yet"),
      el("p", {}, "This project has reporter content, but the staging root does not currently contain completed job bundles for it.")
    ]) : controls,
    !trees.length ? null : el("section", {class: "project-workspace"}, [
      el("div", {class: "project-main"}, [map, table])
    ]),
    modalLayer
  );

  if (trees.length) rerender();
  return root;
}
