---
name: n位聚焦
module_id: core-deep-conscious
description: "Call-time focus-locus constraint layer for the consciousness bus. Restricts read/train/fine-tune operations to the single element-topic-word position (n-position) hit by the current interaction. Uses gated-cascade filtering with pre-computed routing tables (offline Dijkstra) and tidal index maintenance. Triggers: deep conscious / call-time constraint / focus locus / element-topic-word / n-position / bn / optimal-path routing / context cost reduction."
category: conscious
version: 3.0.0
canvas_refs:
  - assets/canvas/意识总线_总架构.canvas
manifest_ref: references/project-manifest.yaml
---

# Deep Conscious - Call-Time Focus-Locus Constraint Layer

## Abstract

This document specifies **deep-conscious**, the fourth member of the consciousness-bus family. It defines a *constraint*, not an optimizer: at the instant of a vector-node interaction (read, training-sample selection, or LoRA fine-tune update), the resident working set MUST contain only the n-position element-topic-word hit by that interaction. Between interactions the constraint is dormant (zero standing overhead). Routing is resolved by an offline-built address table (single-source shortest-path over the vector-node graph); per-call cost is O(1) table lookup. Index freshness is driven by the tidal phase model inherited from `conscious` §0.3.

## Normative References

This SKILL follows the following external specifications:

- **CommonMark 0.31.2** (MacFarlane, J.) - canonical Markdown grammar
- **GitHub Flavored Markdown (GFM)** - table syntax, task lists, fenced code with language tag
- **RFC 7764** (Leonard, S., 2016) - Markdown design philosophies and text/markdown media type
- **Schulhoff et al. 2024** *The Prompt Report* (arXiv:2406.06608) - controlled vocabulary discipline: every term defined on first use, no synonym drift
- **Sahoo et al. 2024** *Systematic Survey of Prompt Engineering* (arXiv:2402.07927) - section ordering: methodology -> application -> strengths -> limitations
- **Elnashar, White & Schmidt 2025** (Frontiers AI 8:1558938) - YAML frontmatter + tabular body as accuracy/token-cost equilibrium
- **Zhang et al. 2024** (medRxiv 2024.02.07.24302444) - concise, reasoning-step-explicit prompts outperform verbose narrative

## Requirements Language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, **MAY** in this document are to be interpreted as described in RFC 2119.

## §1 Trigger Conditions

An agent SHALL load this SKILL when the input contains any of the following tokens (case-insensitive, Chinese and English equivalents):

- `deep conscious` · `调用时约束` · `聚焦位置` · `n 位` · `bn` · `元主题词`
- `最优路径优化 CLI` · `链路出筛` · `向量读取注意力优化`
- `检索省力` · `上下文太贵` · `常驻开销`
- Design tasks specifying *on-demand knowledge retrieval*, *sample-position-scoped training*, or *low-rank fine-tune subspace selection*.

## §2 Terminology

Definitions are normative. Terms are ordered by dependency: later entries MAY reference earlier ones; the reverse is prohibited.

