import test from "node:test";
import assert from "node:assert/strict";
import {mergeProjectSummaries, withProjectContent} from "../src/components/project-content.js";

test("mergeProjectSummaries overlays content onto job-derived projects", () => {
  const projects = mergeProjectSummaries([
    {slug: "alpha", name: "Alpha", tree_count: 2, species_count: 1, risk_counts: {low: 2}, latest_staged_at: "2026-01-01T00:00:00Z", coordinate_count: 2}
  ], [
    {slug: "alpha", name: "Alpha Client Name", description: "Client description.", image: "./alpha.png", map_bounds: {west: 0, south: 0, east: 1, north: 1}}
  ]);

  assert.equal(projects.length, 1);
  assert.equal(projects[0].name, "Alpha Client Name");
  assert.equal(projects[0].tree_count, 2);
  assert.equal(projects[0].description, "Client description.");
  assert.equal(projects[0].has_content, true);
  assert.equal(projects[0].has_jobs, true);
});

test("mergeProjectSummaries includes content-only projects with empty job counts", () => {
  const projects = mergeProjectSummaries([], [
    {slug: "empty", name: "Empty", description: "No jobs yet."}
  ]);

  assert.equal(projects.length, 1);
  assert.equal(projects[0].slug, "empty");
  assert.equal(projects[0].tree_count, 0);
  assert.equal(projects[0].coordinate_count, 0);
  assert.equal(projects[0].has_jobs, false);
});

test("withProjectContent overlays content onto reporter projects", () => {
  const reporter = withProjectContent({
    projects: [{slug: "alpha", name: "Alpha", tree_count: 1, species_count: 1, risk_counts: {low: 1}, coordinate_count: 1}],
    trees: []
  }, [
    {slug: "alpha", name: "Alpha Updated", description: "Updated."},
    {slug: "empty", name: "Empty"}
  ]);

  assert.equal(reporter.projects.length, 2);
  assert.equal(reporter.projects.find((project) => project.slug === "alpha").description, "Updated.");
  assert.equal(reporter.projects.find((project) => project.slug === "empty").tree_count, 0);
});
