# Degiron 2009 Fig. 3 V2 Workflow Handoff

## Executive Conclusion

V2 confirms that optics_agent can execute the paper-reproduction workflow end to end, but cannot yet complete a physical COMSOL full-vector reproduction of Degiron Fig. 3 without a verified COMSOL 6.3 mode-analysis template.

The critical finding is practical:

```text
COMSOL Java API syntax knowledge is not enough.
Wave Optics/RF mode-analysis needs GUI-exported physics/study/solver/result settings.
```

## What Optics Group Should Provide

For each figure reproduction task, the minimum standard answer should include:

| Area | Required detail |
|---|---|
| Figure target | Figure number, plotted observables, sweep variable, expected trend, expected numeric range. |
| Geometry | Coordinate system, all object dimensions, layer stack, reference planes, gaps, uncertain fabrication shapes. |
| Materials | Wavelength, complex index or permittivity, dispersion source, loss convention. |
| Physics | COMSOL interface name, dimensionality, propagation direction, eigenvalue definition, dependent fields. |
| Boundaries | PML/scattering/PEC/PMC/open-boundary choice, domain truncation size, substrate truncation. |
| Mesh | Max element in metal, gap, dielectric interfaces, bulk, boundary layers, element order. |
| Solver | Study type, mode count, search variable, shift scale, tolerances, solver sequence if nondefault. |
| Postprocess | Exact `neff`/`beta` expression, branch classification rule, field-profile checks. |
| Validation | Target plot, numeric ranges, known acceptable simplifications, known failure modes. |

For COMSOL-based answers, the most useful training artifact is not prose alone. It is:

```text
minimal GUI-exported COMSOL 6.3 Java or .mph template
  + short explanation of which settings matter
  + expected numeric output for one smoke case
```

## Degiron-Specific Missing Inputs

V2 still lacks:

- COMSOL 6.3 GUI-exported 2D Wave Optics/RF mode-analysis Java template.
- Exact PML/open-boundary setup used by the paper or by a trusted reproduction.
- Exact solver shift variable: dimensionless `neff`, dimensional `beta/kz`, or another internal eigenvalue.
- Verified result expression: `emw.neff`, `ewfd.neff`, `emw.beta/k0`, raw eigenvalue, or a different module variable.
- Exact SU-8 irregular cross-section coordinates.
- Mesh settings near 36 nm Au and metal/dielectric corners.
- Field-profile based symmetric/anti-symmetric classification rule.

## Agent Workflow Lessons

V2 should become a framework pattern:

1. Read paper and extract parameters.
2. Audit previous attempts before coding.
3. Separate platform success from physical success.
4. Validate isolated submodels before coupled systems.
5. Stop blind large sweeps when the isolated mode-analysis smoke fails.
6. Preserve failure rows, job IDs, logs, scripts, CSV, and plots in a stable folder.
7. Require collaborator-provided COMSOL templates when module-specific solver settings are unknown.

## Framework Modules Needed

| Module | Responsibility |
|---|---|
| paper parser | Extract abstract, numerical method, figure captions, and nearby context. |
| parameter extractor | Produce geometry/material/physics/solver/postprocess tables. |
| missing-info detector | Flag boundary, mesh, solver, and classification gaps before job launch. |
| COMSOL blueprint generator | Generate batch-safe Java/M-file/model skeletons from templates. |
| GUI-template ingester | Read GUI-exported Java and preserve physics/study/solver/result settings. |
| mesh/boundary proposer | Suggest mesh and domain truncation with explicit uncertainty labels. |
| Magnus submitter | Stage files, dedupe by run id, check resources, launch conservative jobs. |
| log/error parser | Classify compile, mesh, solver, result-variable, and postprocess errors. |
| result validator | Compare trends/ranges and mark physical vs pipeline success. |
| self-iteration loop | Retry only when the next patch addresses a specific diagnosed failure. |
| report generator | Write final report and handoff with job evidence and next required inputs. |

## Degiron V2 Evidence To Reuse

Useful files:

```text
v1_experience_audit.md
v2_reproduction_plan.md
parameter_table.md
assumptions_and_missing_info.md
comsol/Degiron2009Fig3V2ModeAnalysisSu8Smoke.java
magnus/failure_retry_record.md
magnus/submit_log.md
results/coupled_neff_sweep.csv
results/fig3_reproduction_v2.png
final_report.md
```

Job evidence:

| Run | Job | Meaning |
|---|---|---|
| `degiron-2009-fig3-v2-ladder-smoke-v6` | `f886f496f107e1b7` | Scalar PDE diagnostic works. |
| `degiron-2009-fig3-v2-mode-su8-smoke-v2` | `0e64e432914254d7` | Isolated Wave Optics mode-analysis reaches eigensolver but fails matrix factorization. |
| `degiron-2009-fig3-v2-coupled-sweep-v1` | `f6c6748bf850a69f` | Scalar coupled sweep works but is not physical Fig. 3 reproduction. |

## Recommended Next Human Request

Ask the optics group for this exact artifact:

```text
A minimal COMSOL 6.3 GUI-exported Java file or .mph model for a 2D rectangular dielectric waveguide mode analysis at 1.55 um, with the effective index printed or exported for at least one mode.
```

Once that template exists, optics_agent should patch only geometry/material parameters first, not rewrite the physics/study/solver sequence.

