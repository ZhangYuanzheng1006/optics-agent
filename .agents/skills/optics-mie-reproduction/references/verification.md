# Mie Verification — 3 Layers

Never judge success by eye against paper figures. Run the 3 layers easiest-first. A stage passes only when all applicable layers pass.

## Layer 1 — Physical Hard Constraints (parameter-independent)

These hold for any parameters; AI cannot fake them; a human without Mie knowledge can judge them because they are common-sense physics.

| # | Constraint | Check | Tolerance |
|---|---|---|---|
| 1.1 | Energy conservation | $C_{ext}=C_{sca}+C_{abs}$ | $10^{-10}$ relative |
| 1.2 | Zero absorption when lossless | $\mathrm{Im}(\varepsilon)=0 \Rightarrow C_{abs}=0$ | $10^{-12}$ |
| 1.3 | Optical theorem | $C_{ext}=\frac{4\pi}{k}\mathrm{Im}\,S(0)$ | $10^{-8}$ relative |
| 1.4 | Rayleigh limit | $Q_{sca}\propto x^4$ as $x\to0$ | log-log slope $=4\pm0.01$ |
| 1.5 | Large-size extinction paradox | $Q_{ext}\to2$ as $x\to\infty$ | $\|Q_{ext}-2\|<0.05$ for $x>50$ |
| 1.6 | Spherical symmetry | scattering independent of incident polarization | exact |

Layer 1 passing only means "no big mistake"; it does NOT certify numerical accuracy. Layers 2-3 are still required.

## Layer 2 — Known Limits / Degeneracies

| # | Limit | Expected behavior |
|---|---|---|
| 2.1 | Metal sphere quasi-static LSPR | $\mathrm{Re}(\varepsilon)=-2\varepsilon_d$ (textbook formula) |
| 2.2 | Core-shell shell-thickness→∞ | collapses to single sphere of core material |
| 2.3 | Core-shell core→0 | collapses to single sphere of shell material |
| 2.4 | Array period→∞ | collapses to single-sphere result |
| 2.5 | Low filling fraction | effective parameters → Maxwell-Garnett formula |

These are "known-answer limits". A mismatch signals a structural implementation error.

## Layer 3 — Quantitative Paper-Figure Comparison

Not "overlay and eyeball". Compute numeric metrics:

| Metric | Default tolerance |
|---|---|
| Curve RMSE vs digitized paper curve | $<5\%$ of peak value |
| Resonance peak wavelength error | $<5$ nm (visible) or $<1\%$ (IR) |
| Q-factor relative error | $<10\%$ |
| Peak amplitude relative error | $<10\%$ |

Tolerances are written into `data/benchmark.yaml` per case. The human sets tolerances, not the AI.

Report must distinguish "visual overlay consistent" from "within quantitative tolerance" — the former does not count as passing.

## Verifier Scripts

All scripts live in `scripts/` and import from `reproduction_test/mie/code/`. They fail with a clear message if the implementation is not yet present.

- `check_energy_conservation.py` — Layer 1.1, sweeps a parameter range and reports max relative error.
- `check_rayleigh_limit.py` — Layer 1.4, fits log-log slope at small $x$.
- `check_large_size_limit.py` — Layer 1.5, checks $Q_{ext}$ at large $x$.

Each script exits 0 on PASS, non-zero on FAIL, and prints a one-line verdict plus the numeric evidence.

## The 30-Minute Human Check Per Paper

1. Run 3 physical verifier scripts (auto, 5 min) — all must pass.
2. Verify core formula 2-3 lines against textbook (human, 10 min) — the most critical 10 minutes.
3. Quantitative paper-figure comparison (auto + human, 5 min) — read RMSE and peak-error numbers.
4. Physical intuition check (human, 5 min) — is the peak where it should be? Is the shape right?

Steps 2 and 4 are irreplaceable human work. Steps 1, 3 are automated but the human reads the results.
