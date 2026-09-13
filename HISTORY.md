# AIMayaTool History

This file records durable product/architecture milestones. It is intentionally concise.

Detailed task execution, transient failures, ACK state, and runtime evidence remain in `bridgeTask.json`. Active goals remain in `bridgeGoals.json`. Git history remains the source of truth for exact code changes.

## 2026-09-12 — Project foundation

- Established AIMayaTool as a separate project repository executed by the AIBrigde platform rather than a fork/copy of the worker runtime.
- Defined rule precedence: AIBrigde system contracts -> AIMayaTool project Guide -> task-specific instructions.
- Added `.aibridge/project.json`, capability/router manifests, project goal/task state, and a reusable project-profile pattern intended for later projects such as AIUnrealTool and AIBlenderTool.
- Established target UX: one Python bootstrap file launches/sets up the package in Maya while implementation remains inside the `aimayatool` package.
- Created initial package structure, registry-driven UI shell, Skinning/Setup/Scene domains, and the first Maya skin adapter primitives.
- Added migration rules: do not bulk-copy MayaScriptNew; migrate vertical slices and redesign helpers/UI/runtime boundaries.

## 2026-09-12 — First deterministic validation

- Added inherited AIBrigde `verification:python` workflow for AIMayaTool project workers.
- Initial verification task exposed a permission-contract error: a `git_pull` precondition requires `permissions.edit=true`.
- Corrected the task and completed deterministic validation successfully at AIMayaTool commit `07c5e66473c61a0756bd93fc4ccee6d036fd8d26`.
- Verified current foundation Python files with `py_compile` and import smoke for `aimayatool` and `aimayatool.registry` under the owner-machine Python 3.14 runtime.

## 2026-09-12 — Multi-project worker integration

- Confirmed AIBrigde is the shared platform/runtime and AIMayaTool workers are project-bound instances using the same runtime.
- Extended AIBrigde Manager compatibility with the nested AIMayaTool project manifest schema.
- Hardened worker launch inheritance so project workers running from `D:/AIMayaTool` can still import the AIBrigde runtime from the platform root.
- Improved worker lifecycle behavior: runtime-lease-aware Stop, duplicate-start protection, and safe Delete Worker registration flow.

## 2026-09-12 — Maya runtime capability bootstrap

- AIMayaTool worker reached `maya:runtime_discovery` and correctly reported `ROUTE_MISSING`, proving project task routing reached the expected integration boundary.
- Added a reusable AIBrigde `maya:runtime_discovery` capability rather than embedding AIMayaTool-specific Maya logic into platform core.
- First focused validation found a schema-invalid unit-test fixture; implementation compile/import checks passed.
- Corrected the fixture and registered the capability in AIBrigde `standard_capabilities()`.
- Deterministic verification then passed at AIBrigde commit `ef72311f95e210860c173f21546437f114a5ffa3`: compile, imports, and two focused Maya runtime capability tests all passed without launching Maya.

## 2026-09-12 — Maya 2024 UI bootstrap proven live

- Added a reusable AIBrigde `maya:ui_smoke` capability for bounded owner-machine Maya UI validation.
- Early live attempts exposed two runtime-boundary issues: Maya batch mode is not suitable for validating a real UI window, and Maya 2024 GUI startup on the owner host did not reliably execute the `-command` probe.
- Reworked the transport to launch Maya GUI without `-batch` or `-command`, use isolated temporary `MAYA_APP_DIR`/`MAYA_SCRIPT_PATH`, inject an isolated `userSetup.py`, defer the probe until Maya startup completes, and persist deterministic success/error evidence to a result file.
- Deterministic verification of the final transport passed at AIBrigde commit `39dbc126c3ffd3240824f24bf285220bad707dff` with compile/import checks and 5 focused tests.
- Live Maya 2024 validation then passed on the owner machine: `bootstrap.install_and_launch` created `AIMayaToolWindow`, the window was verified, the success marker `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow` was recorded, and Maya self-quit with exit code 0 without saving or modifying a user scene.

## 2026-09-12 — First Skinning vertical slice accepted

