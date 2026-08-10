# Retrieval and injection API contract

## Transport

The v1 transport is HTTP JSON over loopback. The server binds to `127.0.0.1` by
default, sends no telemetry, and reads only the configured SQLite database and
optional routing-table file. A bearer token can be required with
`SANYUAN_SIDECAR_TOKEN`.

## Python interface

```python
def retrieve_and_inject(
    query: str,
    top_k: int = 8,
    mode: str = "full",
    *,
    trigger_policy: str = "always",
    query_axes: list[str] | None = None,
    current_path: str | None = None,
) -> InjectionResult:
    ...
```

`mode` accepts `full`, `fast`, or `minimal`:

| Mode | Retrieval | Topology output |
| --- | --- | --- |
| `full` | FTS + vector when available; full rerank | Full read projection and optional offline route lookup |
| `fast` | FTS + available cached vectors | Compact read projection; no route expansion |
| `minimal` | FTS only | Source/title injection only |

`trigger_policy` accepts `always`, `auto`, or `never`. The policy is evaluated
inside the pipeline, while the plugin provides explicit commands that can override
it. `auto` is a conservative lexical intent classifier, not a learned correctness
model.

## HTTP endpoints

### `GET /health`

Returns sidecar availability and detected store capabilities. It never returns
credentials.

### `POST /v1/should-retrieve`

```json
{"query":"find the note about PNPLA8"}
```

### `POST /v1/retrieve-and-inject`

```json
{
  "query": "find the note about PNPLA8",
  "top_k": 8,
  "mode": "full",
  "trigger_policy": "auto",
  "query_axes": ["periodontitis", "PNPLA8", "fibroblast"],
  "current_path": "projects/periodontitis.md"
}
```

The response contains:

- `triggered`: whether retrieval ran;
- `injection`: the reader-facing text block;
- `items`: ranked candidates, transient three-talent storage projections, and
  three-topic read projections;
- `diagnostics`: stage counts, provider names, timing, and explicit degradation;
- `routing`: an optional O(1) offline route-table hit.

No endpoint writes back to Markdown files. Vector indexing, when explicitly run,
writes only the sidecar-owned `sanyuan_vector_index` table in the configured SQLite
database.

## FTS5 compatibility

The store adapter discovers FTS5 virtual tables through `sqlite_master`. A table and
column mapping may be pinned through environment variables:

| Variable | Meaning |
| --- | --- |
| `SANYUAN_FTS_TABLE` | FTS5 table name |
| `SANYUAN_FTS_PATH_COLUMN` | path/source column |
| `SANYUAN_FTS_TITLE_COLUMN` | title column |
| `SANYUAN_FTS_CONTENT_COLUMN` | Markdown/chunk content column |

Identifiers are accepted only after matching the discovered SQLite schema; user
input is never interpolated as a table or column name.

## Optional routing table

The call-time path performs an exact dictionary lookup only. It never runs Dijkstra
or reconstructs the graph. JSON is supported with no dependency; YAML is supported
only when PyYAML is already installed. Missing parsers or keys are reported as a
degradation rather than replaced with guessed routes.

## Security and disclosure

- The plugin sends the user's explicit query or selected text to the configured
  sidecar endpoint.
- The Python process may send that text to the configured embedding provider.
- API keys remain in the Python process environment.
- No telemetry, advertising, analytics, or automatic vault-wide scan is included.
- Remote sidecar URLs require an explicit opt-in in plugin settings.
