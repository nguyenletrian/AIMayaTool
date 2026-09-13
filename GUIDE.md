# AIMayaTool Guide

## Platform inheritance
AIMayaTool is a project executed by the AIBrigde platform; it is not a fork or copy of the AIBrigde worker/runtime.

Rule precedence is:
1. AIBrigde `GUIDE.md` system/runtime contracts;
2. this AIMayaTool project Guide;
3. task-specific instructions.

AIMayaTool may add stricter project rules, Maya-specific validation requirements, and bounded project routers/capabilities, but it must not weaken or duplicate AIBrigde queue, ACK, Git, provider, permission, retry, restart, backup, or repository-integrity contracts.

The canonical project binding is declared in `.aibridge/project.json`. Capability expectations and project router ownership are declared in `.aibridge/capabilities.json` and `.aibridge/routers.json`. Project workflow state lives in `bridgeGoals.json` and `AIMayaToolTask.json` in this repository.

### Project-specific TaskSource rule
AIMayaTool owns `AIMayaToolTask.json` as its canonical TaskSource. Do not use the generic filename `bridgeTask.json` for new AIMayaTool queue state.

This project-specific filename is part of the reusable project-profile contract so multiple AIBrigde-backed projects can run in parallel, including from separate ChatGPT accounts or worker instances, without accidentally sharing, polling, ACKing, or overwriting another project's task file. Every project profile should bind an explicit project-unique TaskSource path in `.aibridge/project.json`.

`bridgeTask.json` may remain in Git history or temporarily exist as a migration artifact, but once the project binding points to `AIMayaToolTask.json`, it is no longer authoritative for AIMayaTool execution and must not receive new AIMayaTool tasks or ACK mutations.

### Reusable project-profile rule
Design AIMayaTool's AIBrigde integration as a reusable project-profile pattern for later projects such as AIUnrealTool or AIBlenderTool:
- keep generic orchestration/runtime behavior in AIBrigde;
- keep product/domain behavior in the project repository;
- bind each worker instance to one explicit project id/repository/workdir/Guide/task source;
- give each project a project-unique TaskSource filename rather than sharing a generic task filename;
- reuse existing AIBrigde routes when semantics match;
- add a generic AIBrigde capability only when multiple projects can reasonably reuse it;
- keep project-specific routing metadata local when behavior belongs only to that project/domain;
- never copy the AIBrigde worker implementation into the project repository.

### Durable history contract
`HISTORY.md` records concise, durable product and architecture milestones. It is not a duplicate task log.

Use these sources for different kinds of truth:
- `HISTORY.md`: accepted architecture/product milestones, stable checkpoints, reusable capability introductions, and owner-visible workflows proven in Maya;
- `bridgeGoals.json`: active goal/milestone state;
- `AIMayaToolTask.json`: bounded recent task execution/ACK/runtime evidence;
- Git history: exact code changes, older TaskSource history, and commit identity.

Update `HISTORY.md` when a durable conclusion is reached, not for every transient task result. When a migration slice is accepted, record the relevant proven commit/checkpoint and the validation tier that passed.

Future project profiles should use the same separation so history stays readable while task evidence remains machine-oriented.

## Mission
Build a clean Maya toolset from the proven ideas in `nguyenletrian/MayaScriptNew`, while redesigning helpers, UI, structure, loading, and runtime boundaries for maintainability and speed.

The user experience target is one Python file that can be dragged/dropped or executed in Maya to install/open AIMayaTool. That bootstrap file must not contain the tool implementation itself; it only locates/installs the package and hands off to the package entry point.

## Source repository
- Reference/source: `https://github.com/nguyenletrian/MayaScriptNew`
- Target/product: `https://github.com/nguyenletrian/AIMayaTool`

MayaScriptNew is reference evidence, not a structure to copy wholesale. Preserve useful algorithms and workflow behavior, but remove hard-coded local paths, legacy reload patterns, giant monolithic modules, duplicate helpers, checked-in bytecode, and UI/business-logic coupling.

## Product scope
Initial domains:
- Skinning
- Setup / rigging helpers
- Scene / scene-pattern workflows

Future domains may be added through the same registry/package contracts.

## Architecture

### Bootstrap boundary
`bootstrap.py` is the only file users need to drag into Maya or execute manually.

Responsibilities:
1. resolve a writable AIMayaTool install root;
2. make the package importable without hard-coded developer paths;
3. call `aimayatool.launch()`;
4. fail with a concise Maya-visible error when setup is incomplete.

Bootstrap must stay small, dependency-light, idempotent, and safe to rerun.

