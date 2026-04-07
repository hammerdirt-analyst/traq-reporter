export function boundsFromProject(project) {
  const bounds = project?.map_bounds;
  if (!bounds) return null;
  const {west, south, east, north} = bounds;
  if (![west, south, east, north].every(Number.isFinite)) return null;
  return [[south, west], [north, east]];
}

export function treeLatLngs(trees) {
  return trees
    .filter((tree) => Number.isFinite(tree.latitude) && Number.isFinite(tree.longitude))
    .map((tree) => [tree.latitude, tree.longitude]);
}
