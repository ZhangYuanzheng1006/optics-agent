# Degiron 2009 NJP Fig. 3 V2 Final Report

## Target

Degiron 2009 Fig. 3 computes the complex effective indices of two coupled eigenmodes in a 2D `x-y` cross-section of a plasmonic/dielectric directional coupler. Propagation is along `z`, the eigenvalue is the propagation wavevector, and the plotted quantity is:

```text
neff = kz / k0
```

The target comparison is `Re(neff)` and `Im(neff)` for the symmetric and anti-symmetric hybrid modes while sweeping total BCB thickness `t`, with anticrossing / hybridization expected around `t ~= 5.6 um`.

## Parameters Used

The v2 parameter baseline is recorded in `parameter_table.md`. Key values:

| Item | Value |
|---|---|
| wavelength | `1.55 um` |
| Au stripe | width `4.6 um`, thickness `36 nm` |
| SU-8 guide | rectangle approximation, width `2.0 um`, thickness `1.5 um` |
| lateral gap | `2.5 um` from Au right edge to SU-8 left edge |
| vertical placement | bottom of Au/SU-8 at `3.3 um` above BCB/SiO2 interface in v2 interpretation |
| BCB sweep | `4.8-10.0 um`, denser near `5.6 um` |
| Au permittivity | `-132 + 12.65i` |
| BCB index | `1.535` |
| SiO2 index | `1.444` |
| SU-8 index | `1.57 + 8e-5i` |

## Actual Models

V2 produced two kinds of COMSOL tests.

### 1. Scalar TM-like PDE diagnostic

Files:

```text
comsol/Degiron2009Fig3V2ScalarPdeLadderSmoke.java
comsol/Degiron2009Fig3V2ScalarPdeCoupledSweep.java
```

This model uses a controlled scalar approximation:

```text
u ~= Hx
-div((1/epsr) grad(u)) - k0^2 u = lambda (1/epsr) u
lambda = -beta^2
neff = beta/k0
```

It uses a finite rectangular window with Dirichlet boundary. This is not full-vector Wave Optics mode analysis, has no validated PML/open-boundary treatment, and is not acceptable as physical Fig. 3 reproduction.

### 2. Isolated SU-8 Wave Optics/RF mode-analysis probe

File:

```text
comsol/Degiron2009Fig3V2ModeAnalysisSu8Smoke.java
```

Purpose: test whether a minimal hand-written COMSOL Java mode-analysis model can produce a verified `neff` before attempting the coupled Au+SU8 structure.

Two attempts were made:

| Run | Job | Result | Diagnosis |
|---|---|---|---|
| `degiron-2009-fig3-v2-mode-su8-smoke-v1` | `af985c4c3b0ec6a0` | Success, 0 rows | Failed during physics-controlled mesh setup. |
| `degiron-2009-fig3-v2-mode-su8-smoke-v2` | `0e64e432914254d7` | Success, 0 rows | Explicit mesh fixed the mesh blocker; eigensolver then failed matrix factorization for `neff`, `beta`, and plain shifts. |

The v2b probe proves that the job compiles, runs, meshes, reaches COMSOL mode-analysis eigensolver, and saves `.mph`, but it still does not produce physical modes.

## Magnus Jobs

All jobs used:

```text
image: docker://magnus-local/comsol-runtime:latest
gpu_type: cpu
gpu_count: 0
cpu_count: 8
memory_demand: 32G
priority: B2
license: /opt/comsol-license/license.dat
```

Current v2 job table:

| Case | Run ID | Job ID | Status | Output |
|---|---|---|---|---|
| ladder scalar smoke | `degiron-2009-fig3-v2-ladder-smoke-v6` | `f886f496f107e1b7` | Success | `results/ladder_smoke_neff.csv` |
| isolated SU-8 mode probe | `degiron-2009-fig3-v2-mode-su8-smoke-v2` | `0e64e432914254d7` | Success, 0 rows | `results/degiron-2009-fig3-v2-mode-su8-smoke-v2_neff.csv` |
| coupled scalar sweep | `degiron-2009-fig3-v2-coupled-sweep-v1` | `f6c6748bf850a69f` | Success | `results/coupled_neff_sweep.csv`, `results/fig3_reproduction_v2.png` |

Full command/job record is in `magnus/submit_log.md`; failure/retry history is in `magnus/failure_retry_record.md`.

## Result Summary

Scalar coupled sweep:

| Branch | `Re(neff)` range | `Im(neff)` range |
|---|---:|---:|
| candidate 1 | `1.518792297-1.529490857` | `0-0` |
| candidate 2 | `1.517274191-1.526595259` | `0-0` |

Observed behavior:

- `Re(neff)` is too low compared with the paper target range, roughly `1.530-1.541`.
- Both scalar candidate branches increase monotonically with `t`.
- No clear anticrossing near `t ~= 5.6 um`.
- `Im(neff)` is effectively zero for plotted scalar branches, so the small-`t` anti-symmetric loss trend is not reproduced.

The user-observed v1 problem remains unresolved in v2: the imaginary-index trends are not physically credible. V2 improves honesty and diagnostics, not final agreement.

## Success Judgment

| Level | Status |
|---|---|
| Magnus/COMSOL pipeline | Successful |
| Scalar PDE numerical sweep | Successful as diagnostic |
| Full-vector Wave Optics/RF mode analysis | Not successful |
| Physical Fig. 3 reproduction | Not successful |

The best current statement is:

```text
v2 reproduces the workflow and identifies the blocker, but does not reproduce Fig. 3 physically.
```

## Main Blocker

No COMSOL 6.3 GUI-exported Java template for 2D Wave Optics/RF mode analysis exists locally. The hand-written API model can create the physics and study, but the solver setup is incomplete or wrong enough that even isolated SU-8 mode analysis fails matrix factorization.

This is the same failure class as v1, now confirmed on a smaller isolated validation model rather than only on the coupled structure.

## Next Fixes

1. Obtain a minimal COMSOL 6.3 GUI-exported Java or `.mph` template for a 2D rectangular dielectric waveguide mode analysis at `1.55 um`.
2. The template must include exact physics interface, propagation direction, mode-analysis study settings, solver sequence, boundary/PML settings, and result expressions for `neff` or `beta`.
3. Validate isolated SU-8 first, then isolated Au LR-SPP, then a two-point coupled smoke near `t = 5.6 um`.
4. Only after both isolated models return plausible modes should the coupled sweep be rerun.
5. For final branch classification, add field integrals over Au and SU-8 regions and continuity tracking across `t`, not just sorting by `Re(neff)`.