- Migrated the first Skinning workflow as explicit domain APIs around skinCluster discovery and add/remove influence operations, with thin selection-driven UI wrappers rather than legacy global session/scriptJob behavior.
- Deterministic verification passed for the skin adapter, influence workflow, smoke module, and Skinning UI at AIMayaTool commit `a37f476c39a7960c741cda0df75f09996bea35ee`.
- Live Maya 2024 functional validation created a disposable mesh, joints, and skinCluster, discovered the skinCluster, added and verified a second influence, removed it and verified absence, and returned `AIBRIDGE_UI_SMOKE_OK:SKINNING_INFLUENCE_SMOKE_OK` with exit code 0.
- The first live attempt was blocked by a transient Autodesk license checkout failure before AIMayaTool code executed; retry passed without code changes.
- UI regression validation then passed in Maya 2024: `bootstrap.install_and_launch` still created `AIMayaToolWindow` with the new Skinning controls, and Maya closed cleanly without saving a user scene.

## 2026-09-13 — Skinning mirror and utility slices accepted

- Added explicit mirror-skin APIs matching the proven legacy `closestJoint`/`oneToOne` behavior and validated asymmetric left/right weight transfer in Maya 2024.
- Added Skinning utility APIs for lock/unlock influences, prune, clear-with-redistribution, and affected-vertex discovery with thin selection wrappers and compact UI controls.
- Live Maya 2024 utility validation returned `AIBRIDGE_UI_SMOKE_OK:SKINNING_UTILITIES_SMOKE_OK`; UI regression passed after restarting Maya following a transient Autodesk license checkout failure, with no product code change required.
- The accepted utilities UI retry checkpoint is AIMayaTool commit `5385c1475c6674c31c09aa3910a3cfc579981064`.

## 2026-09-13 — Skinning first slice closed

- Completed the first Skinning migration slice with focused modules for influence management, max-influence handling, copy weights, mirror skin, utility workflows, and XML+manifest skin-data import/export.
- Skin-data round-trip validation passed in Maya 2024 at proven AIMayaTool code commit `05b8c0c502069b208edd3cbcd2b6afd240735829`, including restore into an existing skinCluster and recreation after deleting the skinCluster.
- UI regression emitted `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow`; the subsequent Windows exit `3221227010` occurred after functional acceptance and matches the known Maya shutdown anomaly allowed by the validation contract.
- Created immutable stable checkpoint `backup/2026-09-13-0737-SkinningFirstSlice-05b8c0c` pointing exactly to the proven code commit.

## 2026-09-13 — Setup first slice closed

- Added composable Setup primitives for Circle/Box control creation, explicit world-transform matching, and zero-group insertion while preserving world pose.
- Deterministic verification passed for `controls.py`, Setup smoke, and Setup UI at proven AIMayaTool code commit `5a17a4701de516fc3899907dd2269f201dbde092`.
- Maya 2024 functional validation returned `AIBRIDGE_UI_SMOKE_OK:SETUP_CONTROLS_SMOKE_OK`; the Windows shutdown anomaly occurred only after functional completion.
- The first UI regression attempt timed out without product-failure evidence; a fresh Maya retry then emitted `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow` and exited 0.
- Created immutable stable checkpoint `backup/2026-09-13-0752-SetupFirstSlice-5a17a47` pointing exactly to the proven code commit.

## 2026-09-13 — ScenePattern first slice closed

- Added the versioned `ScenePattern` JSON model and deterministic `PatternRegistry` with duplicate rejection, replacement, lookup, removal, and sorted identifiers.
- Deterministic Python verification passed at proven AIMayaTool code commit `255375819c7dea39672b260b514f8bea669e83de`.
- Introduced the reusable AIBrigde managed-live Maya workflow: reuse a healthy session or launch Maya 2024 automatically, force a fresh scene for each test, never save the test scene, and leave Maya running for later tasks.
- Fixed managed-session lifecycle so `MAYA_APP_DIR` persists outside per-task result cleanup; focused AIBrigde regression verification passed at `59b78bd28ac9daab728658a95762aa405a98cc86`.
- Live ScenePattern validation returned `AIBRIDGE_UI_SMOKE_OK:SCENE_PATTERN_SMOKE_OK`; UI regression then reused the existing Maya session and returned `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow`, with `new_scene_forced=true`, `scene_saved=false`, and `maya_quit=false`.
- Created immutable stable checkpoint `backup/2026-09-13-0830-ScenePatternFirstSlice-2553758` pointing exactly to the proven AIMayaTool code commit.

## 2026-09-13 — ScenePattern operations closed

