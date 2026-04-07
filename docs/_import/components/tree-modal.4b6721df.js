import {el} from "./dom.d2c937d2.js";
import {detailSection, keyValues} from "./fragments.c4951b71.js";
import {fmt, fmtNumber, sectionLabel} from "./reporter-data.243ef50a.js";

export function renderTreeModal(tree, close) {
  if (!tree) return null;

  return el("div", {class: "tree-modal-overlay", role: "presentation"}, [
    el("article", {
      class: "tree-modal",
      role: "dialog",
      "aria-modal": "true",
      "aria-labelledby": "tree-modal-title",
      tabindex: "-1"
    }, [
      el("header", {class: "tree-modal-header"}, [
        el("div", {}, [
          el("p", {class: "eyebrow"}, tree.job_number),
          el("h2", {id: "tree-modal-title"}, fmt(tree.species))
        ]),
        el("button", {type: "button", class: "close-button", onclick: close}, "Close")
      ]),
      el("div", {class: "tree-modal-body"}, [
        keyValues({
          "Tree number": tree.tree_number,
          Assessor: tree.assessor,
          Date: tree.assessed_date,
          DBH: fmtNumber(tree.dbh, " in"),
          Height: fmtNumber(tree.height, " ft"),
          "Crown spread": fmtNumber(tree.crown_spread, " ft"),
          Location: tree.address_tree_location
        }),
        renderTraqDownload(tree),
        detailSection("TRAQ Form Data", renderFormData(tree.form_data), true),
        detailSection("Transcript", el("pre", {class: "transcript"}, tree.transcript || "No transcript recorded."), false),
        detailSection("Images", renderImages(tree.images), false)
      ])
    ])
  ]);
}

function renderTraqDownload(tree) {
  if (!tree.artifacts?.traq_pdf_url) {
    return el("p", {class: "muted"}, "TRAQ form download is not available for this tree.");
  }
  return el("p", {class: "download-actions"}, el("a", {
    href: tree.artifacts.traq_pdf_url,
    download: `${tree.job_number}-traq-form.pdf`
  }, "Download TRAQ form"));
}

function renderFormData(formData) {
  if (!formData) return el("p", {class: "muted"}, "No form data recorded.");
  return el("div", {class: "form-sections"}, Object.entries(formData).map(([key, value]) => detailSection(sectionLabel(key), renderJson(value), false)));
}

function renderJson(value) {
  return el("pre", {class: "json-block"}, JSON.stringify(value, null, 2));
}

function renderImages(images = []) {
  const available = images.filter((image) => image.url);
  if (!available.length) return el("p", {class: "muted"}, "No images available.");
  return el("div", {class: "tree-images"}, available.map((image) => el("figure", {class: "tree-image"}, [
    el("img", {src: image.url, alt: image.caption || "Tree assessment image"}),
    image.caption ? el("figcaption", {}, image.caption) : null
  ])));
}
