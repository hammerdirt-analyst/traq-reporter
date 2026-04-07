export const riskOrder = ["extreme", "high", "moderate", "low", "none", "unknown"];

export const sectionLabels = {
  client_tree_details: "Client and Tree Details",
  site_factors: "Site Factors",
  target_assessment: "Target Assessment",
  trunk: "Trunk",
  roots_and_root_collar: "Roots and Root Collar",
  crown_and_branches: "Crown and Branches",
  tree_health_and_species: "Tree Health and Species",
  load_factors: "Load Factors",
  inspection_limitations: "Inspection Limitations",
  inspection_limitations_describe: "Inspection Limitations Description",
  risk_categorization: "Risk Categorization",
  mitigation_options: "Mitigation Options",
  overall_tree_risk_rating: "Overall Tree Risk Rating",
  overall_residual_risk: "Overall Residual Risk",
  recommended_inspection_interval: "Recommended Inspection Interval",
  work_priority: "Work Priority",
  notes_explanations_descriptions: "Notes, Explanations, and Descriptions",
  advanced_assessment_needed: "Advanced Assessment Needed",
  advanced_assessment_type_reason: "Advanced Assessment Type and Reason",
  data_status: "Data Status"
};

export function fmt(value, fallback = "Not recorded") {
  if (value === null || value === undefined || value === "") return fallback;
  return String(value);
}

export function fmtNumber(value, suffix = "") {
  return Number.isFinite(value) ? `${value}${suffix}` : "Not recorded";
}

export function fmtDate(value) {
  if (!value) return "Not recorded";
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) return value;
  return new Intl.DateTimeFormat("en", {year: "numeric", month: "short", day: "numeric"}).format(new Date(parsed));
}

export function riskKey(value) {
  return String(value ?? "unknown").trim().toLowerCase() || "unknown";
}

export function riskLabel(value) {
  const risk = riskKey(value);
  return risk === "unknown" ? "Unknown" : risk[0].toUpperCase() + risk.slice(1);
}

export function riskClass(value) {
  return `risk-${riskKey(value)}`;
}

export function riskCounts(trees) {
  const counts = Object.fromEntries(riskOrder.map((risk) => [risk, 0]));
  for (const tree of trees) counts[riskKey(tree.overall_risk)] = (counts[riskKey(tree.overall_risk)] ?? 0) + 1;
  return counts;
}

export function projectTrees(data, slug) {
  return data.trees.filter((tree) => tree.project_slug === slug);
}

export function speciesOptions(trees) {
  return Array.from(new Set(trees.map((tree) => tree.species).filter(Boolean))).sort((a, b) => a.localeCompare(b));
}

export function filterTrees(trees, filters = {}) {
  const species = filters.species ?? "all";
  const risk = filters.risk ?? "all";
  return trees.filter((tree) => {
    const speciesMatch = species === "all" || tree.species === species;
    const riskMatch = risk === "all" || riskKey(tree.overall_risk) === risk;
    return speciesMatch && riskMatch;
  });
}

export function portfolioSummary(data) {
  const trees = data.trees ?? [];
  const projects = data.projects ?? [];
  return {
    project_count: projects.length,
    tree_count: trees.length,
    species_count: new Set(trees.map((tree) => tree.species).filter(Boolean)).size,
    coordinate_count: trees.filter((tree) => Number.isFinite(tree.latitude) && Number.isFinite(tree.longitude)).length,
    risk_counts: riskCounts(trees)
  };
}

export function sectionLabel(key) {
  return sectionLabels[key] ?? key.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function truncateText(text, maxLength = 100) {
  const value = fmt(text, "").trim();
  if (value.length <= maxLength) return value;
  return `${value.slice(0, maxLength).trimEnd()}...`;
}
