# COMSOL Java API Index

This file solves: choose the smallest reference file needed for a COMSOL Java API task and understand how this skill maps the COMSOL Java API manual into optics_agent workflows.

## Source Scope

- Manual summarized: `docs/COMSOL/COMSOLJavaAPIReferenceGuide.pdf`, COMSOL Java API Reference Guide, version 4.3, 732 pages.
- Runtime target: optics_agent currently runs COMSOL 6.3 headless batch.
- Rule: use this skill for API shape and common patterns; use COMSOL 6.3 GUI-exported Java for version-sensitive physics feature names and settings.

## Manual Chapter Mapping

| Manual chapter | Main content | Skill files |
|---|---|---|
| Chapter 1 Introduction | model Java-file structure, compile/run modes, batch command, GUI-generated Java | `07-batch-java-files.md`, `08-gui-exported-java.md`, `BatchSafeModel.java` |
| Chapter 2 General Commands | `ModelUtil`, model object, params, variables, functions, selections, materials, physics, coupling operators, study/sol entry points | `01-model-core.md`, `02-general-commands.md` |
| Chapter 3 Geometry | geometry sequences, primitives, booleans, work planes, measurements, object/entity lookup | `03-geometry.md`, `GeometrySequence.java` |
| Chapter 4 Mesh | mesh sequences, `FreeTri`, `FreeTet`, `Size`, physics-controlled mesh, statistics, errors | `04-mesh.md`, `MeshFreeTri.java` |
| Chapter 5 Solver | solution object, solver features, eigenvalue/stationary/time/parametric, matrices, solution vectors | `05-solver-study.md`, `StudySolverEigenvalue.java` |
| Chapter 6 Results | datasets, numerical features, solution selection, tables, data/plot export | `06-results-export.md`, `ResultsEvalExport.java` |
| Chapter 7 GUI | Java model generated for GUI apps, Swing/SWT GUI details | `08-gui-exported-java.md`; GUI widget details are usually irrelevant for headless batch |

## Task Routing

| Task | Read |
|---|---|
| Understand a GUI-exported Java model | `08-gui-exported-java.md`, then layer-specific files |
| Add or fix model parameters, variables, selections, materials, physics | `01-model-core.md`, `02-general-commands.md` |
| Build or debug geometry | `03-geometry.md`, `GeometrySequence.java` |
| Replace failed physics-controlled mesh with explicit mesh | `04-mesh.md`, `MeshFreeTri.java` |
| Add study, solver, eigenvalue shift, or read eigenvalues | `05-solver-study.md`, `StudySolverEigenvalue.java` |
| Extract `neff`, global values, tables, or plot data | `06-results-export.md`, `ResultsEvalExport.java` |
| Make a model run under `comsol batch` | `07-batch-java-files.md`, `BatchSafeModel.java`, then `optics-comsol-batch` |
| Diagnose batch or solver failure | `10-common-errors.md` |
| Build optics waveguide/eigenmode models | `09-api-patterns-for-optics.md`, plus GUI-exported Java or Wave Optics/RF docs |

## Object Quick Lookup

| Object/API | Purpose | Typical call |
|---|---|---|
| `ModelUtil` | Create/load models, standalone/server setup, progress | `Model model = ModelUtil.create("Model");` |
| `Model` | Root model object | `model.param()`, `model.geom()`, `model.study()` |
| `modelNode` / `component` | Model/component container. COMSOL 4.3 manual uses `model.modelNode()`. COMSOL 6.x GUI Java may use `model.component("comp1")`. | `model.modelNode().create("comp1");` |
| `geom` | Geometry sequence | `model.geom().create("geom1", 2);` |
| `mesh` | Mesh sequence | `model.mesh().create("mesh1", "geom1");` |
| `material` | Material definitions and property groups | `model.material().create("mat1");` |
| `physics` | Physics interface and features | `model.physics().create("emw", "...", "geom1");` |
| `study` | Study sequence and steps | `model.study().create("std1");` |
| `sol` | Solver sequence and solution data | `model.sol("sol1").createAutoSequence("std1");` |
| `result` | Datasets, numerical results, plot groups, tables, exports | `model.result().numerical().create("gev1", "EvalGlobal");` |
| `selection` | Explicit or geometric entity selections | `model.selection("sel1").entities(2);` |
| `cpl` | Coupling operators | `model.cpl().create("int1", "Integration", "geom1");` |

## GUI-Exported Java vs Hand-Written Java

| Aspect | GUI-exported Java | Hand-written Java |
|---|---|---|
| Strength | Captures exact feature tags and settings that COMSOL accepted | Short, reviewable, easy to parameterize |
| Risk | Verbose and may include stale/unrun sequences | Easy to omit hidden physics, selection, solver, or result settings |
| Use in optics_agent | Treat as source of truth for physics/mode-analysis details | Use for minimal probes and reusable templates |
| Headless batch | Remove GUI-only logic and ensure solver/result commands are present | Use `public static Model run()` and batch-safe restrictions |

## Version Notes

- COMSOL 4.3 examples often use global `model.geom()`, `model.mesh()`, `model.physics()` style. Some COMSOL 6.x GUI exports use component-scoped calls. Preserve the style of the file being edited.
- `model.study("std1").create(...)` appears in current optics_agent probes; the 4.3 manual documents `model.study("std1").feature().create(...)`. If a method fails in 6.3, fall back to the GUI-exported Java style for that runtime.
