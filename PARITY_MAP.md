# AIMayaTool Legacy Parity Map

Status: Goal 003 Skinning migration reconciled on 2026-09-13. Setup and Scene remain migration work for later goals.

This document maps useful MayaScriptNew behavior into AIMayaTool outcomes. Legacy file/module boundaries are not preserved when a cleaner deterministic API or different domain ownership is more appropriate.

## Skinning — Goal 003 closure

| Legacy workflow family | Goal 003 outcome | AIMayaTool direction |
| --- | --- | --- |
| Skin discovery / skinCluster access | Replaced/Improved | Explicit deterministic Maya adapters; no global legacy session cache as public API |
| Vertex weight query/set | Migrated / Improved | Explicit component/influence APIs and focused adapters |
| Influence add/remove | Migrated | Deterministic API + selection wrappers |
| Source mesh -> target missing influences (`Add Mesh jnt`) | Migrated | `influences.add_missing_from_source` plus UI selection wrapper |
| Remove unused influences (`Clr Unneed`) | Migrated | Deterministic remove-unused API + UI wrapper |
| Max influence check/fix | Migrated | Current check/fix workflow |
| Copy skin / copy weights / component copy | Migrated / Improved | Explicit copy workflows; target creation handled where appropriate |
| Influence transfer / ratio copy | Replaced/Improved | Explicit influence-transfer and ratio/profile primitives |
| Active-joint gradient / graph weighting | Replaced/Improved | Gradient profile + gradient weighting primitives; legacy GraphSkinning monolith retired |
| Mirror skin | Migrated | Current mirror workflow |
| Lock/unlock/prune/clear/select affected | Migrated | Explicit utility APIs and UI actions |
| Paint influence lock/isolate/parent/child/top-two/switch | Migrated / Improved | Deterministic influence state helpers plus thin paint-context adapter |
| Paint replace/add/smooth/flood/pick/switch sign | Migrated / Improved | `brush_weight` + `paint_state`; arbitrary values supersede fixed legacy increment presets |
| Paint copy weight | Migrated | Component weight copy workflow |
| Proxy extraction/mirror/skin transfer | Migrated | Explicit proxy workflow |
| Proxy skin copy/paste clipboard | Migrated | Persistent clipboard state only where UX genuinely requires it |
| Closest-face matching | Migrated | Explicit proxy/component helper exposed in UI |
| Selection-set navigation | Migrated | Thin productivity wrapper; not Skinning core state |
| Skin IO export/import | Migrated / Improved | Explicit export/import, existing-skin import, selected and quick wrappers |
| SkirtParent | Replaced/Improved | Decomposed planner/transfer/smoothing/executor with validated UI adapter |
| Shared topology needed by Skinning | Replaced/Improved | Reusable topology primitives rather than legacy monoliths |
| Legacy scriptJob/global paint session | Intentionally Retired as core API | Deterministic APIs are primary; host state exists only in bounded adapters |
| Legacy animation/keyframe buttons mixed into Skinning UI | Moved out of Skinning scope | General animation/Scene productivity concern |
| Legacy FBX/new-scene export buttons mixed into Skinning UI | Moved out of Skinning scope | Scene/export concern |
| Generic edge/vertex-to-curve and retopology helpers inside proxy code | Moved to shared geometry/Setup/Scene scope | Do not force generic geometry helpers into Skinning |
| Bind Skin convenience | Replaced/Improved | Current copy/bind-capable workflows cover target creation; no duplicate legacy button required |
| Component Editor launcher / native Maya convenience buttons | Intentionally Retired from parity core | Native Maya UI remains available; not duplicated without product value |
| Destructive clear-mesh/history helpers | Moved out of Skinning scope | Scene/cleanup/reliability concern |

### Goal 003 acceptance evidence

- Core influence, max-influence, copy, mirror, utility and skin-IO workflows were migrated and Maya-validated.
- Advanced ratio, gradient, influence-transfer, topology and SkirtParent workflows were decomposed into maintainable primitives and validated in Maya.
- Proxy, selection-set, paint-influence, brush-weight and full Skinning UI parity slices passed managed-live Maya validation.
- Source-to-target influence sync and unused-influence cleanup passed managed-live Maya validation after deterministic fixture correction.
- Final consolidated Skinning regression passed on managed Maya 2024 at commit `6462ecf81c5e47f13837ff200b51139b155e5e26` with marker `AIBRIDGE_UI_SMOKE_OK:SKINNING_CONSOLIDATED_REGRESSION_OK`.
- Stable checkpoint: `backup/2026-09-13-1757-SkinningGoal003FinalPASS-6462ecf`.

Result: every useful Skinning workflow identified for Goal 003 is now Migrated, Replaced/Improved, moved to its correct non-Skinning domain, or intentionally retired with rationale. Goal 003 may close; Goal 004 Skinning 2.0 can focus on performance, safety, batch productivity and UX rather than parity.

## Setup — remaining program work

Setup foundation exists for controls/transforms, but complete legacy parity remains for Goal 005. Important families include control-shape catalog and IO, joint/transform matching, attributes, constraints/space switching, SDK/driven keys, IK/FK composition, secondary rigs, naming/namespace workflows and reusable rig utilities.

## Scene — remaining program work

Scene has the deterministic ScenePattern/data/build foundation, but complete legacy Scene/ScenePattern parity remains for Goal 007 after required Setup primitives exist. Scene should compose Setup APIs rather than reimplement rig mechanics.

## Cross-domain ownership rules

1. Skinning owns weight, influence, paint-skin and skin-proxy workflows.
2. Setup owns reusable rig mechanics such as controls, transforms, constraints, spaces, SDK and IK/FK.
3. Scene owns serializable pattern data, build composition and scene workflow orchestration.
4. Shared geometry helpers live in reusable Maya/geometry layers when more than one domain benefits.
5. Generated bytecode, zero-byte placeholders and exact backup duplicates are not product capabilities.
6. Legacy `NLTA_*` module names are evidence only; they are not the AIMayaTool public API.
