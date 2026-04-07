import test from "node:test";
import assert from "node:assert/strict";
import {boundsFromProject, treeLatLngs} from "../src/components/map-bounds.js";

test("boundsFromProject converts configured map bounds to Leaflet bounds array", () => {
  assert.deepEqual(boundsFromProject({
    map_bounds: {
      west: -121.2,
      south: 38.1,
      east: -121.1,
      north: 38.2
    }
  }), [[38.1, -121.2], [38.2, -121.1]]);
});

test("boundsFromProject returns null for missing or malformed bounds", () => {
  assert.equal(boundsFromProject(null), null);
  assert.equal(boundsFromProject({map_bounds: {west: -121.2}}), null);
});

test("treeLatLngs returns mapped tree coordinate pairs", () => {
  assert.deepEqual(treeLatLngs([
    {latitude: 38, longitude: -121},
    {latitude: null, longitude: -122}
  ]), [[38, -121]]);
});
