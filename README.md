# Reporter Client

This repo is designed to run through `uv`.

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

## Main Commands

Generate docs:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync reporter-client generate-docs
```

The repo-root config is [reporter_client.yaml](/home/roger/projects/codex_trial/agent_client/reporter_client/reporter_client.yaml). It currently points the staged-job root at:

```text
../server/testdata/staged_jobs_manual
```

Run tests:

```bash
env OPENAI_API_KEY='' UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m unittest discover -s tests -p 'test_*.py'
```

Use `discover` as the standard unittest entrypoint for this repo. Plain
`python -m unittest` is not the supported test command here.

Serve the MkDocs site locally:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync mkdocs serve -a 0.0.0.0:8000
```

Build the MkDocs site:

```bash
env UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync mkdocs build
```

## Notes

- `OPENAI_API_KEY` enables the real summary-generation path.
- If `OPENAI_API_KEY` is not set, the summary generator falls back to the local stub path.
- `REPORTER_OPENAI_SUMMARY_MODEL` is optional. If omitted, the default is `gpt-4o-mini`.
