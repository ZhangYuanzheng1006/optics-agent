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

## Recent Work (2026-06)

- **Agent skill & workflow self-iteration survey**: `notes/agent_skill_self_iteration/` — covers skill system design, self-improving agents, tool use, meta-cognition, SWE agents, framework comparison, and scientific computing agents.
- **Workflow engine design**: `notes/workflow_engine_design.md` — YAML-declared dual-agent (supervisor/worker) workflow system with MCP communication, branch routing, experience notes, and self-iteration.
- **Mie theory reproduction**: `reproduction_test/mie_internal_plan.md` — analytical Mie scattering models for sphere arrays, Python-only, 6-week plan covering single sphere → multilayer → arrays → effective medium.

Keep local development in:

```text
C:\Users\27370\Desktop\project\optics_agent
```

Canonical GitHub repository:

```text
https://github.com/PKU-QNO/optics-agent-zyz
```

Use Gustation/Magnus for containerized compute jobs.

## Skill Routing

| User intent | Load |
|---|---|
| Paper figure reproduction, parameter extraction, missing-info tables, optics-group standard answers, reproduction reports, self-iteration workflow lessons | `optics-paper-reproduction` |
| COMSOL runtime image, active `magnus-local` image, license mount, runtime folder, admin handoff | `optics-comsol-runtime` |
| COMSOL `batch`, `.java`, `.mph`, `.m`, smoke tests, manifest contract | `optics-comsol-batch` |
| COMSOL Java API syntax, GUI-exported Java, feature tags, study/solver syntax, results API, Java templates | `comsol-java-api` |
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

## Current Paper-Reproduction Status

Degiron 2009 Fig. 3 has two private rehearsal folders:

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/
```

Use them as workflow evidence, not as successful physical reproduction evidence:

- V1 proved paper reading, parameter extraction, Magnus submission, Java batch cleanup, stdout parsing, CSV/plot generation, and final reporting. Its final sweep is `surrogate_fallback`.
- V2 proved scalar TM-like PDE diagnostics and ran an isolated SU-8 Wave Optics/RF mode-analysis probe. The probe reached the eigensolver after explicit mesh construction but failed matrix factorization and produced zero physical `neff` rows.
- The current blocker is missing COMSOL 6.3 GUI-exported Wave Optics/RF mode-analysis physics/study/solver/result settings.

## Credentials

- Store credentials in `C:\Users\27370\Desktop\project\secret.json`.
- Do not hard-code tokens, registry passwords, SSH keys, or license content in repo files, blueprints, or skills.
- SSH target commonly used in this project:
  `zhangyuanzheng@Gustation`.

## Important Files

```text
AGENTS.md
CLAUDE.md
.codex/skills/
.claude/skills -> .codex/skills
.agents/skills -> .codex/skills
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
- Treat `AGENTS.md` as the always-on project rulebook. `CLAUDE.md` should be a hard link to `AGENTS.md`; if project rules change, update `AGENTS.md` and the relevant `.codex/skills/*/SKILL.md` together. `.codex/skills` is canonical; `.claude/skills` and `.agents/skills` should remain junctions to it.
- For long-running reproductions, keep the report state current enough that a PI-facing WeChat update can be generated from `final_report.md`, `workflow_handoff*.md`, and `todo.md` without rereading raw logs.
