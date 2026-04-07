import test from "node:test";
import assert from "node:assert/strict";
import {withSiteContent} from "../src/components/site-content.js";

test("withSiteContent overlays editable home copy", () => {
  const reporter = withSiteContent({projects: []}, {
    home: {
      eyebrow: "Custom eyebrow",
      title: "Custom title",
      links: [{label: "Docs", href: "https://example.com"}]
    }
  });

  assert.equal(reporter.site.home.eyebrow, "Custom eyebrow");
  assert.equal(reporter.site.home.title, "Custom title");
  assert.equal(typeof reporter.site.home.lede, "string");
  assert.equal(reporter.site.home.links[0].label, "Docs");
});
