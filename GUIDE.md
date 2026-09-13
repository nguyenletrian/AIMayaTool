# AIMayaTool Guide

## Platform inheritance
AIMayaTool is a project executed by the AIBrigde platform; it is not a fork or copy of the AIBrigde worker/runtime.

Rule precedence is:
1. AIBrigde `GUIDE.md` system/runtime contracts;
2. this AIMayaTool project Guide;
3. task-specific instructions.

AIMayaTool may add stricter project rules, Maya-specific validation requirements, and bounded project routers/capabilities, but it must not weaken or duplicate AIBrigde queue, ACK, Git, provider, permission, retry, restart, backup, or repository-integrity contracts.

The canonical project binding is declared in `.aibridge/project.json`. Capability expectations and project router ownership are declared in `.aibridge/capabilities.json` and `.aibridge/routers.json`. Project workflow state lives in `bridgeGoals.json` and `bridgeTask.json` in this repository.

### Reusable project-profile rule
Design AIMayaTool's AIBrigde integration as a reusable project-profile pattern for later projects such as AIUnrealTool or AIBlenderTool:
- keep generic orchestration/runtime behavior in AIBrigde;
- keep product/domain behavior in the project repository;
- bind each worker instance to one explicit project id/repository/workdir/Guide/task source;
- reuse existing AIBrigde routes when semantics match;
- add a generic AIBrigde capability only when multiple projects can reasonably reuse it;
- keep project-specific routing metadata local when behavior belongs only to that project/domain;
- never copy the AIBrigde worker implementation into the project repository.

### Durable history contract
`HISTORY.md` records concise, durable product and architecture milestones. It is not a duplicate task log.

Use these sources for different kinds of truth:
- `HISTORY.md`: accepted architecture/product milestones, stable checkpoints, reusable capability introductions, and owner-visible workflows proven in Maya;
- `bridgeGoals.json`: active goal/milestone state;
- `bridgeTask.json`: detailed task execution, retries, failures, ACK state, and runtime evidence;
- Git history: exact code changes and commit identity.

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

## AIBridge workflow
Repository evidence is current truth. Architect may autonomously perform low-risk implementation, migration, tests, commits, and task publication within this goal.

### Mandatory TaskSource serialization contract
All Architect writes to `bridgeTask.json` are machine-structured operations. Hand-written, manually concatenated, partially copied, or text-patched JSON is forbidden.

For every TaskSource publish, ACK, recovery, or metadata mutation, Architect must follow this exact safety pattern:
1. fetch the current authoritative `bridgeTask.json` and its current blob SHA from `main`;
2. parse the full document with a JSON parser before any mutation;
3. mutate only the parsed object/list structure in memory;
4. validate required root/task fields, task-id uniqueness, and dependency references;
5. serialize with a JSON serializer, never by constructing JSON punctuation manually;
6. parse the serialized result again before any remote write;
7. if any parse/schema/dependency validation fails, do not write the TaskSource;
8. write only against the fetched current blob SHA;
9. re-fetch the written file and parse it again before considering the mutation complete;
10. preserve all existing task history unless an explicit recovery operation is required and the preserved history is proven from a valid Git blob.

A missing brace, quote, comma, malformed object boundary, duplicate key/id, unresolved dependency, or any other invalid TaskSource structure is a release-blocking defect. Architect must repair it immediately and must not publish new work on top of malformed TaskSource state.

### Automation continuity / anti-sabotage contract
Architect must never intentionally create an error, malformed TaskSource, invalid dependency state, false failure, artificial queue exhaustion, blocking condition, stale-state trap, or other fault in order to pause, stop, slow, bypass, or manipulate the automation loop.

Architect must never use failure as a control-flow mechanism when a valid state transition, dependency, ACK, queue update, retry, or explicit stop condition exists. Deliberately making `bridgeTask.json` invalid so Bridge stops or asks for help is strictly forbidden.

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
