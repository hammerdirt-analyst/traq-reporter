import {filterTrees} from "./reporter-data.js";

export function projectSlugFromLocation(location, fallbackSlug) {
  const params = new URLSearchParams(location.search);
  return params.get("slug") ?? location.hash.replace(/^#/, "") ?? fallbackSlug;
}

export function createProjectModel(data, slug) {
  const project = data.projects.find((candidate) => candidate.slug === slug) ?? data.projects[0] ?? null;
  const trees = project ? data.trees.filter((tree) => tree.project_slug === project.slug) : [];
  return {project, trees};
}

export function createInitialProjectState() {
  return {species: "all", risk: "all", selectedId: null};
}

export function projectViewModel(trees, state) {
  const filtered = filterTrees(trees, {species: state.species, risk: state.risk});
  const selectedId = state.selectedId && filtered.some((tree) => tree.id === state.selectedId) ? state.selectedId : null;
  const selectedTree = selectedId ? filtered.find((tree) => tree.id === selectedId) : null;
  return {filtered, selectedId, selectedTree};
}
