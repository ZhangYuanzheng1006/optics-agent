---
name: optics-magnus-platform
description: Magnus/Gustation HPC platform operations for optics_agent. Use when the user mentions Magnus, Gustation, blueprint save/launch, job status/logs, file transfer, FileSecret, MAGNUS_RESULT, MAGNUS_ACTION, mounts, /data/public/zhangyuanzheng staging, COMSOL runtime jobs, or resource settings.
---

# Optics Magnus Platform

## Connection

Use the Python `magnus` SDK and credentials from:

```text
C:\Users\27370\Desktop\project\secret.json
```

Prefer GU/Gustation keys when present:

```text
magnus_address-gu
magnus_token-gu
```

Do not hard-code tokens in code, docs, blueprints, or skills.

## COMSOL Runtime Blueprint

- Blueprint id: `Optics_COMSOL_Runtime_zyz`.
- Local blueprint source: `comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py`.
- Official blueprint package: `.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml`.
- Active image: `docker://magnus-local/comsol-runtime:latest`.
- Do not refresh or replace this image.
- Runtime folder on Gustation:
  `/data/public/zhangyuanzheng/comsol-runtime`.
- License:
  `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`.
- Output:
  `/home/magnus/data/optics_agent/comsol/runs`.

Save blueprint:

```powershell
python comsol\automation\submit_comsol.py --save-only
```

Launch env check:

```powershell
python comsol\automation\submit_comsol.py --run-mode env_check --license-mode server_env --license-path /opt/comsol-license/license.dat --container-image docker://magnus-local/comsol-runtime:latest
```

## Job Query Pattern

Use read-only calls for diagnosis:

```python
import magnus
magnus.configure(address=address, token=token)
job = magnus.get_job(job_id)
logs = magnus.get_job_logs(job_id, page=-1)
```

Do not launch large resource jobs, A-class jobs, or GPU jobs unless explicitly requested and reviewed.

## Resource Defaults

For COMSOL smoke/env checks:

```text
gpu_type=cpu
gpu_count=0
cpu_count=8
memory_demand=32G
ephemeral_storage=40G-100G
job_type=B2
```

Use `A2` or larger CPU/RAM only for explicit larger COMSOL solves.
Do not launch A-class jobs automatically; A-class work can preempt B-class jobs.

## Blueprint Authoring Rules

Use Magnus blueprints as small public interfaces:

- Define a function named `blueprint`.
- Use typed parameters; `typing.Annotated` metadata drives UI labels, descriptions, bounds, and choices.
- Call `submit_job(...)` inside the function body.
- Keep license files, tokens, long runner code, and private case files outside the blueprint.
- For `Optics_COMSOL_Runtime_zyz`, keep `namespace="Rise-AGI"` and `repo_name="magnus"`. `repo_name="optics-agent"` failed before container start with `Failed to clone repo: Failed to determine default branch`.

Useful UI mappings:

```text
bool -> switch
int/float -> number input
str -> text input
Literal[...] -> dropdown
FileSecret -> file upload
```

For COMSOL, prefer long-lived mounted storage for runtime code/license and use `FileSecret` only for temporary uploaded input bundles.

For platform artifact packaging details such as `.magnus.yaml`, `.magnus.skill.yaml`, raw `.magnus.py` sources, suffix conventions, and import/export wrappers, load `optics-magnus-artifacts`.

## Magnus File Flow

Use three file-flow layers:

```text
FileSecret  -> temporary file/directory transfer
mounts      -> long-lived data, license, runtime code, large outputs
SSH/SCP     -> platform-external admin handoff or manual staging
```

### FileSecret Inputs

Use `FileSecret` for temporary user-provided files or directories, such as case bundles, parameter cards, small data packs, and one-off input folders:

```python
CaseBundle = Annotated[FileSecret, {
    "placeholder": "114514-apple-banana-cat",
    "description": "Temporary case bundle uploaded through Magnus",
}]
```

