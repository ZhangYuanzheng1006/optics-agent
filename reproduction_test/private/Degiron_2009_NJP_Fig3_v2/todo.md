# Degiron 2009 NJP Fig. 3 V2 TODO

Use this file as the durable execution state. Do not mix v2 job IDs or outputs with v1.

## Setup

- [x] Read updated `comsol-java-api` skill.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Skill now requires GUI-exported Java for version-sensitive Wave Optics mode-analysis details.

- [x] Read v1 reports and failure records.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: V1 completed workflow only; final sweep was `surrogate_fallback`, not physical reproduction.

- [x] Create isolated v2 folder.
  - status: done
  - job_id:
  - run_id:
  - output_dir: `reproduction_test/private/Degiron_2009_NJP_Fig3_v2/`
  - notes: No v2 jobs submitted yet.

## Rebaseline Paper And Parameters

- [x] Re-read local PDF text and figures for Fig. 3.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Rechecked text and rendered pages 3-6 under private v2 folder for visual inspection of Fig. 1(b), Fig. 2, and Fig. 3.

- [x] Write v2 `paper_notes.md`.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Written with scalar TM-like PDE route explicitly marked as approximation.

- [x] Write v2 `parameter_table.md`.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Includes geometry/material/sweep/validation targets.

- [x] Write v2 `assumptions_and_missing_info.md`.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Records missing GUI-exported full-vector template and scalar PDE approximation risks.

## COMSOL Template And Model

- [x] Locate or obtain COMSOL 6.3 GUI-exported Wave Optics mode-analysis Java template.
  - status: not found locally
  - job_id:
  - run_id:
  - output_dir:
  - notes: Repository search found no GUI-exported Wave Optics/RF mode-analysis Java template. Only a minimal frequency-domain `WaveOpticsProbe.java` exists.

- [x] If no template exists, write a minimal template-missing diagnostic note.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Recorded in `v1_experience_audit.md` and `assumptions_and_missing_info.md`; v2 proceeds with scalar PDE diagnostic.

- [x] Implement isolated SU-8 model.
  - status: diagnostic implemented, physical solve failed
  - job_id: `0e64e432914254d7`
  - run_id: `degiron-2009-fig3-v2-mode-su8-smoke-v2`
  - output_dir:
  - notes: `Degiron2009Fig3V2ModeAnalysisSu8Smoke.java` compiles and reaches the mode-analysis eigensolver after explicit mesh fix, but returns zero rows due matrix factorization failure.

- [ ] Implement isolated Au LR-SPP model.
  - status:
  - job_id:
  - run_id: `degiron-2009-fig3-v2-isolated-au-smoke-v1`
  - output_dir:
  - notes:

- [x] Implement coupled Au+SU8 model.
  - status: scalar approximation implemented, full-vector blocked
  - job_id: `f6c6748bf850a69f`
  - run_id: `degiron-2009-fig3-v2-coupled-sweep-v1`
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-coupled-sweep-v1`
  - notes: Coupled scalar TM-like PDE model produced a sweep; it is not physical Fig. 3 reproduction.

- [x] Implement v2 postprocess script.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: `comsol/postprocess_degiron_fig3_v2.py` parses stdout CSV markers and writes CSV/figure/metrics.

- [x] Implement v2 submitter with dedupe/resource checks.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: `magnus/submit_degiron_fig3_v2.py` defaults to ladder smoke only; resource and duplicate checks are built in.

## Static Checks

- [x] Check Java public class names match file names.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: Both Java files match public class names and contain OK/CSV markers.

- [x] `python -m py_compile` v2 Python scripts.
  - status: done
  - job_id:
  - run_id:
  - output_dir:
  - notes: `postprocess_degiron_fig3_v2.py` and `submit_degiron_fig3_v2.py` compile.

- [x] Dry-run submitter.
  - status: done
  - job_id:
  - run_id: `degiron-2009-fig3-v2-mode-su8-smoke-v2`
  - output_dir:
  - notes: Dry-run resource check passed with 8 CPU / 32G below half of cluster totals.

## Magnus Execution

- [x] Stage v2 files to `/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2`.
  - status: done
  - job_id:
  - run_id:
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2`
  - notes: Staged scalar Java files, isolated SU-8 mode-analysis probe, run configs, and postprocess script.

