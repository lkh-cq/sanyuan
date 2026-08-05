# Palindrome ↔ Jiugong runtime MVP

This directory is an **experimental executable prototype**. It does not modify
the frozen ontology in `references/architecture.md` and does not claim an LLM,
a biological mechanism, or measured acceleration.

## Root contract

The runtime separates three layers:

1. **PAL storage syntax** — bilateral-inward storage of the independent head and
   singular center.
2. **Jiugong compute carrier** — center-outward materialization into four
   complementary orbits plus one fixed center.
3. **Mapping pack** — the only authoritative bridge between storage addresses
   and compute coordinates.

Canonical PAL 0.1 text:

```text
pal@palindrome-jiugong-v0.1[A>B>C>D|e]
```

Its logical full form is:

```text
A B C D e D C B A
```

and its legacy nested view is:

```text
{A{B{C{D{e}D}C}B}A}
```

The matrix carrier is materialized from the center outward:

```text
A B C
D e D
C B A
```

## Packages

- `palindrome-syntax/`: dependency-free Python parser and AST for PAL 0.1.
- `palindrome-matrix-torch/`: differentiable PyTorch mapping, closure checks,
  and a minimal concurrent center-context emergence layer.
- `palindrome-matrix-r/`: base-R PAL parser, mapping, closure checks, constant-
  time complementary lookup, and a generic snapshot/commit emergence step.
- `mapping-packs/jiugong-v0.1.json`: shared coordinate and invariant contract.

## Frozen MVP semantics

- Storage order is outer-to-inner head plus center: `[A,B,C,D,e]`.
- The complementary tail is lazy: `complement(reverse(head))`.
- Writing is bilateral-inward; compute expansion is center-outward.
- A head address determines its complementary logical and matrix address
  without scanning the tail.
- Compute matrices must close under the mapping pack before being stored.
- The five orbit updates read one old snapshot and commit together.

## Local tests

```bash
cd runtime/palindrome-syntax
python -m pytest

cd ../palindrome-matrix-torch
python -m pytest

R CMD check ../palindrome-matrix-r
```

The R package is intentionally dependency-free at runtime; `testthat` is only a
suggested test dependency.
