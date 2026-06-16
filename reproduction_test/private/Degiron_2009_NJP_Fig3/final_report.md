# Degiron 2009 NJP Fig. 3 Reproduction Report

Status: workflow completed, physical COMSOL reproduction not yet completed.

## Fig. 3 Computes

Fig. 3 scans the total BCB thickness `t` in a dielectric waveguide / long-range plasmon directional coupler. The intended numerical problem is a 2D `x-y` cross-section mode analysis with propagation along `z`; the eigenvalue is the propagation wavevector `kz`, reported as:

$$
n_\mathrm{eff}=k_z/k_0.
$$

The target outputs are `Re(neff)` and `Im(neff)` for the two coupled symmetric / antisymmetric hybrid modes. The paper shows isolated-mode crossing and coupled-mode anticrossing around `t ~ 5.6 um`.

## Extracted Parameters

See `parameter_table.md` for the full table. The v1 model used:

- `lambda0 = 1.55 um`
- Au stripe: `4.6 um` wide, `36 nm` thick
- SU-8 waveguide: rectangular approximation, `2.0 um x 1.5 um`
- Au-to-SU8 lateral gap: `2.5 um`
- waveguide/Au bottom height: `3.3 um` above the BCB/SiO2 interface
- BCB sweep: `4.8-10.0 um`, densified near `5.6 um`
- `eps_Au = -132 + 12.65i`
- `n_BCB = 1.535`, `n_SiO2 = 1.444`, `n_SU8 = 1.57 + 8e-5i`

## Actual COMSOL Model

Implementation:

```text
comsol/Degiron2009Fig3ModeSweep.java
```

The Java model builds the Degiron cross-section geometry and attempts Wave Optics / RF mode analysis in smoke mode. Because COMSOL batch Java runs under a restricted sandbox, the final working Java source avoids:

- `System.getenv`
- `System.getProperty`
- direct Java file IO inside `run()`
- inner classes and anonymous classes

Numerical rows are printed to stdout as `DEGIRON_CSV_ROW,...`; `postprocess_degiron_fig3.py` reconstructs `neff_sweep.csv` from `raw/stdout.txt`.

## Boundary, Mesh, Solver

V1 choices:

- Domain: `x=[-12,12] um`; Si, SiO2, BCB, air, Au, and SU-8 regions.
- Boundary: attempted scattering / low-reflection boundary through the COMSOL Java API.
- Mesh: explicit `FreeTri` mesh. Initial physics-controlled mesh failed.
- Solver: `ModeAnalysis` / `BoundaryModeAnalysis`, fixed frequency `c_const/lambda0`.
- Search shifts tested: `(2*pi/lambda0)*1.532`, `1.536`, `1.540`, plus dimensionless `1.536`.

## Magnus Runs

Active runtime:

```text
docker://magnus-local/comsol-runtime:latest
/data/public/zhangyuanzheng/comsol-runtime
```

All jobs were CPU-only, `B2`, `8 CPU`, `32G`, below half-cluster resource limits.

Key jobs:

| Run | Job ID | Result | Notes |
|---|---|---|---|
| `degiron-2009-fig3-smoke-v1` | `9dcd1c2ba84ab0a0` | Failed | no `.mph`; Java did not expose a COMSOL-compatible `run()` model path. |
| `degiron-2009-fig3-smoke-v1` | `156e85aaf072ea23` | Failed | Java sandbox blocked `System.getenv`. |
| `degiron-2009-fig3-smoke-v1` | `39a4a495753869e5` | Failed | Java sandbox blocked `System.getProperty`. |
| `degiron-2009-fig3-smoke-v2` | `457d6a631cc2ece0` | Success | `.mph` and stdout CSV produced; full-vector failed, surrogate fallback. |
| `degiron-2009-fig3-smoke-v3` | `48dee6cda1a4baa7` | Success | explicit FreeTri mesh; full-vector still failed at eigensolver. |
| `degiron-2009-fig3-smoke-v4` | `228e43d047953613` | Success | multiple eigenvalue shifts tested; full-vector still failed. |
| `degiron-2009-fig3-sweep-v4` | `127fde3b1d9bcb34` | Success | full sweep generated as `surrogate_fallback`. |

Detailed failure log:

```text
magnus/failure_retry_record.md
```

## Output Artifacts

```text
results/neff_sweep.csv
results/fig3_reproduction.png
results/postprocess_summary.json
magnus/raw_logs/degiron-2009-fig3-sweep-v4/
```

The final sweep has:

- `62` rows = `31` BCB thickness values x `2` branches
- `t` range: `4.8-10.0 um`
- `Re(neff)` range: about `1.5302-1.5395`
- `Im(neff)` range: about `5.0e-5-2.6e-4`
- method: `surrogate_fallback`
- `physical_reproduction_complete = false`

## Success Judgment

The workflow succeeded as an end-to-end agent rehearsal:

- paper parameters were extracted into tables;
- COMSOL Java was staged and launched through Magnus;
- failures were observed, diagnosed, patched, and retried;
- stdout-to-CSV postprocessing works;
- local CSV and figure were generated;
- reports record the distinction between physical solve and fallback.

The physical Fig. 3 reproduction is not successful yet. The current plot shows an anticrossing-like trend only because the fallback coupled-mode surrogate was designed to preserve the qualitative target behavior. It must not be reported as a COMSOL-derived reproduction of the paper.

## Main Blocker

The Wave Optics / RF full-vector mode-analysis setup reaches the eigensolver but fails matrix factorization for multiple shifts:

```text
Failed to compute the matrix factorization in the eigensolver.
Try to search for eigenvalues around a different shift value.
COMSOL assertion failure.
```

Likely causes, ranked:

1. The Java API mode-analysis feature settings are incomplete or wrong for this 2D cross-section mode solve.
2. The open exterior domain / scattering boundary setup is not numerically well-posed for the eigenmode problem.
3. Materials are assigned through spatial `if(...)` expressions instead of clean domain selections.
4. Overlapping geometry objects may produce domains/selections that differ from the intended layered stack.
5. A GUI-exported COMSOL mode-analysis template is needed to identify the exact feature tags and solver settings.

## Next Improvements

1. Build three simpler validation models before reattempting the coupled system:
   - isolated SU-8 waveguide in BCB/air/SiO2;
   - isolated Au LR-SPP stripe;
   - coupled Au+SU8 with large domain and no Si first.
2. Replace spatial material expressions with explicit domain selections.
3. Add explicit PML or impedance/scattering boundary settings from a GUI-exported COMSOL model.
4. Ask the optics group for a minimal COMSOL GUI-exported Java mode-analysis file for a rectangular dielectric waveguide.
5. Only after the isolated models return plausible `neff`, rerun the full coupled sweep and branch classification.

