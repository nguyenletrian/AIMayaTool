# AIMayaTool Guide

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

Never treat successful import as proof that a Maya operation works.

## AIBridge workflow
Repository evidence is current truth. Architect may autonomously perform low-risk implementation, migration, tests, commits, and task publication within this goal.

Codex is reviewer-only when requested. Owner is final acceptance tester for Maya-visible behavior.

For each substantial migration slice:
`inventory -> implement -> deterministic verification -> review if useful -> Maya live validation -> accepted checkpoint`.

## Current goal
Establish the new AIMayaTool foundation and then migrate Skinning, Setup, and Scene workflows from MayaScriptNew into the new architecture, optimizing helpers/UI/runtime instead of preserving legacy module boundaries.
