# MayaScriptNew -> AIMayaTool Migration

## Foundation
- [x] GUIDE and architecture rules
- [x] `.gitignore`
- [x] drag/drop `bootstrap.py`
- [x] `aimayatool` package entry point
- [x] registry-driven Maya UI shell
- [x] Skinning / Setup / Scene domains
- [x] AIBridge project manifest

## Goal 002 execution output
`PARITY_MAP.md` is the durable legacy-to-new reconciliation surface. This document converts that evidence into dependency-ordered vertical slices for Goals 003-008. These slices are implementation order, not permission to bulk-copy legacy modules.

### Goal 003 — Skinning complete migration
Source references:
- `UIs/Skinning.py`
- `Libs/NLTA_Skinning.py`
- `Libs/NLTA_GraphSkinning.py`
- `Libs/NLTA_Brush.py`
- `Libs/NLTA_Proxy.py`
- relevant mesh/general helpers

Already accepted primitives must be reused rather than rewritten: influence add/remove, max-influence check/fix, copy/mirror core paths, explicit influence transfer, ratio/profile weighting, gradient weighting, topology/region helpers, SkirtParent workflow, lock/unlock/prune/clear helpers, and core skin IO.

Remaining vertical slices, in order:
1. **Skin IO parity** — reconcile existing-skin import, folder/quick-folder variants, error handling, selection wrappers and batch-safe behavior around the accepted core serializer.
2. **Paint-state adapter** — keep influence lock/active-joint/session behavior outside the deterministic core; add only the Maya paint-context adapter required by interactive workflows.
3. **Brush weight editing** — modern replacements for smooth/pick/copy/flood/direct add/replace operations with explicit inputs underneath thin selection callbacks.
4. **Proxy skin workflow** — extract selected faces, optional mirror, bind/copy weights, copy/paste proxy skin data and closest-face matching; shared geometry helpers live outside Skinning.
5. **Graph UX parity** — expose only options still missing after mapping legacy `NLTA_GraphSkinning` behavior to accepted ratio/gradient/profile/influence primitives.
6. **Selection/navigation utilities** — retain only genuinely useful set/navigation actions and place cross-domain helpers outside Skinning when appropriate.
7. **Skinning UI parity + Maya regression** — compact workflow grouping, actionable validation, then mayapy/batch/live validation as required.

### Goal 004 — Skinning 2.0 modernization
After parity is complete:
1. profile API2/geometry/weight hot paths;
2. add bounded batch/preview/progress patterns where they materially help;
3. improve undo/error boundaries and invalid-selection guidance;
4. polish Skinning interaction design without moving domain logic back into UI.

### Goal 005 — Setup complete migration
Source references:
- `UIs/Setup.py`
- `Libs/NLTA_Control.py`
- reusable general/axis/IK helpers
- ScenePattern modules that currently embed rig mechanics

Dependency order is deliberate because Goal 007 Scene composition depends on these APIs:
1. **Control-shape library + offsets** — explicit shape data catalog, deterministic create/copy/mirror/serialize/deserialize operations, zero/offset-group primitives and thin UI presets.
2. **Transform/joint matching** — joint creation/orient/freeze, match T/R/all, hierarchy matching, FBX/hierarchy-to-joints behavior, with explicit inputs.
3. **Attribute primitives** — create/connect/copy/unlock/show/proxy-style attributes and reusable utility-node wiring.
4. **Constraint/space primitives** — parent/point/orient/aim helpers, maintain-offset behavior, enum space selection, optional blend/slide weights and reusable offset/default-space groups.
5. **SDK/driven-key primitives** — serialized driver/driven maps, reusable SDK groups, deterministic key creation/update, mirroring/merge behavior where retained.
6. **IK/FK composition** — chain creation/orientation, duplicate IK/FK chains, pole vectors, IK controls, matching/switching and space integration. Legacy `Scene_Pattern_CreateIK.py` is a compound consumer of these primitives, not the API design.
7. **Secondary rigs** — spline/rope/dynamic/additive helpers and other reusable secondary setup mechanics.
8. **Naming/namespace/project utilities** — migrate useful workflows with explicit data boundaries; retire one-off environment toggles when they are not product capabilities.
9. **Setup UI parity + Maya regression** — expose coherent workflows, not historical module groupings.

