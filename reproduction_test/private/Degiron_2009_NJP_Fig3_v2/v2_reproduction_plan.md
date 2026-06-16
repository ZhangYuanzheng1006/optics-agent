# Degiron 2009 NJP Fig. 3 V2 Reproduction Plan

## Goal

Rerun the Degiron 2009 NJP Fig. 3 reproduction as a second, isolated attempt.

Target figure:

```text
Fig. 3: Dispersion of the two eigenmodes as a function of the BCB thickness t.
```

Target numerical outputs:

- `Re(neff)` for symmetric and anti-symmetric hybrid modes.
- `Im(neff)` for symmetric and anti-symmetric hybrid modes.
- BCB thickness sweep around `t = 4.8-10.0 um`, with dense points near `t ~= 5.6 um`.
- Evidence for or against anticrossing / mode hybridization near `t ~= 5.6 um`.

V2 success requires COMSOL-derived full-vector or explicitly documented physical mode-analysis output. A surrogate dataset is allowed only as a pipeline diagnostic and must not be plotted or reported as reproduction success.

## Non-Negotiable Constraints

| Constraint | Rule |
|---|---|
| Output isolation | Use only `reproduction_test/private/Degiron_2009_NJP_Fig3_v2/` for v2 local artifacts. |
| Active image | Keep `docker://magnus-local/comsol-runtime:latest`; do not refresh or replace it. |
| GPU | Do not use GPU. Set `gpu_type=cpu`, `gpu_count=0`. |
| Resource limit | Before each submit, query cluster resources and keep planned CPU/memory under half of cluster totals. |
| Job dedupe | Before each submit, query existing Magnus jobs by exact v2 `run_id`. |
| Failed jobs | Do not silently rerun failed/terminated jobs without a new run-id suffix and failure record. |
| Secrets | Do not write token, license contents, SSH key, or private PDF text dumps into v2 artifacts. |
| Fallback | `surrogate_fallback` may validate file flow only; it is not physical reproduction. |

## Locked Parameters From V1

These remain the starting values unless the PDF reread or GUI template forces a correction.

| Category | Parameter | V2 starting value |
|---|---|---|
| wavelength | `lambda0` | `1.55 um` |
| propagation | direction | `z` |
| computational plane | cross-section | `x-y` |
| eigenvalue | propagation wavevector | `kz` |
| effective index | definition | `neff = kz/k0` |
| Au stripe | width | `4.6 um` |
| Au stripe | thickness | `36 nm = 0.036 um` |
| SU-8 | width | `2.0 um` |
| SU-8 | thickness | `1.5 um` |
| gap | Au right edge to SU-8 left edge | `2.5 um` |
| vertical reference | waveguide/Au bottom above BCB/SiO2 | `3.3 um` in v1 interpretation |
| BCB | scan | `4.8-10.0 um`, dense near `5.6 um` |
| SiO2 | layer | `4 um` |
| Au | permittivity | `-132 + 12.65i` |
| BCB | refractive index | `1.535` |
| SiO2 | refractive index | `1.444` |
| SU-8 | refractive index | `1.57 + 8e-5i` |

## V2 Main Technical Change

V1 tried the full coupled model too early. V2 uses a validation ladder.

```text
paper reread
  -> GUI-export template or mode-analysis syntax source
  -> isolated SU-8 mode smoke
  -> isolated Au LR-SPP mode smoke
  -> coupled Au+SU8 smoke at 1-2 t values
  -> coupled sweep
  -> physical validator
  -> final report
```

## Phase 0: Re-Read And Rebaseline

Files to write:

```text
paper_notes.md
parameter_table.md
assumptions_and_missing_info.md
```

Actions:

1. Re-open the local PDF and recheck abstract, introduction, section 2, Fig. 1(b), Fig. 2, Fig. 3, caption and nearby text.
2. Re-render or inspect Fig. 1(b), Fig. 2, and Fig. 3 visually if needed.
3. Confirm whether `3.3 um` means bottom, centerline, or another reference plane.
4. Record the v2 interpretation separately from v1; do not overwrite v1 files.
5. Keep unresolved items explicit instead of burying them in code.