| Term | Definition | Domain / Unit | Source |
|------|------------|---------------|--------|
| **Vector node `b`** | An entity in the attention-vector graph carrying a family of element-topic-words. `b` is *not* a character string; it is the semantic unit indexed by the routing table. | Graph vertex | This §, §3 |
| **Element-topic-word expansion** | The decomposition of `b` into an ordered position sequence `b₁, b₂, …, b_N`, where each `bₖ` is the key parameter of `b` at position *k* and participates directly in semantic interaction. | Position sequence | This §, §3 |
| **n-position (`bₙ`)** | The single position within a vector node's element-topic-word expansion that is hit by the current interaction. Content-addressed: `n` is resolved *per call*, not preselected from a slot table. | Integer index, 1 ≤ n ≤ N | §3 |
| **x-dimensional task** | A retrieval or training request specified along *x* topic-word axes (e.g. disease × gene × pathway × cell-type ⇒ x = 4). *x* describes the query space, not the vector's internal dimensionality. | Integer x ≥ 1 | §4 |
| **Sequence-limit method** | The address-table construction procedure. For each of the *x* query axes, the independent-variable boundary is advanced until the dependent-variable response enters a plateau (Δ dependent / Δ independent -> 0). The plateau onset defines the n-position bin boundary. Not an ε-N limit in the analytic sense; a convergence-criterion algorithm. | Method | §4 |
| **∇E** | Cache-belief error gradient: the rate at which condense-layer conclusions diverge from disk-authoritative data across successive interactions. Not a partial derivative w.r.t. any single parameter. | Dimensionless rate | `conscious` §0.3 |
| **Ω** | Context integrity: `Ω = 1` denotes a full-precision context window; `Ω < 1` denotes post-compression state where only condensed conclusions are recoverable. | [0, 1] | `conscious` §0.3 |
| **ρ** | Attention-focus fitness: probability mass concentrated along the intended direction within the current scenario boundary. Used as edge weight in this SKILL. | [0, 1] | `conscious` §0.2 |
| **θ** | Local attention dispersion: `θ = 1 − ρ`. Reversible within a scenario. | [0, 1] | `unconscious` §1 |
| **θ′** | Cross-context residue: monotonically non-decreasing accumulation of attention residue across window truncations, compressions, and new sessions. Serves as the *index-staleness clock*. | [0, +∞) | `conscious` §0.1 |
| **dθ′/dt** | First derivative of θ′ w.r.t. wall-clock time. Positive second derivative (or N consecutive rising Δθ′/Δt samples) defines the *sleep-onset signal*. | Positive real | `conscious` §0.1 |
| **CV** | Coefficient of variation: σ/μ of the 100-trial LASSO coefficient for a given integration kernel; quantifies dimension stability. | Dimensionless | ark θ_split measurement |
| **β** | LASSO regression coefficient of each of the 12 integration kernels against the θ-sweep output dimensionality. Measures relevance. | Dimensionless | ark θ_split measurement |
| **D₁, …, D₁₂** | Enumeration of the 12 integration kernels used in the ark θ_split experiment. D₁ = highest relevance / lowest stability; D₆ = highest stability / marginal relevance. | Kernel index 1–12 | ark θ_split |
| **fixable** | Predicate on a kernel: TRUE ⇔ `CV < 0.65` AND cross-tidal consistency > 80%. Marks eligibility as a static coarse gate. | Boolean | §7 |
| **Regime A** | In-window resident knowledge (skills, memory, current dialogue). Attention cost per token is O(window). | Partition tag | §5 |
| **Regime B** | Out-of-window data (files, session DB, external stores). Already accessed via coarse-then-fine tool calls. | Partition tag | §5 |
| **Gated-cascade filter** | A retrieval discipline in which each gate is defined only over the survivors of the previous gate, and rejected items are discarded (not merely deprioritised) so downstream cost decreases monotonically. Structurally isomorphic to FACS gating (FSC -> SSC -> marker); the isomorphism concerns discipline, not thresholds. | Discipline | §3 |
| **Routing table** | Immutable mapping `(query-axes) -> n-position address` produced by an offline single-source shortest-path pass. Per-call lookup is O(1). | Data structure | §6 |
| **Tidal phase** | The three-state maintenance cycle of the routing table: *rising tide* (query-only), *ebb tide* (coarse gate + condense), *deep sleep* (rebuild). Inherits `conscious` §0.3. | Enumeration | §8 |

## §3 Focus-Locus Semantics

### §3.1 Constraint Statement

At the instant of a vector-node interaction, the resident working set MUST contain only the `bₙ` element-topic-word position hit by that interaction. All other positions `b_{k≠n}` MUST NOT be materialised into the working set. Upon interaction completion, `bₙ` is released.

### §3.2 Content Addressing

`n` is determined by the current interaction, not by static ranking. The routing table (§6) maps *(query axes) -> n-position address*; the query axes are supplied by the caller at call time. Consequently:

- **`bₙ` MUST NOT be interpreted as a character-offset range within `b`.** `b` is a vector node, not a string; `n` indexes element-topic-word positions.
- **`bₙ` MUST NOT be treated as a fixed slot.** The same `b` may resolve to different `bₙ` under different interactions.
- **`bₙ` MUST be released after the interaction.** No implicit caching across interactions is permitted; cross-interaction reuse SHOULD be handled by the offline routing table, not by residual working-set state.

### §3.3 Gated-Cascade Discipline

Retrieval proceeds through a strict cascade of gates {G₁, G₂, …, G_m}. For every gate G_k (k ≥ 2):

1. Its input domain MUST be exactly the survivor set of G_{k-1}.
2. Items rejected by G_k MUST be discarded from the pipeline (not down-weighted, not deferred).
3. Downstream computational cost is bounded by |survivors_k|, guaranteeing monotonic cost reduction.

