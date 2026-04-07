export const reporterStyles = `
.hero {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 16px;
  padding: 2rem;
  background: linear-gradient(135deg, var(--theme-background-alt), var(--theme-background));
}

.eyebrow {
  margin: 0 0 0.35rem;
  color: var(--theme-foreground-muted);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.lede {
  max-width: 76ch;
  font-size: 1.05rem;
}

.stat-grid,
.project-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0;
}

.stat-card {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 12px;
  padding: 0.85rem;
  background: var(--theme-background);
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
}

.stat-label,
.muted {
  color: var(--theme-foreground-muted);
}

.panel,
.map-panel,
.tree-table-wrap {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 14px;
  padding: 1rem;
  background: var(--theme-background);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.project-card {
  display: block;
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 16px;
  padding: 1rem;
  color: inherit;
  text-decoration: none;
  background: var(--theme-background);
}

.project-card:hover {
  border-color: var(--theme-foreground-muted);
}

.project-card-header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 1rem;
}

.project-card h2 {
  margin-top: 0;
}

.project-card-image,
.project-hero-image {
  width: 100%;
  max-height: 260px;
  object-fit: cover;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.project-action,
.risk-pill,
.hero-links a {
  border-radius: 999px;
  padding: 0.2rem 0.55rem;
  background: var(--theme-background-alt);
  font-size: 0.8rem;
  white-space: nowrap;
}

.hero-links,
.risk-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
}

.risk-low { color: #16833a; }
.risk-moderate { color: #c89b00; }
.risk-high,
.risk-extreme { color: #c92a1f; }
.risk-unknown,
.risk-none { color: var(--theme-foreground-muted); }

.back-link {
  display: inline-block;
  margin-bottom: 0.75rem;
}

.filter-bar-inner {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: end;
  margin: 1rem 0;
}

.filter-bar label {
  display: grid;
  gap: 0.25rem;
  font-weight: 600;
}

.filter-bar select,
.filter-bar button {
  min-height: 2.2rem;
}

.project-workspace {
  display: block;
}

.project-main {
  display: grid;
  gap: 1rem;
}

.coordinate-map {
  width: 100%;
  max-height: 460px;
}

.leaflet-map {
  height: 460px;
  border-radius: 10px;
  overflow: hidden;
}

.map-bg {
  fill: var(--theme-background-alt);
}

.map-point {
  fill: currentColor;
  stroke: white;
  stroke-width: 2;
  cursor: pointer;
}

.map-point.is-selected {
  stroke: black;
  stroke-width: 3;
}

.map-caption,
.table-caption {
  margin-bottom: 0.5rem;
  color: var(--theme-foreground-muted);
}

.tree-table {
  width: 100%;
  border-collapse: collapse;
}

.tree-table th,
.tree-table td {
  border-bottom: 1px solid var(--theme-foreground-faint);
  padding: 0.55rem;
  text-align: left;
}

.risk-cell {
  font-weight: 700;
}

.tree-table tr {
  cursor: pointer;
}

.tree-table tr.is-selected {
  background: var(--theme-background-alt);
}

.detail-section {
  border-top: 1px solid var(--theme-foreground-faint);
  padding: 0.7rem 0;
}

.detail-section summary {
  cursor: pointer;
  font-weight: 700;
}

.key-values {
  display: grid;
  grid-template-columns: minmax(110px, 0.45fr) minmax(0, 1fr);
  gap: 0.35rem 0.75rem;
}

.key-values dt {
  color: var(--theme-foreground-muted);
  font-weight: 700;
}

.key-values dd {
  margin: 0;
}

.json-block,
.transcript {
  max-height: 24rem;
  overflow: auto;
  white-space: pre-wrap;
}

.download-actions a {
  display: inline-block;
  border-radius: 999px;
  padding: 0.35rem 0.7rem;
  background: var(--theme-background-alt);
}

.tree-images {
  display: grid;
  gap: 1rem;
}

.tree-image {
  margin: 0;
}

.tree-image img {
  width: 100%;
  border-radius: 10px;
}

.tree-image figcaption {
  margin-top: 0.35rem;
  color: var(--theme-foreground-muted);
  font-size: 0.9rem;
}

.empty-state,
.sidebar-empty {
  color: var(--theme-foreground-muted);
}

.tree-modal-open {
  overflow: hidden;
}

.tree-modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 1rem;
  background: rgb(0 0 0 / 0.55);
}

.tree-modal {
  width: min(960px, 100%);
  max-height: min(900px, calc(100dvh - 2rem));
  overflow: auto;
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 16px;
  background: var(--theme-background);
  box-shadow: 0 24px 80px rgb(0 0 0 / 0.35);
}

.tree-modal-header {
  position: sticky;
  top: 0;
  z-index: 1;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
  border-bottom: 1px solid var(--theme-foreground-faint);
  padding: 1rem;
  background: var(--theme-background);
}

.tree-modal-header h2 {
  margin: 0;
}

.tree-modal-body {
  padding: 1rem;
}

.close-button {
  min-height: 2.2rem;
}

@media (max-width: 900px) {
  .tree-modal-overlay {
    padding: 0;
  }

  .tree-modal {
    width: 100vw;
    height: 100dvh;
    max-height: none;
    border-radius: 0;
  }
}
`;
