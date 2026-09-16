# AIMayaTool History

This file records durable product/architecture milestones. Detailed task execution remains in `AIMayaToolTask.json`; active goals remain in `bridgeGoals.json`; Git history is the source of truth for exact changes.

## 2026-09-16 — Scene CreateCurve slice accepted

- Migrated the useful legacy ScenePattern CreateCurve behavior into deterministic AIMayaTool Scene planning/execution: multiline XYZ points, degree derived from point count, optional parent, hidden output, and optional rebuild spans.
- Corrected legacy semantics by making rebuild conditional instead of preserving the apparent always-rebuild behavior.
- Python route evidence proved both CreateCurve modules compile/import; the route twice omitted requested unittest execution, so that omission remains recorded as inconclusive route evidence rather than being misreported as a unit-test pass.
- Managed Maya 2024 validation passed in the existing managed session with a fresh unsaved scene: basic parented/hidden curve, optional rebuilt curve, and missing-parent world fallback all returned true; marker payload reported `success: True`.
- Accepted managed-smoke/product checkpoint: `e500a457bed90a90fe77facecc15a20913d33325`.
- Validation tier: normal Python compile/import evidence + managed live Maya 2024 host mutation.

## 2026-09-16 — Scene CreateAttribute slice accepted

- Migrated the legacy ScenePattern CreateAttribute workflow into deterministic AIMayaTool Scene APIs with normalized planning separated from Maya mutation.
- Corrected the shared Setup attribute primitive so Maya `matrix` attributes use dataType semantics consistently with `string` attributes.
- Python verification passed compile/import and 5/5 focused contract tests covering numeric, enum, dataType normalization, missing-object, and existing-attribute behavior.
- Managed Maya 2024 validation passed in the existing managed session with a fresh unsaved scene: numeric, enum, string, matrix, existing-attribute skip, and missing-object skip all returned true; marker payload reported `success: True`.
- Accepted product commits: `fa762952c8c2669664521f3f6d752a25bbb3e6bc`, `8494706a1779592e5786d0676a334926e3e26cea`, `1863258573e73f2793025add087d92bf87d7ac3d`; managed Maya smoke entrypoint commit `e9cd6549c244c01c23c238eec0ab67bb54cfa785`.
- Validation tier: normal Python deterministic verification + managed live Maya 2024 host mutation.

## Prior durable milestones

Earlier accepted architecture, Skinning, Setup, and Scene milestones remain preserved in Git history through the prior HISTORY checkpoint blob `c9404f150db66b6a9e55803a275872815d403e4e`.