- Added deterministic ScenePattern create/edit/save/load APIs with overwrite protection and explicit filesystem validation, while keeping Scene package imports usable outside Maya through lazy host imports.
- Python verification passed at proven AIMayaTool commit `e3c792e676217510086213516838d815b6b00953`, including compile/import checks and the focused operations unit suite.
- Reusable managed-live validation exposed a stale module-cache issue when reusing a Maya session; AIBrigde now invalidates import caches and reloads the requested target module before each live probe, verified at AIBrigde commit `221f1601954ba9bfed70d4e29d0496b2c7b74f55`.
- Maya 2024 operations validation then reused the existing session and returned `AIBRIDGE_UI_SMOKE_OK:SCENE_PATTERN_OPERATIONS_SMOKE_OK`; UI regression returned `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow`, with a fresh unsaved scene and Maya left running.
- Created immutable stable checkpoint `backup/2026-09-13-0852-ScenePatternOperations-e3c792e` pointing exactly to the proven AIMayaTool commit.

## 2026-09-13 — Scene display-layer helpers closed

- Added reusable Scene display-layer helpers for deterministic layer creation, membership add/remove/query, visibility, and displayType control, while keeping the Python-only Scene API importable outside Maya.
- Deterministic verification passed at proven AIMayaTool main `d60cde8f0b0aef7afad242a2e6b9795fa29f7f8e`; focused unit tests passed 2/2 and explicitly cover the default full-DAG-name membership contract plus `full_names=False` short-name behavior.
- Initial live Maya smoke exposed a validation expectation mismatch rather than an API failure: Maya correctly returned full DAG paths by default. The smoke was corrected and the deterministic gate was also corrected so Maya-only smoke modules are compiled but not imported by normal Python.
- Managed Maya 2024 retry returned `AIBRIDGE_UI_SMOKE_OK:SCENE_DISPLAY_LAYER_SMOKE_OK`; UI regression returned `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow`, both reusing the existing session with a fresh scene, no save, and no Maya quit.
- Created immutable stable checkpoint `backup/2026-09-13-0900-SceneDisplayLayers-d60cde8` pointing exactly to the proven main commit.

## 2026-09-13 — Scene build actions closed

- Added reusable Scene build actions for deterministic transform-group creation, hierarchy construction, and explicit parenting with world-transform preservation by default.
- Deterministic verification passed at proven AIMayaTool main `eb1502dc41ff77b7ff03c92b4a096ad94bc30dde`: compile/import checks passed and focused unit tests passed 3/3.
- Managed Maya 2024 functional validation returned `AIBRIDGE_UI_SMOKE_OK:SCENE_BUILD_ACTIONS_SMOKE_OK`, proving hierarchy construction plus world-space preservation after parenting in a fresh unsaved scene.
- UI regression returned `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow`; both live checks reused the managed Maya session with no scene save and no Maya quit.
- Created immutable stable checkpoint `backup/2026-09-13-0900-SceneBuildActions-eb1502d` pointing exactly to the proven main commit.

## 2026-09-13 — Scene legacy-adapter assessment closed

- Inspected the MayaScriptNew main tree before adding any compatibility code. `Libs/NLTA_Scene.py` is empty, `Libs/NLTA_Json.py` only prints a string, and targeted searches found no legacy ScenePattern/JSON load-save schema that warrants preservation.
- Accepted the explicit decision to add no legacy Scene JSON adapter until real source data or an owner workflow requires one; the versioned AIMayaTool `ScenePattern` format remains canonical.
- Post-assessment deterministic regression passed at proven AIMayaTool main `fc048d0a73c73b8d54ca1fd777428840511aeef7`: the Scene stack compiled, all five Python-safe imports passed, and focused Scene tests passed 8/8.
- Managed Maya UI regression reused the existing Maya 2024 session and returned `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow` with a fresh unsaved scene, no save, and no Maya quit.
- Created immutable stable checkpoint `backup/2026-09-13-0900-SceneLegacyAssessment-fc048d0` pointing exactly to the proven main commit.

## 2026-09-13 — Explicit influence-weight transfer accepted

