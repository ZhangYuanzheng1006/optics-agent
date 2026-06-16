# V1 Experience Audit

This audit was written before starting v2. It summarizes the previous reproduction attempt under:

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
```

## What V1 Completed

| Area | V1 state |
|---|---|
| Paper reading | Abstract, introduction, section 2, Fig. 1(b), Fig. 2, Fig. 3, and nearby text were summarized. |
| Parameter extraction | Geometry, materials, sweep variable, and target observables were written to `parameter_table.md`. |
| Missing-info analysis | Boundary, mesh, solver, mode sorting, and geometry ambiguity were listed explicitly. |
| Magnus pipeline | COMSOL Java source was staged to Gustation and submitted through `Optics_COMSOL_Runtime_zyz`. |
| Runtime contract | Java compile, COMSOL batch launch, output MPH normalization, stdout parsing, local postprocess, CSV, and plot generation all worked. |
| Reporting | `final_report.md` and `workflow_handoff_A.md` separated workflow success from physical reproduction failure. |

## What V1 Did Not Complete

V1 did not complete a physical COMSOL full-vector reproduction of Fig. 3.

The final successful sweep job was:

```text
run_id: degiron-2009-fig3-sweep-v4
job_id: 127fde3b1d9bcb34
status: Success
method: surrogate_fallback
physical_reproduction_complete: false
```

That data validated the pipeline only. It must not be used as a paper-reproduction result.

## Observed User-Level Result Problem

The v1 plot looked partly plausible in `Re(neff)`, but this was not physical evidence because the sweep was a fallback surrogate.

The user observed that the imaginary-index behavior was not acceptable:

| Branch | Observed v1 issue |
|---|---|
| anti-symmetric / blue | At small BCB thickness, the trend is completely wrong. |
| symmetric / red | Trend is only barely reasonable; values have large deviation. |

This should be treated as a validator failure, not as a minor plotting issue.

## Technical Failures V1 Solved

These should remain fixed in v2:

| Failure | V1 resolution |
|---|---|
| `OUTPUT_MPH_MISSING` | Use batch-safe Java with `public static Model run()` returning a model and `main()` saving `args[0]`. |
| COMSOL sandbox blocked `System.getenv` | No environment reads inside COMSOL Java `run()`. |
| COMSOL sandbox blocked `System.getProperty` | No system-property reads inside COMSOL Java `run()`. |
| COMSOL sandbox blocked direct Java file IO | Use stdout markers and runner-side postprocessing instead. |
| Java inner/anonymous class errors | Use one public class with simple static helper methods. |
| Physics-controlled mesh failed | Prefer explicit user-controlled mesh, at least as fallback. |

## Main Unsolved V1 Blocker

The hand-written Wave Optics / RF mode-analysis model reached the eigensolver and then failed matrix factorization for multiple shifts:

```text
Failed to compute the matrix factorization in the eigensolver.
Try to search for eigenvalues around a different shift value.
COMSOL assertion failure.
```

The most likely cause is incomplete or wrong COMSOL 6.3 mode-analysis setup in hand-written Java:

1. Mode-analysis feature tags/settings were guessed rather than exported from a verified GUI model.
2. Eigenvalue shift scale may have mixed `neff`, `beta`, and raw eigenvalue units.
3. Boundary/PML/open-domain setup was not validated for eigenmodes.
4. Material assignment used spatial `if(...)` expressions over overlapping geometry rather than explicit non-overlapping domains/selections.
5. Coupled geometry was attempted before isolated SU-8 and isolated Au modes were validated.

## V2 Design Consequences

V2 changes the order and success criteria:

1. Do not tune or report `surrogate_fallback` as a reproduction.
2. Do not start with the coupled structure.
3. First validate the COMSOL mode-analysis interface on isolated SU-8.
4. Then validate isolated Au LR-SPP.
5. Only then run the coupled two-waveguide smoke and sweep.
6. Prefer COMSOL 6.3 GUI-exported Java as the source of truth for physics, study, solver, PML/boundary, and result variables.
7. If no GUI-exported Java template is available, v2 may still run diagnostic probes, but the report must clearly state the remaining template blocker.

## Current Repository Check

The updated `comsol-java-api` skill says the COMSOL Java API manual is useful for syntax but insufficient for production Wave Optics mode analysis. It explicitly recommends COMSOL 6.3 GUI-exported Java for version-sensitive feature tags and solver sequences.

Repository search found no ready-to-use GUI-exported Wave Optics mode-analysis Java template. The existing v1 Java file contains guessed candidates such as `ElectromagneticWavesFrequencyDomain`, `ModeAnalysis`, `BoundaryModeAnalysis`, `emw.neff`, and `ewfd.neff`; these are exactly the uncertain points v2 must validate before sweeping.

