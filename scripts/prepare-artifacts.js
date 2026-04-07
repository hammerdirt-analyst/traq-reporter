import fs from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import {fileURLToPath} from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const defaultJobsRoot = path.resolve(projectRoot, "../server/staging/jobs");
const jobsRoot = path.resolve(process.env.TRAQ_STAGING_ROOT ?? defaultJobsRoot);
const outputRoot = path.resolve(projectRoot, "src/generated/jobs");

async function pathExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function copyIfExists(source, destination) {
  if (!(await pathExists(source))) return false;
  await fs.mkdir(path.dirname(destination), {recursive: true});
  await fs.copyFile(source, destination);
  return true;
}

async function copyJobArtifacts(jobNumber) {
  const jobDirectory = path.join(jobsRoot, jobNumber);
  const outputDirectory = path.join(outputRoot, jobNumber);
  const manifest = JSON.parse(await fs.readFile(path.join(jobDirectory, "manifest.json"), "utf8"));
  let copied = 0;

  if (await copyIfExists(path.join(jobDirectory, "traq_page1.pdf"), path.join(outputDirectory, "traq_page1.pdf"))) copied += 1;

  for (const image of manifest.images ?? []) {
    if (!image.source_path) continue;
    const relativePath = image.source_path.replace(/^\.\//, "");
    if (await copyIfExists(path.join(jobDirectory, relativePath), path.join(outputDirectory, relativePath))) copied += 1;
  }

  return copied;
}

async function main() {
  const entries = await fs.readdir(jobsRoot, {withFileTypes: true});

  // This deletes only reporter-owned copied artifacts. It never mutates server staging.
  await fs.rm(outputRoot, {recursive: true, force: true});
  await fs.mkdir(outputRoot, {recursive: true});

  let jobCount = 0;
  let artifactCount = 0;
  for (const entry of entries.filter((entry) => entry.isDirectory()).sort((a, b) => a.name.localeCompare(b.name))) {
    jobCount += 1;
    artifactCount += await copyJobArtifacts(entry.name);
  }

  console.log(`Prepared ${artifactCount} artifacts for ${jobCount} jobs in ${path.relative(projectRoot, outputRoot)}`);
}

main().catch((error) => {
  console.error(error.stack ?? error.message);
  process.exit(1);
});
