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

`MayaScriptNew/Libs/NLTA_Skinning.py` confirms lower-level responsibilities that must be reconciled independently from the old UI grouping:
- skin-session discovery/cache and active paint-influence tracking;
- skinCluster discovery and API 2.0 `MFnSkinCluster` access;
- explicit vertex-weight query/set helpers;
- joint-weight totals and normalized ratio extraction;
- skin envelope activation/deactivation;
- paint-context lock/unlock and active-influence workflows;
- selection-driven wrappers layered directly over global mutable session state and scriptJobs.

`MayaScriptNew/Libs/NLTA_GraphSkinning.py` confirms that several legacy graph-skinning algorithms are already conceptually superseded by accepted AIMayaTool primitives. The legacy module implements active-joint distance gradients, source-to-target ratio copying, explicit influence transfer, graph/profile evaluation, direct `MFnSkinCluster` weight access, and viewport refresh/normalization wrappers. These should not be migrated again as a monolith: Goal 002 should map each behavior to current `gradient_profile`, `gradient_weights`, ratio/weight-profile, influence-transfer, topology/region, and Maya adapter primitives, leaving only genuine missing UX or host-adapter behavior for Goal 003.

`MayaScriptNew/Libs/NLTA_Proxy.py` mixes two different capability families that must be separated in AIMayaTool:
- **Skin proxy workflow:** extract selected faces to a proxy mesh, optional axis mirror, bind/copy skin weights, clipboard-style copy/paste proxy skin data, and closest-face matching.
- **Geometry/retopology helpers:** edge/vertex to curve conversion, geometric center/farthest-point helpers, oriented curve creation and other mesh/curve operations.
The first family belongs primarily to Skinning workflow UX; reusable geometric operations belong in shared Maya/geometry primitives and must not force the whole legacy `NLTA_Proxy` module into Skinning.

The old UI directly imports/reloads many global `NLTA_*` modules. AIMayaTool must preserve useful behavior while replacing that coupling with deterministic domain APIs plus thin interactive wrappers. Stateful scriptJob/session behavior should only survive when a modern workflow truly needs it; deterministic functions must remain the primary API.

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

`MayaScriptNew/Libs/NLTA_Control.py` contains a large reusable control-shape template catalog rather than only one or two primitive shapes. That legacy data is a candidate for a modern explicit control-shape library, but not for wholesale module copying. The modern target should separate shape data, deterministic creation/mirroring/serialization primitives, and UI presets.

These are migration candidates, not a mandate to preserve historical UI grouping or implementation shape.

### Scene legacy surface
`MayaScriptNew/UIs/Scene.py` provides dynamic default/project functions plus ScenePattern items. Known pattern types include SingleScript, Global, DefaultValue, SpaceSwitch, Visibility, Layer, ControlShape, DefaultSwitchIKFK, NewSwitchIKFK, DrivenKey, ModuloSDK, ProxyAttribute, Rivet, Rename, GradientTexture, RopeStraight, RopeRoll, AimConstraint, Group, CreateRef, ReplacePath, and Note.

The actual `MayaScriptNew/UIs/ScenePattern/` directory is broader than that visible button list and includes additional concrete pattern modules such as AimConstraint, animation backup, blendshape-sequence generation, clear/create offsets, ControlShape variants, CreateAttribute, CreateCurve, CreateIK, CreateRef and other specialized builders. Goal 002 must inventory the directory itself, not infer parity only from `UIs/Scene.py`.

`MayaScriptNew/UIs/SceneDefaultFunctions/` currently contains five curve-oriented ad-hoc scripts: Export Curve, Import Curve, Export Curve Up, Import Curve Up, and Update Curve Up. These are not five independent product capabilities; they form one control/curve-data workflow family with orientation/update variants. Their modern destination should be the shared Setup control-shape/curve serialization API, with Scene only composing or exposing that capability where project workflows need it.

AIMayaTool already has the deterministic ScenePattern/data/build foundation, but most legacy pattern behaviors and equivalent modern UI exposure still require reconciliation.

## Preliminary parity classification