### Package layout
```text
bootstrap.py
aimayatool/
    __init__.py
    app.py
    registry.py
    core/
        paths.py
        logging.py
        result.py
    maya/
        host.py
        selection.py
        scene.py
    ui/
        main_window.py
        sections.py
    tools/
        skinning/
        setup/
        scene/
```

### Layer rules
- `core`: Python-only helpers where practical. No UI imports. No project-specific scene assumptions.
- `maya`: Maya API/cmds adapters and host integration.
- `tools`: domain logic. A tool should expose a small callable API and metadata; avoid creating UI inside core algorithms.
- `ui`: presentation/composition only. It calls tool APIs through the registry.
- `registry`: the single discoverable catalog of tool groups/actions.
- `bootstrap`: installation/loading only.

Do not re-create the old pattern where UI files import a long list of global `NLTA_*` modules and reload all of them on every launch.

## UI principles
- One main AIMayaTool window/workspace.
- Sections: Skinning, Setup, Scene.
- Tools are grouped by workflow, not by historical source module.
- Compact controls; repeated actions use reusable UI builders.
- UI callbacks must be thin wrappers around domain functions.
- Long operations should report progress/status and surface actionable errors.
- Avoid duplicate control IDs/global mutable UI dictionaries unless state genuinely must be shared.

## Helper redesign
Before migrating an old helper:
1. search for duplicate/near-duplicate behavior in MayaScriptNew;
2. identify the narrow reusable primitive;
3. choose the correct layer (`core`, `maya`, or domain tool);
4. preserve Maya behavior with focused tests or smoke scripts;
5. only then migrate callers.

Prefer explicit inputs/returns over functions that implicitly depend on current selection. Selection-driven convenience wrappers may exist, but should call deterministic primitives underneath.

Prefer Maya API 2.0 for geometry-heavy operations where it materially improves speed; use `maya.cmds` where readability and host integration are more important.

## Migration strategy
Do not bulk-copy the legacy repository.

Work in vertical slices:
1. inventory source behavior;
2. migrate one coherent workflow;
3. add registry entry/UI exposure;
4. validate in Python where possible and in Maya where required;
5. remove duplication before starting the next slice.

Priority order:
1. foundation/bootstrap/registry/UI shell;
2. Skinning essentials;
3. Setup essentials;
4. Scene + ScenePattern framework;
5. advanced/rare helpers.

## Skinning migration priorities
First-wave candidates from MayaScriptNew:
- skinCluster discovery and influence helpers;
- add/remove influence;
- max-influence validation/fix;
- copy skin / copy weights;
- mirror skin;
- prune/clear/unlock/isolate workflows;
- export/import skin data;
- graph/gradient/proxy helpers after primitives are stable.

Algorithms should accept explicit mesh/skinCluster/joints/components when possible, with separate selection wrappers for interactive use.

## Setup migration priorities
- transform/control helpers;
- constraints and spaces;
- IK/FK primitives;
- driven-key/SDK helpers;
- spline/rope/secondary setup primitives;
- proxy attributes and common rig utility nodes.

Each setup feature should be composable and avoid embedding character-specific naming unless exposed as configuration.

## Scene migration priorities
- ScenePattern data model and serialization;
- pattern registry;
- deterministic create/load/edit operations;
- display-layer helpers;
- reusable scene setup/build actions;
- migration adapters for useful legacy JSON only when required.

Avoid rebuilding a single giant Scene module.

## Naming and compatibility
- New package code uses `aimayatool` naming.
- Legacy `NLTA_*` names are not the new public API.
- Temporary adapters may wrap legacy functions during migration, but every adapter must be marked and removable.
- Keep compatibility with Maya versions that support the Python syntax/API used by the target production environment. Avoid unnecessary third-party dependencies.

## Repository hygiene
- Never commit `.pyc`, `__pycache__`, Maya temp files, local config, credentials, or user-specific absolute paths.
- No access tokens in source.
- No hard-coded `D:/code/Github` or equivalent developer path.
- Keep modules focused; split large files before they become monoliths.

## Verification gate
For changed Python:
- compile every changed module;
- import-smoke Python-only modules outside Maya when possible;
- isolate Maya-host imports so non-Maya tests can still cover pure helpers;
- run focused unit tests for deterministic helpers;
- run Maya smoke validation for host-specific behavior before declaring migrated workflows accepted.

Validation should use the cheapest sufficient tier in this order:
1. normal Python deterministic verification;
2. `mayapy`/headless Maya-Python when host APIs are required but UI is not;
3. Maya batch for bounded scene/runtime behavior;
4. interactive Maya only for UI, drag/drop, selection, viewport, or behavior that genuinely requires the live application.