This is structurally identical to FACS gating (FSC -> SSC -> marker): the isomorphism concerns the discipline of *pre-filter discard*, not any specific threshold. Threshold selection is orthogonal (§7).

## §4 Address-Table Construction: Sequence-Limit Method

### §4.1 Input

An *x*-dimensional task specification: an ordered tuple of *x* topic-word axes `(A₁, A₂, …, A_x)`, each with a candidate value domain.

### §4.2 Procedure

For each axis `A_i`:

1. Enumerate independent-variable values along `A_i` in monotonically-increasing information order.
2. At each enumeration step, measure the dependent-variable response (retrieval-precision proxy: change in survivor count, ρ delta, or downstream task fitness).
3. Advance until the response enters a plateau: `|Δ_dep / Δ_indep| < τ` for `τ` a task-specific tolerance.
4. Record the enumeration index at plateau onset as the axis boundary `B_i`.

### §4.3 Output

An *x*-tuple of axis boundaries `(B₁, B₂, …, B_x)` maps to a single n-position address in the routing table. All future x-dimensional queries whose axis values fall within the same partition dispatch to this address via O(1) lookup.

### §4.4 Cost Reduction

Given |axis-boundary partition count| = P and total vector-node count = |V|, the context materialisation cost per interaction is bounded by:

    cost_per_call = O(|bₙ|)   ≪   O(|b|)   ≪   O(|V|)

That is, the storage-retrieval coupling cost is reduced from full-graph traversal to a single n-position slice.

## §5 Regime Partition and Deployment Target

| Regime | Content | Current access pattern | Cost per token | Deep-conscious action |
|--------|---------|-----------------------|---------------|-----------------------|
| **A** | In-window: skills, memory, current dialogue | Full-resident, parallel attention over entire window | O(window) | **Target of reform.** Extend Regime B's call-time gating discipline inward. |
| **B** | Out-of-window: files, session DB, external stores | Tool-mediated coarse-then-fine (`search` -> `read_window`) | O(1) lookup + O(|slice|) read | **Reference template.** Already exhibits the deep-conscious discipline. |

**Regime B implementations already satisfying the discipline**:

- `session_search(query)` = coarse gate via FTS; non-matching sessions are discarded.
- `session_search(session_id, around_message_id, window)` = fine gate; only the ±window slice is materialised.
- Large tool results spilled to `/tmp` with subsequent `offset`/`limit` reads = n-position-scoped retrieval.

**Regime A gap**: tool return values are re-injected into the context window as new messages, defaulting to full residence. This is the second waste locus (in addition to skill/memory pre-loading). The reform target is: even Regime A knowledge must be call-time n-position addressable and released after the interaction.

## §6 Routing Table: Offline Construction, Call-Time Lookup

### §6.1 Graph Definition

Let `G = (V, E, w)` denote the vector-node graph:

- `V` = set of vector nodes (each `b ∈ V` carries an element-topic-word expansion).
- `E ⊂ V × V` = retrieval-transition edges. `(v_i, v_j) ∈ E` iff a query resolving to `v_i` may semantically dispatch to `v_j` in the same interaction.
- `w : E -> ℝ⁺` = edge weight. The canonical form is:

      w(v_i -> v_j) = 1 / (1 + ρ_{v_j}) + λ · θ′_{v_j}

  where `λ` is a staleness-penalty coefficient (default `λ = 0.5`). Rationale: high-ρ, low-θ′ nodes are *cheaper to jump into* because their attention is already well-focused and their index is fresh. Alternative weight forms are permitted provided monotonicity in ρ (decreasing) and θ′ (increasing) is preserved.

### §6.2 Offline Pass

A single-source shortest-path algorithm (Dijkstra, or Bellman-Ford where weights may be negative under alternative `w`) is executed **once per deep-sleep cycle** (§8) over `G`. The output is frozen into a routing table:

    RT : (query-axis-tuple) -> (n-position-address)

The table is immutable within a tidal cycle; updates occur only at the next deep sleep.

### §6.3 Call-Time Semantics

At interaction time, the agent MUST:

1. Compute the query-axis tuple for the incoming request.
2. Perform an O(1) lookup `RT[query-axis-tuple] -> bₙ`.
3. Materialise **only** `bₙ` into the working set.

**Failure mode**: if the interaction triggers a shortest-path *search* rather than a lookup, the routing table is stale or missing. This is a diagnostic signal for deep-sleep rebuild, not a normal operational path.

