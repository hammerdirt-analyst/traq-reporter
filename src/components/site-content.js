export const defaultSiteContent = {
  home: {
    eyebrow: "TRAQ observation reporter",
    title: "Start with the observation. End with something Observable.",
    lede: "This reporter turns completed tree risk observations into project inventory, risk views, maps, and exportable tree-level detail. The value is the workflow: field observation to structured, traceable, defensible output.",
    links: []
  }
};

export function withSiteContent(reporter, siteContent) {
  return {
    ...reporter,
    site: {
      home: {
        ...defaultSiteContent.home,
        ...(siteContent?.home ?? {}),
        links: siteContent?.home?.links ?? defaultSiteContent.home.links
      }
    }
  };
}
