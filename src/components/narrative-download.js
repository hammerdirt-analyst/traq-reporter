import {fmt, riskLabel} from "./reporter-data.js";

export function narrativeMarkdown(tree) {
  return [
    `# ${fmt(tree.species)} (${tree.job_number})`,
    "",
    `Project: ${fmt(tree.project)}`,
    `Tree number: ${fmt(tree.tree_number)}`,
    `Assessor: ${fmt(tree.assessor)}`,
    `Assessment date: ${fmt(tree.assessed_date)}`,
    `Overall risk: ${riskLabel(tree.overall_risk)}`,
    `Residual risk: ${riskLabel(tree.residual_risk)}`,
    "",
    "## Narrative",
    "",
    tree.narrative || "No narrative recorded.",
    "",
    "## Risk Conditions",
    "",
    JSON.stringify(tree.risk_conditions, null, 2),
    "",
    "## Mitigation Options",
    "",
    JSON.stringify(tree.mitigation_options, null, 2)
  ].join("\n");
}

export function downloadNarrative(tree) {
  const blob = new Blob([narrativeMarkdown(tree)], {type: "text/markdown"});
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${tree.job_number}-narrative.md`;
  link.click();
  URL.revokeObjectURL(link.href);
}
