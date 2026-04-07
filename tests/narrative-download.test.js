import test from "node:test";
import assert from "node:assert/strict";
import {narrativeMarkdown} from "../src/components/narrative-download.js";

test("narrativeMarkdown renders tree identity and narrative", () => {
  const markdown = narrativeMarkdown({
    species: "Quercus agrifolia",
    job_number: "J0002",
    project: "American River",
    tree_number: "1",
    assessor: "Erismann",
    assessed_date: "03/29/2026",
    overall_risk: "low",
    residual_risk: "low",
    narrative: "Tree narrative.",
    risk_conditions: [{condition: "branches"}],
    mitigation_options: [{option: "prune"}]
  });
  assert.equal(markdown.includes("# Quercus agrifolia (J0002)"), true);
  assert.equal(markdown.includes("Tree narrative."), true);
  assert.equal(markdown.includes("branches"), true);
});