- Added a focused Skinning primitive that transfers the selected source influence weight into an explicitly selected target influence on explicit components, plus a thin selection wrapper/UI action.
- Corrected the Skinning package boundary so Python-only imports remain usable outside Maya; deterministic verification then passed compile, non-Maya import, and focused tests 3/3 at proven code state `753786ea6fb2055e5892ee68a11047d45af9f91e`.
- Managed Maya 2024 functional validation reused the existing session and returned `AIBRIDGE_UI_SMOKE_OK:SKINNING_INFLUENCE_TRANSFER_SMOKE_OK`, proving the real skinCluster source-to-target transfer in a fresh unsaved scene.
- Final UI regression reused the managed Maya session and returned `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow`, with no scene save and no Maya quit.

## 2026-09-13 — Advanced ratio and gradient Skinning primitives accepted

- Added explicit influence-ratio redistribution and source-to-target ratio-copy primitives that preserve each target component's combined selected-influence weight while leaving unrelated influences untouched.
- Added a reusable normalized animCurve-backed weight profile and inverse-distance profile mapping extracted from legacy `GradientActiveJoint` behavior.
- Added explicit active-influence distance gradient weighting composed from those deterministic primitives rather than relying on legacy selection, envelope, timeline, or implicit normalization side effects.
- Deterministic gradient-weighting verification passed 4/4 focused tests at proven main `e3fea2a3a1d24547e4ac699e9deee36a1c396aeb`.
- Managed Maya 2024 validation reused the existing session and returned `AIBRIDGE_UI_SMOKE_OK:SKINNING_GRADIENT_WEIGHTS_SMOKE_OK` in a fresh unsaved scene with Maya left running.

## 2026-09-13 — Reusable mesh topology primitives accepted

- Added explicit component-index parsing, edge-to-vertex conversion, closed edge-loop detection, and ring-path with loop-path fallback as the first topology layer required by higher-level skirt workflows.
- Deterministic verification passed compile/import plus 4/4 focused topology tests at proven main `8bc754c832be6164a86603fca43f109bb4204183`.
- Managed Maya 2024 validation reused the existing session and returned `AIBRIDGE_UI_SMOKE_OK:SKINNING_TOPOLOGY_SMOKE_OK` on a fresh unsaved mesh with Maya left running.

## 2026-09-13 — Advanced SkirtParent workflow accepted

- Composed the legacy-inspired SkirtParent behavior into explicit phases: non-mutating planning, parent-to-skirt influence transfer, adjacent-joint smoothing-plan construction, smoothing apply, and an end-to-end workflow executor.
- Live diagnostics identified a Maya API lifetime hazard: retaining an `MFnMesh` created before `skinCluster` history insertion can destabilize later topology/skin queries. The accepted workflow resolves a fresh post-skin `MFnMesh` before planner execution instead of carrying the pre-history function set across mutation.
- Full managed Maya 2024 validation passed with `AIBRIDGE_UI_SMOKE_OK:SKINNING_SKIRT_PARENT_WORKFLOW_SMOKE_OK`, proving planner, four parent transfers, production smoothing-plan construction, smoothing apply, zero-pair-safe ratio propagation, and final transferred-weight checks in a fresh unsaved scene.
- The accepted full-workflow checkpoint is AIMayaTool main `8b8b0d6400ee26440b16558f0dd950100076b07a`; the smoothing zero-pair guard was introduced at `2d6d4307937c5c9cdc4214e141e62679d10016b7` and the live-smoke dependency reload fix at `ddf9ce291134d2614c5af333fbaf03be8d98761a`.

## 2026-09-13 — SkirtParent interactive UI accepted

- Added the thin selection adapter and Skinning UI exposure for the accepted SkirtParent workflow while keeping domain execution outside the UI layer.
- Managed Maya 2024 interactive validation passed for the selection adapter, preserving parent-first joint ordering, skirt-joint inputs, one-mesh root-loop edges, skinCluster discovery, and end-to-end SkirtParent execution.
- Final standard UI regression through `bootstrap.install_and_launch` emitted `AIBRIDGE_UI_SMOKE_OK:AIMayaToolWindow` at main `6952e625d3ec6cf5049d499ea2466dbdad7c0acf`.
- Windows exit `3221227010` occurred only after the success marker and remains the known accepted Maya shutdown anomaly, not a product failure.

## Recording rule

Add an entry here when one of these happens:
- a product/architecture boundary changes;
- a migration slice is accepted or retired;
- a reusable AIBrigde/project capability is introduced;
- a stable checkpoint/backup is created;
- a significant owner-visible workflow becomes proven in Maya.

Do not copy every task result here. Keep transient retries and diagnostic details in `bridgeTask.json` and only promote durable conclusions to this history.
