# Observable Reporter UI Design Note

## Product Direction

Hammerdirt does not need to invent a new category of output. The reporter should produce the outputs buyers already value: inventory views, risk ratings, prioritization, forecasting inputs, maps, and reports. The difference is the workflow that produces them.

The product logic is:

**Start with the observation. End with something Observable.**

The strength is the chain from observation to structured result. The assessor stays focused on the tree, the field record is preserved, and the final result is more traceable and defensible.

## Source Data

The reporter should read completed staged job bundles from:

```text
../server/staging/jobs/<job_number>/
```

Each staged job currently contains:

```text
manifest.json
final.json
final.geojson
traq_page1.pdf
images/
```

The staging README identifies this as the canonical local staging root for real completed-job bundles. The Observable reporter should preserve this model rather than inventing a separate domain model.

The expected loader flow is:

1. Read every staged job directory.
2. Load `manifest.json`, `final.json`, and `final.geojson`.
3. Normalize each job into a tree assessment record for UI use.
4. Derive project summaries and map/table records from the normalized records.

The normalized record should keep the source fields traceable, especially:

- `job_number`
- `job_id`
- `project`
- `project_slug`
- `client_revision_id`
- `server_revision_id`
- `form.data`
- `narrative.text`
- `transcript`
- `report_images`
- `manifest.images`
- `artifacts`

## Home Page

The first thing the user should see is an opening explanation of what this is:

- This is an Observable reporter for TRAQ-style tree risk observations.
- It turns completed field observations into project inventory, maps, risk views, and exportable tree-level details.
- It demonstrates the workflow advantage: field observation to structured, traceable, defensible output.

After the opening, the home page should show summary data for all projects:

- Total projects.
- Total assessed trees.
- Species count.
- Risk distribution.
- Assessment or staging date range.
- Count of records with map coordinates.

Below the summary, show one button or card for each project. Each project card should include:

- Project name.
- Tree count.
- Species count.
- Risk counts.
- Latest staged or assessed date.
- Primary action: open the project view.

## Project View

A project view is the main working interface. It does not need to be a hand-authored project page. Prefer one generic project interface driven by project slug or selected project state.

The project view should contain:

- Project header with project name and summary metrics.
- Filters for species and risk rating.
- Optional later filters for target type, work priority, or assessment date.
- Map with one point per filtered tree.
- Table below the map with the same filtered trees.
- Sidebar/detail panel for the selected tree.

The map and table must share state:

- The table filter state controls which points are visible on the map.
- Clicking a map point selects the tree and opens the sidebar.
- Clicking a table row selects the tree and opens the sidebar.
- If a filter removes the selected tree from the filtered set, clear the selection.
- The selected tree should be visibly selected in both the map and table.

## Tree Detail Sidebar

There should not be a separate tree page by default. The selected tree detail should live in the project view sidebar.

The sidebar should give access to the TRAQ form data and export actions for the selected tree. Suggested sections:

- Identity: job number, tree number, species, assessor, date, DBH, height, crown spread, location.
- Risk summary: overall risk, residual risk, work priority.
- Risk categorization: condition, tree part, target, likelihood, consequences, risk rating.
- Targets: target label, occupancy, zone, practical-to-move, restriction-practical.
- Mitigation: recommended options and residual risk.
- Narrative: generated narrative text for the tree.
- TRAQ form data: collapsible sections from `form.data`.
- Images: staged report images if static serving is available.
- Source: revision IDs, staged date, artifact links, source JSON/GeoJSON links if useful.

The sidebar should include download/export options:

- Download TRAQ form PDF.
- Download narrative report for the selected tree.
- Optional later: download source JSON or GeoJSON.

## Tree Pages

A separate tree page is not needed for the default workflow.

The purpose of a future tree page would be option 3: a shareable, export-quality detail report for one tree that can be sent to someone else. It should not replace the project map/table/sidebar workflow.

If added later, a tree page should use the same selected-tree data model as the sidebar and focus on shipping the details of one tree:

- Tree identity and location.
- Photos.
- Narrative report.
- TRAQ sections.
- Risk categorization.
- Mitigation options.
- Transcript and source traceability.
- Download links for the TRAQ form and narrative report.

## Routing Recommendation

Start with a single generic project interface rather than manually authored project pages.

Reasonable first implementation:

- Home page renders portfolio summary and project cards.
- Project cards link to one reusable project view using a project slug in URL state, for example query string or hash state.
- The project view filters the normalized tree records by `project_slug`.

Static generated project pages can be added later if clean client-facing URLs become important.

## Asset Handling

JSON and GeoJSON can be loaded through Observable data loaders.

Images and PDFs need a deliberate static-serving strategy for deployment. Referencing `../server/staging/...` directly is not enough for a published static site.

Likely approach:

1. The loader or a companion preparation step reads the staged artifacts.
2. Required PDFs and images are copied into a static path under the Observable source tree.
3. Normalized records store the deployable relative URLs.

This can be deferred until the first map/table/sidebar workflow is working, but the download buttons depend on it.

## Open Questions

- Should the project view use query string state, hash state, or generated routes?
- Should the first implementation copy staged PDFs and images into the Observable app, or initially show only JSON-backed details?
- What format should the downloadable narrative report use first: Markdown, HTML, or PDF?
- Which TRAQ form sections should be shown expanded by default in the sidebar?
