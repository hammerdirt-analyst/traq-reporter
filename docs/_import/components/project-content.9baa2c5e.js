const emptyRiskCounts = Object.freeze({
  extreme: 0,
  high: 0,
  moderate: 0,
  low: 0,
  none: 0,
  unknown: 0
});

export function normalizeProjectContent(project) {
  return {
    slug: project.slug,
    name: project.name ?? project.slug,
    description: project.description ?? "",
    image: project.image ?? null,
    map_bounds: project.map_bounds ?? null
  };
}

export function mergeProjectSummaries(jobProjects, contentProjects) {
  const bySlug = new Map();

  for (const project of jobProjects) {
    bySlug.set(project.slug, {
      ...project,
      description: project.description ?? "",
      image: project.image ?? null,
      map_bounds: project.map_bounds ?? null,
      has_content: Boolean(project.has_content),
      has_jobs: project.tree_count > 0
    });
  }

  for (const content of contentProjects.map(normalizeProjectContent)) {
    const existing = bySlug.get(content.slug);
    bySlug.set(content.slug, {
      slug: content.slug,
      name: content.name,
      tree_count: existing?.tree_count ?? 0,
      species_count: existing?.species_count ?? 0,
      risk_counts: existing?.risk_counts ?? {...emptyRiskCounts},
      latest_staged_at: existing?.latest_staged_at ?? null,
      coordinate_count: existing?.coordinate_count ?? 0,
      description: content.description,
      image: content.image,
      map_bounds: content.map_bounds,
      has_content: true,
      has_jobs: (existing?.tree_count ?? 0) > 0
    });
  }

  return Array.from(bySlug.values()).sort((a, b) => a.name.localeCompare(b.name));
}

export function withProjectContent(reporter, contentProjects) {
  return {
    ...reporter,
    projects: mergeProjectSummaries(reporter.projects ?? [], contentProjects ?? [])
  };
}
