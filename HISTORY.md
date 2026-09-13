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

## Recording rule

Add an entry here when one of these happens:
- a product/architecture boundary changes;
- a migration slice is accepted or retired;
- a reusable AIBrigde/project capability is introduced;
- a stable checkpoint/backup is created;
- a significant owner-visible workflow becomes proven in Maya.

Do not copy every task result here. Keep transient retries and diagnostic details in `bridgeTask.json` and only promote durable conclusions to this history.
