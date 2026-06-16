---
name: comsol-java-api
description: Use when Codex needs to read, write, debug, or summarize COMSOL Java API model files, GUI-exported Java models, geometry/mesh/study/solver/results API calls, COMSOL batch Java files, or convert COMSOL Java API/manual knowledge into executable model templates for optics_agent headless COMSOL workflows.
---

# COMSOL Java API

Use this skill for COMSOL Java syntax and model-file structure: GUI-exported Java, hand-written model Java files, geometry/mesh/study/solver/result API calls, and batch-safe Java templates.

## Boundaries

- COMSOL runtime image, license, mounts, and Magnus paths: use `optics-comsol-runtime`.
- COMSOL batch runner contract, run modes, and output manifest: use `optics-comsol-batch`.
- Magnus job launch/status/logs, FileSecret, MAGNUS_RESULT/ACTION, and platform file flow: use `optics-magnus-platform`.
- Paper-figure reproduction planning and reports: use `optics-paper-reproduction`.
- Java API object syntax, feature tags, settings, and templates: use this skill.

## Quick Workflow

1. Prefer a GUI-exported Java model as the source of truth for physics feature tags, boundary conditions, study steps, and solver sequences.
2. Identify which layer is being edited: model core, geometry, mesh, study/solver, results/export, or batch wrapper.
3. Read only the relevant reference file below, starting with `references/00-index.md`.
4. Preserve tags, feature type strings, selections, units, and solver sequence order when patching Java.
5. For optics_agent batch runs, keep `public static Model run()` returning the model, then let `main(String[] args)` save `args[0]` if provided.
6. Run a batch smoke test through the existing COMSOL batch tooling after editing an executable model.

## API Principles

- Treat the bundled COMSOL Java API manual as API-reference material, not as proof that a physics model is correct.
- The Java API Reference can verify API syntax and object patterns; it cannot by itself prove a Wave Optics/RF mode-analysis physics model is well posed.
- The manual used for this skill is COMSOL 4.3; the active optics_agent runtime is COMSOL 6.3. Validate version-sensitive feature names, setting keys, and solver-sequence structure against COMSOL 6.3 GUI-exported Java.
- Hand-written Java should keep stable tags for geometry, selections, physics, study, solver, datasets, numerical results, and tables.
- Avoid `System.getenv`, `System.getProperty`, direct Java file IO inside `run()`, inner classes, and anonymous classes in Magnus/COMSOL batch Java unless that exact pattern has been validated.
- Mark uncertain physics-specific setting keys as requiring GUI-exported Java validation instead of guessing.
- For Wave Optics/RF mode analysis, stop blind retries after an isolated dielectric waveguide smoke reaches the eigensolver but fails matrix factorization across multiple shift scales. At that point, request a COMSOL 6.3 GUI-exported `.java` or `.mph` template instead of continuing to invent physics/study/solver keys.
- Degiron 2009 Fig. 3 v2 confirmed this boundary: explicit mesh fixed a mesh blocker, but isolated SU-8 mode analysis still failed matrix factorization and produced zero physical `neff` rows.

## References

- `references/00-index.md`: routing, manual chapter mapping, object quick lookup.
- `references/01-model-core.md`: `ModelUtil`, model object, parameters, model nodes/components.
- `references/02-general-commands.md`: variables, functions, materials, physics, selections, coupling operators.
- `references/03-geometry.md`: geometry sequences, primitives, booleans, work planes, measurements.
- `references/04-mesh.md`: mesh sequences, `FreeTri`, `FreeTet`, `Size`, boundary layers, mesh diagnostics.
- `references/05-solver-study.md`: study and solver sequences, `createAutoSequence`, eigenvalue settings, solution data.
- `references/06-results-export.md`: datasets, numerical evaluations, solution selection, tables, exports.
- `references/07-batch-java-files.md`: COMSOL Java-file structure, compile/run modes, headless-safe wrapper.
- `references/08-gui-exported-java.md`: how to read and reuse GUI-exported Java.
- `references/09-api-patterns-for-optics.md`: optics_agent waveguide/eigenmode patterns and gaps.
- `references/10-common-errors.md`: compile, batch, mesh, solver, result, and runner failure diagnosis.

## Templates

Copy from `assets/templates/` when starting a new model:

- `BasicModel.java`: model creation, params, simple geometry, mesh, save.
- `GeometrySequence.java`: primitives, boolean difference, stable geometry tags.
- `MeshFreeTri.java`: explicit user-controlled triangular mesh with size feature.
- `StudySolverEigenvalue.java`: generic PDE eigenvalue study and `getPVals()`.
- `ResultsEvalExport.java`: numerical evaluation and table pattern without Java file IO in `run()`.
- `BatchSafeModel.java`: minimal batch-safe `run()` plus `main()` that only saves `args[0]` when provided.
