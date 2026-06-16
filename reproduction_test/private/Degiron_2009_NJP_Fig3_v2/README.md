# Degiron 2009 NJP Fig. 3 Reproduction V2

This folder is isolated from the first rehearsal folder:

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
```

V2 must not reuse v1 results as physical evidence. V1 may be cited only as an experience log.

## Current State

- V2 Magnus/COMSOL jobs have been submitted and completed.
- The scalar TM-like PDE ladder and coupled sweep produced CSV/plot artifacts.
- The isolated Wave Optics/RF mode-analysis probe compiled, meshed, reached the eigensolver, and saved `.mph`, but produced zero `neff` rows because the eigensolver failed matrix factorization.
- Physical Fig. 3 reproduction is not complete.
- The active COMSOL runtime remains:

```text
docker://magnus-local/comsol-runtime:latest
```

- Do not rebuild, refresh, pull, retag, or replace that image.

## Main Documents

| File | Purpose |
|---|---|
| `v1_experience_audit.md` | What v1 proved, what failed, and what must change. |
| `v2_reproduction_plan.md` | New execution plan for the second reproduction attempt. |
| `todo.md` | Persistent checklist for v2 execution and later context recovery. |
| `final_report.md` | V2 outcome, jobs, results, mismatch, and next fixes. |
| `workflow_handoff_A_v2.md` | Handoff for optics-agent framework and optics-group standard answers. |

## Artifact Layout

```text
paper_notes.md
parameter_table.md
assumptions_and_missing_info.md
comsol/
  Degiron2009Fig3V2ScalarPdeLadderSmoke.java
  Degiron2009Fig3V2ScalarPdeCoupledSweep.java
  Degiron2009Fig3V2ModeAnalysisSu8Smoke.java
  run_config_*.json
  postprocess_degiron_fig3_v2.py
magnus/
  submit_degiron_fig3_v2.py
  submit_log.md
  job_ids.md
  failure_retry_record.md
  raw_logs/
results/
  ladder_smoke_neff.csv
  degiron-2009-fig3-v2-mode-su8-smoke-v2_neff.csv
  coupled_neff_sweep.csv
  fig3_reproduction_v2.png
  mode_profiles/
final_report.md
workflow_handoff_A_v2.md
```

## Current Job IDs

| Case | Run ID | Job ID | Physical meaning |
|---|---|---|---|
| scalar ladder smoke | `degiron-2009-fig3-v2-ladder-smoke-v6` | `f886f496f107e1b7` | Pipeline/scalar diagnostic only. |
| isolated SU-8 mode probe | `degiron-2009-fig3-v2-mode-su8-smoke-v2` | `0e64e432914254d7` | Reaches eigensolver, no physical mode rows. |
| scalar coupled sweep | `degiron-2009-fig3-v2-coupled-sweep-v1` | `f6c6748bf850a69f` | Scalar diagnostic sweep only. |
