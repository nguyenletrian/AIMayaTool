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

Legacy Scene patterns provide direct evidence that Setup must own several reusable rig-building primitives:
- `Scene_Pattern_SpaceSwitch.py` creates offset/default-space groups, parent constraints, enum/slide attributes, condition/reverse-style utility logic and weighted space blending. This is Setup constraints/spaces functionality; Scene should only store/compose the pattern data.
- `Scene_Pattern_Drivenkey.py` creates reusable SDK offset groups, driver/driven mappings, keyed driver values and linear driven keys. This belongs in Setup SDK/driven-key primitives; Scene should serialize and invoke them rather than recreate keyframe mechanics.
- `Scene_Pattern_CreateIK.py` performs joint-chain creation/orientation, duplicate IK/FK chains, pole-vector construction, control creation, grouping, parent constraints and local/world space switching. This is strong evidence that Goal 005 must establish controls, offsets, constraints/spaces and IK/FK composition APIs before Goal 007 migrates equivalent Scene patterns.

These are migration candidates, not a mandate to preserve historical UI grouping or implementation shape.

### Scene legacy surface
`MayaScriptNew/UIs/Scene.py` provides dynamic default/project functions plus ScenePattern items. Known pattern types include SingleScript, Global, DefaultValue, SpaceSwitch, Visibility, Layer, ControlShape, DefaultSwitchIKFK, NewSwitchIKFK, DrivenKey, ModuloSDK, ProxyAttribute, Rivet, Rename, GradientTexture, RopeStraight, RopeRoll, AimConstraint, Group, CreateRef, ReplacePath, and Note.

The actual `MayaScriptNew/UIs/ScenePattern/` directory is broader than that visible button list. Directory evidence includes AimConstraint, AnimationBackup, BSSequenceFromObjKeys, ClearOffset, ControlShape and ControlShapeAS, CreateAttribute, CreateCurve, CreateIK, CreateOffset, CreateRef and additional pattern modules. Goal 002 therefore treats the directory itself as authoritative inventory rather than inferring parity only from `UIs/Scene.py`.

`MayaScriptNew/UIs/SceneDefaultFunctions/` contains five curve-oriented ad-hoc scripts: Export Curve, Import Curve, Export Curve Up, Import Curve Up, and Update Curve Up. These are not five independent product capabilities; they form one control/curve-data workflow family with orientation/update variants. Their modern destination should be the shared Setup control-shape/curve serialization API, with Scene only composing or exposing that capability where project workflows need it.

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
| Shared geometry | Edge/vertex-to-curve and geometric proxy helpers | Replaced/Improved or Goal 003/005 dependency | Reuse accepted topology primitives first; migrate only uncovered generic mesh/curve helpers into shared Maya geometry APIs |
| Skinning | Graph skinning monolith | Replaced/Improved as primitives | Do not migrate monolith; reconcile remaining UX/adapter gaps only |
| Skinning | Selection sets/navigation | Missing, low-level UX family | Preserve useful navigation behavior only as thin UI/productivity actions; do not make selection-set state a Skinning core primitive |
| Setup | Basic controls/zero group | Migrated foundation | Expand beyond first slice |
| Setup | Control-shape catalog | Missing / partial foundation | Build explicit reusable shape library rather than copy `NLTA_Control` wholesale |
| Setup | Curve-shape IO/mirror/copy | Missing | Migrate as reusable control-shape workflow |
| Setup | Joint/transform matching | Missing | Migrate as deterministic transform/joint primitives |
| Setup | Attribute utilities | Missing | Migrate reusable connect/copy/visibility/lock helpers |
| Setup | Space switching / weighted parent spaces | Missing | Build explicit constraints/spaces API covering enum selection, optional blend/slide weights and reusable offset groups |
| Setup | Driven key / SDK graph | Missing | Build explicit serialized driver/driven key-data API and executor with predictable offset-group behavior |
| Setup | IK/FK chain construction | Missing | Build composable joint-chain, controls, pole-vector, IK/FK and matching primitives before Scene CreateIK parity |
| Setup | Naming/namespace workflows | Missing | Redesign with explicit data/config boundaries |
| Setup | Constraint metadata helpers | Missing | Reconcile with future constraints/spaces goal |
| Scene | ScenePattern model/serialization | Replaced/Improved | Keep current deterministic architecture |
| Scene | Display layers | Replaced/Improved | Reconcile legacy Layer pattern behavior |
| Scene | Build/hierarchy actions | Replaced/Improved | Reconcile legacy Group/CreateRef/etc. |
| Scene | CreateAttribute / CreateCurve / CreateIK / offset patterns | Missing | Implement through reusable Setup/core primitives, then expose as Scene composition |
| Scene | SpaceSwitch / IKFK / DrivenKey / SDK patterns | Missing but Setup-dependent | Scene should serialize/compose accepted Setup APIs; do not duplicate rig mechanics |
| Scene | ProxyAttribute / Rivet / Rope / AimConstraint patterns | Missing | Reconcile dependencies and migrate vertically |
| Scene | ControlShape patterns | Missing but Setup-dependent | Reuse modern Setup control-shape library rather than preserve duplicate pattern implementation |
| Scene | Default curve import/export/update scripts | Missing but Setup-dependent | Collapse five ad-hoc scripts into one shared curve/control-shape data workflow with explicit orientation/update options |
| Scene | BSSequence / animation-backup family | Missing or intentionally retired after usefulness review | Treat `AnimationBackup` as supporting/backup evidence, not automatically a public capability; evaluate the concrete blendshape-sequence workflow and preserve only production-useful behavior |
| Scene | Dynamic project/default functions | Replaced/Improved direction | Replace ad-hoc module discovery/loading with explicit registry/plugin contracts; retain project extensibility without arbitrary UI-time imports |
| Legacy repo hygiene | `.pyc` / `__pycache__` | Intentionally Retired | Generated bytecode is never a migration capability and must not enter AIMayaTool source |
| Legacy repo hygiene | zero-byte `NLTA_IK.py` / `NLTA_Scene.py` | Duplicate/Internal-only / Retired | Empty placeholders provide no behavior to migrate; actual IK/Scene behavior is inventoried from concrete callers/modules |
| Legacy repo hygiene | exact duplicate backups (for example `NLTA_Proxy_Backup.py`) | Duplicate/Internal-only | Do not count an identical backup blob as a second capability |
| Legacy repo hygiene | divergent `_Backup.py` files | Evidence only pending behavior reconciliation | Compare only where needed to discover behavior absent from the active module; never migrate backup files as separate product features |

