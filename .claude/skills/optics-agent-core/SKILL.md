---
name: optics-agent-core
description: Core index for the optics_agent project. Use when the user mentions project structure, workflow, credentials, SSH, GitHub, Magnus, Docker, COMSOL, blueprints, or asks which project-local skill should handle a task.
---

# Optics Agent Core

## Project Goal

Build an automation workflow for frontier optics paper reproduction:

```text
paper -> theory notes -> numerical implementation -> Magnus/COMSOL runs -> artifacts
```

Treat paper reproduction as regression tests for reusable scientific-computing blueprints, not as the endpoint. The longer arc is:

```text
paper reproduction -> reusable blueprint -> case/DSL -> parameter sweeps -> new scientific exploration
```

Group-meeting direction:

- Treat optics as the current funding/use-case entry point, not the project boundary; AI should transfer to unfamiliar scientific and engineering domains.
- Build general blueprints that expose sweepable mathematical, physical, numerical, and compute parameters.
- Aim for one complete blueprint to cover multiple paper reproductions and then support new-case exploration.
- Develop a small case/DSL layer so papers, parameters, sweeps, metrics, resources, and failures are machine-readable instead of scattered across scripts and notes.

Keep local development in:

```text
C:\Users\27370\Desktop\project\optics_agent
```

Use Gustation/Magnus for containerized compute jobs.

## Skill Routing

| User intent | Load |
|---|---|
| Paper figure reproduction, parameter extraction, missing-info tables, optics-group standard answers, reproduction reports, self-iteration workflow lessons | `optics-paper-reproduction` |
| COMSOL runtime image, active `magnus-local` image, license mount, runtime folder, admin handoff | `optics-comsol-runtime` |
| COMSOL `batch`, `.java`, `.mph`, `.m`, smoke tests, manifest contract | `optics-comsol-batch` |
| Magnus jobs, logs, blueprint save/launch, FileSecret, MAGNUS_RESULT/ACTION, mounts, `/data/public/zhangyuanzheng` staging | `optics-magnus-platform` |
| Magnus artifact formats, `.magnus.yaml`, `.magnus.skill.yaml`, blueprint/skill import-export packaging, suffix conventions | `optics-magnus-artifacts` |
| Docker images, archive, ACR, PKU registry, image size/hash | `optics-docker-images` |
| Creating or updating project skills | `skill-creator` |

When COMSOL and Magnus are both mentioned, load `optics-comsol-runtime` first, then `optics-magnus-platform`.

## Current COMSOL Runtime Facts

- Active image: `docker://magnus-local/comsol-runtime:latest`.
- Image was administrator-imported and is about `1.38G`.
- Do not refresh, pull, overwrite, retag, rebuild, or replace it unless explicitly requested.
- Runtime folder:
  `/data/public/zhangyuanzheng/comsol-runtime`.
- License:
  `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`.
- Output root:
  `/home/magnus/data/optics_agent/comsol/runs`.
- Blueprint id:
  `Optics_COMSOL_Runtime_zyz`.

## Credentials

- Store credentials in `C:\Users\27370\Desktop\project\secret.json`.
- Do not hard-code tokens, registry passwords, SSH keys, or license content in repo files, blueprints, or skills.
- SSH target commonly used in this project:
  `zhangyuanzheng@Gustation`.

## Important Files

```text
comsol/runtime/
comsol/automation/submit_comsol.py
comsol/automation/sync_comsol_runtime_to_gustation.py
comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
comsol/docs/admin/COMSOL_ADMIN_README.md
comsol/manifests/comsol-runtime-image-manifest.json
comsol/docs/plans/comsol_blueprint_runtime_plan.md
docs/magnus/magnus_ai4s_0604_useful_notes.md
```

## Working Rules

- Prefer read-only Magnus queries for diagnosis unless the user asks to launch or change jobs.
- Never mutate the active COMSOL image accidentally.
- Use `python comsol\automation\submit_comsol.py --save-only` after changing the COMSOL blueprint.
- For Magnus file flow, prefer: temporary user files via `FileSecret`, persistent code/license/results via mounts, admin handoff via SSH/SCP to `/data/public/zhangyuanzheng`.
- Keep long logs and plans in Markdown files; summarize only the high-signal lines to the user.
