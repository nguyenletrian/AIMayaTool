# AIMayaTool Legacy Parity Map

Status: Work in progress for `aimayatool-002`.

This document is the durable reconciliation surface between `nguyenletrian/MayaScriptNew` and AIMayaTool. It is not a request to copy legacy modules. Each useful legacy workflow must end in one of these states before program completion: `Migrated`, `Replaced/Improved`, `Missing`, `Duplicate/Internal-only`, or `Intentionally Retired` with rationale.

## Current AIMayaTool baseline

### Skinning
Current UI/API already exposes influence add/remove, max-influence check/fix, copy skin weights, explicit influence transfer, SkirtParent, mirror skin, lock/unlock, prune, clear joint weights from vertices, select affected vertices, and skin-data import/export. Advanced deterministic primitives already exist for ratio/gradient/topology/SkirtParent workflows and have prior Maya validation evidence in HISTORY.md.

### Setup
Current UI is intentionally small: create matched Circle/Box controls and create zero groups. The domain currently contains reusable control/transform primitives, but does not yet approach the breadth of the legacy Setup UI.

### Scene
Current API contains deterministic ScenePattern model/registry/create/load/edit/save operations, display-layer helpers, and reusable scene build/hierarchy actions. The current Scene UI is descriptive/minimal and does not yet expose the breadth of the legacy Scene workflow surface.

## Legacy evidence baseline

### Skinning legacy surface
`MayaScriptNew/UIs/Skinning.py` exposes a substantially broader interactive surface. Known workflow families include:
- animation/keyframe convenience actions mixed into the old Skinning UI;
- paint-skin unlock/isolate/smooth/pick/copy/flood/brush switching;
- direct incremental weight buttons and replace/add weight operations;
- mirror skin;
- proxy creation/copy/paste/closest-faces helpers;
- copy/bind/add/remove/cleanup skin influences;
- export/import skin, existing-skin import, folder and quick-folder skin IO;
- FBX/new-scene export helpers;
- component/fix/clear-weight utilities;
- selection-set navigation;
- max-influence check/fix;
- graph-skinning and proxy/curve helpers.

The old UI directly imports/reloads many global `NLTA_*` modules. AIMayaTool must preserve useful behavior while replacing that coupling with deterministic domain APIs plus thin interactive wrappers.

### Setup legacy surface
`MayaScriptNew/UIs/Setup.py` exposes workflow families including:
- curve-shape export/import/mirror/copy;
- joint creation, freeze, axis/orient, transform matching, hierarchy matching, FBX-joint and hierarchy-to-joints workflows;
- per-channel attribute copy;
- namespace create/delete;
- attribute create/connect/unlock/show and clipboard-style helpers;
- joint/object naming export/import/temp restore workflows;
- rotate-order/object-on-curve/point-on-plane pattern helpers;
- FBX cleanup, ngon checks, parent-constraint data capture/restore, AI-attribute cleanup, and OCIO helper actions.

These are migration candidates, not a mandate to preserve historical UI grouping or implementation shape.

### Scene legacy surface
`MayaScriptNew/UIs/Scene.py` provides dynamic default/project functions plus ScenePattern items. Known pattern types include SingleScript, Global, DefaultValue, SpaceSwitch, Visibility, Layer, ControlShape, DefaultSwitchIKFK, NewSwitchIKFK, DrivenKey, ModuloSDK, ProxyAttribute, Rivet, Rename, GradientTexture, RopeStraight, RopeRoll, AimConstraint, Group, CreateRef, ReplacePath, and Note.

AIMayaTool already has the deterministic ScenePattern/data/build foundation, but most legacy pattern behaviors and equivalent modern UI exposure still require reconciliation.

## Preliminary parity classification

| Domain | Workflow family | Current state | Direction |
| --- | --- | --- | --- |
| Skinning | Influence add/remove | Migrated | Keep deterministic API + thin selection UI |
| Skinning | Max influence check/fix | Migrated | Preserve and modernize UX |
| Skinning | Copy skin / weight transfer | Migrated / Improved | Keep explicit APIs, reconcile remaining legacy variants |
| Skinning | Mirror skin | Migrated | Validate remaining option parity |
| Skinning | Skin data import/export | Migrated (core path) | Reconcile folder/existing/quick variants |
| Skinning | Paint/brush workflow | Missing | Redesign as coherent modern weight-edit workflow |
| Skinning | Proxy workflow | Missing | Reconcile useful proxy behavior before migration |
| Skinning | Graph skinning | Partially Replaced/Improved | Map legacy graph actions onto accepted gradient/ratio primitives and identify remaining gaps |
| Skinning | Selection sets/navigation | Missing or cross-domain | Decide correct modern domain/UI placement |
| Setup | Basic controls/zero group | Migrated foundation | Expand beyond first slice |
| Setup | Joint/transform matching | Missing | Migrate as deterministic transform/joint primitives |
| Setup | Attribute utilities | Missing | Migrate reusable connect/copy/visibility/lock helpers |
| Setup | Naming/namespace workflows | Missing | Redesign with explicit data/config boundaries |
| Setup | Curve-shape IO/mirror/copy | Missing | Migrate as reusable control-shape workflow |
| Setup | Constraint metadata helpers | Missing | Reconcile with future constraints/spaces goal |
| Scene | ScenePattern model/serialization | Replaced/Improved | Keep current deterministic architecture |
| Scene | Display layers | Replaced/Improved | Reconcile legacy Layer pattern behavior |
| Scene | Build/hierarchy actions | Replaced/Improved | Reconcile legacy Group/CreateRef/etc. |
| Scene | SpaceSwitch / IKFK / DrivenKey / SDK patterns | Missing | Implement on reusable Setup primitives rather than duplicating rig logic in Scene |
| Scene | ProxyAttribute / Rivet / Rope / AimConstraint patterns | Missing | Reconcile dependencies and migrate vertically |
| Scene | Dynamic project/default functions | Partially Missing | Replace unsafe ad-hoc loading with explicit registry/plugin contract if still useful |

## Next Goal 002 work
1. Complete full source/module/UI inventory for all three target domains, including helper symbols and duplicate/backup modules.
2. Expand every useful legacy workflow into this matrix with file/symbol evidence and one final classification.
3. Identify cross-domain dependencies so Scene patterns reuse Setup primitives and Skinning helpers reuse shared geometry/selection primitives.
4. Produce dependency-ordered migration slices for Goals 003-008.

This file remains incomplete until Goal 002 acceptance is satisfied.