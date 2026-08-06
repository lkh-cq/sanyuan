# visualR

R-based runtime prototype for PAL (Palindrome Address Language) and Jiugong topology computation.

## Position

visualR is the reference R implementation layer:

- PAL recursive containment storage
- Jiugong matrix materialization
- minimal diamond field generation
- rotation measure based operator expansion
- provenance-aware conflict detection

The design principle:

> PAL stores topology. Matrix materializes computation.

## Core layers

```
visualR
├── storage
│   └── PAL containment syntax
├── geometry
│   └── diamond minimal field
├── operator
│   └── Jiugong 0-4 states
├── phase
│   └── rotation measures
└── runtime
    └── emerge / wrap / validate
```

## Initial constraints

- Fourth-order PAL state expands to a 3x3 carrier.
- Repeated symbols are relations, not duplicated storage.
- Compute views are generated from rules, not stored permanently.
- Conflict detection must preserve symbol, position, phase and provenance.

Status: experimental MVP.
