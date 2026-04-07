import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";

const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = path.resolve(projectRoot, "src/generated/jobs");
const outputRoot = path.resolve(projectRoot, "docs/_file/generated/jobs");

async function main() {
  await fs.rm(outputRoot, {recursive: true, force: true});
  await fs.mkdir(path.dirname(outputRoot), {recursive: true});
  await fs.cp(sourceRoot, outputRoot, {recursive: true});
  await fs.writeFile(path.resolve(projectRoot, "docs/.nojekyll"), "");
  console.log(`Copied prepared artifacts to ${path.relative(projectRoot, outputRoot)}`);
}

main().catch((error) => {
  console.error(error.stack ?? error.message);
  process.exit(1);
});
