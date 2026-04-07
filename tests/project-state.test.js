import test from "node:test";
import assert from "node:assert/strict";
import {createProjectModel, projectSlugFromLocation, projectViewModel} from "../src/components/project-state.js";

const data = {
  projects: [{slug: "alpha", name: "Alpha"}, {slug: "beta", name: "Beta"}],
  trees: [
    {id: "a", project_slug: "alpha", species: "Oak", overall_risk: "low"},
    {id: "b", project_slug: "beta", species: "Maple", overall_risk: "low"}
  ]
};

test("projectSlugFromLocation reads query string before hash", () => {
  assert.equal(projectSlugFromLocation({search: "?slug=beta", hash: "#alpha"}, "alpha"), "beta");
});

test("createProjectModel falls back to first project", () => {
  const model = createProjectModel(data, "missing");
  assert.equal(model.project.slug, "alpha");
  assert.deepEqual(model.trees.map((tree) => tree.id), ["a"]);
});

test("projectViewModel clears selection filtered out of view", () => {
  const view = projectViewModel(data.trees, {species: "Oak", risk: "all", selectedId: "b"});
  assert.deepEqual(view.filtered.map((tree) => tree.id), ["a"]);
  assert.equal(view.selectedId, null);
  assert.equal(view.selectedTree, null);
});
