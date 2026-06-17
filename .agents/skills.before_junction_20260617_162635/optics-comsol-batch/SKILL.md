---
name: optics-comsol-batch
description: COMSOL non-GUI/headless batch simulation for optics_agent. Use when the user mentions COMSOL, comsol batch, comsolbatch, headless simulation, .mph/.java/.m batch jobs, optics/fluid smoke tests, COMSOL license mounting, or Magnus COMSOL blueprint execution.
---

# Optics COMSOL Batch

## Preferred Backend

Use `comsol batch` inside the validated Magnus runtime image:

```text
docker://magnus-local/comsol-runtime:latest
```

This image is administrator-imported and must not be refreshed or replaced without explicit instruction.

## Blueprint And Runner

- Blueprint id: `Optics_COMSOL_Runtime_zyz`.
- Blueprint source: `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`.
- Official blueprint package: `.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml`.
- Private/public-staged runner:
  `/data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py`.
- Staged license:
  `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`.
- Validated solve license mount:
  `$HOME/.comsol-container-license:/opt/comsol-license`.
- Validated in-container license file:
  `/opt/comsol-license/license.dat`.
- Output root:
  `/home/magnus/data/optics_agent/comsol/runs`.

Default launch image:

```text
docker://magnus-local/comsol-runtime:latest
```

## Run Modes

The runner supports:

```text
env_check
batch_java
batch_mph
batch_mfile
```

For `env_check`, expect COMSOL version, `comsol batch -help`, Python dependency imports, and a `manifest.json`.

For batch modes, pass an input file:

```text
--input-file /home/magnus/data/optics_agent/comsol/papers/<case>/model.java
--input-file /home/magnus/data/optics_agent/comsol/papers/<case>/model.mph
--input-file /home/magnus/data/optics_agent/comsol/papers/<case>/model.m
```

## License Mount For Solves

The active `magnus-local` image solved real COMSOL cases with this host-to-container bind:

```text
$HOME/.comsol-container-license:/opt/comsol-license
```

Set license variables through `system_entry_command` with Apptainer env forwarding:

```bash
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
```

If using the private runner with `license_mode=personal_storage`, ensure the chosen `license_path` is under a mounted path such as `/data/public/...` or `/home/magnus/data/...`. For direct solve jobs, prefer the proven `/opt/comsol-license/license.dat` path and `license_mode=server_env`.

## Artifact Contract

Each run writes:

```text
/home/magnus/data/optics_agent/comsol/runs/<run_id>/
  manifest.json
  command.json
  env_report.json
  raw/
    model_output.mph
    comsol.log
    stdout.txt
    stderr.txt
  results/
    tables/
    figures/
  errors/
    failure.json
```

Failure codes include:

```text
COMSOL_NOT_FOUND
LICENSE_UNAVAILABLE
BATCH_EXIT_NONZERO
OUTPUT_MPH_MISSING
POSTPROCESS_FAILED
INPUT_MISSING
```

## Validated Magnus Jobs

Use these as known-good evidence:

```text
de368ea77db7da7f  smoke: COMSOL 6.3.0.290, batch help, Python imports
deb10848cb99128a  license-mounted solve
3681f26d40ccbf7b  L-shaped membrane eigenmode solve
```

Capability probe campaign `comsol-capability-20260613-v1` on `docker://magnus-local/comsol-runtime:latest`:

```text
f2c00784c24041eb  envcheck                 Success
6752b0d0afb11f7a  core-pde-eigenmode       Success
42ce2ba174d5b9a6  optics-helmholtz         Success
1d9a03b77815f140  wave-optics-probe        Success
a43412fc80ab0608  fluid-laminar-probe      Success
993a3c1a90b69429  fluid-pde-fallback       Success
```

The batch runner now compiles Java sources with `comsol compile` before `comsol batch`, then normalizes COMSOL's generated `*_Model.mph` file to `raw/model_output.mph` when needed. Future Java probes should print a `*_OK` marker to stdout; the runner records those markers in the manifest.

Earlier comparison jobs used `docker://simulation-runtime:latest`:
`973e8c9bd19298ad`, `909944d000b92a09`, `3cd1d9e8abac4115`.

## Common Commands

Save blueprint only:

```powershell
python comsol\automation\submit_comsol.py --save-only
```

Launch env check:

```powershell
python comsol\automation\submit_comsol.py --run-mode env_check --license-mode server_env --license-path /opt/comsol-license/license.dat --container-image docker://magnus-local/comsol-runtime:latest
```

Query job logs with Magnus SDK/CLI; do not mutate the image while diagnosing COMSOL batch behavior.
