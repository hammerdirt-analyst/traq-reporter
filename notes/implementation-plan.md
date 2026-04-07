# Observable Reporter Implementation Plan

## Goal

Build an Observable Framework reporter that reads real staged TRAQ job bundles, summarizes the portfolio on the home page, and provides a project-level interactive map/table/sidebar interface for inspecting individual tree assessments.

The first implementation should prove the core loop:

```text
staged observation JSON -> normalized tree records -> project summary -> project map/table -> selected tree details/export links
```

## Constraints

- Source data lives outside the Observable source tree at `../server/staging/jobs`.
- Each job bundle contains `manifest.json`, `final.json`, `final.geojson`, `traq_page1.pdf`, and `images/`.
- The project currently has only `@observablehq/framework` as a runtime dependency.
- Do not invent a new domain model. Normalize the staged model only enough to support the UI.
- Preserve traceability back to staged job artifacts and TRAQ form sections.
- Defer a separate tree page unless a shareable single-tree report becomes a requirement.
- Keep browser rendering modules small. Pure data, state, layout, and export formatting logic should live in separate modules with Node tests.
- Do not grow a catch-all UI file. New features should be added as focused modules with explicit ownership.

## Architecture Principles

The reporter should be organized around testable seams:

- Data loader: reads staged files and normalizes records.
- Data helpers: formatting, filtering, summaries, and labels.
- State helpers: selected project, filter state, selected tree behavior.
- Layout helpers: map coordinate projection and other pure calculations.
- Export helpers: narrative Markdown and future artifact-link generation.
- View modules: home, project shell, filters, map, table, sidebar.
- Thin barrel modules: re-export stable page-facing APIs only.

Unit tests should target the pure modules first. DOM rendering tests can be added later if the UI grows complex enough to justify a DOM test dependency.

## Phase 1: Data Loader

Create a loader that reads the staged jobs and emits one app-facing JSON bundle.

Likely file:

```text
src/data/reporter.json.js
```

Responsibilities:

- Resolve staging root from `TRAQ_STAGING_ROOT`, falling back to `../server/staging/jobs` relative to the project root.
- Read reporter-owned project content from `src/project-content.json`.
- List job directories.
- For each job, read `manifest.json`, `final.json`, and `final.geojson`.
- Normalize each completed job into a tree record.
- Derive project summaries from the tree records.
- Merge job-derived projects with reporter-owned content projects.
- Emit a JSON object with `projects`, `trees`, `geojson`, and `metadata`.

Suggested output shape:

```js
{
  metadata: {
    staging_root,
    generated_at,
    job_count,
    warnings
  },
  projects: [
    {
      slug,
      name,
      tree_count,
      species_count,
      risk_counts,
      latest_staged_at,
      coordinate_count,
      description,
      image,
      map_bounds,
      has_content,
      has_jobs
    }
  ],
  trees: [
    {
      id,
      job_number,
      job_id,
      project,
      project_slug,
      species,
      tree_number,
      assessor,
      assessed_date,
      staged_at,
      dbh,
      height,
      crown_spread,
      latitude,
      longitude,
      overall_risk,
      residual_risk,
      work_priority,
      targets,
      risk_conditions,
      mitigation_options,
      narrative,
      transcript,
      form_data,
      images,
      artifacts,
      revisions
    }
  ],
  geojson: {
    type: "FeatureCollection",
    features: []
  }
}
```

Acceptance criteria:

- `npm run build` can execute the loader without requiring network access.
- Missing optional fields do not crash the loader.
- Loader emits warnings for malformed or incomplete jobs.
- Project content records without job bundles still appear as zero-tree projects.
- All visible UI fields can be read from the normalized output.

## Phase 2: Shared Data Helpers

Create a small client-side module for derived values and formatting.

Likely file:

```text
src/components/reporter-data.js
```

Responsibilities:

- Filter trees by project, species, and risk.
- Compute risk counts.
- Compute species lists.
- Format dates and empty values.
- Provide stable labels for TRAQ form section keys.

Acceptance criteria:

- Home and project pages do not duplicate filtering and formatting logic.
- Missing/null values render as readable empty states rather than `undefined`.

## Phase 3: Home Page

Replace the starter `src/index.md` with the reporter landing page.

Responsibilities:

