# Degiron 2009 NJP Fig. 3 V2 Assumptions And Missing Information

| Missing / unclear item | V2 decision | Risk |
|---|---|---|
| Exact COMSOL full-vector weak-form equations | Start with scalar TM-like Coefficient Form PDE for `Hx`; record as approximation. | May miss vector coupling, metal boundary physics, and correct losses. |
| Exact COMSOL Wave Optics mode-analysis Java settings | No working GUI-exported 6.3 template found locally. | Full-vector reproduction remains blocked until template/manual details are supplied. |
| Exact SU-8 irregular cross-section | Use rectangle `2.0 um x 1.5 um`. | Shifts effective index and hybridization point. |
| Whether `3.3 um` is bottom or center reference | Use Au/SU-8 bottom/reference line at `y=3.3 um`, consistent with Fig. 1(b). | If paper uses a different reference, vertical confinement is wrong. |
| Exact outer boundary/PML | Use finite window with Dirichlet boundary in scalar PDE v2 smoke. | `Im(neff)` can be strongly boundary-sensitive. |
| Exact lateral computational width | Start with `x=[-8,8] um`. | Wider field tails may be truncated. |
| Exact top air thickness | Start with `2 um` above BCB/air interface. | Air truncation may perturb slab hybrid modes. |
| Si substrate details | Use truncated lossless Si below 4 um SiO2. | Lower boundary may perturb LR-SPP/slab modes. |
| Metal mesh convergence | Start with explicit FreeTri and global conservative mesh; refine later if solve works. | 36 nm Au layer needs local refinement for accurate loss. |
| Mode classification near anticrossing | Start with sorted modes and branch continuity; field-overlap metrics deferred. | Red/blue labels may swap incorrectly near anticrossing. |
| Isolated dashed curves | V2 explicitly runs isolated SU-8 and isolated Au before coupled sweep. | Scalar approximation may reproduce trends but not full-vector values. |

## V2 Physical Status Labels

Use these labels in CSV and reports:

| Label | Meaning |
|---|---|
| `scalar_tm_hx_pde` | COMSOL Coefficient Form PDE scalar TM-like eigenmode approximation. |
| `full_vector_mode_analysis` | Verified Wave Optics/RF full-vector mode-analysis result. Not available yet. |
| `surrogate_fallback` | Nonphysical analytic/file-flow fallback. Must not be reported as reproduction. |
| `template_missing` | Blocker caused by absence of COMSOL 6.3 GUI-exported mode-analysis template. |
| `wave_optics_mode_analysis_probe` | Hand-written isolated Wave Optics/RF mode-analysis diagnostic. In v2 it reaches the eigensolver but produces no physical rows. |

## Stop Rule

If the isolated Wave Optics/RF mode-analysis probe fails before producing plausible `neff`, do not submit a full-vector coupled sweep. Record the failure and request a GUI-exported COMSOL mode-analysis template.

## Verified V2 Blocker

`degiron-2009-fig3-v2-mode-su8-smoke-v2` fixed the earlier mesh blocker by building explicit `FreeTri + Size` mesh before creating the Wave Optics physics interface. The model then reached `sol1/e1` and failed matrix factorization for all tested shift styles: dimensionless `neff`, dimensional `beta`, and plain `1.536`.

This means the remaining issue is not the Magnus runner or Java wrapper. It is missing or incorrect COMSOL mode-analysis physics/study/solver setup.
