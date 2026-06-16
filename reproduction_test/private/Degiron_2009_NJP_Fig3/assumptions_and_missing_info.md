# Assumptions And Missing Information

This file is intentionally explicit. These are the details a paper often omits but a numerical reproduction needs.

| Missing / unclear item | V1 decision | Risk |
|---|---|---|
| Exact COMSOL weak-form equations used by the paper | Use COMSOL Wave Optics / RF mode analysis if available. | API or physics-interface mismatch can block full-vector reproduction. |
| Exact SU-8 irregular cross-section coordinates | Use rectangular SU-8 cross section: `2.0 um x 1.5 um`. | Can shift `neff` and hybridization point. |
| Meaning of `3.3 um` vertical position | Interpret as Au/SU-8 bottom height above BCB/SiO2 interface. | If paper used a centerline or another reference, geometry is vertically shifted. |
| Exact outer boundary condition | Use large finite domain and attempt scattering/low-reflection boundary. | Reflections can perturb `Im(neff)`. |
| Whether PML was used | Not used by default in v1; add if boundary sensitivity appears. | Missing PML can affect leaky/slab-hybrid modes. |
| Exact computational window size | Use `x=[-12,12] um`, air thickness `4 um`, Si below `2 um`. | Window can affect slab-mode hybridization. |
| Si optical constants | Use lossless `n=3.48` if Si included. | Silicon loss/dispersion may matter weakly through lower boundary. |
| Mesh near 36 nm Au | Use target max element `<=12 nm` in plan; Java v1 may fall back to global/finer auto mesh if local sizing API fails. | Metal loss and mode confinement are mesh-sensitive. |
| Element order | Use COMSOL default for selected physics unless explicit quadratic setting works. | Low-order elements may need finer mesh. |
| BCB sweep step | Use coarse plus dense grid near `5.6 um`: `0.2 um` coarse and `0.1 um` near anticrossing. | Paper does not specify exact sampling. |
| Eigenmode search shift | Start near `neff=1.536`; if needed scan `1.532`, `1.536`, `1.540`. | Wrong shift can find irrelevant modes. |
| Symmetric / antisymmetric classification | Prefer field sign/localization; fallback uses branch continuity and coupled-mode surrogate labels. | Ambiguous near anticrossing. |
| Isolated dashed reference curves | Not required for v1 success; add isolated Au-only and SU8-only runs after coupled sweep works. | Without them, Fig. 3 comparison is partial. |
| COMSOL batch Java sandbox | Generated Java must avoid env reads, system-property reads, direct file IO, inner classes, and anonymous classes. | Otherwise a job may save `.mph` but fail to emit usable data. |
| User-downloadable output path | Use `/data/public/zhangyuanzheng/comsol-runtime/runs` for this rehearsal after pre-creating it with write permission. | `/home/magnus/data` is job-writable but not directly SSH-readable by the user account. |
| Full-vector eigensolver state | Current coupled model reaches eigensolver but fails matrix factorization for multiple shifts. | Need isolated-mode validation and/or GUI-exported Java template before claiming physical reproduction. |

## Fallback Policy

If true COMSOL mode analysis fails because the Java API or physics interface is unavailable, the run may create a `surrogate_fallback` dataset. That fallback exists only to validate the paper-to-Magnus workflow and plotting/report pipeline. It is not counted as a successful physical COMSOL reproduction.

The final report must distinguish:

- `full_vector_mode_analysis`: physical reproduction candidate.
- `full_vector_mode_analysis_partial_extraction`: COMSOL solve ran but some postprocessing used fallback estimates.
- `surrogate_fallback`: workflow-only output; not a physical reproduction.

## Observed Runtime Blockers

- `System.getenv(...)` failed under COMSOL Java security preferences.
- `System.getProperty("user.dir")` failed under COMSOL Java security preferences.
- Java direct filesystem access to `"."` failed under COMSOL Java security preferences.
- Java inner class loading caused a COMSOL-side class execution error.
- Physics-controlled mesh failed; explicit `FreeTri` mesh avoided that first blocker.
- The current full-vector Wave Optics/RF mode analysis still fails in the eigenvalue solver with matrix factorization errors, even after testing several beta/neff shifts.