| Domain | Workflow family | Current state | Direction |
| --- | --- | --- | --- |
| Skinning | Skin discovery / skinCluster access | Replaced/Improved | Keep explicit deterministic discovery/API; retire global session coupling unless needed by interactive paint UX |
| Skinning | Vertex weight query/set primitives | Partially Replaced/Improved | Reconcile existing AIMayaTool weight primitives against legacy helper coverage |
| Skinning | Influence add/remove | Migrated | Keep deterministic API + thin selection UI |
| Skinning | Max influence check/fix | Migrated | Preserve and modernize UX |
| Skinning | Copy skin / weight transfer | Migrated / Improved | Keep explicit APIs, reconcile remaining legacy variants |
| Skinning | Influence ratio copy | Replaced/Improved | Use accepted ratio/profile primitives rather than re-migrating `NLTA_GraphSkinning.CopyRatioWeight` |
| Skinning | Active-joint distance gradient | Replaced/Improved | Use accepted gradient profile/weighting primitives; reconcile only missing UI options |
| Skinning | Mirror skin | Migrated | Validate remaining option parity |
| Skinning | Skin data import/export | Migrated (core path) | Reconcile folder/existing/quick variants |
| Skinning | Paint lock/unlock / active influence | Partially Migrated | Separate deterministic influence-lock operations from optional paint-context adapter |
| Skinning | Paint/brush weight editing | Missing | Redesign as coherent modern weight-edit workflow |
| Skinning | Proxy mesh extraction/mirror/skin copy | Missing | Migrate as explicit proxy workflow with deterministic mesh/skin primitives and thin selection UI |
| Shared geometry | Edge/vertex-to-curve and geometric proxy helpers | Partially Replaced/Unclassified | Reuse current topology primitives where possible; move generic mesh/curve operations out of Skinning-specific API |
| Skinning | Graph skinning monolith | Replaced/Improved as primitives | Do not migrate monolith; reconcile remaining UX/adapter gaps only |
| Skinning | Selection sets/navigation | Missing or cross-domain | Decide correct modern domain/UI placement |
| Setup | Basic controls/zero group | Migrated foundation | Expand beyond first slice |
| Setup | Control-shape catalog | Missing / partial foundation | Build explicit reusable shape library rather than copy `NLTA_Control` wholesale |
| Setup | Curve-shape IO/mirror/copy | Missing | Migrate as reusable control-shape workflow |
| Setup | Joint/transform matching | Missing | Migrate as deterministic transform/joint primitives |
| Setup | Attribute utilities | Missing | Migrate reusable connect/copy/visibility/lock helpers |
| Setup | Naming/namespace workflows | Missing | Redesign with explicit data/config boundaries |
| Setup | Constraint metadata helpers | Missing | Reconcile with future constraints/spaces goal |
| Scene | ScenePattern model/serialization | Replaced/Improved | Keep current deterministic architecture |
| Scene | Display layers | Replaced/Improved | Reconcile legacy Layer pattern behavior |
| Scene | Build/hierarchy actions | Replaced/Improved | Reconcile legacy Group/CreateRef/etc. |
| Scene | CreateAttribute / CreateCurve / CreateIK / offset patterns | Missing | Implement through reusable Setup/core primitives, then expose as Scene composition |
| Scene | SpaceSwitch / IKFK / DrivenKey / SDK patterns | Missing | Implement on reusable Setup primitives rather than duplicating rig logic in Scene |
| Scene | ProxyAttribute / Rivet / Rope / AimConstraint patterns | Missing | Reconcile dependencies and migrate vertically |
| Scene | ControlShape patterns | Missing but Setup-dependent | Reuse modern Setup control-shape library rather than preserve duplicate pattern implementation |
| Scene | Default curve import/export/update scripts | Missing but Setup-dependent | Collapse five ad-hoc scripts into one shared curve/control-shape data workflow with explicit orientation/update options |
| Scene | Animation/blendshape backup/build patterns | Unclassified | Determine usefulness and domain ownership before migration or retirement |
| Scene | Dynamic project/default functions | Partially Missing | Replace unsafe ad-hoc loading with explicit registry/plugin contract if still useful |

## Architecture deductions for migration ordering

1. **Skinning paint state is an adapter concern.** Legacy `scriptJob`/global-session behavior must not become the new core API. First preserve deterministic skin/weight/influence primitives; then add an optional interactive paint-state adapter only for UX that genuinely requires persistent Maya context.
2. **Graph skinning is mostly already decomposed.** Ratio copying, influence transfer and active-joint gradient logic should reconcile against accepted AIMayaTool primitives before any new implementation; only uncovered option/UI behavior should create Goal 003 work.
3. **Proxy is not one domain primitive.** Proxy extraction/skin transfer is a Skinning workflow, while edge/vertex-to-curve and geometric helpers should be shared geometry/Maya primitives. Do not recreate `NLTA_Proxy` as a monolith.
4. **Control-shape data is a Setup primitive used by Scene.** Build one modern control-shape library and let Scene patterns compose it. Do not create separate Scene and Setup copies.
5. **Scene rig patterns depend on Setup.** SpaceSwitch, IK/FK, DrivenKey/SDK, AimConstraint, CreateIK, ProxyAttribute and related patterns should be thin composition/data layers over accepted Setup primitives.
6. **ScenePattern directory inventory is authoritative.** The visible `Scene.py` menu is insufficient because the directory contains additional modules not surfaced in the initial button map.
7. **Default Scene curve scripts collapse into one reusable primitive family.** Export/import/up-orientation/update variations belong in shared curve/control-shape serialization rather than five standalone Scene features.
8. **Backup/duplicate legacy files are evidence, not separate capabilities.** `_Backup.py`, `.pyc`, duplicate ControlShape variants and similar artifacts must be reconciled to one behavior classification, not counted as independent migration requirements.

## Migration-priority implications emerging from Goal 002

- Goal 003 Skinning should first finish genuine user-facing gaps around paint/brush workflows, proxy extraction/skin transfer, remaining IO variants and any graph-skinning options not already covered by accepted primitives.
- Goal 005 Setup is a dependency hub: control-shape library/IO, transform/joint matching, attributes, constraints/spaces, IK/FK and SDK primitives unlock a large fraction of Scene parity.
- Goal 007 Scene should avoid implementing rig mechanics directly until the corresponding Setup primitives exist; Scene patterns should become composition/data wrappers over those APIs.
- Shared geometry helpers discovered inside legacy Skinning/Proxy code should move to reusable Maya/geometry layers so Skinning, Setup and Scene can all consume them without duplication.

## Next Goal 002 work
1. Complete full source/module/UI inventory for all three target domains, including helper symbols and duplicate/backup modules.
2. Expand every useful legacy workflow into this matrix with file/symbol evidence and one final classification.
3. Identify cross-domain dependencies so Scene patterns reuse Setup primitives and Skinning helpers reuse shared geometry/selection primitives.
4. Produce dependency-ordered migration slices for Goals 003-008.

This file remains incomplete until Goal 002 acceptance is satisfied.