- [x] Submit isolated SU-8 smoke after dedupe/resource check.
  - status: done, physical rows absent
  - job_id: `0e64e432914254d7`
  - run_id: `degiron-2009-fig3-v2-mode-su8-smoke-v2`
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-mode-su8-smoke-v2`
  - notes: Platform Success and `.mph` saved. Mesh blocker fixed versus v1; eigensolver matrix factorization failed for `neff`, `beta`, and plain shifts.

- [x] Inspect isolated SU-8 output and classify physical plausibility.
  - status: failed physical validation
  - job_id: `0e64e432914254d7`
  - run_id: `degiron-2009-fig3-v2-mode-su8-smoke-v2`
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-mode-su8-smoke-v2`
  - notes: No mode rows. Full-vector path remains blocked without GUI-exported mode-analysis template.

- [ ] Submit isolated Au smoke only if SU-8 passes.
  - status:
  - job_id:
  - run_id: `degiron-2009-fig3-v2-isolated-au-smoke-v1`
  - output_dir:
  - notes:

- [ ] Inspect isolated Au output and classify physical plausibility.
  - status: partial
  - job_id: `f886f496f107e1b7`
  - run_id: `degiron-2009-fig3-v2-ladder-smoke-v6`
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-ladder-smoke-v6`
  - notes: Scalar PDE produced rows but does not recover expected loss scale; use only as approximation diagnostic.

- [ ] Submit coupled smoke only if both isolated models pass.
  - status: partial via ladder smoke
  - job_id: `f886f496f107e1b7`
  - run_id: `degiron-2009-fig3-v2-ladder-smoke-v6`
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-ladder-smoke-v6`
  - notes: Coupled scalar rows exist; physical quality is insufficient but enough to justify one diagnostic sweep.

- [x] Submit coupled sweep only if coupled smoke returns two physical branches.
  - status: submitted as scalar diagnostic, not physical acceptance
  - job_id: `f6c6748bf850a69f`
  - run_id: `degiron-2009-fig3-v2-coupled-sweep-v1`
  - output_dir: `/data/public/zhangyuanzheng/comsol-runtime/runs/degiron-2009-fig3-v2-coupled-sweep-v1`
  - notes: Kept as scalar diagnostic because no full-vector mode-analysis rows were available.

## Validation And Reports

- [x] Generate v2 CSV outputs.
  - status: done
  - job_id: `f6c6748bf850a69f`
  - run_id: `degiron-2009-fig3-v2-coupled-sweep-v1`
  - output_dir: `results/`
  - notes: `ladder_smoke_neff.csv`, `coupled_neff_sweep.csv`, and empty-header `degiron-2009-fig3-v2-mode-su8-smoke-v2_neff.csv` generated.

- [x] Generate `results/fig3_reproduction_v2.png`.
  - status: done
  - job_id: `f6c6748bf850a69f`
  - run_id: `degiron-2009-fig3-v2-coupled-sweep-v1`
  - output_dir: `results/fig3_reproduction_v2.png`
  - notes: Figure shows scalar PDE candidates only; no anticrossing and `Im(neff)` is zero.

- [x] Write `magnus/failure_retry_record.md`.
  - status: done
  - job_id:
  - run_id:
  - output_dir: `magnus/failure_retry_record.md`
  - notes: Includes mode-analysis smoke v1 mesh failure and v2 eigensolver failure.

- [x] Write `final_report.md`.
  - status: done
  - job_id:
  - run_id:
  - output_dir: `final_report.md`
  - notes: States that v2 is not a physical Fig. 3 reproduction.

- [x] Write `workflow_handoff_A_v2.md`.
  - status: done
  - job_id:
  - run_id:
  - output_dir: `workflow_handoff_A_v2.md`
  - notes: Emphasizes GUI-exported COMSOL 6.3 mode-analysis template as required next artifact.
