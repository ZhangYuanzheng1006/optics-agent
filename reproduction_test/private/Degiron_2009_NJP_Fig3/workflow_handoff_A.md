# Workflow Handoff A: Paper Reproduction And Self-Iteration

This handoff records what optics_agent needs from optics-group collaborators and what modules the agent framework should implement.

## Minimum Input From Optics Group

For each target figure, the group should provide:

| Required item | Why it matters |
|---|---|
| Paper PDF and target figure number | Defines scope and avoids broad paper reproduction. |
| Physical question of the figure | Prevents copying plots without understanding what is being computed. |
| Geometry table with coordinates | COMSOL needs exact dimensions and reference planes. |
| Material table with wavelength-dependent constants | Optical simulations are highly material-sensitive. |
| Physics interface or equation form | Eigenmode, frequency-domain scattering, transient, heat, fluid, etc. |
| Boundary conditions and truncation | Missing PML/scattering/domain size can dominate losses. |
| Mesh settings | Thin metal layers and gaps need explicit resolution. |
| Solver settings | Mode count, search shift, frequency, tolerances, sweep parameters. |
| Output observables | `neff`, loss, field profile, transmission, coupling length, etc. |
| Validation figure and expected trend | Lets the agent judge success qualitatively and quantitatively. |
| Known simplifications allowed | Defines what v1 may approximate. |

## Standard Answer Format For Training Self-Iteration

A useful "standard answer" from the optics group should include:

1. Figure goal: one paragraph explaining what is computed.
2. Parameter table: geometry, materials, source/wavelength, solver, sweep.
3. Missing-info table: what the paper omits and what assumption is chosen.
4. COMSOL model description: physics, boundary, mesh, solver, outputs.
5. Expected result: trend, approximate numeric ranges, success criteria.
6. Failure notes: common errors and how to recognize them in logs/plots.
7. Final comparison: what matches, what differs, and why.

## COMSOL Fields That Must Be Explicit

Every COMSOL reproduction task should explicitly state:

- geometry
- materials
- physics interface or equation form
- boundary conditions
- computational domain truncation
- mesh near small/high-loss features
- solver type and search/tolerance settings
- sweep step and dense regions
- validation figure and target numeric range
- output files and columns
- failure log and retry record

## Proposed optics_agent Modules

| Module | Responsibility |
|---|---|
| paper parser | Extract text, figures, captions, equations, and figure context. |
| parameter extractor | Convert paper setup into structured geometry/material/solver tables. |
| missing-info detector | Flag omitted numerical details that must be assumed. |
| COMSOL blueprint generator | Produce Java/M-file/template input following current runtime contract. |
| mesh/boundary proposer | Choose initial domain, PML/scattering boundaries, and mesh settings. |
| Magnus submitter | Stage files, dedupe jobs, check cluster resources, submit CPU-only jobs. |
| log/error parser | Classify compile, license, COMSOL API, solver, mesh, and output failures. |
| result validator | Check output ranges, branch labels, plots, and qualitative target trends. |
| self-iteration loop | Patch one failure at a time, rerun smoke before full sweep. |
| final-report generator | Write reproducible, auditable reports for humans and training data. |

## Degiron Fig. 3 Lessons So Far

- A target figure can look simple but still requires many hidden numerical details.
- The key missing details are not abstract theory; they are boundary conditions, mesh, mode-search settings, and branch classification.
- A training answer must include enough implementation-level detail that an agent can create and debug a COMSOL model, not just explain SPP physics.
- Fallback data must be labeled. A workflow-only surrogate is useful for pipeline testing but must never be reported as physical reproduction success.

## Additional Lessons From The Actual Run

The Degiron Fig. 3 rehearsal exposed several framework requirements that are easy to miss in a theory-only design:

| Issue found | Framework implication |
|---|---|
| COMSOL batch Java sandbox blocks env reads, system-property reads, and direct file IO inside `run()`. | The COMSOL generator must use sandbox-safe Java patterns and put data transfer through stdout, COMSOL tables, or runner-side postprocessing. |
| Java inner classes / anonymous classes caused COMSOL-side class execution errors. | Generated Java should be a single public class with simple static helper methods and primitive/string data structures. |
| SSH user could not read `/home/magnus/data`, but could read `/data/public/zhangyuanzheng` after permissions were set. | The submitter must distinguish job-writable persistent output from user-downloadable output, and preflight directory permissions. |
| Physics-controlled mesh failed before the solver. | The mesh proposer needs explicit fallback meshes and should record mesh setup errors separately from solver errors. |
| Full-vector mode analysis reached the eigensolver but failed matrix factorization for several shifts. | The self-iteration loop needs a validation ladder: isolated dielectric waveguide, isolated LR-SPP, then coupled system. |
| The final sweep succeeded only as `surrogate_fallback`. | The validator must treat "job Success" and "physical reproduction success" as separate states. |

## Minimum Standard Answer For Optics Group

For a paper figure to become useful training data, the optical group answer should include enough information to prevent blind solver guessing:

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
  COMSOL_interface:
  dependent_fields:
  propagation_direction:
  eigenvalue_definition:
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
  mode_count:
  search_shift:
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

For Degiron Fig. 3 specifically, the next useful human-provided artifact would be a minimal GUI-exported COMSOL Java model for one rectangular waveguide mode analysis. That would fix the exact Wave Optics/RF feature tags, boundary settings, and eigenmode solver settings faster than guessing through remote batch jobs.
