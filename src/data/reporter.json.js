import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import {fileURLToPath} from "node:url";
import {mergeProjectSummaries} from "../components/project-content.js";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const defaultJobsRoot = path.resolve(projectRoot, "../server/staging/jobs");
const jobsRoot = path.resolve(process.env.TRAQ_STAGING_ROOT ?? defaultJobsRoot);
const projectContentPath = path.resolve(projectRoot, "src/project-content.json");

const riskOrder = ["extreme", "high", "moderate", "low", "none", "unknown"];

function value(value, fallback = null) {
  return value === undefined ? fallback : value;
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function nonEmptyString(value, fallback) {
  return typeof value === "string" && value.trim() ? value : fallback;
}

function riskKey(value) {
  return String(value ?? "unknown").trim().toLowerCase() || "unknown";
}

function riskCounts(trees) {
  const counts = Object.fromEntries(riskOrder.map((risk) => [risk, 0]));
  for (const tree of trees) counts[riskKey(tree.overall_risk)] = (counts[riskKey(tree.overall_risk)] ?? 0) + 1;
  return counts;
}

function latestDate(values) {
  const timestamps = values
    .map((date) => Date.parse(date))
    .filter((timestamp) => Number.isFinite(timestamp));
  return timestamps.length ? new Date(Math.max(...timestamps)).toISOString() : null;
}

async function normalizeTree(jobNumber, manifest, final, geojson, warnings) {
  const formData = final?.form?.data ?? {};
  const details = formData.client_tree_details ?? {};
  const gps = details.gps ?? {};
  const feature = geojson?.features?.[0];
  const coordinates = feature?.geometry?.type === "Point" ? feature.geometry.coordinates : [];
  const longitude = value(gps.longitude, coordinates[0]);
  const latitude = value(gps.latitude, coordinates[1]);
  const artifacts = manifest?.artifacts ?? {};
  const jobDirectory = path.join(jobsRoot, jobNumber);
  const pdfPath = path.join(jobDirectory, value(artifacts.traq_pdf, "./traq_page1.pdf"));
  const assetBase = `./_file/generated/jobs/${jobNumber}`;

  const images = asArray(manifest?.images).map((image) => {
    const sourcePath = value(image.source_path, null);
    const assetPath = sourcePath?.replace(/^\.\//, "");
    return {
      caption: value(image.caption, ""),
      image_ref: value(image.image_ref, null),
      source_path: sourcePath,
      variant: value(image.variant, null),
      url: assetPath ? `${assetBase}/${assetPath}` : null
    };
  });

  return {
    id: jobNumber,
    job_number: jobNumber,
    job_id: value(final?.job_id, manifest?.job_id),
    project: nonEmptyString(manifest?.project, "Unknown project"),
    project_slug: nonEmptyString(manifest?.project_slug, "unknown-project"),
    species: value(details.tree_species, "Unknown species"),
    tree_number: value(details.tree_number, null),
    assessor: value(details.assessors, final?.user_name ?? null),
    assessed_date: value(details.date, null),
    staged_at: value(manifest?.staged_at, null),
    archived_at: value(final?.archived_at, manifest?.archived_at ?? null),
    address_tree_location: value(details.address_tree_location, null),
    dbh: value(details.dbh, null),
    height: value(details.height, null),
    crown_spread: value(details.crown_spread_dia, null),
    latitude: value(latitude, null),
    longitude: value(longitude, null),
    overall_risk: value(formData.overall_tree_risk_rating?.rating, "unknown"),
    residual_risk: value(formData.overall_residual_risk?.rating, null),
    work_priority: value(formData.work_priority?.priority, null),
    targets: asArray(formData.target_assessment?.targets),
    risk_conditions: asArray(formData.risk_categorization),
    mitigation_options: asArray(formData.mitigation_options?.options),
    recommended_inspection_interval: value(formData.recommended_inspection_interval?.text, null),
    narrative: value(final?.narrative?.text, ""),
    transcript: value(final?.transcript, ""),
    form_data: formData,
    images,
    artifacts: {
      final_json: value(artifacts.final_json, "./final.json"),
      final_geojson: value(artifacts.final_geojson, "./final.geojson"),
      traq_pdf: value(artifacts.traq_pdf, "./traq_page1.pdf"),
      traq_pdf_url: `${assetBase}/traq_page1.pdf`
    },
    revisions: {
      client_revision_id: value(final?.client_revision_id, manifest?.client_revision_id ?? null),
      server_revision_id: value(final?.server_revision_id, null),
      round_id: value(final?.round_id, null)
    },
    source: {
      job_directory: jobDirectory,
      manifest_path: path.join(jobDirectory, "manifest.json"),
      final_json_path: path.join(jobDirectory, "final.json"),
      final_geojson_path: path.join(jobDirectory, "final.geojson"),
      traq_pdf_path: pdfPath
    }
  };
}

function projectSummaries(trees) {
  const byProject = new Map();
  for (const tree of trees) {
    const projectTrees = byProject.get(tree.project_slug) ?? [];
    projectTrees.push(tree);
    byProject.set(tree.project_slug, projectTrees);
  }
  return Array.from(byProject.entries(), ([slug, projectTrees]) => ({
    slug,
    name: nonEmptyString(projectTrees[0]?.project, nonEmptyString(slug, "Unknown project")),
    tree_count: projectTrees.length,
    species_count: new Set(projectTrees.map((tree) => tree.species).filter(Boolean)).size,
    risk_counts: riskCounts(projectTrees),
    latest_staged_at: latestDate(projectTrees.map((tree) => tree.staged_at)),
    coordinate_count: projectTrees.filter((tree) => Number.isFinite(tree.latitude) && Number.isFinite(tree.longitude)).length
  })).sort((a, b) => nonEmptyString(a.name, a.slug).localeCompare(nonEmptyString(b.name, b.slug)));
}

function toGeojson(trees) {
  return {
    type: "FeatureCollection",
    features: trees
      .filter((tree) => Number.isFinite(tree.latitude) && Number.isFinite(tree.longitude))
      .map((tree) => ({
        type: "Feature",
        geometry: {
          type: "Point",
          coordinates: [tree.longitude, tree.latitude]
        },
        properties: {
          id: tree.id,
          job_number: tree.job_number,
          project: tree.project,
          project_slug: tree.project_slug,
          species: tree.species,
          overall_risk: tree.overall_risk,
          residual_risk: tree.residual_risk,
          work_priority: tree.work_priority
        }
      }))
  };
}

async function readJson(filePath) {
  return JSON.parse(await fs.readFile(filePath, "utf8"));
}

async function readProjectContent(warnings) {
  try {
    const content = await readJson(projectContentPath);
    if (!Array.isArray(content)) {
      warnings.push(`${projectContentPath} must contain an array of projects; ignoring project content.`);
      return [];
    }
    return content.filter((project) => {
      if (project?.slug) return true;
      warnings.push("Ignoring project content record without a slug.");
      return false;
    });
  } catch (error) {
    if (error.code !== "ENOENT") warnings.push(`Unable to read project content ${projectContentPath}: ${error.message}`);
    return [];
  }
}

async function main() {
  const warnings = [];
  let entries = [];

  try {
    entries = await fs.readdir(jobsRoot, {withFileTypes: true});
  } catch (error) {
    warnings.push(`Unable to read staging jobs root ${jobsRoot}: ${error.message}`);
  }

  const trees = [];
  const projectContent = await readProjectContent(warnings);
  for (const entry of entries.filter((entry) => entry.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
    const jobNumber = entry.name;
    const jobDirectory = path.join(jobsRoot, jobNumber);

    try {
      const [manifest, final, geojson] = await Promise.all([
        readJson(path.join(jobDirectory, "manifest.json")),
        readJson(path.join(jobDirectory, "final.json")),
        readJson(path.join(jobDirectory, "final.geojson"))
      ]);
      trees.push(await normalizeTree(jobNumber, manifest, final, geojson, warnings));
    } catch (error) {
      warnings.push(`Skipping ${jobNumber}: ${error.message}`);
    }
  }

  const output = {
    metadata: {
      staging_root: jobsRoot,
      generated_at: new Date().toISOString(),
      job_count: trees.length,
      warnings
    },
    projects: mergeProjectSummaries(projectSummaries(trees), projectContent),
    trees,
    geojson: toGeojson(trees)
  };

  process.stdout.write(JSON.stringify(output));
}

main().catch((error) => {
  process.stderr.write(`${error.stack ?? error.message}\n`);
  process.exit(1);
});