## Architecture deductions for migration ordering

1. **Skinning paint state is an adapter concern.** Legacy `scriptJob`/global-session behavior must not become the new core API. First preserve deterministic skin/weight/influence primitives; then add an optional interactive paint-state adapter only for UX that genuinely requires persistent Maya context.
2. **Graph skinning is mostly already decomposed.** Ratio copying, influence transfer and active-joint gradient logic should reconcile against accepted AIMayaTool primitives before any new implementation; only uncovered option/UI behavior should create Goal 003 work.
3. **Proxy is not one domain primitive.** Proxy extraction/skin transfer is a Skinning workflow, while edge/vertex-to-curve and geometric helpers should be shared geometry/Maya primitives. Do not recreate `NLTA_Proxy` as a monolith.
4. **Control-shape data is a Setup primitive used by Scene.** Build one modern control-shape library and let Scene patterns compose it. Do not create separate Scene and Setup copies.
5. **Setup must own rig mechanics before Scene parity.** Space switching, SDK/driven-key execution, control/offset groups, constraint composition and IK/FK construction are reusable Setup responsibilities proven by legacy ScenePattern implementations. Scene should only own serializable pattern data, ordering and composition.
6. **CreateIK is a compound consumer, not the primitive.** Its behavior decomposes into control creation, offset/group creation, joint-chain generation/orientation, IK/FK duplication, pole-vector placement, constraints and space switching. Goal 005 should implement/test these pieces independently before Goal 007 exposes a CreateIK pattern.
7. **ScenePattern directory inventory is authoritative.** The visible `Scene.py` menu is insufficient because the directory contains additional modules not surfaced in the initial button map.
8. **Default Scene curve scripts collapse into one reusable primitive family.** Export/import/up-orientation/update variations belong in shared curve/control-shape serialization rather than five standalone Scene features.
9. **Backup/generated files are evidence, not product scope.** `.pyc`, `__pycache__`, zero-byte placeholders and exact duplicate backups are explicitly non-capabilities; divergent backups are inspected only if they contain behavior absent from active code.

## Migration-priority implications emerging from Goal 002

- Goal 003 Skinning should first finish genuine user-facing gaps around paint/brush workflows, proxy extraction/skin transfer, remaining IO variants and any graph-skinning options not already covered by accepted primitives.
- Goal 005 Setup is a dependency hub. Recommended early order inside Goal 005 is: **control-shape/offset primitives -> transform/joint matching -> attributes -> constraints/space switching -> SDK/driven keys -> IK/FK composition -> secondary rigs**. This sequence unlocks a large fraction of Goal 007 Scene patterns.
- Goal 007 Scene should avoid implementing rig mechanics directly until the corresponding Setup primitives exist; Scene patterns should become composition/data wrappers over those APIs.
- Shared geometry helpers discovered inside legacy Skinning/Proxy code should move to reusable Maya/geometry layers so Skinning, Setup and Scene can all consume them without duplication.

## Goal 002 closure blockers

Goal 002 may close only when these remaining evidence checks are resolved:
1. reconcile any production-useful behavior that exists only in divergent `NLTA_Mesh_Backup.py` or `NLTA_Skinning_Backup.py`; otherwise classify the backup-only differences as obsolete/internal with rationale;
2. finish the remaining ScenePattern directory family grouping, especially specialized animation/blendshape/build helpers, without treating each historical file as a separate product requirement;
3. verify current AIMayaTool public/domain inventory still matches the parity assumptions recorded here;
4. then mark every Goal 002 milestone complete and activate Goal 003.

## Next Goal 002 work
1. Resolve the closure blockers above with bounded source comparisons rather than broad re-inventory.
2. Preserve only behavior-level capability differences; generated/duplicate artifacts remain excluded.
3. Once closure blockers are resolved, finalize Goal 002 state and immediately begin Goal 003 Skinning vertical slices.

This file remains incomplete until Goal 002 acceptance is satisfied.