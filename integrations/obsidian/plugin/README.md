# Sanyuan Context Router

Desktop Obsidian client for the Sanyuan retrieval sidecar. The plugin sends an
explicit query or editor selection to a user-configured endpoint, previews the
returned read-injection block, and lets the user copy or insert it.

## Privacy and network disclosure

- No telemetry, analytics, advertising, or background vault scan.
- No request is made merely by loading the plugin.
- The default endpoint is `http://127.0.0.1:8765`.
- A non-loopback endpoint requires an explicit setting opt-in.
- The query text, current note path, and optional `sanyuan_axes` frontmatter are
  sent to the configured endpoint when a retrieval command is invoked.
- Embedding-provider credentials stay in the Python sidecar environment and are
  never stored by this plugin.

## Commands

- `Retrieve context`: always run retrieval.
- `Smart retrieve context`: run only when the sidecar's conservative trigger
  recognizes an explicit retrieval intent.
- `Check sidecar`: verify connectivity and display detected status.

If the current selection is empty, the plugin asks for a query. Optional query axes
can be declared in frontmatter:

```yaml
sanyuan_axes:
  - periodontitis
  - PNPLA8
  - fibroblast
```

## Development

```bash
npm ci
npm run build
```

Manual installation requires `main.js`, `manifest.json`, and `styles.css` in the
vault plugin directory.

This source currently retains all rights. Community-directory submission and any
open-source licensing require a separate owner decision.
