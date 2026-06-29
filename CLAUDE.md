# optics_agent Agent Manual

This file is the always-on project rulebook for AI coding agents working in this repository. Treat it as the project-level AI README. It is stronger than ordinary notes and should be kept synchronized with project skills when conventions change.

## Project Identity

- Repository root: `C:\Users\27370\Desktop\project\optics_agent`
- Canonical GitHub repository: `https://github.com/PKU-QNO/optics-agent-zyz`
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

## SEPR Sister Workspace

- **SEPR** (self-evo-paper-repro, `C:\Users\27370\Desktop\project\self-evo-paper-repro`) is optics_agent's sister workspace for paper reproduction + skill/blueprint self-evolution experiments.
- Isolates self-evolution context from optics_agent's coding-and-production context.
- Uses Claude Code 3-layer sub-agents (main-agent → sub-agent → sub-sub-agent) instead of workflow state machines.
- `.human/` = Chinese human-review drafts; `.claude/` = English prompt-engineered execution versions.
- 4-agent architecture: Reproduction (main-agent + sub-agent, 10 steps) + Self-evolution (evolution-agent + sub-E-agent, 5 steps).
- Mie Phase 1 infrastructure runs in SEPR; code shares `reproduction_test/mie/` via junction.

## Current Project Status

- **Mie theory analytical reproduction** (new, 2026-06): Infrastructure built in SEPR workspace. Verification: 4-layer → 3-layer — PyMieScatt deprecated, physical hard constraints + Rayleigh/large-size limit degradation + paper figure quantitative comparison retained, two-party consistency. 11 reference papers in `papers/mie/` (mirrored in `.paper/mie/`). Textbook PDFs (Bohren & Huffman / Kerker) pending — core formulas from primary textbooks. Complete plan in `reproduction_test/mie/mie_reproduction_plan-CN.md` + skill `optics-mie-reproduction` + todolist. **Blocker**: awaiting user textbook confirmation before Phase 1.
- **Agent skill & workflow self-iteration survey** completed. See `notes/agent_skill_self_iteration/`.
- **Workflow engine design** (v2) in progress. Canonical: `notes/workflow_v2_plan-CN.md` (+ `notes/project_flow_plan-CN.md`, `notes/workflow_v2_risks-CN.md`). The v1 self-evolving-DSL design is archived under `project/to-do-future/DSL/` and is no longer the active plan.
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
workflows/              <-- 工作流定义、prompt 文件、状态文件
```

Keep root clutter low. New COMSOL work should go under `comsol/`; paper-specific reproduction artifacts should go under `reproduction_test/private/<case>/`; notes should go under `notes/` or `docs/` by topic.

## Workflow System

optics_agent 用 YAML 定义的**固定拓扑**工作流编排论文复现。当前为 v2（简化版）；v1 的"可自迭代拓扑"声明式 DSL 已废弃（自由度过高导致风险爆炸，见 commit `bc3b5b6` 的风险报告）。

权威设计文档（细节在 `notes/`，本文件只保留不可违反的原则）：

```text
notes/workflow_v2_plan-CN.md      工作 workflow + 自迭代 workflow（已归档；SEPR 用子 agent 替代 workflow 状态机）
notes/workflow_v2_risks-CN.md     v2 风险清单
notes/project_flow_plan-CN.md     项目状态树版本控制（project-flow）
project/to-do-future/DSL/         v1 可变拓扑 DSL（已归档，远期）
```

### 不可违反的架构原则

1. **拓扑写死，人工管**。workflow 拓扑由人工编写的固定 YAML 定义。agent 不得自动改拓扑、节点指令或分支条件。学长意见：小成本项目（不是扫几十万篇文献）不需要也不能有可变拓扑的自由度。
2. **只有智能断点用 agent**。能用确定性脚本做的（物理通用检查、导出、schema 校验）必须写死成脚本，不用 agent。每个 agent 节点要能回答"为什么脚本不能做"。
3. **无 supervisor/worker 双对话**。不采用"主管 agent + 工作 agent 两条独立长对话互相中继"的架构。改为：固定脊柱 + 节点内 agent 自由调子 agent。多目标复现（如 Fig2+Fig3 无关）= 在同一固定拓扑的节点内并发多个子 agent，拓扑不变。
4. **自迭代只碰经验层**。自迭代只更新 skill 内容 + 提示词备注，全部走 human gate；绝不改 workflow 拓扑、蓝图结构、`AGENTS.md`、或自迭代系统自身。
5. **自迭代不迭代自己**。自迭代 workflow 的拓扑、节点指令、专用 SKILL 人工写死，禁止自我修改。
6. **核心卖点 = 垂域可验证效果**。光学复现 + deterministic verifier + 可审计执行是目标，agent 只是手段；不是 agent 框架，不是 DSL 自演化平台。

### 三种状态改变（project-flow）

系统状态只由三种操作改变，每种走临时镜像 → 回传白名单守门 → 新状态节点：

```text
paper_reproduction   跑一篇论文复现
self_iteration       自迭代一轮 skill/备注
human_intervention   人工改 SKILL/规则/参数/记忆
```

### 实现状态

v2 设计已完成但代码未实现（2026-06）。SEPR 工作区用 claude 三层子 agent 替代 workflow 状态机，已实际运行 Mie 复现基础设施。`workflows/` 下现存文件（`paper_reproduction.workflow.yaml`、`ENGINE.md`、`prompts/`）是 v1 残留，暂不重写——SEPR 子 agent 方案是当前有效路径。

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
| Mie theory analytical/semi-analytical calculations, Lorenz-Mie coefficients, scattering/absorption/extinction cross sections, metal LSPR, dielectric Mie modes, core-shell recursive Mie, coupled dipole approximation, surface lattice resonances, binary arrays, S-parameter retrieval effective medium, Maxwell-Garnett, Mie-vs-Bragg phase diagram, Python-only scattering benchmark data, Mie physical verifiers, 3-layer physical verification (energy conservation, Rayleigh/large-size limits, paper figure comparison; PyMieScatt deprecated) | `optics-mie-reproduction` + `reproduction_test/mie/mie_reproduction_plan-CN.md` |
| Paper figure reproduction, parameter tables, missing-info analysis, handoff reports, workflow-based reproduction, COMSOL/Magnus reproduction (non-Mie) | `optics-paper-reproduction` + `workflows/paper_reproduction.workflow.yaml` |
| COMSOL runtime image, active Magnus-local image, license mounts, runtime folder | `optics-comsol-runtime` |
| COMSOL batch/headless jobs, `.java`/`.mph`/`.m`, smoke cases, manifest contract | `optics-comsol-batch` |
| COMSOL Java API syntax, GUI-exported Java, feature/study/solver tags | `comsol-java-api` |
| Magnus/Gustation jobs, logs, blueprint save/launch, staging paths | `optics-magnus-platform` |
| Magnus artifact formats, `.magnus.yaml`, `.magnus.skill.yaml`, import/export packaging | `optics-magnus-artifacts` |
| Docker image build/push/archive/handoff, ACR/PKU registry, image size/hash | `optics-docker-images` |
| Reproduction 复现编排 (SEPR workspace) | `main-agent` (SEPR `.human/skills/`) |
| Reproduction 复现执行 (SEPR workspace) | `sub-agent` (SEPR `.human/skills/`) |
| Self-evolution 自迭代编排 (SEPR workspace) | `evolution-agent` (SEPR `.human/skills/`) |
| Self-evolution 自迭代执行 (SEPR workspace) | `sub-E-agent` (SEPR `.human/skills/`) |

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

## Search & Information Retrieval

Use the global MCP routing rules first, then apply these project-specific refinements:

- Physics, optics, photonics, plasmonics, Mie theory, COMSOL validation, and paper-reproduction literature: prefer `paper-search-wos` / Web of Science MCP for bibliographic metadata, citation counts, journal/source information, and screening abstracts when available.
- AI agent, workflow, skill, LLM training, or evaluation papers used to improve the agent system: prefer `arxiv-research` MCP.
- Non-paper searches such as COMSOL API usage, Magnus/cluster behavior, Docker issues, code examples, web documentation, and current public information: prefer `exa` MCP.
- Use `semantic-scholar`, `openalex`, or `crossref`-based MCPs to fill missing abstracts, citation graph context, DOI metadata, or author/institution metadata after the primary source.
- Use `firecrawl` for known URLs that need reliable extraction, and browser automation only when the page requires interaction.
- Do not rely on training data alone for API syntax, model/library versions, paper claims, or current platform behavior.

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
