import test from "node:test";
import assert from "node:assert/strict";
import {coordinateLayout} from "../src/components/tree-map.js";

test("coordinateLayout skips unmapped trees and returns coordinates for mapped trees", () => {
  const layout = coordinateLayout([
    {id: "a", latitude: 38, longitude: -121},
    {id: "b", latitude: null, longitude: -121}
  ]);
  assert.equal(layout.length, 1);
  assert.equal(layout[0].tree.id, "a");
  assert.equal(Number.isFinite(layout[0].x), true);
  assert.equal(Number.isFinite(layout[0].y), true);
});
