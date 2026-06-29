---
name: optics-mie-reproduction
description: Mie theory analytical/semi-analytical scattering calculations for optics_agent — single sphere, metal LSPR, dielectric modes, core-shell, periodic arrays, binary arrays, effective medium. Use when the task involves Mie scattering, Lorenz-Mie coefficients, scattering/absorption/extinction cross sections, Drude dispersion LSPR, dielectric nanosphere magnetic dipole modes, core-shell recursive Mie, coupled dipole approximation (CDA), surface lattice resonances (SLR), Rayleigh anomaly, binary nanoparticle arrays, S-parameter retrieval effective medium, Maxwell-Garnett, Mie-vs-Bragg phase diagram, or building Python-only scattering benchmark data for later COMSOL validation. Also use when writing Mie physical verifiers (energy conservation, Rayleigh limit, large-size extinction paradox, optical theorem) or building Python-only scattering benchmark data for later COMSOL validation.
---

# Optics Mie Reproduction

## Purpose

Produce auditable, verifier-checked Mie scattering benchmark data in Python. No COMSOL. All output under `reproduction_test/mie/`. This is both a physics reproduction task and the low-cost benchmark for later workflow self-iteration experiments.

Authoritative human-facing plan: `reproduction_test/mie/mie_reproduction_plan-CN.md`. Task list for the executing agent: `reproduction_test/mie/todolist.md`. Papers in `papers/mie/`.

## Core Principle: How A Human Knows The AI Got It Right

Never judge success by eye against paper figures. Use 3 verification layers, easiest-first. Full detail in `references/verification.md`.

1. **Physical hard constraints** (parameter-independent, AI cannot fake): energy conservation $C_{ext}=C_{sca}+C_{abs}$, zero absorption when $\mathrm{Im}(\varepsilon)=0$, optical theorem $C_{ext}=\frac{4\pi}{k}\mathrm{Im}\,S(0)$, Rayleigh $Q_{sca}\propto x^4$, large-size $Q_{ext}\to2$, spherical symmetry.
2. **Known limits / degeneracies**: quasi-static LSPR $\mathrm{Re}(\varepsilon)=-2\varepsilon_d$, core-shell shell-thickness→∞ collapses to single sphere, array period→∞ collapses to single sphere, low-filling→Maxwell-Garnett.
3. **Quantitative paper-figure comparison**: RMSE, resonance peak error (nm), Q-factor relative error. "Looks similar" does not count.

## What To Trust Vs Not Trust About AI-Generated Work

**Trust AI (low risk, glance at result)**: PDF text extraction, formula OCR, special-function evaluation via `scipy.special` (trust scipy, not AI-generated special functions), code scaffolding, plotting templates, unit conversions, literature search.

**Do NOT trust AI (high risk, human must confirm)**:
- Final Mie coefficient expressions $a_n, b_n$ — the core 2-3 lines; AI frequently inverts numerator/denominator or drops the $n$ order. Verify against textbook (Bohren & Huffman or Kerker), not against the review paper alone.
- Boundary condition application (tangential vs normal continuity).
- Physical parameter selection — units (nm vs m), real/imaginary index, wavelength range. One order-of-magnitude unit error invalidates everything.
- "Success" declaration — AI tends to say "looks good". Never let AI self-declare success.
- Tolerance thresholds — the human sets "how much error passes", not the AI.
- Paper-figure comparison conclusions — read the quantitative numbers, not AI's "basically consistent".
- Promoting a single-case lesson to a general rule — single reproduction experience must NOT become a long-term skill without repeated evidence.

## Workflow Per Paper

1. **Read paper** — abstract, modeling section, target figure, caption, nearby text.
2. **Extract parameters** → `formalization/<case>.yaml` (human gate ①: units, ranges, indices).
3. **Physics formalization** → structured spec: geometry, materials, equations, boundary conditions, sources, solver, observables, assumptions, missing fields (human gate ②).
4. **Derive core formulas** — full derivation in `notes/<case>.md`; the Mie coefficient expressions $a_n,b_n$ are checked against a textbook, not the review paper (human gate ③).
5. **Implement** — `code/<case>.py` using `scipy.special` for spherical Bessel/Legendre. Write `tests/test_<case>.py` at the same time (TDD: physical constraints are hardcoded, code must satisfy tests).
6. **Run 3-layer verification** — physical hard constraints → known limits → quantitative paper comparison.
7. **Append to benchmark** — `data/benchmark.yaml` entry with parameters, expected values, tolerance, two-way agreement status.
8. **Human gate ④** — review quantitative comparison numbers; do not accept "looks similar".

## Required Artifacts Per Stage

```text
reproduction_test/mie/
  code/<case>.py
  tests/test_<case>.py
  formalization/<case>.yaml
  notes/<case>.md          # derivation, Markdown + PDF
  data/benchmark.yaml      # appended, never overwritten
  figs/<case>_<observable>.png
```

## 4 Human Gates (agent runs freely between them)

1. After parameter extraction — units, ranges, indices correct.
2. After physics formalization — structured spec matches the paper's physical problem.
3. After core formula derivation — $a_n,b_n$ verified against textbook.
4. After paper-figure comparison — quantitative error numbers reviewed.

## Skill Lifecycle (avoid Degiron lesson)

This skill starts as `status: candidate` covering only single-sphere Mie. Promote to `active` only after core-shell (stage 4) also passes — i.e., repeated evidence, not single-case. Every skill item carries `applies_when` / `does_not_apply_when` / `source_cases`.

## References (load when needed)

- `references/papers.md` — the 11-paper list with abstracts, reproduction points, verification criteria, and execution order.
- `references/verification.md` — 3-layer verification detail, verifier script usage, tolerance defaults.
- `references/benchmark_format.md` — `benchmark.yaml` schema and example entries.

## Scripts

- `scripts/check_energy_conservation.py` — verify $C_{ext}=C_{sca}+C_{abs}$ within 1e-10.
- `scripts/check_rayleigh_limit.py` — verify $Q_{sca}\propto x^4$ slope in log-log at small $x$.
- `scripts/check_large_size_limit.py` — verify $Q_{ext}\to2$ at large $x$.

Scripts import from `reproduction_test/mie/code/`; they fail with a clear message if the implementation is not yet present.

## Textbook Dependency

Core formulas (especially $a_n,b_n$) use a textbook as primary source:
- Bohren & Huffman, *Absorption and Scattering of Light by Small Particles* (preferred)
- Kerker, *The Scattering of Light* (fallback)

Review papers (Akimov etc.) are cross-checks, not the single source — reviews occasionally have typos.

## COMSOL Boundary

This skill is Python-only. When a task needs COMSOL/Magnus execution, switch to `optics-comsol-runtime` + `optics-comsol-batch` + `optics-magnus-platform`. The benchmark data produced here is the validation target for those COMSOL runs.
