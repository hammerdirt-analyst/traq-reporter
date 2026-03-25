# Design Note: Export Sync Contract For Reporting Client

Date: 2026-03-24

## Goal

Expose a minimal server-side export/sync contract for one authorized downstream client that builds:

- reports/documents
- dashboards
- geospatial products
- blog/article content

The TRAQ server remains the system of record for capture, extraction, review, correction, and finalization. The downstream reporting client owns persistence, transformation, rendering, and publication workflows.

This document is the final explicit contract for the first external consumer. The first real consumer will be a CLI. A frontend client should use the same service contract, not a parallel one-off path.

## Decision

Add a small export API to the server rather than embedding reporting logic into the core server.

Server responsibilities:

- authenticate one export client account
- expose a stable sync contract
- return only records changed since the client's last acknowledged sync point
- distinguish `in_process` from `completed`
- expose metadata and artifact fetch endpoints for images and GeoJSON
- maintain enough bookkeeping to support reliable incremental sync

Reporting client responsibilities:

- store the last acknowledged sync cursor
- persist received records and artifacts locally
- fetch images as needed
- generate reports, dashboards, maps, and articles
- handle retry, caching, and reprocessing locally

## Export Categories

Two export categories are required:

- `in_process`
  - job is not yet archived/finalized
  - payload source is latest persisted review payload
- `completed`
  - job is archived/finalized
  - payload source is archived final snapshot and archived GeoJSON

Transitions from `in_process` to `completed` must be explicitly visible in sync responses.

## Recommended API Shape

### 1. Incremental sync endpoint

`GET /v1/export/changes?cursor=<cursor>`

Purpose:

- return only records changed since the provided cursor
- include category transitions
- return a new cursor for the client to persist after successful processing

Authentication:

- dedicated export API key or bearer token
- scoped to export access only

Response shape:

```json
{
  "cursor": "chg_0000001248",
  "server_time": "2026-03-24T18:45:00Z",
  "in_process": [
    {
      "job_id": "job_123",
      "job_number": "TRAQ-123",
      "category": "in_process",
      "status": "REVIEW_RETURNED",
      "updated_at": "2026-03-24T18:40:00Z",
      "profile": null,
      "server_revision_id": "rev_round_7",
      "review": {
        "round_id": "round_7",
        "transcript": "...",
        "form": { "data": {} },
        "images": [
          {
            "image_id": "img_1",
            "caption": "oak canopy",
            "uploaded_at": "2026-03-24T18:31:00Z",
            "download_url": "/v1/export/jobs/job_123/images/img_1"
          }
        ]
      }
    }
  ],
  "completed": [
    {
      "job_id": "job_456",
      "job_number": "TRAQ-456",
      "category": "completed",
      "status": "ARCHIVED",
      "updated_at": "2026-03-24T18:41:00Z",
      "archived_at": "2026-03-24T18:41:00Z",
      "profile": {
        "name": "Jane Arborist",
        "phone": "555-111-2222",
        "isa_number": "WE-1234A",
        "correspondence_email": "jane@example.com"
      },
      "final": {
        "round_id": "round_2",
        "transcript": "...",
        "form": { "data": {} },
        "report_images": [
          {
            "image_ref": "report_1",
            "caption": "root flare",
            "download_url": "/v1/export/jobs/job_456/images/report_1"
          }
        ],
        "geojson_url": "/v1/export/jobs/job_456/geojson"
      }
    }
  ],
  "transitioned_to_completed": [
    {
      "job_id": "job_456",
      "job_number": "TRAQ-456",
      "previous_category": "in_process",
      "current_category": "completed",
      "updated_at": "2026-03-24T18:41:00Z"
    }
  ]
}
```

Notes:

- `in_process` and `completed` contain current canonical state.
- `transitioned_to_completed` is a convenience feed so the client can update downstream indexes cleanly.
- Image bytes are not inlined in the change response.
- `profile` is part of the contract. For completed jobs it comes from the archived final payload. For in-process jobs it may be `null` until earlier profile persistence is added.

### 2. Image fetch endpoint

