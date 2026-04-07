---
title: TRAQ Reporter
---

```js
import {renderHome} from "./components/reporter-ui.js";
import {reporterStyles} from "./components/reporter-styles.js";
import {withProjectContent} from "./components/project-content.js";
import {withSiteContent} from "./components/site-content.js";
```

```js
const reporter = withSiteContent(
  withProjectContent(
    await FileAttachment("data/reporter.json").json(),
    await FileAttachment("project-content.json").json()
  ),
  await FileAttachment("site-content.json").json()
);
```

```js
display(html`<style>${reporterStyles}</style>`);
display(renderHome(reporter));
```
