// See https://observablehq.com/framework/config for documentation.
const siteUrl = "https://hammerdirt-analyst.github.io/traq-reporter/";
const siteTitle = "TRAQ Reporter | Hammerdirt";
const siteDescription =
  "Hammerdirt TRAQ Reporter publishes tree risk assessment observations as project inventories, maps, TRAQ form detail, transcripts, images, and downloadable forms.";

const structuredData = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "TRAQ Reporter",
  url: siteUrl,
  description: siteDescription,
  publisher: {
    "@type": "Organization",
    name: "Hammerdirt",
    url: "https://hammerdirt.solutions"
  },
  inLanguage: "en-US"
};

export default {
  // The app’s title; used in the sidebar and webpage titles.
  title: "TRAQ Reporter",

  // The pages and sections in the sidebar. If you don’t specify this option,
  // all pages will be listed in alphabetical order. Listing pages explicitly
  // lets you organize them into sections and have unlisted pages.
  pages: [
    {name: "Projects", path: "/"},
    {name: "Project view", path: "/project"}
  ],

  // Shared metadata for search engines and link previews.
  head: `
    <link rel="icon" href="observable.png" type="image/png" sizes="32x32">
    <link rel="canonical" href="${siteUrl}">
    <meta name="description" content="${siteDescription}">
    <meta name="robots" content="index,follow">
    <meta name="author" content="Hammerdirt">
    <meta name="application-name" content="TRAQ Reporter">
    <meta name="theme-color" content="#111827">
    <meta property="og:type" content="website">
    <meta property="og:site_name" content="Hammerdirt TRAQ Reporter">
    <meta property="og:title" content="${siteTitle}">
    <meta property="og:description" content="${siteDescription}">
    <meta property="og:url" content="${siteUrl}">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="${siteTitle}">
    <meta name="twitter:description" content="${siteDescription}">
    <script type="application/ld+json">${JSON.stringify(structuredData)}</script>
  `,

  // The path to the source root.
  root: "src",

  header: "",
  sidebar: false,
  toc: false,
  footer: "Built with Observable.",
  pager: false,
  output: "docs",

  // Some additional configuration options and their defaults:
  // theme: "default", // try "light", "dark", "slate", etc.
  // header: "", // what to show in the header (HTML)
  // footer: "Built with Observable.", // what to show in the footer (HTML)
  // sidebar: true, // whether to show the sidebar
  // toc: true, // whether to show the table of contents
  // pager: true, // whether to show previous & next links in the footer
  // output: "dist", // path to the output root for build
  // search: true, // activate search
  // linkify: true, // convert URLs in Markdown to links
  // typographer: false, // smart quotes and other typographic improvements
  // preserveExtension: false, // drop .html from URLs
  // preserveIndex: false, // drop /index from URLs
};