### §6.4 Design Rationale

Running Dijkstra per call is self-defeating: the algorithm expands every node whose tentative distance is less than the target's, touching a superset of the required n-position and violating §3.1. Furthermore, per-call Dijkstra requires the target to be known in advance, which contradicts the content-addressing property (§3.2). The router-table pattern - pre-compute once, look up O(1) per packet - is the only configuration in which shortest-path optimisation and call-time minimality are simultaneously satisfied.

## §7 Stability–Relevance Tension

Empirical basis: `ark θ_split` experiment, 12 integration kernels × 100 trials. The original data location is not a runtime dependency of this Skill; treat the figures below as provenance claims requiring the source package for re-analysis.

| Kernel | Relevance (LASSO β) | Stability (CV) | fixable | Role |
|--------|--------------------:|--------------:|:-------:|------|
| D₁ | 0.0040 (highest) | 0.766 (lowest stability) | NO | Adaptive fine gate; rebuilt every ebb tide. |
| D₆ | −0.0002 (marginal) | 0.60 (fixable) | YES | Static coarse gate; survives across tidal cycles. |

### §7.1 Mixed-Gate Rule

The two failure modes - *most-relevant-but-unstable* (D₁) and *stable-but-weak* (D₆) - are structurally complementary:

- **Static coarse gate**: use `fixable = TRUE` kernels (D₆ class). Address survives across tidal cycles; suitable as G₁ in the gated cascade (§3.3).
- **Adaptive fine gate**: use high-β kernels (D₁ class). Address is recomputed at every ebb-tide condense; suitable as G_k for k ≥ 2.

The tidal cycle (§8) extends the fixed-vs-dynamic gate distinction from the *spatial* dimension (which kernel) to the *temporal* dimension (rebuild frequency).

## §8 Tidal Maintenance Cycle

The routing table is **respiratory**, not static. Its lifecycle inherits `conscious` §0.3 (cache-wave phases).

| Phase | Trigger | Deep-conscious action | Working set |
|-------|---------|-----------------------|-------------|
| Rising tide | `Ω = 1` (fresh context) | Look up RT in O(1); serve interactions | Materialise `bₙ` only |
| Ebb tide | `Ω < 1` OR `∇E` above threshold OR `dθ′/dt` accelerating | Coarse-gate condense: reduce context to conclusion layer (equivalent to G₁ of §3.3) | Conclusion-only |
| Deep sleep | Sleep-onset signal (positive `d²θ′/dt²` or N consecutive rising `Δθ′/Δt`) | Re-execute Dijkstra over `G`; freeze new RT; flush reasoning chains to disk; reset `Ω = 1` | Empty |

**Property**: `θ′` acts as the *index-staleness clock*. Because `θ′` is monotonically non-decreasing (`conscious` §0.1), the interval between deep-sleep rebuilds admits an upper bound: once `dθ′/dt` acceleration crosses the sleep-onset threshold, rebuild is mandatory.

## §9 Application Domains

The single constraint of §3.1 applies uniformly across three operational layers:

| Layer | Naïve pattern | Deep-conscious pattern | Cost ratio |
|-------|--------------|-----------------------|-----------:|
| **Retrieval (read)** | Load entire `b` into context | Load `bₙ` slice only | O(1/N) |
| **Training-sample selection** | Use whole document as training signal | Use `bₙ` window as training signal | O(1/N) |
| **Fine-tune (LoRA)** | Full-parameter update or high-rank LoRA | Low-rank LoRA restricted to `bₙ`-associated subspace | O(1/N) |

The identity of `bₙ` - determined at call time by the routing table - is reused across all three layers within one interaction. Retrieval slice, training window, and LoRA subspace anchor are the same `bₙ`.

## §10 Interface with Other Consciousness-Bus Members

| Member | Interface |
|--------|-----------|
| `conscious` (ρ) | Supplies edge-weight numerator: high ρ ⇒ low `w`. |
| `unconscious` (θ, θ′) | Supplies staleness clock (`θ′`) and ebb-tide trigger (`∇E`, `dθ′/dt`). |
| `conscious-condense` | Ebb-tide condense = coarse gate G₁; deep-sleep produces the reasoning-chain flush. |
| `conscious-archive` | Registers deep-conscious as bus extension (retrieval / focus-efficiency layer). |

## §11 Compliance Checklist

