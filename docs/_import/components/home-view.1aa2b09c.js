import {el} from "./dom.d2c937d2.js";
import {stat} from "./fragments.c4951b71.js";
import {fmtDate, truncateText} from "./reporter-data.243ef50a.js";

export function renderHome(data) {
  const home = data.site?.home ?? {};
  const root = el("div", {class: "reporter-home"});

  root.append(
    el("section", {class: "hero"}, [
      el("p", {class: "eyebrow"}, home.eyebrow ?? "TRAQ observation reporter"),
      el("h1", {}, home.title ?? "Start with the observation. End with something Observable."),
      el("p", {class: "lede"}, home.lede ?? ""),
      renderHomeLinks(home.links)
    ]),
    el("section", {class: "project-grid"}, data.projects.map(projectCard))
  );

  return root;
}

function renderHomeLinks(links = []) {
  if (!links.length) return null;
  return el("div", {class: "hero-links"}, links.map((link) => el("a", {
    href: link.href,
    target: "_blank",
    rel: "noreferrer"
  }, link.label)));
}

function projectCard(project) {
  return el("a", {class: "project-card", href: `./project?slug=${encodeURIComponent(project.slug)}`}, [
    project.image ? el("img", {class: "project-card-image", src: project.image, alt: ""}) : null,
    el("div", {class: "project-card-header"}, [
      el("h2", {}, project.name),
      el("span", {class: "project-action"}, "Open project")
    ]),
    project.description ? el("p", {}, truncateText(project.description, 100)) : null,
    el("p", {class: "muted"}, project.has_jobs
      ? `Latest staged record: ${fmtDate(project.latest_staged_at)}`
      : "Project content is available; no staged tree jobs yet.")
  ]);
}