Never treat successful import as proof that a Maya operation works.

### Maya client crash / popup / relaunch recovery
When a Maya live-validation task fails because of the Maya client/runtime rather than conclusive AIMayaTool product behavior, recovery should be persistent rather than immediately escalating a transient failure.

Treat the following as Maya-runtime loss signals when no product exception/failure marker was returned: a blocking startup popup/dialog, transient license/startup state, an unresponsive launch, launch timeout, live-socket `ConnectionRefusedError` / WinError 10061 after a previously healthy session, `MAYA_LIVE_SESSION_LOST`, disappearance of the Maya process/window, abrupt process exit, or an OS/application crash report.

If runtime evidence establishes that Maya 2024 is installed/available on the owner machine:
1. preserve the exact failed task/runtime evidence and classify the first runtime-loss event as inconclusive rather than a product failure unless a product-level exception already proves otherwise;
2. dismiss/close blocking Maya popups or dialogs when the route can safely do so;
3. treat a missing/refused live listener after a previously healthy session as a stale or crashed Maya instance, not as a reusable session;
4. close any stale/half-alive Maya process when necessary, then launch Maya again in a fresh managed session;
5. re-establish the live listener and force a fresh unsaved scene before invoking AIMayaTool product code again;
6. retry the same bounded validation so the comparison is meaningful;
7. if the same bounded product operation crashes Maya again on a genuinely fresh session, preserve both runs and classify the repeated crash as a reproducible product-level Maya crash blocker for investigation; do not keep relaunching indefinitely once reproducibility is established;
8. if the fresh retry succeeds, retain the earlier crash/session-loss evidence as transient runtime evidence and continue the workflow;
9. never fabricate a success marker, hide a crash, or convert a transport/runtime failure into an AIMayaTool PASS.

Once Maya availability has already been proven, prefer this crash/popup-dismiss/relaunch/retry recovery automatically for later AIMayaTool Maya tasks. A crashed process or refused listener must trigger fresh-session recovery before any subsequent live validation.

## AIBridge workflow
Repository evidence is current truth. Architect may autonomously perform low-risk implementation, migration, tests, commits, and task publication within this goal.

### Mandatory TaskSource serialization contract
All Architect writes to `AIMayaToolTask.json` are machine-structured operations. Hand-written, manually concatenated, partially copied, or text-patched JSON is forbidden.

**This serialization contract is a write-safety procedure, never a reason to withhold valid work.** If a safe dependency-ready task can be identified, Architect must perform the required parse/mutate/validate/serialize/reparse/write/refetch sequence and publish it in the same turn. The fact that a serializer or structured mutation step is required does not justify leaving the queue empty, replying with only a plan, or deferring publication. If the currently available tool surface cannot execute one required serialization step directly, Architect must use an available structured/runtime method to complete that step when possible; only a genuine unavailable capability or failed validation may block the write, and that blocker must be concrete rather than assumed.

For every TaskSource publish, ACK, recovery, retention, or metadata mutation, Architect must follow this exact safety pattern:
1. fetch the current authoritative `AIMayaToolTask.json` and its current blob SHA from `main`;
2. parse the full document with a JSON parser before any mutation;
3. mutate only the parsed object/list structure in memory;
4. validate required root/task fields, task-id uniqueness, and dependency references;
5. serialize with a JSON serializer using human-readable pretty-printed/indented JSON; compact one-line TaskSource serialization is forbidden;
6. parse the serialized result again before any remote write;
7. if any parse/schema/dependency validation fails, do not write the TaskSource;
8. write only against the fetched current blob SHA;
9. re-fetch the written file and parse it again before considering the mutation complete;
10. preserve recent task evidence according to the bounded retention rule below and rely on Git history/HISTORY.md for older durable evidence.

#### Queue-exhaustion continuity rule
A truthful `queue_exhausted` request is an instruction to actively look for the next safe work inside the already approved goal, not a stop condition.

When Bridge requests additional work because the queue is exhausted, Architect must in the same turn:
1. re-read the current Guide, goal state, and authoritative `AIMayaToolTask.json`;
2. inspect enough repository/reference evidence to identify the next bounded migration, verification, assessment, or recovery slice;
3. if architecture, permissions, dependencies, and acceptance criteria are clear, publish one or more pending tasks immediately using the mandatory serialization contract;
4. prefer a dependency chain of multiple tasks when implementation -> deterministic verification -> Maya validation -> UI regression is already predictable and each step has clear acceptance criteria;
5. do not create speculative implementation tasks when product intent is genuinely ambiguous, but do publish a bounded assessment/inventory task when that assessment itself is safe and useful;
6. only leave the queue empty when no safe task or bounded assessment can be identified from available evidence, or when a concrete tool/runtime/validation blocker prevents a valid TaskSource write.

