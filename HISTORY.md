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

## Recording rule

Add an entry here when one of these happens:
- a product/architecture boundary changes;
- a migration slice is accepted or retired;
- a reusable AIBrigde/project capability is introduced;
- a stable checkpoint/backup is created;
- a significant owner-visible workflow becomes proven in Maya.

Do not copy every task result here. Keep transient retries and diagnostic details in `bridgeTask.json` and only promote durable conclusions to this history.
