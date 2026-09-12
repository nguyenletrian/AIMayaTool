# MayaScriptNew -> AIMayaTool Migration

## Foundation
- [x] GUIDE and architecture rules
- [x] `.gitignore`
- [x] drag/drop `bootstrap.py`
- [x] `aimayatool` package entry point
- [x] registry-driven Maya UI shell
- [x] Skinning / Setup / Scene domains
- [x] AIBridge project manifest

## Skinning — first slice
Source references:
- `UIs/Skinning.py`
- `Libs/NLTA_Skinning.py`
- `Libs/NLTA_GraphSkinning.py`
- `Libs/NLTA_Brush.py`
- `Libs/NLTA_Proxy.py`
- relevant mesh/general helpers

Target primitives, in order:
1. skinCluster lookup and explicit mesh/component normalization
2. influence query/add/remove
3. max-influence inspection/fix
4. copy/mirror skin
5. unlock/isolate/prune/clear workflows
6. skin import/export
7. graph/gradient/proxy tools

Each primitive gets a selection-based convenience action only after the explicit API is stable.

## Setup — second slice
Source references:
- `UIs/Setup.py`
- control/axis/graph/general/IK and ScenePattern setup helpers

Target areas:
- transforms/controls
- constraints and spaces
- IK/FK
- SDK/driven key
- spline/rope/secondary rig setup
- proxy attributes and rig nodes

## Scene — third slice
Source references:
- `UIs/Scene.py`, `SceneU.py`, `SceneUNew.py`, `Scene_.py`
- `UIs/ScenePattern/*`
- scene JSON data

Target areas:
- typed/validated ScenePattern data model
- pattern registry
- deterministic create/load/edit APIs
- display layers
- migration adapter for useful legacy JSON

## Rules during migration
- Do not bulk-copy a legacy module.
- Do not preserve `NLTA_*` as the new public API.
- No hard-coded local paths.
- No checked-in bytecode.
- UI callbacks remain thin.
- Geometry-heavy code may use Maya API 2.0 when measurably useful.
- Every migrated vertical slice must have deterministic checks plus Maya live validation where required.
