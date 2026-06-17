---
name: optics-comsol-runtime
description: COMSOL 6.3 headless runtime on Magnus/Gustation. Use when the user mentions COMSOL runtime images, magnus-local/comsol-runtime, Optics_COMSOL_Runtime_zyz, COMSOL license mounting, /data/public/zhangyuanzheng staging, or asks to run/check/submit COMSOL jobs through Magnus.
---

# Optics COMSOL Runtime

## Current State

- Active Magnus image: `docker://magnus-local/comsol-runtime:latest`.
- Reported image size: about `1.38G`.
- This image was imported/built by the administrator through a route different from the original archive plan.
- Do not refresh, pull, overwrite, retag, rebuild, or replace this image unless the administrator explicitly asks.
- Original archive remains only for provenance/fallback:
  `/data/public/zhangyuanzheng/comsol-runtime-6.3-zyz-v1.docker.tar`.
- Treat COMSOL as the current simulation backend for blueprint iteration; the larger project target is reusable scientific blueprints, sweeps, case/DSL, and new discovery beyond optics.

## Runtime Paths

- Public staging root: `/data/public/zhangyuanzheng`.
- Runtime folder: `/data/public/zhangyuanzheng/comsol-runtime`.
- Runner: `/data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py`.
- Staged license path: `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`.
- Validated in-container license path for solves: `/opt/comsol-license/license.dat`.
- Job output root: `/home/magnus/data/optics_agent/comsol/runs`.
- Blueprint source: `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`.
- Official blueprint package: `.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml`.
- Blueprint id: `Optics_COMSOL_Runtime_zyz`.

The blueprint mounts:

```text
/data/public/zhangyuanzheng:/data/public/zhangyuanzheng
/home/magnus/data:/home/magnus/data
```

For actual COMSOL solves on the active image, also mount the administrator-provided license directory:

```text
$HOME/.comsol-container-license:/opt/comsol-license
```

Use `APPTAINERENV_` variables in `system_entry_command` so the license variables enter the container:

```bash
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
```

## Verified Entry Command Patterns

Known job evidence:

```text
973e8c9bd19298ad  simulation-runtime smoke: no data mount; comsol -version / batch -help / imports
909944d000b92a09  simulation-runtime runner env_check: mounted /data/public and /home/magnus/data
3cd1d9e8abac4115  simulation-runtime real solve: mounted /data/public and /home/magnus/data, license path under /home/magnus/data
de368ea77db7da7f  magnus-local smoke: no data mount; comsol -version / batch -help / imports
deb10848cb99128a  magnus-local real solve: mounted $HOME/.comsol-container-license -> /opt/comsol-license
3681f26d40ccbf7b  magnus-local eigenmodes solve: mounted $HOME/.comsol-container-license -> /opt/comsol-license
```

Minimal smoke command for image health:

```bash
set -e
comsol -version
comsol batch -help >/dev/null 2>&1 && echo batch_help_ok
python3 -c "import numpy,scipy,pandas,matplotlib,h5py,meshio,mph,jpype; print('imports_ok')"
echo COMSOL_SMOKE_OK | tee "$MAGNUS_RESULT"
```

Minimal system command for image health:

```bash
export MAGNUS_HOME=/magnus
unset VIRTUAL_ENV SSL_CERT_FILE
```

Recommended combined `system_entry_command` for future COMSOL blueprint jobs:

```bash
mounts=(
  "/data/public/zhangyuanzheng:/data/public/zhangyuanzheng"
  "/home/magnus/data:/home/magnus/data"
  "$HOME/.comsol-container-license:/opt/comsol-license"
)
export APPTAINER_BIND="${APPTAINER_BIND:+$APPTAINER_BIND,}$(IFS=,; echo "${mounts[*]}")"
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
export MAGNUS_HOME=/magnus
mkdir -p /home/magnus/data 2>/dev/null || true
unset VIRTUAL_ENV SSL_CERT_FILE
```

Use `$MAGNUS_HOME/workspace/...` for temporary model generation and `/home/magnus/data/...` for persistent artifacts.

## COMSOL File Flow

Use a small public blueprint and keep private or heavy files outside it.

Recommended input layers:

```text
runtime code       -> /data/public/zhangyuanzheng/comsol-runtime
temporary cases    -> FileSecret, received into $MAGNUS_HOME/workspace or /tmp
persistent cases   -> mounted /data/public/zhangyuanzheng/... or /home/magnus/data/...
license            -> /opt/comsol-license/license.dat through mount/env
```

Use `FileSecret` only for one-off user case bundles such as `.mph`, `.java`, `.m`, mesh/data packs, or sweep config archives. Receive them with `magnus receive` or `magnus.download_file(...)`, then run through `comsol_runner.py`.

Do not use `FileSecret` for the COMSOL license. Use the administrator-provided license mount:

```text
$HOME/.comsol-container-license:/opt/comsol-license
LM_LICENSE_FILE=/opt/comsol-license/license.dat
COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
```

Recommended output contract:

```text
/home/magnus/data/optics_agent/comsol/runs/<run_id>/
  manifest.json
  logs/
  results/
  figures/
```

Write a compact JSON summary to `$MAGNUS_RESULT` with:

```text
success
message
run_id
output_dir
manifest_path
comsol_version
license_status
```

If the user needs a local download, optionally run `magnus custody <output_dir>` and write a single `magnus receive <secret> --output <target>` command to `$MAGNUS_ACTION`. Keep durable COMSOL results on `/home/magnus/data` even when using `MAGNUS_ACTION`.

## Validated Jobs

Use these as evidence before changing anything:

| Job ID | Task | Image | Status | Evidence |
|---|---|---|---|---|
| `de368ea77db7da7f` | `comsol-smoke-minimal` | `docker://magnus-local/comsol-runtime:latest` | Success | COMSOL 6.3.0.290, batch help, imports |
| `deb10848cb99128a` | `comsol-universal-licensemount-solve` | `docker://magnus-local/comsol-runtime:latest` | Success | license mount solve |
| `3681f26d40ccbf7b` | `comsol-Lmembrane-eigenmodes` | `docker://magnus-local/comsol-runtime:latest` | Success | L-shaped membrane eigenmodes |
| `f1442f2403e37150` | `COMSOL-blueprint-envcheck-20260613-170818` | `docker://magnus-local/comsol-runtime:latest` | Success | updated blueprint, `server_env`, `/opt/comsol-license`, manifest output |

Capability probe campaign `comsol-capability-20260613-v1`:

| Job ID | Probe | Status | Evidence |
|---|---|---|---|
| `f2c00784c24041eb` | `envcheck` | Success | COMSOL 6.3.0.290, `comsol batch`, Python imports, license env |
| `6752b0d0afb11f7a` | `core-pde-eigenmode` | Success | Java compiled, generic Coefficient Form PDE eigenmode solved, `.mph` output |
| `42ce2ba174d5b9a6` | `optics-helmholtz` | Success | scalar Helmholtz-like optics field solve through core PDE tools |
| `1d9a03b77815f140` | `wave-optics-probe` | Success | minimal electromagnetic Wave Optics/RF-style Java API probe solved |
| `a43412fc80ab0608` | `fluid-laminar-probe` | Success | minimal Laminar Flow/Creeping Flow-style Java API probe solved |
| `993a3c1a90b69429` | `fluid-pde-fallback` | Success | flow-like scalar PDE fallback solved through core PDE tools |

Interpretation: the image supports headless COMSOL 6.3, batch Java API runs, generic PDE/eigenmode solves, a minimal scalar optics field solve, and minimal professional electromagnetic and fluid interface probes. These are smoke tests, not proof that large production Wave Optics/CFD models are already validated.

Earlier comparison jobs used `docker://simulation-runtime:latest`, not the active image:
`973e8c9bd19298ad`, `909944d000b92a09`, `3cd1d9e8abac4115`.

## Safe Workflow

1. For status checks, query Magnus jobs/logs only. Do not run Docker image mutation commands.
2. For blueprint updates, edit `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`, then save/package with:

```powershell
python comsol\automation\submit_comsol.py --save-only
```

3. For runtime code updates, upload only files under `comsol/runtime/` to:

```text
/data/public/zhangyuanzheng/comsol-runtime
```

4. Preserve license privacy:

```bash
chmod 700 /data/public/zhangyuanzheng/comsol-runtime/secrets
chmod 700 /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol
chmod 600 /data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat
```

The blueprint `submit_job(...)` should keep `repo_name="magnus"` and `namespace="Rise-AGI"` for these runtime jobs. A test with `repo_name="optics-agent"` failed before container start with `Failed to clone repo: Failed to determine default branch`.

## Launch Defaults

Use these defaults unless the user says otherwise:

```text
container_image=docker://magnus-local/comsol-runtime:latest
code_root=/data/public/zhangyuanzheng/comsol-runtime
license_mode=server_env
license_path=/opt/comsol-license/license.dat
output_root=/home/magnus/data/optics_agent/comsol/runs
gpu_type=cpu
gpu_count=0
job_type=B2
```

Example env check:

```powershell
python comsol\automation\submit_comsol.py --run-mode env_check --license-mode server_env --license-path /opt/comsol-license/license.dat --container-image docker://magnus-local/comsol-runtime:latest
```

## Artifacts

- Admin README: `comsol/docs/admin/COMSOL_ADMIN_README.md`.
- Public admin README: `/data/public/zhangyuanzheng/README.md`.
- Image manifest: `comsol/manifests/comsol-runtime-image-manifest.json`.
- Full plan: `comsol/docs/plans/comsol_blueprint_runtime_plan.md`.