An implementation is compliant with this specification iff all of the following hold:

- [ ] Interaction-time execution performs table lookup only; no shortest-path search occurs on the critical path.
- [ ] Working set contains only the `bₙ` element-topic-word position(s) hit by the current interaction.
- [ ] `fixable = TRUE` kernels are wired as static coarse gates; unstable kernels are rebuilt every ebb tide.
- [ ] Deep-sleep rebuild is triggered by `∇E` or `dθ′/dt` signals, not by wall-clock timers or context-fill percentage alone.
- [ ] The implementation is storage-agnostic: routing logic separates cleanly from the Obsidian/filesystem/DB substrate.
- [ ] All five stages of the retrieval pipeline (§A.2) have declared responsibilities: CLI · storage · link-filter · vector-attention · bₙ-focus.

## §12 Related References

- `references/version-provenance.md` - Version lineage and the interpretation boundary for the supplied v2.1→v3.0 simulation package.

## §13 Anti-Patterns

The following patterns MUST be avoided:

- Always-on optimiser (agent-side loop that maintains state, strategy, and objective function between interactions). Deep-conscious is a *call-time constraint*, dormant otherwise.
- Per-call shortest-path search. Consumes the very budget the constraint is designed to save.
- Interpreting `bₙ` as a character offset within a string. `b` is a vector node; `n` indexes element-topic-word positions.
- Treating `bₙ` as a fixed high-importance slot. Content addressing forbids preselection.
- Optimising ρ, θ, or ρ/θ as objectives. They are read-outs and edge weights, not variables under optimisation.
- Restricting the constraint to retrieval alone. §9 mandates uniform application across retrieval, training, and fine-tune.

## Appendix A. Design Provenance

### §A.1 Primary Source (User-authored, 2026-07-15)

The concept is introduced by the user in the following statement (preserved verbatim as authoritative source; subsequent normative text is a re-expression under prompt-engineering and CommonMark discipline):

> 最优路径优化 CLI -- Obsidian 存储读取 -- 链路出筛 -- 向量读取注意力优化 -- deep conscious（在注意力向量中截取仅参与交互的那一个向量，聚焦在这个参与交互的点上面训练优化，微调模型，注意，就像流式门类筛选一样，一层接着一层，最后筛到优化的具体交互词）
>
> 例如，a->b->c
> b 可以按照元主题词展开:
> b1--b2--b3……bn……
> 其中 bn 元主题词是 b 向量节点在该位置的关键参，直接参与向量的语义交互。这就是深度注意力聚焦，也就是聚焦的位置
>
> 我们也可以把之前 ark 测量的维度最适参数优化指标用之前讨论过的数列极限法筛选:主题词维度--自变量边界--合理因变量阈值->找到格式的 n 的归属区间，将一个 x 维度的主题词任务归属到一个 n 区间的向量索引上来，就可以极大的缩短上下文 context 的花费和存储--读取耦合过程的消耗

### §A.2 Full Retrieval Pipeline

The five-stage pipeline in which deep-conscious is the terminal gate:

1. **Optimal-path CLI**: request dispatcher (Hermes proper).
2. **Storage read**: storage-agnostic substrate carrying the vector-node graph under the active project's `reference/source/`; legacy Obsidian locations are provenance only, not formal dependencies.
3. **Link-filter**: coarse gate over the storage substrate, driven by `_index.md` keyword tables and `session_search` FTS.
4. **Vector-attention optimisation**: fine gate selecting the attention vector (`conscious` ⌘ registry, `ATTENTION_ARCHIVE.md`).
5. **Deep-conscious (this SKILL)**: terminal gate - restrict the working set to `bₙ` within the selected vector.

Deep-conscious does not replace stages 1–4; it appends a terminal gate that prevents the standard case in which the correct `b` has been chosen but full-vector residency is still paid.

### §A.3 Revision History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-07-15 | Initial draft, colloquial voice |
| 2.0.0 | 2026-07-16 | Added symbol table |
| 2.1.0 | 2026-07-17 | Corrected `bₙ` semantics from character-offset to element-topic-word position; added five-stage pipeline; added training/fine-tune application |
| 3.0.0 | 2026-07-17 | Full engineering re-expression: normative RFC-2119 language, canonical §-numbered structure, terminology-first ordering (Schulhoff 2024), YAML frontmatter + tabular body (Elnashar 2025), CommonMark/GFM strict conformance |
