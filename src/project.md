---
title: Project
---

<link rel="stylesheet" href="./leaflet.css">

```js
import {renderProject} from "./components/reporter-ui.js";
import {reporterStyles} from "./components/reporter-styles.js";
import {withProjectContent} from "./components/project-content.js";
```

```js
const reporter = withProjectContent(
  await FileAttachment("data/reporter.json").json(),
  await FileAttachment("project-content.json").json()
);
```

```js
display(html`<style>${reporterStyles}</style>`);
display(renderProject(reporter));
```