## Phase 1: COMSOL 6.3 Mode-Analysis Template Acquisition

Preferred route:

1. Obtain or generate a minimal COMSOL 6.3 GUI-exported Java file for a 2D rectangular optical waveguide mode analysis.
2. Preserve exact component-scoped style, physics tags, study step, solver sequence, boundary/PML features, and result expressions.
3. Trim only GUI-only artifacts; do not rewrite physics strings by guesswork.

If no GUI-exported template is available:

1. Run only minimal diagnostic Java probes, not a full sweep.
2. Treat the result as `template_missing` unless the isolated SU-8 mode produces plausible `neff` through a verified mode-analysis variable.
3. Ask the optics group for a GUI-exported `.java` or `.mph` template before declaring v2 blocked.

V2 must explicitly record which of these two routes was used.

## Phase 2: COMSOL Model Construction

Planned Java files:

```text
comsol/Degiron2009Fig3_IsolatedSU8.java
comsol/Degiron2009Fig3_IsolatedAu.java
comsol/Degiron2009Fig3_Coupled.java
```

Shared batch rules:

- Use official COMSOL Java API imports.
- Use `public static Model run()`.
- Use `main(String[] args)` only to save `args[0]` and print markers.
- Avoid `System.getenv`, `System.getProperty`, direct Java file IO inside `run()`, inner classes, and anonymous classes.
- Emit stdout markers:

```text
DEGIRON_V2_CSV_HEADER,...
DEGIRON_V2_CSV_ROW,...
DEGIRON_2009_FIG3_V2_<CASE>_OK ...
```

Geometry rules:

- Prefer non-overlapping domains and explicit selections.
- Avoid v1's single global material with spatial `if(...)` expressions unless forced by API limitations.
- Use named selections for Au, SU-8, BCB, SiO2, Si/air, and exterior/PML boundaries.
- Check entity IDs after every geometry change if selections are ID-based.

Mesh rules:

| Region | Initial target |
|---|---|
| Au 36 nm layer | max element `<= 0.012 um` |
| Au edges / gap / SU-8 boundary | max element `<= 0.05-0.08 um` |
| bulk BCB / SiO2 / air | max element `<= 0.25 um` |
| v2 mesh fallback | explicit `FreeTri` with local `Size` features |

Boundary rules:

- Prefer PML/open-boundary settings from GUI-exported COMSOL 6.3 Java.
- If using scattering/low-reflection boundary, label the run boundary-sensitive.
- Do not compare `Im(neff)` to Fig. 3 until boundary/PML treatment is physically defensible.

Solver rules:

- Preserve GUI-exported mode-analysis study and solver sequence where available.
- Record whether the search shift is `neff`, `beta`, `kz`, or raw eigenvalue.
- Start with `neff ~= 1.536`, but do not mix dimensionless and dimensional shifts.
- Request enough modes to catch both relevant TM-like branches and reject slab/radiation modes.

Result extraction rules:

- Use COMSOL variable names from the working GUI-exported model if available.
- Do not assume `emw.neff` or `ewfd.neff` exists.
- Export mode index, raw eigenvalue if accessible, `Re(neff)`, `Im(neff)`, and branch-classification metrics.
- For coupled modes, classify by field profile and continuity, not only by sorted `Re(neff)`.

## Phase 3: Magnus Submission Plan

Remote case directory:

```text
/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2
```

Remote output root:

```text
/data/public/zhangyuanzheng/comsol-runtime/runs
```

Blueprint:

```text
Optics_COMSOL_Runtime_zyz
```

Image:

```text
docker://magnus-local/comsol-runtime:latest
```

License mode:

```text
server_env
/opt/comsol-license/license.dat
```

Default resources:

| Stage | Run ID | CPU | Memory | Storage | Priority |
|---|---|---:|---:|---:|---|
| isolated SU-8 smoke | `degiron-2009-fig3-v2-isolated-su8-smoke-v1` | 8 | 32G | 100G | B2 |
| isolated Au smoke | `degiron-2009-fig3-v2-isolated-au-smoke-v1` | 8 | 32G | 100G | B2 |
| coupled smoke | `degiron-2009-fig3-v2-coupled-smoke-v1` | 8 | 32G | 100G | B2 |
| coupled sweep | `degiron-2009-fig3-v2-coupled-sweep-v1` | 8 | 32G | 100G | B2 |

Submit order:

1. Stage v2 case files.
2. Dry-run submitter.
3. Submit isolated SU-8 smoke.
4. Inspect `neff` and field/profile metrics.
5. Submit isolated Au smoke only if SU-8 mode analysis is physically plausible.
6. Submit coupled smoke only if both isolated models produce plausible modes.
7. Submit sweep only if coupled smoke produces two distinct hybrid branches.

Before every submit:

1. `magnus.list_jobs(limit=100, search=<run_id>)`
2. Reuse active/success job.
3. Skip failed/terminated job unless the new run ID records a deliberate retry.
4. `magnus.get_cluster_stats(timeout=20)`
5. Block submit if planned CPU/memory after submit exceeds half cluster total.
6. Confirm GPU is not requested.

Polling:

| Stage | Polling |
|---|---|
| isolated/coupled smoke | 60 s for first 10 min, then 180 s, max 45 min |
| coupled sweep | 5 min for first hour, then 15 min, max 6 h |

## Phase 4: Validation Criteria

### Isolated SU-8 Acceptance

- COMSOL job reaches `Success`.
- Full-vector or verified physical mode-analysis rows exist.
- At least one guided mode has plausible `Re(neff)` between BCB and SU-8 index.
- `Im(neff)` is small and consistent with SU-8 loss scale.
- Result variable source is recorded.

### Isolated Au Acceptance

- COMSOL job reaches `Success`.
- At least one LR-SPP-like mode appears with plausible `Re(neff)` near the Fig. 3 isolated Au dashed trend.
- `Im(neff)` is positive and in the expected `1e-4` order, subject to boundary/mesh sensitivity.
- Field localization / classification metric identifies Au/LR-SPP character.

### Coupled Smoke Acceptance

- Two relevant hybrid branches are extracted at `t = 5.6 um` and one nearby point.
- The two branches can be classified by field pattern or branch continuity.
- No surrogate rows are used in the acceptance CSV.

### Coupled Sweep Acceptance

- `results/coupled_neff_sweep.csv` contains two physical branches for most/all `t` values.
- `results/fig3_reproduction_v2.png` plots `Re(neff)` and `Im(neff)` versus `t`.
- The report states clearly whether anticrossing near `t ~= 5.6 um` is observed.
- If `Im(neff)` disagrees, the report ranks likely causes instead of hiding the mismatch.

## Stop Conditions

Stop before a full sweep if any of these occur:

| Condition | Action |
|---|---|
| No verified mode-analysis variable can be extracted | Record `template_missing` or `result_variable_missing`; request GUI-export Java. |
| Isolated SU-8 fails matrix factorization | Do not attempt coupled model; fix boundary/solver/template first. |
| Isolated Au fails matrix factorization | Do not attempt coupled model; fix PML/metal mesh/material first. |
| Coupled smoke returns only surrogate rows | Do not sweep; mark physical blocker. |
| Cluster resources exceed half-limit | Do not submit; wait and recheck. |

## Final Reports

V2 must end with:

```text
final_report.md
workflow_handoff_A_v2.md
```

`final_report.md` must include:

- What Fig. 3 computes.
- V2 parameter table.
- Actual COMSOL model and whether it used GUI-exported template settings.
- Boundary, mesh, solver, sweep.
- Job IDs and statuses.
- CSV/figure paths.
- Physical success / partial success / failure judgment.
- Direct discussion of `Im(neff)` mismatch, especially the anti-symmetric branch at small `t`.
- Next fixes.

`workflow_handoff_A_v2.md` must include:

- What optics group standard answers must contain.
- What information was still missing after v2.
- Which parts should become framework modules.
- A clear statement that GUI-exported COMSOL templates are critical training artifacts for Java API based self-iteration.

