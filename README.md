# Reporter Client

This repo builds the local reporter documentation site from staged job bundles in the sibling `server` repo.

The generated MkDocs source lives in [site-src](/home/roger/projects/codex_trial/agent_client/reporter_client/site-src). The deployable built site lives in [docs](/home/roger/projects/codex_trial/agent_client/reporter_client/docs) and is committed for GitHub Pages.

## What This Repo Does

- reads staged job bundles from the configured staging root
- publishes assets into `site-src/assets/...`
- renders:
  - home page
  - project pages
  - tree pages
- generates:
  - tree summaries
  - project maps
  - tree maps
- serves the documentation through MkDocs

## Repo Layout

- source code: [src/reporter_client](/home/roger/projects/codex_trial/agent_client/reporter_client/src/reporter_client)
- authored content: [content](/home/roger/projects/codex_trial/agent_client/reporter_client/content)
- generated docs source: [site-src](/home/roger/projects/codex_trial/agent_client/reporter_client/site-src)
- deployable built site: [docs](/home/roger/projects/codex_trial/agent_client/reporter_client/docs)
- config: [reporter_client.yaml](/home/roger/projects/codex_trial/agent_client/reporter_client/reporter_client.yaml)
- tests: [tests](/home/roger/projects/codex_trial/agent_client/reporter_client/tests)

## Setup

1. Create or update `.env` in the repo root.

```env
OPENAI_API_KEY=your_openai_api_key_here
REPORTER_OPENAI_SUMMARY_MODEL=gpt-4o-mini
```

You can copy from [.env.example](/home/roger/projects/codex_trial/agent_client/reporter_client/.env.example).

2. Sync dependencies:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv sync
```

## Configuration

The repo-root config is [reporter_client.yaml](/home/roger/projects/codex_trial/agent_client/reporter_client/reporter_client.yaml).

The current staged-job root is:

```text
../server/staging
```

That means the reporter expects staged manifests under:

```text
../server/staging/jobs/*/manifest.json
```

## CLI Manual

### `generate-docs`

Regenerates the full docs set from the current staged job bundles and authored content.

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync reporter-client generate-docs
```

Use this when:
- you want a full refresh
- you changed templates
- you changed content
- you want to force tree summaries to regenerate

### `publish-staged`

Runs the incremental staged publication path.

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync reporter-client publish-staged
```

What it does:
- scans staged manifests
- compares them to the local publish index
- rebuilds only new or changed jobs
- republishes affected project pages
- republishes home/about when needed

Use this for normal day-to-day staged publishing.

### `build-basemap`

Builds an exact project basemap from OpenStreetMap tiles using the provided bounding box.

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync reporter-client build-basemap \
  --slug briarwood \
  --west -121.28101670195525 \
  --east -121.27448722406692 \
  --south 38.613356397796935 \
  --north 38.61699761222076
```

What it writes:
- `site-src/assets/map-bases/<slug>_base.jpg`
- `site-src/assets/map-bases/<slug>_base.json`

No padding is added by the tool. The supplied bounding box is used exactly.

## Local Build Workflow

### Run tests

```bash
env OPENAI_API_KEY='' UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m unittest discover -s tests -p 'test_*.py'
```

Use `discover` as the standard unittest entrypoint for this repo. Plain `python -m unittest` is not the supported command here.

### Generate docs

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync reporter-client generate-docs
```

### Serve locally

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync mkdocs serve -a 0.0.0.0:8000
```

Open:

```text
http://127.0.0.1:8000/traq-reporter/
```

### Build the MkDocs site

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync mkdocs build
```

## Git And Build Notes

There is no checked-in CI workflow file in this repo right now. The build workflow is local and command-driven:

1. run tests
2. run `reporter-client generate-docs` or `reporter-client publish-staged`
3. run `mkdocs serve` for review or `mkdocs build` for a site build
4. review changes in `site-src/`
5. run `mkdocs build`
6. review changes in `docs/`
7. commit the source and built site together when appropriate

Important repo behavior:
- `site-src/` is treated as generated MkDocs source and is committed
- `docs/` is the built GitHub Pages output and is committed
- `site/` is an unused local build path and is ignored
- `.state/` is local runtime state and is ignored

## Basemap Bounding Boxes

These are the exact bounding-box coordinates passed to OpenStreetMap when building project basemaps.

### Briarwood

```text
west  = -121.28101670195525
east  = -121.27448722406692
south = 38.613356397796935
north = 38.61699761222076
```

### American River

```text
west  = -121.29353585346439
east  = -121.2838424751227
south = 38.61734479859987
north = 38.62316523581157
```

### Arboretum

```text
west  = -121.43074717273919
east  = -121.4267454093663
south = 38.563799990800874
north = 38.56620294217032
```

## Notes

- `OPENAI_API_KEY` enables the real tree summary-generation path.
- If `OPENAI_API_KEY` is not set, the summary generator falls back to the local stub path.
- `REPORTER_OPENAI_SUMMARY_MODEL` is optional. If omitted, the default is `gpt-4o-mini`.