### Goal 006 — Setup 2.0 modernization
After Setup parity:
1. composable rig recipes built from accepted primitives;
2. mirror/batch operations with explicit preview/validation;
3. presets and preflight checks;
4. interaction polish and safer destructive actions.

### Goal 007 — Scene complete migration
Source references:
- `UIs/Scene.py`, `SceneU.py`, `SceneUNew.py`, `Scene_.py`
- `UIs/ScenePattern/*`
- `UIs/SceneDefaultFunctions/*`
- scene JSON data

Scene owns serializable pattern data, ordering and composition. It must not duplicate Setup rig mechanics.

Vertical slices, after required Setup APIs exist:
1. **Pattern inventory closure** — reconcile every concrete `ScenePattern` module, including modules not surfaced by the old menu, and collapse backup/duplicate variants to one capability classification.
2. **Primitive-backed patterns** — SpaceSwitch, DrivenKey/SDK, CreateIK, ControlShape, CreateAttribute, CreateCurve, offsets, AimConstraint and ProxyAttribute become thin Scene composition/data wrappers over Setup/shared APIs.
3. **Scene-native patterns** — Visibility, Layer, Group, CreateRef, Rename, ReplacePath, Note, DefaultValue/Global/SingleScript where still useful, using deterministic Scene APIs.
4. **Secondary/specialized patterns** — Rivet, RopeStraight/RopeRoll, GradientTexture, animation/blendshape backup/build helpers; classify each as migrated, replaced/improved or intentionally retired with rationale.
5. **Default/project function replacement** — replace ad-hoc script discovery/execution with an explicit registry/plugin contract where this workflow remains useful. The five curve default functions collapse into the shared Setup curve/control-shape serialization workflow.
6. **Legacy data compatibility** — add only adapters required by real legacy project data; keep canonical new data typed/versionable.
7. **Scene UI parity + Maya regression** — pattern create/edit/compare/run UX over deterministic APIs.

### Goal 008 — Scene 2.0 modernization
After Scene parity:
1. stronger preset/version management;
2. compare/edit/validation workflows;
3. reusable staged build pipelines;
4. clearer status/progress and interaction polish.

## Cross-domain dependency rules
- Skinning paint/session state is an adapter concern; deterministic skin/weight functions remain the primary API.
- Generic geometry helpers discovered in `NLTA_Proxy` belong in shared Maya/geometry layers, not a Skinning monolith.
- Control-shape data is owned once by Setup and consumed by Scene.
- Constraints/spaces, SDK, IK/FK and similar rig mechanics are owned by Setup; Scene stores and composes pattern data around them.
- Backup files, `.pyc`, duplicate variants and historical monoliths are evidence, not independent migration requirements.
- UI modernization happens during every vertical slice; Goal 009 is final product-wide unification/polish, not the first time UX is improved.

## Rules during migration
- Do not bulk-copy a legacy module.
- Do not preserve `NLTA_*` as the new public API.
- Before migrating a helper, identify duplicate/near-duplicate behavior and the narrow reusable primitive.
- Separate deterministic APIs from selection/context wrappers.
- No hard-coded local paths or checked-in bytecode.
- UI callbacks remain thin.
- Geometry-heavy code may use Maya API 2.0 when measurably useful.
- Every migrated vertical slice gets the cheapest sufficient deterministic verification plus Maya validation when host behavior requires it.
- Do not declare the migration program complete until Goal 013 rescans MayaScriptNew from scratch and every useful Skinning, Setup and Scene workflow is `Migrated`, `Replaced/Improved`, or `Intentionally Retired` with explicit rationale.
