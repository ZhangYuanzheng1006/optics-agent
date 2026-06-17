# optics_agent Agent Manual

This file is the always-on project rulebook for AI coding agents working in this repository. Treat it as the project-level AI README. It is stronger than ordinary notes and should be kept synchronized with project skills when conventions change.

## Project Identity

- Repository root: `C:\Users\27370\Desktop\project\optics_agent`
- Current branch: `main`
- Primary user environment: Windows + PowerShell, with SSH access to Gustation.
- Project role: local control workspace for optics_agent paper reproduction, COMSOL/Magnus runtime work, plasmonics notes, and reusable scientific-computing workflow design.

Long-term direction:

```text
paper reproduction
  -> reusable scientific blueprint
  -> case/DSL + parameter sweeps
  -> new scientific exploration
```

Paper reproduction is a regression test for blueprint iteration, not the final objective. Optics is the current use case; the workflow should generalize to unfamiliar scientific and engineering domains.

## Current Project Status

- COMSOL/Magnus runtime exists and is usable through the active Magnus image:

```text
docker://magnus-local/comsol-runtime:latest
```

- The active image was imported by the administrator. Do not refresh, pull, retag, rebuild, overwrite, or replace it unless the user explicitly asks.
- Runtime staging path:

```text
/data/public/zhangyuanzheng/comsol-runtime
```

- Validated COMSOL solve license mount inside the container:

```text
/opt/comsol-license/license.dat
```

- Canonical local COMSOL structure:

```text
comsol/runtime/
comsol/automation/
comsol/docker/
comsol/blueprints/source/
comsol/docs/
comsol/manifests/
```

- Official Magnus blueprint package:

```text
.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
```

