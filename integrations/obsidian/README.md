# Sanyuan × Obsidian integration

This directory is an experimental, storage-agnostic adapter for using an Obsidian
vault as a retrieval substrate. It does not change the frozen Sanyuan ontology and
does not treat retrieval scores as `rho`, `theta`, or evidence strength.

## Components

| Component | Purpose |
| --- | --- |
| `python/` | Importable retrieval core and loopback REST sidecar |
| `plugin/` | Standalone TypeScript plugin for Obsidian desktop |
| `docs/api-contract.md` | Stable request, response, degradation, and privacy contract |
| `config/topology-routing-table.example.json` | Optional offline `query_axes -> b_n` lookup table |

The plugin is self-contained as a source package and can be moved to a dedicated
repository before a Community Plugins submission. Its current license follows the
parent repository's reserved-rights policy; choosing an open-source license and
publishing release assets remain explicit owner decisions.

## Pipeline

```text
query
  -> optional embedding
  -> SQLite FTS5 + optional vector index
  -> strict G1/G2/G3 retrieval cascade
  -> three-topic read projection
  -> reader-facing injection block
```

The cascade is deliberately named as retrieval gates, not as a redefinition of the
mathematical gates in other Sanyuan experiments:

1. `G1`: union and score FTS/vector candidates.
2. `G2`: discard empty, duplicate, and unsupported candidates.
3. `G3`: rerank the survivors and retain `top_k`.

Rejected candidates do not enter later gates. The default reranker is a transparent
lexical/vector heuristic because no cross-encoder is assumed. A future reranker can
implement the same provider interface without changing the REST contract.

## Ontology boundary

The generated label follows the current `read-injection.md` contract:

```text
[[天题×地题×人题: 本来样貌 × 读取方式 × 读取记录]]
```

An ordinary FTS row is first represented as a transient three-talent storage
projection, not silently promoted to a formal StoreNode. The legacy-looking form
`[[天题×人题→地题]]` is not emitted: it makes 地题 an
output with an intrinsic direction, which conflicts with the repository's frozen
architecture. Retrieval produces transient `ReadProjection` objects. It does not
claim to persist a schema-valid `CouplingState` unless StoreNode, MutualNode, and
ReadNode references are all present.

## Quick start

```bash
cd integrations/obsidian/python
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .

export SANYUAN_OBSIDIAN_DB=/absolute/path/to/obsidian-memory.db
sanyuan-obsidian inspect
sanyuan-obsidian serve
```

Embedding is optional. To enable an OpenAI-compatible Doubao/Ark embeddings
endpoint, provide environment variables to the Python process, never to the plugin:

```bash
export DOUBAO_EMBEDDING_BASE_URL=https://ark.cn-beijing.volces.com/api/v3/embeddings
export DOUBAO_EMBEDDING_API_KEY=your-key
export DOUBAO_EMBEDDING_MODEL=your-endpoint-or-model-id
```

Then build the Obsidian plugin:

```bash
cd ../plugin
npm ci
npm run build
```

For manual installation, copy `main.js`, `manifest.json`, and `styles.css` into:

```text
<vault>/.obsidian/plugins/sanyuan-context-router/
```

Start the sidecar first, enable the plugin, and use either command:

- `Retrieve context` forces retrieval.
- `Smart retrieve context` lets the sidecar decide whether the query is retrieval-like.

## Degradation is part of the contract

- Missing embedding configuration: FTS-only retrieval.
- Missing vector table: FTS recall plus embedding rerank of recalled candidates.
- Missing routing table or query axes: no cross-domain projection.
- Missing relationship references: read projection remains `incomplete` and is not
  mislabeled as a persisted coupling state.

Every downgrade is returned in `diagnostics.degraded`; it is never silently hidden.