SDK behavior:

- `launch_blueprint(...)` auto-uploads local paths for blueprint parameters typed `FileSecret`.
- Existing values starting with `magnus-secret:` pass through unchanged.
- Directories are archived as `.tar.gz`; `magnus receive` and `download_file(...)` extract them inside the job.
- Defaults are short-lived: commonly `expire_minutes=60` and `max_downloads=1`.

Inside a job, receive inputs with:

```bash
magnus receive "$CASE_SECRET" --output /tmp/case
```

or in Python:

```python
from magnus import download_file
download_file(case_secret, target_path="/tmp/case")
```

Do not use `FileSecret` for persistent COMSOL licenses, long-lived datasets, or large reusable model libraries.

### Repository Code Inputs

Use repo files for public scripts, templates, and stable runner code. Keep the blueprint small and call a real script from `entry_command`, for example:

```bash
export PYTHONPATH=$PWD
python3 scripts/run_case.py --case_secret "$CASE_SECRET" --target_path "$TARGET_PATH"
```

The job working directory is the cloned repo root:

```text
/magnus/workspace/repository
```

### Mount Inputs And Outputs

Use mounts for persistent data and large outputs. In `system_entry_command`, declare literal bash array entries so Magnus can parse Docker/local bind mounts:

```bash
mounts=(
  "/data/public/zhangyuanzheng:/data/public/zhangyuanzheng"
  "/home/magnus/data:/home/magnus/data"
  "$HOME/.comsol-container-license:/opt/comsol-license"
)
export APPTAINER_BIND="${APPTAINER_BIND:+$APPTAINER_BIND,}$(IFS=,; echo "${mounts[*]}")"
```

Important parser limits:

- Docker/local mode extracts only quoted strings inside `mounts=(...)`.
- It ignores arbitrary shell logic, `$PWD`, command substitution, and conditionals for bind discovery.
- It expands `$HOME` and `${HOME}` on the host side.
- Cluster/Apptainer mode uses `APPTAINER_BIND` and `APPTAINERENV_*`.

For environment variables that must enter Apptainer containers, set `APPTAINERENV_...` in `system_entry_command`. Plain `export ...` is fine inside `entry_command`, because that command runs inside the container.

### Runtime Workspace

Magnus jobs expose:

```text
/magnus                         -> $MAGNUS_HOME
/magnus/workspace               -> host bind mount
/magnus/workspace/repository    -> repo root / working directory
/magnus/workspace/.magnus_result -> $MAGNUS_RESULT
/magnus/workspace/.magnus_action -> $MAGNUS_ACTION
/magnus/workspace/metrics        -> $MAGNUS_METRICS_DIR
```

After completion, only protocol artifacts such as `slurm/`, `metrics/`, `.magnus_result`, and `.magnus_action` are kept. Do not leave important outputs only under `/magnus/workspace`; copy large or durable outputs to a persistent mount such as `/home/magnus/data/...`.

### Job Results

Use `$MAGNUS_RESULT` for small structured summaries:

```bash
printf '{"success": true, "output_dir": "/home/magnus/data/..."}\n' > "$MAGNUS_RESULT"
```

Prefer JSON with at least:

```text
success
message
run_id
output_dir
manifest_path
```

### Downloadable Outputs

Use `magnus custody` to upload a result file/folder to file custody, then write exactly one receive command to `$MAGNUS_ACTION`:

```bash
SECRET=$(magnus custody "$OUTDIR" --expire-minutes 120 --max-downloads 5 | grep -o 'magnus-secret:[^ ]*')
echo "magnus receive $SECRET --output '$TARGET_PATH'" > "$MAGNUS_ACTION"
```

Keep `$MAGNUS_ACTION` simple. Web UI only supports allowlisted `magnus receive <secret> [--output path]` actions and will not execute arbitrary shell.

For large or long-lived results, write to a mounted persistent directory and put the path in `$MAGNUS_RESULT`; use `$MAGNUS_ACTION` only as an optional convenience download.

