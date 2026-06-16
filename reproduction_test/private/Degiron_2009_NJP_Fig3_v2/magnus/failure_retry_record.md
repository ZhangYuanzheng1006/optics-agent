# Degiron 2009 Fig. 3 V2 Failure And Retry Record

V2 starts with `scalar_tm_hx_pde` ladder smoke. This is a controlled scalar FEM approximation, not a full-vector Wave Optics reproduction.

## Attempts

| Step | Run/job | Outcome | Diagnosis | Patch |
|---|---|---|---|---|
| 1 | `degiron-2009-fig3-v2-ladder-smoke-v1` / `bdf4761c9081cd28` | Magnus `Success`, 0 data rows | COMSOL Java created mesh feature tag `ftri1` although a feature with that tag already existed. All seven ladder subcases printed `An object with the given name already exists - Tag: ftri1`. | Changed FreeTri creation to `ftri_user` with catch fallback; advanced ladder run id to `degiron-2009-fig3-v2-ladder-smoke-v2`. |
| 2 | `degiron-2009-fig3-v2-ladder-smoke-v2` / `e77cafac0698c270` | Magnus `Success`, 0 data rows | COMSOL study feature rejected `rtol`: `Unknown property - Property: rtol`. | Wrapped `rtol` setting in `try/catch`; advanced ladder run id to `degiron-2009-fig3-v2-ladder-smoke-v3`. |
| 3 | `degiron-2009-fig3-v2-ladder-smoke-v3` / `980cdfcf54c36dab` | Magnus `Success`, 0 data rows | Anonymous `Comparator` generated `Degiron2009Fig3V2ScalarPdeLadderSmoke$1`; COMSOL batch could not load that helper class. | Replaced anonymous comparator with explicit in-place sort helper; advanced ladder run id to `degiron-2009-fig3-v2-ladder-smoke-v4`. |
| 4 | `degiron-2009-fig3-v2-ladder-smoke-v4` / `434f769ac54aa4eb` | Magnus `Success`, 0 data rows | Solver completed but all extracted modes were filtered out as implausible before raw values were saved. | Changed Java to output up to 8 raw modes per subcase and mark implausible rows with `_raw`; advanced ladder run id to `degiron-2009-fig3-v2-ladder-smoke-v5`. |
| 5 | `degiron-2009-fig3-v2-ladder-smoke-v5` / `c6a9043a4f4f405a` | Magnus `Success`, 56 raw rows | Java converted `beta` using `k0` in `1/um` while COMSOL eigenvalues are SI-scale `1/m^2`; `neff` was inflated by `1e6`, which also broke sorting. | Changed Java `K0` to `2*pi/(1.55e-6)`; advanced ladder run id to `degiron-2009-fig3-v2-ladder-smoke-v6`. |
| 6 | `degiron-2009-fig3-v2-mode-su8-smoke-v1` / `af985c4c3b0ec6a0` | Magnus `Success`, 0 data rows | The isolated SU-8 Wave Optics/RF mode-analysis probe compiled and saved `.mph`, but all shift attempts failed during mesh setup: `Failed to set up physics-controlled mesh` / `Failed to set mesh size automatically`. | Moved explicit `FreeTri + Size` mesh construction before creating the Wave Optics physics interface; advanced mode-analysis smoke run id to `degiron-2009-fig3-v2-mode-su8-smoke-v2`. |
