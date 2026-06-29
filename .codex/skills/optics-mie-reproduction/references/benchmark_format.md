# benchmark.yaml Format

`reproduction_test/mie/data/benchmark.yaml` is the frozen standard-answer file. Start it at stage 1 and append per stage — never overwrite. This file is the validation target for later COMSOL runs and the reward signal for workflow self-iteration experiments.

## Schema

```yaml
version: 1
last_updated: <YYYY-MM-DD>
cases:
  - case_id: <string>          # e.g. akimov_single_sphere_n1p5
    stage: <int>               # 1-7
    paper: <string>            # short name, e.g. Akimov
    figure_ref: <string>       # paper figure identifier
    parameters:
      geometry:                # radius, layer stack, etc.
      materials:               # wavelength range, complex permittivity, dispersion source
      environment:             # background index
    expected:
      observable: <string>     # e.g. Q_sca, C_ext, LSPR_wavelength, n_eff
      values:                  # list of (param, expected_value) points
        - point: {x: 0.1}
          value: 0.0009
        - point: {x: 1.0}
          value: 0.21
      trends:                  # qualitative trends to check
        - "Q_sca proportional to x^4 at small x"
        - "Q_ext approaches 2 at large x"
    tolerance:
      cross_section_relative: 1.0e-6
      peak_wavelength_nm: 5
      q_factor_relative: 0.10
      rmse_peak_fraction: 0.05
    provenance:
      our_impl:                # values from our code
      paper_figure:            # values digitized from paper
    two_way_agreement: <pass|partial|fail|pending>
    verifier_results:
      energy_conservation: <pass|fail>
      rayleigh_limit: <pass|fail>
      large_size_limit: <pass|fail|na>
    human_gate_4: <pass|fail|pending>   # human reviewed quantitative comparison
    notes: <string>            # caveats, simplifications, missing info
```

## Example Entry (stage 1, placeholder until implementation runs)

```yaml
cases:
  - case_id: akimov_single_sphere_n1p5
    stage: 1
    paper: Akimov
    figure_ref: "Fig. Q_sca(x)"
    parameters:
      geometry: {sphere_radius_m: 1.0e-6}
      materials: {sphere_index: 1.5, background_index: 1.0, loss_imag: 0.0}
      environment: {wavelength_range_m: [0.1e-6, 30e-6]}
    expected:
      observable: Q_sca
      values:
        - point: {x: 0.1}
          value: 0.0009
        - point: {x: 1.0}
          value: 0.21
      trends:
        - "Q_sca proportional to x^4 at small x"
        - "Q_ext approaches 2 at large x"
    tolerance:
      cross_section_relative: 1.0e-6
      peak_wavelength_nm: 5
      q_factor_relative: 0.10
      rmse_peak_fraction: 0.05
    provenance:
      our_impl: pending
      paper_figure: pending
    two_way_agreement: pending
    verifier_results:
      energy_conservation: pending
      rayleigh_limit: pending
      large_size_limit: pending
    human_gate_4: pending
    notes: "Stage 1 baseline; values to be filled after implementation."
```

## Rules

- Append-only within a case; never overwrite a frozen value. If a value is corrected, add a new case_id suffix `_v2` and mark the old one `superseded_by`.
- `two_way_agreement` becomes `pass` only when our impl and the paper figure agree within tolerance. `partial` means they disagree — investigate, do not proceed.
- `human_gate_4` is set by the human after reviewing quantitative numbers, never by the AI.
- Tolerances are set by the human, not auto-derived from the implementation.