### External SSH/SCP

Use SSH/SCP/rsync outside Magnus for administrator handoff, image archives, or manual staging:

```bash
scp -r local_folder zhangyuanzheng@Gustation:/data/public/zhangyuanzheng/
rsync -av local_folder/ zhangyuanzheng@Gustation:/data/public/zhangyuanzheng/local_folder/
```

Running SSH from inside a job is possible only when the image has the tools, network access works, and credentials are provided through a private mount or short-lived secret. Do not put SSH keys or tokens in blueprints, images, logs, or skills.

## Job Lifecycle Diagnostics

Interpret Magnus jobs by state:

```text
Preparing -> Pending -> Queued -> Running -> Success / Failed
Paused
Terminated
```

- `Preparing`: image pull/import, code clone, mount setup, or workdir preparation.
- `Pending`: resources are prepared and the job is ready to submit to SLURM/Docker.
- `Queued`: backend accepted the job; inspect resources, priority, and queue pressure.
- `Running`: inspect runner logs, license state, exit code, and output contract.
- `Success`: may depend on the job writing a `.magnus_success` marker.
- `Paused`: usually preempted; can return to `Preparing` after resources are released.
- `Terminated`: user-cancel path; if a backend id still exists, resources may still be releasing.

Priority order is:

```text
A1 > A2 > B1 > B2
```

A-class jobs can preempt B-class jobs. COMSOL smoke tests should remain `B2`; use higher priority only when the user explicitly asks and the resource impact is reviewed.

## Image And Storage Model

- Magnus `Image` is Docker-like in local mode and Apptainer `.sif`-like in cluster mode.
- Cluster jobs run isolated with temporary writable storage; do not assume container writes persist unless mounted/output paths are explicit.
- Image cache can be evicted by LRU, so image-related failures may be cache/import problems rather than Dockerfile problems.
- File custody uses token-addressed uploaded files and job artifacts with TTL; do not rely on temporary file tokens for persistent COMSOL licenses.
- SDK/agent auth uses trust tokens; Web auth uses JWT. Keep credentials in `secret.json`, not in blueprints or skills.

## Known COMSOL Jobs

Active `magnus-local` image:

```text
de368ea77db7da7f  comsol-smoke-minimal                  Success
deb10848cb99128a  comsol-universal-licensemount-solve   Success
3681f26d40ccbf7b  comsol-Lmembrane-eigenmodes           Success
f1442f2403e37150  updated blueprint env_check            Success
```

Earlier comparison image `docker://simulation-runtime:latest`:

```text
973e8c9bd19298ad
909944d000b92a09
3cd1d9e8abac4115
```

## Mounts For COMSOL Blueprint

Use mounts according to the job type:

- Image smoke only: no persistent data mount is required.
- Runner/env-check jobs: bind runtime code and output storage.
- Real COMSOL solves on the active `magnus-local` image: also bind the administrator-provided license directory to `/opt/comsol-license`.

Proven data mounts:

```text
/data/public/zhangyuanzheng:/data/public/zhangyuanzheng
/home/magnus/data:/home/magnus/data
```

Proven license mount for active-image solve jobs:

```text
$HOME/.comsol-container-license:/opt/comsol-license
```

Recommended combined `system_entry_command`:

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

Use `APPTAINERENV_` in `system_entry_command`; plain `export LM_LICENSE_FILE=...` there may stay outside the container. Plain exports are fine inside `entry_command`, because that command runs inside the container.

`/home/zhangyuanzheng` is not the current runtime target for COMSOL; use `/data/public/zhangyuanzheng`.

## Public Staging Directory

Admin handoff files live at:

```text
/data/public/zhangyuanzheng/
  README.md
  Optics_COMSOL_Runtime_zyz.magnus
  comsol/manifests/comsol-runtime-image-manifest.json
  comsol_blueprint_runtime_plan.md
  comsol/runtime/
```
