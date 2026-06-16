---
name: optics-paper-reproduction
description: Plan, execute, audit, and report optics paper figure reproductions in optics_agent. Use when the user asks to reproduce a paper figure, read a paper for numerical parameters, design a COMSOL/Magnus reproduction workflow, define optics-group standard answers, record failed simulation iterations, judge physical-vs-pipeline success, or create handoff reports for paper-to-agent self-iteration.
---

# Optics Paper Reproduction

## Purpose

Use paper reproduction as an auditable workflow test for optics_agent, not as a one-off plot recreation. A good run must leave durable artifacts that explain what was read, what was assumed, what was simulated, what failed, what was fixed, and whether the final result is a physical reproduction or only a pipeline fallback.

When the task involves COMSOL or Magnus execution, also load the relevant runtime skills:

- `optics-comsol-runtime` for active image, license, mounts, and runtime paths.
- `optics-comsol-batch` for Java/M-file/.mph batch patterns and runner contracts.
- `optics-magnus-platform` for job dedupe, resource checks, logs, and file flow.

## Workflow

1. Scope the target figure.
   - Record paper path, figure number, target observable, and what is explicitly out of scope.
   - Prefer one target figure over an entire paper.
   - Read abstract, introduction context, numerical modeling section, target figure/caption, and nearby explanatory text.

2. Extract parameters into tables.
   - Geometry: coordinate system, layer stack, dimensions, gaps, sweep variables, reference planes.
   - Materials: wavelength, complex index/permittivity, dispersion source, loss terms.
   - Physics: dimensionality, propagation direction, eigenvalue/observable definitions, source type, boundary conditions.
   - Solver: study type, mode count, search shift, time/frequency points, tolerances.
   - Postprocessing: exported fields, branch classification, validation metrics, expected numeric ranges.

3. List missing information before coding.
   - Boundary/PML/truncation details.
   - Mesh near metal, gaps, thin layers, and high-index contrast.
   - Exact COMSOL interface or weak-form equations.
   - Sweep step and dense regions.
   - Mode sorting or field-profile classification rule.
   - Fabrication-shape approximations such as rectangular vs irregular cross sections.

4. Build the smallest executable model first.
   - Start with smoke cases over 1-2 parameter values.
   - Keep the first model simple but explicitly label every simplification.
   - For hard eigenmode problems, validate isolated components before the coupled system.

5. Submit jobs conservatively.
   - Before every Magnus submit, query existing jobs by `run_id`; reuse active/success jobs.
   - Query cluster resources; keep CPU and memory below half of the total; do not use GPU unless explicitly required.
   - Use short polling for fast smoke jobs and longer polling for real sweeps.

6. Diagnose failures one cause at a time.
   - Preserve logs and job IDs.
   - Patch one issue per retry where possible.
   - Keep failed jobs in the record; do not overwrite the explanation with the final success.

7. Validate physical meaning separately from job status.
   - `Magnus Success` means the platform contract completed.
   - `COMSOL solve success` means the intended solver ran and produced expected data.
   - `physical reproduction success` means the result matches expected ranges/trends with defensible modeling assumptions.
   - A `surrogate_fallback` can validate file flow and plotting, but it is not a paper reproduction.

## Required Artifacts

For each reproduction run, create a stable folder such as:

```text
reproduction_test/private/<paper_or_case>/
  paper_notes.md
  parameter_table.md
  assumptions_and_missing_info.md
  comsol/
    model.java
    run_config_smoke.json
    run_config_sweep.json
    postprocess_<case>.py
  magnus/
    submit_<case>.py
    submit_log.md
    job_ids.md
    failure_retry_record.md
    raw_logs/
  results/
    <observable>.csv
    <target_figure>.png
    mode_profiles/
  final_report.md
  workflow_handoff_A.md
```

Do not write tokens, license contents, SSH keys, or private credentials into these artifacts. Literal runtime paths such as `/opt/comsol-license/license.dat` are acceptable; secret contents are not.

## Standard Answer Format For Optics Group

Ask collaborators to provide paper-reproduction answers in this shape:

```text
figure_id:
physical_goal:
geometry:
  coordinate_system:
  layer_stack:
  object_coordinates:
  uncertain_dimensions:
materials:
  wavelength:
  complex_indices_or_permittivities:
physics:
  interface_or_equation:
  dependent_fields:
  propagation_direction:
  eigenvalue_or_observable:
boundaries:
  exterior_domain_size:
  PML_or_scattering_boundary:
  substrate_truncation:
mesh:
  metal_max_element:
  gap_max_element:
  bulk_max_element:
solver:
  study_type:
  mode_count_or_time_steps:
  search_shift_or_frequency:
  tolerances:
sweep:
  parameter:
  points:
validation:
  expected_numeric_range:
  expected_trend:
  target_plot:
failure_notes:
  common_solver_errors:
  acceptable_simplifications:
```

This format should be detailed enough for an agent to generate a COMSOL input, submit it, detect wrong results, and iterate. A theory-only explanation is not enough.

## COMSOL Batch Lessons

When generating COMSOL Java for the current Magnus runtime, prefer sandbox-safe Java:

- Provide `public static Model run()` and return a `Model`.
- Avoid `System.getenv`, `System.getProperty`, direct Java file IO inside `run()`, inner classes, and anonymous classes.
- Use simple static helper methods and primitive/string arrays.
- Emit case-specific tabular data through stdout markers when COMSOL sandbox blocks file writing.
- Let runner-side Python reconstruct CSV/JSON from stdout if needed.
- Treat generated `.mph` as necessary but insufficient; inspect stdout markers, metrics, and result tables.

Degiron 2009 Fig. 3 exposed these specific failure classes:

- `OUTPUT_MPH_MISSING` when Java did not return/save a COMSOL-compatible model.
- COMSOL Java security blocked environment reads, system-property reads, and filesystem reads.
- Inner helper classes caused COMSOL-side class execution errors.
- Physics-controlled mesh failed; explicit `FreeTri` mesh avoided the mesh setup blocker.
- Full-vector mode analysis reached the eigensolver but failed matrix factorization across several shifts; this requires isolated-mode validation or a GUI-exported Java template.

## Report Requirements

`final_report.md` must state:

- what the target figure computes;
- extracted parameters and their source/assumption status;
- actual numerical model, boundary conditions, mesh, solver, and sweep;
- job IDs, statuses, and resource policy;
- output CSV/figure paths;
- whether the result is physical reproduction, partial reproduction, or fallback only;
- differences from the paper and ranked next fixes.

`workflow_handoff_A.md` must generalize the run into framework lessons:

- what optics collaborators must provide;
- what a standard answer must contain;
- what agent modules are needed: paper parser, parameter extractor, missing-info detector, COMSOL generator, mesh/boundary proposer, Magnus submitter, log parser, validator, self-iteration loop, final-report generator.