Serialization safety and automation continuity are complementary requirements: **serialize correctly and continue**, rather than choosing one at the expense of the other.

#### Bounded TaskSource retention
`AIMayaToolTask.json` must contain at most the 10 newest task records, preserving their chronological order. Apply this retention rule whenever Architect publishes, ACKs, recovers, or otherwise rewrites TaskSource.

Before removing an older task:
- ensure it is already `architect_ack: true` and `bridge_completed: true`; never evict active, unACKed, or incomplete work merely to satisfy the limit;
- check whether any retained task has `depends_on` or `retry_of` pointing to the task being removed;
- if a retained completed task still references an evicted prerequisite/retry source, replace that live dependency reference with compact `archived_prerequisite` or equivalent archival metadata containing enough task id/result/ACK/completion evidence to prove the dependency had already resolved;
- never create a dangling dependency by trimming;
- older detailed TaskSource state remains recoverable from Git history; accepted product/milestone conclusions belong in `HISTORY.md`.

If more than 10 records are temporarily required because active/unACKed/dependency-critical tasks cannot safely be evicted, correctness wins over the numeric limit; retain the necessary records until they become safely archivable, then trim back to 10 on the next valid mutation.

A missing brace, quote, comma, malformed object boundary, duplicate key/id, unresolved dependency, or any other invalid TaskSource structure is a release-blocking defect. Architect must repair it immediately and must not publish new work on top of malformed TaskSource state.

### Automation continuity / anti-sabotage contract
Architect must never intentionally create an error, malformed TaskSource, invalid dependency state, false failure, artificial queue exhaustion, blocking condition, stale-state trap, or other fault in order to pause, stop, slow, bypass, or manipulate the automation loop.

Architect must never use failure as a control-flow mechanism when a valid state transition, dependency, ACK, queue update, retry, or explicit stop condition exists. Deliberately making `AIMayaToolTask.json` invalid so Bridge stops or asks for help is strictly forbidden.

Within an owner-approved goal, the default objective is continuous safe forward progress. If Architect introduces a defect accidentally, Architect must treat recovery as urgent: `detect -> stop further mutation -> restore last proven-valid state -> validate parser/schema/dependencies -> resume automation -> report`. Architect must not leave a known self-created defect in place to force owner intervention.

Architect must prefer no-op/waiting behavior over destructive or invalid behavior when there is temporarily no safe dependency-ready task. Queue exhaustion must remain a truthful runtime state, never a state manufactured by corrupting or withholding valid workflow data.

### Critical no-confirmation execution contract
For work already inside an owner-approved AIMayaTool/AIBrigde goal, Architect must not stop to ask for routine confirmation before performing safe, reversible, dependency-ready work that Architect can complete with available repository/runtime tools.

This rule is intentionally strict and high-priority. When current evidence identifies a concrete non-destructive fix or recovery action, Architect should execute it in the same turn instead of replying with a plan and waiting for the owner. This includes, when permitted by the inherited AIBrigde Guide: repairing malformed TaskSource JSON while preserving history, correcting task metadata/state, publishing follow-up tasks, bounded diagnostics, deterministic verification, low-risk code fixes, ACK processing, queue recovery, and approved restart/runtime-freshness barriers.

Architect must continue autonomously through all safe steps that are already implied by the active goal and current evidence. Owner confirmation is required only when the action materially changes product intent, expands privileges/security exposure, is destructive or irreversible, incurs meaningful external cost, or genuinely needs owner-only information or judgment. Uncertainty that can be resolved from repository/runtime evidence is not a reason to ask the owner.

If Bridge reports an error and the repair is safe and within scope, the default sequence is `inspect evidence -> repair now -> validate -> update workflow state -> let Bridge resume -> report outcome`; never `report error -> wait for owner confirmation` unless one of the explicit escalation conditions above applies.

Codex is reviewer-only when requested. Owner is final acceptance tester for Maya-visible behavior.

Bridge executes owner-machine work through the inherited AIBrigde runtime. AIMayaTool tasks must target this repository/workdir and may request Maya-specific capabilities, but lifecycle processing remains governed by AIBrigde.

For each substantial migration slice:
`inventory -> implement -> deterministic verification -> review if useful -> Maya live validation -> accepted checkpoint`.

## Current goal
Establish the new AIMayaTool foundation and then migrate Skinning, Setup, and Scene workflows from MayaScriptNew into the new architecture, optimizing helpers/UI/runtime instead of preserving legacy module boundaries.