- Degiron 2009 Fig. 3 reproduction rehearsals exist under:

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/
```

V1 completed the engineering workflow but not physical COMSOL full-vector reproduction; its final sweep is labelled `surrogate_fallback`. V2 completed a scalar TM-like PDE diagnostic sweep and an isolated SU-8 Wave Optics/RF mode-analysis probe. The v2 probe compiles, meshes, reaches the eigensolver, and saves `.mph`, but produces zero physical `neff` rows because the eigensolver fails matrix factorization. Do not present either v1 or v2 as a successful Fig. 3 paper reproduction.

## Root Layout

Expected high-level directories:

```text
.codex/
.claude/
.magnus/
comsol/
docs/
notes/
papers/
reproduction_test/
services/
```

Keep root clutter low. New COMSOL work should go under `comsol/`; paper-specific reproduction artifacts should go under `reproduction_test/private/<case>/`; notes should go under `notes/` or `docs/` by topic.

## Skill System

Project skills live in:

```text
.codex/skills/
```

Claude and Agents skills are synchronized by Windows junctions:

```text
.claude/skills -> .codex/skills
.agents/skills -> .codex/skills
```

Edit `.codex/skills` as the canonical path. Read the relevant `SKILL.md` completely before acting on a matching task.

Current routing:

| Task | Skill |
|---|---|
| Project routing, goals, credentials, important files | `optics-agent-core` |
| Paper figure reproduction, parameter tables, missing-info analysis, handoff reports | `optics-paper-reproduction` |
| COMSOL runtime image, active Magnus-local image, license mounts, runtime folder | `optics-comsol-runtime` |
| COMSOL batch/headless jobs, `.java`/`.mph`/`.m`, smoke cases, manifest contract | `optics-comsol-batch` |
| COMSOL Java API syntax, GUI-exported Java, feature/study/solver tags | `comsol-java-api` |
| Magnus/Gustation jobs, logs, blueprint save/launch, staging paths | `optics-magnus-platform` |
| Magnus artifact formats, `.magnus.yaml`, `.magnus.skill.yaml`, import/export packaging | `optics-magnus-artifacts` |
| Docker image build/push/archive/handoff, ACR/PKU registry, image size/hash | `optics-docker-images` |

If COMSOL and Magnus are both involved, load `optics-comsol-runtime` first, then `optics-magnus-platform`. If paper reproduction is involved, also load `optics-paper-reproduction`.

## AGENTS And Skill Update Policy

When project rules change, update the persistent rule surfaces in the same task:

1. Update `AGENTS.md` for always-on project policy.
2. Update the relevant `.codex/skills/*/SKILL.md` for task-specific procedural knowledge.
3. Validate changed skills with:

```powershell
python C:\Users\27370\.codex\skills\.system\skill-creator\scripts\quick_validate.py .codex\skills\<skill-name>
```

4. If the change affects Claude or Agents behavior, confirm `.claude/skills` and `.agents/skills` still point to `.codex/skills`.
5. Keep `CLAUDE.md` synchronized with `AGENTS.md`. In this repo, `CLAUDE.md` should be a hard link to `AGENTS.md`; do not replace it with divergent content.

If an editor or patch tool breaks the hard link, recreate it after merging content:

```powershell
Remove-Item -LiteralPath .\CLAUDE.md
New-Item -ItemType HardLink -Path .\CLAUDE.md -Target .\AGENTS.md
```

Only run the above after verifying both resolved paths are inside the repository.

## Progress Reporting Policy

For paper-reproduction or COMSOL/Magnus tasks that last beyond a smoke test, maintain a human-facing progress trail suitable for PI updates:

- Record stage status in the run folder as work proceeds, not only at the end.
- Keep `final_report.md` and `workflow_handoff*.md` current enough that a short WeChat status can be generated without reconstructing history from raw logs.
- Separate these states in every report and PI update:

```text
workflow/pipeline completed
COMSOL job completed
physical reproduction completed
```

- When a result is a scalar diagnostic, surrogate, fallback, or failed probe, say that directly.
- When progress stalls on missing human/domain input, state the exact requested artifact, for example a COMSOL 6.3 GUI-exported Wave Optics/RF mode-analysis `.java` or `.mph` template.
- For PI messages, prefer concise status plus current blocker plus concrete request from the optics group. Do not overstate numerical agreement.

## Safety Constraints

Never write or echo secret contents:

- `C:\Users\27370\Desktop\project\secret.json`
- SSH private keys under `C:\Users\27370\.ssh\`
- COMSOL license files
- Docker registry passwords
- Magnus tokens

It is acceptable to mention secret key names and non-secret mount paths, for example `/opt/comsol-license/license.dat`; it is not acceptable to copy the actual license or token contents.

Treat these as private or sensitive unless the user explicitly says otherwise:

```text
papers/private/
reproduction_test/private/
comsol-runtime/secrets/
```

Do not upload private PDFs, license files, SSH keys, or raw credentials to public paths or public registries.

High-risk operations:

- Do not run destructive git commands such as `git reset --hard` or `git checkout --` unless explicitly requested.
- Do not recursively delete or move directories without first resolving and verifying the absolute path is inside the intended workspace.
- Do not kill, resubmit, or duplicate Magnus jobs unless the user asks or the task plan explicitly requires it.
- Do not launch GPU jobs, A-class jobs, or jobs consuming more than half cluster CPU/memory without explicit review.
- Do not mutate the active COMSOL image unless explicitly requested.

## Magnus And COMSOL Rules

Credentials are stored in:

```text
C:\Users\27370\Desktop\project\secret.json
```

Prefer GU/Gustation keys when present:

```text
motif: magnus_address-gu, magnus_token-gu
```

Use SSH target:

```text
zhangyuanzheng@Gustation
```

Before submitting Magnus jobs:

1. Query existing jobs by `run_id`; reuse active or successful jobs.
2. Query cluster resources.
3. Keep `gpu_type=cpu`, `gpu_count=0` unless GPU is explicitly required.
4. Keep planned CPU and memory under half of cluster totals unless explicitly reviewed.

Default COMSOL smoke resources:

```text
gpu_type=cpu
gpu_count=0
cpu_count=8
memory_demand=32G
ephemeral_storage=40G-100G
job_type=B2
```

Real COMSOL solves on the active image require the license mount:

```text
$HOME/.comsol-container-license:/opt/comsol-license
```

Forward license variables into Apptainer with:

```bash
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
```

Use `/data/public/zhangyuanzheng` for public staging and admin handoff. Do not switch back to `/home/zhangyuanzheng` or registry-first delivery unless the user explicitly changes the deployment target.

## COMSOL Java And Paper Reproduction Lessons

Current COMSOL batch Java runs through official COMSOL Java API, but hand-written Java API calls are not automatically equivalent to a correct GUI-built model.

For current Magnus runtime Java:

- Provide `public static Model run()` and return a `Model`.
- Avoid `System.getenv`, `System.getProperty`, direct Java file IO inside `run()`, inner classes, and anonymous classes.
- Prefer GUI-exported Java templates for exact physics/study/solver tags.
- Treat generated `.mph` as necessary but insufficient; inspect stdout markers, metrics, result tables, and physical validation.

Distinguish these states:

```text
Magnus Success
  != COMSOL intended solve success
  != physical paper reproduction success
```

For paper reproduction, a fallback/surrogate result may validate the workflow but must never be reported as physical reproduction.

Degiron v1/v2 specific lessons:

- V1 proved the Magnus/COMSOL Java pipeline and stdout-to-CSV reporting, but its final plot was a `surrogate_fallback`.
- V2 proved a scalar TM-like PDE sweep can run, but its `Im(neff)` is effectively zero and no anticrossing is recovered; it is diagnostic only.
- V2 isolated SU-8 Wave Optics/RF mode-analysis reached the eigensolver after explicit mesh construction, then failed matrix factorization for multiple shift styles.
- The next meaningful technical input is a verified COMSOL 6.3 GUI-exported mode-analysis template; blind changes to Java feature strings or eigenvalue shifts should stop once isolated mode analysis fails.

## Development Practices

- Use `rg` / `rg --files` first for search.
- Use `apply_patch` for manual edits.
- Prefer scoped changes over broad refactors.
- Do not commit unless the user asks.
- Preserve user changes in a dirty worktree.
- Keep long plans, logs, and reports in Markdown files; keep chat summaries concise.

Common checks:

```powershell
python -m py_compile comsol\automation\*.py
python comsol\automation\submit_comsol.py --help
python C:\Users\27370\.codex\skills\.system\skill-creator\scripts\quick_validate.py .codex\skills\<skill-name>
```

PowerShell may not expand Python wildcards. If needed, expand file lists in PowerShell first and pass explicit paths to Python.