`GET /v1/export/jobs/{job_id}/images/{image_id}`

Purpose:

- download original or report-ready image bytes

Suggested query parameters:

- `variant=original|report`

### 3. GeoJSON fetch endpoint

`GET /v1/export/jobs/{job_id}/geojson`

Purpose:

- fetch archived GeoJSON for completed jobs

### 4. Optional bootstrap endpoint

`GET /v1/export/bootstrap`

Purpose:

- initial one-time sync for a newly provisioned reporting client
- may internally behave like `changes` from cursor zero

This is optional if `cursor` supports an empty or zero value.

## Cursor And Bookkeeping Model

Do not use "last download timestamp" as the primary sync contract.

Use a monotonic cursor backed by a persisted change log or an equivalent monotonic sequence.

Minimum server bookkeeping:

- one export client identity
- one persisted last-issued or acknowledged cursor per export client
- one monotonic change sequence for export-visible job changes

Export-visible job changes include:

- review payload updated
- final snapshot created
- correction snapshot created if corrections are export-visible
- image metadata changed
- job status/category changed
- GeoJSON created or replaced

Recommended implementation:

- add an `export_change_log` table with:
  - `seq`
  - `job_id`
  - `change_type`
  - `category`
  - `created_at`
- add an `export_clients` table with:
  - `client_id`
  - `name`
  - `api_key_hash` or token identity
  - `last_acknowledged_seq`

If we want the smallest possible first version, the server can avoid storing acknowledgements and simply accept a client-provided cursor. The client persists the cursor locally. This is acceptable if we trust the client and only need one integration.

## Canonical Payload Sources

### In-process

Source of truth:

- latest persisted round review payload

Include:

- job metadata needed by reporting
- current status
- latest round id
- `profile` when available, otherwise `null`
- transcript
- normalized review form payload
- image metadata and download URLs
- revision ids

### Completed

Source of truth:

- archived final snapshot
- archived GeoJSON export

Include:

- job metadata needed by reporting
- exported user profile
- archived/final timestamps
- transcript from final payload
- final normalized form payload
- report image metadata and download URLs
- GeoJSON download URL

## Contract Rules

1. The export API returns canonical current state, not raw internal runtime structures.
2. Completed jobs are exported from archived final artifacts, not mutable live review payloads.
3. The server should only return records changed since the cursor.
4. The client must treat sync as idempotent.
5. Images should be fetched separately from the change feed.
6. The server must preserve stable identifiers across syncs.
7. If a field was corrected by the review client and persisted into review/final payloads, export returns that persisted value, not a re-extracted value.
8. `profile` is part of the export contract and should be treated as business data, not presentation-only metadata.

## What The New Client Should Assume

The reporting client should assume:

- it is downstream of the operational review system
- sync is incremental and repeatable
- a job may appear multiple times as it changes
- a job can move from `in_process` to `completed`
- completed payloads should replace in-process payloads for publication purposes
- images may be fetched lazily after metadata sync

## First Implementation Scope

Minimal first version:

- one export auth mechanism
- one `GET /v1/export/changes`
- one image download endpoint
- one GeoJSON download endpoint
- cursor based on monotonic sequence
- payloads for `in_process`, `completed`, and `transitioned_to_completed`
- profile included in completed payloads

Defer:

- multi-client tenancy
- webhooks
- bulk zip exports
- deletions/tombstones unless needed
- downstream publication orchestration

## CLI First

The first external consumer should be a CLI that talks only to the export service contract.

The CLI should:

- call `GET /v1/export/changes`
- persist the cursor after successful processing
- download images and GeoJSON by URL when needed
- write normalized payloads to local disk for inspection
- fail loudly on contract violations

This validates the service boundary before a richer frontend client is built.

## Note For The New Client

Build the reporting client as an independent service/application.

It should:

- persist the sync cursor after successful processing
- maintain a local cache/database of jobs and artifacts
- download images on demand
- render documents and dashboards from normalized exported payloads
- treat completed jobs as authoritative final publication inputs

The TRAQ server should not own report generation, dashboard rendering, or article production beyond exposing the export contract and stored artifacts.
