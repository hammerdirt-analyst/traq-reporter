# TRAQ Observable Reporter

This is an [Observable Framework](https://observablehq.com/framework/) app for reporting staged TRAQ observation jobs.

The reporter reads completed job bundles from the local staging root:

```text
../server/staging/jobs/<job_number>/
```

Set `TRAQ_STAGING_ROOT` to point at a different `jobs` directory.

Project-specific reporter content lives in:

```text
src/project-content.json
```

Use this file for descriptions, project images, and map bounding boxes that are not part of the server-produced job bundles. Projects defined there appear in the UI even if no staged tree jobs exist yet.

The pages load this file directly as an Observable `FileAttachment`, so edits to `src/project-content.json` are explicit page inputs. If the dev server still shows old content, run `npm run clean` and restart `npm run dev`; for published output, rerun `npm run build`.

Tree artifacts are first copied from staging into a reporter-owned generated source cache:

```text
src/generated/jobs/<job_number>/
```

During `npm run build`, Observable writes the site to `docs/`, and the prepared artifacts are then copied into:

```text
docs/_file/generated/jobs/<job_number>/
```

Run `npm run prepare:artifacts` to refresh the cache manually. The copy steps only delete/recreate reporter-owned files under `src/generated/jobs` and `docs/_file/generated/jobs`; they never mutate `../server/staging`.

GitHub Pages must publish from `main` and `/docs`. The build writes `docs/.nojekyll` so GitHub Pages serves Observable's underscored asset directories, including `_observablehq`, `_import`, `_file`, `_node`, and `_npm`.

Site-level copy lives in:

```text
src/site-content.json
```

Use this file for the home page eyebrow, title, opening copy, and home-page links. It is also loaded directly as an Observable `FileAttachment`.

To install the required dependencies, run:

```
npm install
```

Then, to start the local preview server, run:

```
npm run dev
```

Then visit <http://localhost:3000> to preview your app.

For more on the agreed design, see `notes/reporter-ui-design.md` and `notes/implementation-plan.md`.

## Current Structure

The first implementation contains:

```ini
.
├─ src
│  ├─ components
│  │  ├─ reporter-data.js      # formatting and filtering helpers
│  │  ├─ reporter-styles.js    # app styles
│  │  └─ reporter-ui.js        # home and project UI exports
│  ├─ data
│  │  └─ reporter.json.js      # staged job data loader
│  ├─ index.md                 # portfolio home page
│  └─ project.md               # generic project view
├─ notes
│  ├─ implementation-plan.md
│  └─ reporter-ui-design.md
├─ .gitignore
├─ observablehq.config.js      # the app config file
├─ package.json
└─ README.md
```

The project page uses Leaflet with OpenStreetMap tiles. Tree detail opens in a blocking modal with TRAQ form data, transcript, images, and a TRAQ PDF download link.

## Command reference

| Command           | Description                                              |
| ----------------- | -------------------------------------------------------- |
| `npm install`            | Install or reinstall dependencies                        |
| `npm run dev`        | Start local preview server                               |
| `npm run build`      | Build your static site, generating `./docs`              |
| `npm run deploy`     | Deploy your app to Observable                            |
| `npm run clean`      | Clear the local data loader cache                        |
| `npm run observable` | Run commands like `observable help`                      |
