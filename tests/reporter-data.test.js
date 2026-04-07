import test from "node:test";
import assert from "node:assert/strict";
import {filterTrees, portfolioSummary, riskClass, riskCounts, speciesOptions, truncateText} from "../src/components/reporter-data.js";

const trees = [
  {id: "a", species: "Oak", project_slug: "p", overall_risk: "low", latitude: 1, longitude: 2},
  {id: "b", species: "Maple", project_slug: "p", overall_risk: "moderate", latitude: null, longitude: 2},
  {id: "c", species: "Oak", project_slug: "p", overall_risk: null, latitude: 3, longitude: 4}
];

test("filterTrees filters by species and risk", () => {
  assert.deepEqual(filterTrees(trees, {species: "Oak", risk: "low"}).map((tree) => tree.id), ["a"]);
  assert.deepEqual(filterTrees(trees, {species: "all", risk: "unknown"}).map((tree) => tree.id), ["c"]);
});

test("speciesOptions returns sorted unique species", () => {
  assert.deepEqual(speciesOptions(trees), ["Maple", "Oak"]);
});

test("riskCounts includes all known risk buckets", () => {
  assert.equal(riskCounts(trees).low, 1);
  assert.equal(riskCounts(trees).moderate, 1);
  assert.equal(riskCounts(trees).unknown, 1);
  assert.equal(riskCounts(trees).high, 0);
});

test("riskClass maps risk values to shared CSS class names", () => {
  assert.equal(riskClass("low"), "risk-low");
  assert.equal(riskClass("moderate"), "risk-moderate");
  assert.equal(riskClass("high"), "risk-high");
  assert.equal(riskClass(null), "risk-unknown");
});

test("portfolioSummary summarizes projects, trees, species, and mapped records", () => {
  const summary = portfolioSummary({projects: [{slug: "p"}], trees});
  assert.equal(summary.project_count, 1);
  assert.equal(summary.tree_count, 3);
  assert.equal(summary.species_count, 2);
  assert.equal(summary.coordinate_count, 2);
});

test("truncateText caps long descriptions and appends ellipsis", () => {
  assert.equal(truncateText("short", 100), "short");
  assert.equal(truncateText("a".repeat(101), 100), `${"a".repeat(100)}...`);
});