- Opening explanation of the reporter.
- Portfolio summary cards.
- Risk distribution summary.
- Project cards/buttons.
- Link each project card to the generic project view with project slug in URL state.

Likely route strategy for first implementation:

```text
/project?slug=<project_slug>
```

If Observable routing or deployment behavior makes query-string handling awkward, use:

```text
/project#<project_slug>
```

Acceptance criteria:

- User can understand what the reporter is before seeing controls.
- User can see all staged projects and open one.
- Summary counts match the loader output.

## Phase 4: Generic Project View

Create one reusable project interface.

Likely file:

```text
src/project.md
```

Responsibilities:

- Read selected project slug from URL state.
- Render project summary metrics.
- Render filters for species and overall risk.
- Render a map-like coordinate view for filtered trees.
- Render a table of filtered trees below the map.
- Maintain a selected tree state shared between map and table.
- Open a sidebar/detail panel when a tree is selected.

Important interaction rules:

- The table and map consume the same filtered tree list.
- Selecting a point selects the corresponding table row.
- Selecting a table row selects the corresponding point.
- Changing filters updates both the map and table.
- If filters exclude the selected tree, clear the selection.

Map implementation options:

- First pass: use Observable Plot or SVG-based coordinate scatter if available through Framework defaults.
- If a true basemap is required, add a mapping dependency such as Leaflet or MapLibre later.
- Do not block the first implementation on tiled basemaps.

Acceptance criteria:

- Project page works for American River and Briarwood from the staged data.
- Species and risk filters affect both map and table.
- Map/table selection opens the same tree sidebar.

## Phase 5: Tree Detail Sidebar

Implement the selected-tree detail panel inside the project view.

Likely file:

```text
src/components/tree-detail.js
```

Responsibilities:

- Render selected tree identity.
- Render risk summary and risk categorization.
- Render targets.
- Render mitigation options.
- Render generated narrative text.
- Render collapsible TRAQ form sections from `form_data`.
- Render source/revision metadata.
- Render export/download links where available.

Initial default expanded sections:

- Identity.
- Risk summary.
- Narrative.
- Risk categorization.

Initial collapsed sections:

- Targets.
- Mitigation.
- TRAQ form data.
- Transcript.
- Source metadata.

Acceptance criteria:

- Sidebar shows useful detail without navigating away.
- TRAQ form sections remain accessible and traceable.
- Sidebar handles missing sections without failing.

## Phase 6: Asset and Download Strategy

Add a static asset preparation step after the JSON UI works.

Likely options:

- A preparation script copies PDFs and report images into `src/generated/jobs/<job_number>/`.
- Artifact URLs use Observable's `/_file/generated/jobs/<job_number>/...` serving namespace.
- After `observable build`, a copy step publishes prepared artifacts into `docs/_file/generated/jobs/<job_number>/`.
- A companion script copies assets before `observable build`.
- Normalized records store URLs to copied assets.

Initial downloads:

- TRAQ PDF: link to copied `traq_page1.pdf`.
- Narrative report: generate a client-side Markdown or HTML download from normalized tree data.

Deferred downloads:

- PDF narrative generation.
- Bundled tree packet with PDF, images, JSON, and narrative.

Acceptance criteria:

- Download links work in a static built site.
- No deployed page depends on filesystem paths outside the Observable output.

## Phase 7: Polish and Validation

Responsibilities:

- Update `observablehq.config.js` title and navigation.
- Update `README.md` with local staging and build instructions.
- Run `npm run build`.
- Add a short verification note with known staged project counts.
- Keep visual styling simple and readable.

Acceptance criteria:

- Build succeeds.
- Home page and project page are navigable.
- Data summary numbers match staged jobs.
- No known runtime errors for missing optional TRAQ fields.

## Deferrals

- Separate tree pages for shareable single-tree reports.
- Generated static project pages.
- Tiled basemap integration.
- PDF generation for narrative reports.
- Full artifact bundle export.
- Authentication or remote cloud sync.

## Open Decisions Before Coding

- Use query string or hash state for the generic project route.
- Use simple SVG/Plot coordinates first, or add a true map dependency immediately.
- Copy staged PDFs/images during the loader step or in a separate asset preparation script.
- Use Markdown or HTML as the first downloadable narrative report format.
