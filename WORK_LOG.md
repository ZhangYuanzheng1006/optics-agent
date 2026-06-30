# SEPR 工作日志（完整交接文档）

> **用途**：本文档是 SEPR 工作区从创建到 2026-06-30 的完整工作记录。供上下文压缩或新开对话时快速恢复。
> **最后更新**：2026-06-30
> **当前阶段**：设计阶段 + 风险审查 + 16 条落地 + 双系统适配（Claude Code + OpenCode）+ 子 agent 深度/工具限制全部完成。待启动 Mie 第一阶段。

---

## 0. 一句话定位

**两个工作区分工**：
- **optics_agent**（`C:\Users\27370\Desktop\project\optics_agent`）= **设计 SEPR 的元工作区**。在这里设计 SEPR 的框架（4 agent 架构、workflow、spawn 模版、六维裁决、失败防护等），也做自身的 COMSOL/Magnus 工作。
- **SEPR**（本工作区，`C:\Users\27370\Desktop\project\self-evo-paper-repro`）= **agent 复现论文的执行工作区**。Claude Code 在这里以 main-agent 身份跑 10 步复现 workflow，或以 evolution-agent 身份跑自迭代。

**人工预训练工作流**（核心，非 E-flow 自动）：
```
1. optics_agent 设计 SEPR 框架（已完成设计阶段）
2. CC 在 SEPR 区复现一篇论文（用 .claude/skills/ 详细版）
3. 把 SEPR 复现过程的上下文（WORK_LOG.md + 复现报告）发给 optics_agent 的 CC
4. optics_agent 的 CC 读 SEPR 经验，人工改进 SEPR 设计（不直接用 E-flow 自迭代）
5. 重跑论文，验证改进
6. 循环 2-5 = 人工预训练
```

**关键边界**：SEPR 复现论文时反馈的经验，由 optics_agent 的 CC 人工审查后改进设计，不是 SEPR 自己跑 E-flow 自动改。E-flow 是后期才用的（攒够 case 后人工开专门 evolution session）。

SEPR 采用 Claude Code 3 层子 agent 架构（main-agent → sub-agent → sub-sub-agent），替代 workflow 状态机。4 个 agent 身份（复现 main+sub / 自迭代 evolution+sub-E），两套对称 workflow（10 步复现 + 6 步自迭代）。

---

## 1. 工作路径

- **SEPR 工作区**：`C:\Users\27370\Desktop\project\self-evo-paper-repro`
- **optics_agent**：`C:\Users\27370\Desktop\project\optics_agent`
- **GitHub**：`https://github.com/PKU-QNO/optics-agent-zyz`（optics_agent）
- **平台**：Windows + PowerShell，SSH 到 Gustation 集群
- **教材**：`.paper/scattering.pdf`（Bohren & Huffman《Absorption and Scattering of Light by Small Particles》，27.8MB）
- **Mie 论文**：`.paper/mie/` 11 篇 PDF

---

## 2. 整个工作过程（从头）

### 阶段一：workflow 风险评审（optics_agent）
- 分析 `papers/self-evolution/` 13 个分类 127 篇论文，挖出 R-1~R-49 共 49 条风险，组织成 7 组
- 合并三份风险文件为一份 `optics_agent/notes/workflow_risk_review-CN.md`
- 提出 18 条框架修改建议给 `workflow_engine_design-CN.md`

### 阶段二：pivot 到 Mie + 建 SEPR
- 用户决定暂停 workflow 规划，先做 Mie 复现 Phase 1
- 建 Mie 复现计划（`reproduction_test/mie/mie_reproduction_plan-CN.md`）+ `optics-mie-reproduction` skill + todolist
- 验证体系从 4 层改 3 层（物理硬约束→极限退化→论文图量化），三方一致性→两方一致性
- **PyMieScatt 弃用**（"太机械"），清理 12 个文件
- 用户决定建独立工作区 SEPR，用 claude 三层子 agent 替代 workflow 状态机
- 设计 10 步复现 workflow + main agent 第 11 步报告
- 4 agent 架构：复现（main-agent + sub-agent）+ 自迭代（evolution-agent + sub-E-agent）

### 阶段三：自迭代设计
- 调研 ECC（github 222k 星）hook 驱动自动演化，蒸馏 6 条改动
- 设计 5 步自迭代 workflow + evolution-agent 第 6 步报告
- `.human/`（人话版中文审查稿）vs `.claude/`（英文 prompt-engineered 执行版）双目录机制
- claude 隔离配置：git init + claudeMdExcludes + disableBundledSkills + autoMemoryEnabled=false

### 阶段四：细节设计
- subsubagent 规范（用户不批示，讨论确定）：用调 subagent 的标准方式调，多调防上下文过长，第 3 层不再 spawn
- spawn 输入模版机制：全局模版（W/E 各一份）+ 每步局部模版 + 主 agent 拼接
- 一个节点多子 agent 并发（fan-out，独立子任务才并发）
- 四选一裁决改进（AI4S 适配）：六维裁决（加 Fork/Archive）+ 三级治理（Tier-1/2/3）
- validate_and_replay 实现：selective replay 层 A/B/C，E-flow 不调 W-flow
- 记忆要求：每个 agent 开始前搜 memento，结束前更新
- 子 agent tools 控制：MCP 全量注入，用 allowlist `tools: Read, Write, Edit, Bash, Glob, Grep, ToolSearch, Skill`
- 蓝图扫描泛用能力：Annotated 参数 + scan_parameters 字段
- CLAUDE.md 全规范：全程中文 + Markdown + 公式 `$...$`

### 阶段五：落地 + 验证
- 建目录：toEflow/ + .E-history/ + todo.md
- .E-history 报告模板（evolution 第 6 步用）
- Wflow step10/11 输出 4 类文档（全过程报告/简报/SKILL建议/蓝图建议）
- quick_validate 9 个 .human skill 全通过（sub-E-agent frontmatter name 改小写）
- 建 PROJECT_STATUS.md
- 更新 optics_agent/AGENTS.md（加 SEPR 姊妹工作区说明）

### 阶段六：v3 文献审查（94 篇）
- 用户要求审查整个 v3 设计风险（不只 prompt 工程，是整个框架）
- 派子 agent 多源查 arxiv+exa+github+firecrawl，94 篇文献分 A-K 11 类下载到 `optics_agent/papers/SEPR/`
- 产出 3 份报告：CONTEXT-for-subagent.md / CATEGORY-READING-NOTES.md / REVIEW-REPORT.md
- 5 条最高优先级风险：LLM-as-judge 把 fallback 当成功 / 自迭代假进步 / 子 agent 递归越权 / 记忆污染 / 蓝图无 schema 变随机实验

### 阶段七：失败防护 + 16 条落地
- 落地失败防护：同一步重跑最多 5 轮 + 每轮新证据/新假设 + retry fingerprint + case/evolution 级资源上限
- 在另一 fork 派 3 个子 agent 落地 REVIEW-REPORT 16 条建议（P0/P1/P2 三批）
- 本 session grep 验证 16 条全部命中目标文件
- DESIGN.md §15 更新为"16 条全部落地"完整表格

### 阶段八：.claude 详细版 + 双系统适配 + 三文件同步（2026-06-30）
- **.claude/skills/ 4 身份详细版完成**：把 .human/（中文大纲）提示词工程详细化到 .claude/skills/（中文 prompt-engineered 执行版），4 身份（main/sub/evolution/sub-E）共 6465 行，42 个 Markdown 文件，quick_validate 全通过。每个 workflow 步骤有完整 spawn 指令（全局+局部拼接好）+retry_budget+blocker_condition+决策问题+gate
- **OpenCode 适配落地**（GPT-5.5 备选方案）：Opus 不稳定，备选 GPT-5.5。判定 OpenCode 适配优于 Codex（支持层级委派+permission 统一+skill 懒加载接近 Claude Code）。调研结论：OpenCode 无硬隔离字段，规则文件从当前目录向上找 AGENTS.md/CLAUDE.md 第一个命中胜出；skill 懒加载（只暴露 name/description，agent 调 skill tool 加载正文）；子 agent 递归用 permission.task 控制。落地：SEPR/AGENTS.md（隔离上级）+ opencode.json（permission/agent 配置 108 行）+ .opencode/prompts/（4 角色 prompt，强制先加载 skill）+ scripts/start-opencode-sepr.ps1 + notes/opencode-adaptation-CN.md（166 行调研报告）
- **三文件同步规则落地**：SEPR 三个根配置文件（CLAUDE.md/AGENTS.md/opencode.json）改任何一个必须同步审改其它两个，避免 Claude Code 和 OpenCode 行为分叉。规则写进 SEPR/CLAUDE.md + SEPR/AGENTS.md + optics_agent/AGENTS.md（OA 的 CC 改 SEPR 时遵守）
- **hardlink 修复**：发现 optics_agent 的 AGENTS.md 和 CLAUDE.md 内容不同（编辑工具破坏 hardlink），用 Remove-Item + New-Item -ItemType HardLink 重建。教训：每次改 AGENTS.md/CLAUDE.md 后要验证 hash 一致
- **两工作区分工架构明确**：optics_agent = 设计 SEPR 的元工作区；SEPR = agent 复现论文执行工作区；人工预训练循环：设计→SEPR 复现→经验反馈给 OA 的 CC→OA 改进设计→重跑
- **optics_agent 系统更新**：AGENTS.md/CLAUDE.md 同步（329 行）+ 9 个 skill quick_validate 通过 + SEPR 边界明确 + Mie blocker 解除 + FINAL Mie 复现计划（7 阶段顺序+论文简介+启动指令）

### 阶段九：子 agent 深度+工具限制配置（2026-06-30）
- **Claude Code `.claude/agents/` 4 文件落地**：`main-agent.md` / `evolution-agent.md` 的 `tools` 含 `Agent`、`maxTurns=50`，`sub-agent.md` / `sub-E-agent.md`（frontmatter `name: sub-e-agent`）的 `tools` 含 `Agent`、`maxTurns=15`，四者均设 `disallowedTools: mcp__*, NotebookEdit`；第 3 层叶子由 sub/sub-E spawn 时省略 `Agent`，不再继续 spawn。
- **OpenCode `opencode.json` 细化为 6 agent**：`sepr-main` / `sepr-evolution` 为编排层 `maxTurns=50`，只放行对应执行层和 leaf；`sepr-sub` / `sepr-sub-e` 为执行层 `maxTurns=15`，只放行对应 leaf；新增 `sepr-sub-leaf` / `sepr-sub-e-leaf` 两个叶子角色，`maxTurns=15` 且 `permission.task: deny`。
- **两系统对齐表**：编排层可 spawn，执行层只 spawn 叶子，叶子层禁止 spawn；工具 allowlist 统一为 `Read/Write/Edit/Bash/Glob/Grep/ToolSearch/Skill/Agent`（OpenCode 对应 read/glob/grep/list/edit/bash/skill/task），`edit/bash` 默认 `ask`。
- **文档同步完成**：`CLAUDE.md` 新增“子 Agent 深度与工具限制”节，`AGENTS.md` 更新 Tool/Spawn Policy，`.opencode/prompts/` 6 个 prompt 明确 leaf 机制与“不再委派”。

---

## 3. 当前状态（2026-06-30）

### ✅ 已完成
- SEPR 工作区 + claude 隔离配置
- 4 agent 架构 + 两套 workflow（10步复现 + 6步自迭代）
- spawn 模版机制（全局+局部+拼接）+ subsubagent 规范 + 多子 agent 并发
- 六维裁决 + 三级治理落地 step05
- .E-history 模板 + Wflow 4 类输出 + 蓝图扫描泛用
- CLAUDE.md 全规范（中文/记忆/tools/新目录/validate_and_replay/失败防护/result_class/run_manifest）
- .human/DESIGN.md 项目计划（373 行）
- PyMieScatt 清理 + 教材就位 + papers 复制
- skill-print.py + skill 互转脚本
- 94 篇 v3 文献审查 + REVIEW-REPORT.md
- 16 条风险建议全部落地（P0/P1/P2）
- 9 个 .human skill quick_validate 通过
- **.claude/skills/ 4 身份详细版完成（6465 行，42 文件，quick_validate 全通过）**
- PROJECT_STATUS.md
- **OpenCode 适配落地**（AGENTS.md + opencode.json + .opencode/prompts/ + 启动脚本 + 调研报告）
- **三文件同步规则**（CLAUDE.md/AGENTS.md/opencode.json 同步改）
- **两工作区分工架构明确**（OA 设计 SEPR + SEPR 执行复现 + 人工预训练循环）
- **optics_agent 系统更新**（AGENTS/CLAUDE 同步 + 9 skill 验证 + SEPR 边界 + FINAL Mie 计划）
- **子 agent 深度+工具限制配置**（Claude `.claude/agents/` + OpenCode `opencode.json` 对齐，leaf 机制防递归）

### ⏳ 待完成（只剩 2 项，都等用户发话）
1. **任务 9 残留**：英文 prompt-engineered 版（现在 .claude/skills/ 是中文详细版，够用；英文版是后期优化，非必须）
2. **Mie 第一阶段实际执行**（教材已就位，含 4 个人工 gate，不能全自动）

---

## 4. 文件结构

### SEPR 根 `C:\Users\27370\Desktop\project\self-evo-paper-repro`
```
CLAUDE.md           247行  工作区路由+红线+全规范+三文件同步规则+子 Agent 深度/工具限制（规则主源）
AGENTS.md            32行  OpenCode 本地规则入口（隔离上级）+ 三文件同步+Tool/Spawn Policy
opencode.json       182行  OpenCode permission/agent 配置（6 agent+leaf 防递归）
WORKSPACE.md         73行  工作区基础说明
PROJECT_STATUS.md    91行  项目状态总览
todo.md              22行  全局日志（每次 workflow/Eflow 结束前填）
WORK_LOG.md                本文档（完整工作记录）
.gitignore
```

### .opencode/（OpenCode 适配层）
```
prompts/
  sepr-main.md       SEPR main-agent OpenCode prompt（强制先加载 skill）
  sepr-sub.md        sub-agent prompt
  sepr-evolution.md  evolution-agent prompt
  sepr-sub-e.md      sub-E-agent prompt
  sepr-sub-leaf.md   W 第 3 层叶子 prompt（task deny，不再委派）
  sepr-sub-e-leaf.md E 第 3 层叶子 prompt（task deny，不再委派）
```
注：OpenCode skill 懒加载，prompts/ 强制各角色先调 skill tool 加载对应 SKILL.md；leaf prompt 明确禁止继续 spawn。

### scripts/
```
start-opencode-sepr.ps1   OpenCode 启动脚本
```

### notes/
```
opencode-adaptation-CN.md   166行  OpenCode 调研报告+迁移方案
self_iteration_design-CN.md        ECC 6 改动+自迭代 5 步
```

### .paper/（论文原文区，只读）
```
scattering.pdf      27.8MB  Bohren & Huffman 教材（核心公式 an,bn 主源）
mie/                11 篇 Mie 论文 PDF + 部分源码
```

### .human/（人话版中文审查稿，给用户看）
```
DESIGN.md            373行  项目计划主线（14 章 + §15 文献审查 + 附录）
skills/
  main-agent/               W 编排：SKILL+模版拼接+并发+失败防护
    SKILL.md
    references/spawn_template_global.md   W 全局 spawn 模版
    references/main_report_template.md    4 类输出模板（全过程/简报/SKILL建议/蓝图建议）
    workflow/01-11/SKILL.md               11 步（各带局部模版+retry_budget+blocker_condition）
  sub-agent/                W 执行
    SKILL.md
    references/report_template.md         8字段报告+固定头6字段+uncertainty+missing_evidence
    workflow/01-10/SKILL.md               10 步
  evolution-agent/          E 编排
    SKILL.md
    references/spawn_template_global.md   E 全局 spawn 模版
    references/evolution_history_template.md  .E-history 报告模板（12字段）
    workflow/01-06/SKILL.md               6 步（各带局部模版+candidate_id等5字段）
  sub-E-agent/              E 执行
    SKILL.md
    references/report_template.md         报告模板
    workflow/01-05/SKILL.md               5 步
  optics-mie-reproduction/  Mie 复现 3 层检验
    references/verification.md            Layer 1 硬约束（含适用条件/容差/失败解释/不适用）
  optics-magnus-platform/   Magnus 平台
  optics-magnus-artifacts/  artifact 格式（蓝图完整 schema）
  optics-agent-core/        基础路由
  skill-creator/            skill 规范+互转脚本
```

### .claude/（中文 prompt-engineered 详细执行版，4 身份 6465 行）
```
settings.local.json        claude 隔离配置（git+claudeMdExcludes+disableBundled+autoMemory=false）
skill-print.py             sub-agent 启动时获取 skill 列表（需 PYTHONUTF8=1）
agents/                    4 个项目级 subagent 定义（tools/disallowedTools/maxTurns）
  main-agent.md            maxTurns=50，tools 含 Agent
  sub-agent.md             maxTurns=15，tools 含 Agent（只派叶子）
  evolution-agent.md       maxTurns=50，tools 含 Agent
  sub-E-agent.md           maxTurns=15，name: sub-e-agent，tools 含 Agent（只派叶子）
skills/
  main-agent/              14 文件 2193 行（SKILL+spawn模版+4类输出模板+11步workflow各步详细化）
  sub-agent/               12 文件 1650 行（SKILL+报告模板+10步workflow）
  evolution-agent/         9 文件 1556 行（SKILL+E全局模版+ehistory模板+6步workflow）
  sub-E-agent/              7 文件 1066 行（SKILL+报告模板+5步workflow，frontmatter name: sub-e-agent）
  optics-agent-core/       中文（项目基础路由，已更新含 SEPR 边界）
  optics-magnus-platform/  中文（Magnus 平台）
  optics-magnus-artifacts/ 中文（artifact 格式，蓝图完整 schema）
  optics-mie-reproduction/ 中文（Mie 3 层检验，已更新含 FINAL 计划+教材）
  skill-creator/           中文（skill 规范+互转脚本）
  pdf/                     空白骨架（PDF 提取/OCR/数字化，待英文）
  magnus/                  空白骨架（Magnus HPC，SLURM/973G/128核，含 blueprint schema+sweep_manifest）
```
注：4 身份（main/sub/evolution/sub-E）是中文 prompt-engineered 详细版，每步 workflow 有完整 spawn 指令（全局+局部拼接好）+retry_budget+blocker_condition+决策问题+gate。Claude Code 读 .claude/skills/ 预加载，OpenCode 通过 skill tool 懒加载同一份 SKILL.md。

### .work/（agent 工作沙箱）
```
.sub-report/               子 agent 完整报告
.todo/<paper>/             单论文 workflow 过程文件 + skill 草稿缓冲
.evolution/<timestamp>/    evolution 进行中工作区（含 conflict_ledger.yaml）
memento-cache/
```

### toEflow/（workflow→evolution 缓冲，只增不删）
```
<paper>.skill.yaml        workflow 提交的 skill 草稿
<paper>.skill-suggestion.md  SKILL 更改建议
<paper>.blueprint-suggestion.md  蓝图建议
<paper>.todo-entry.md     迭代需求
```

### .E-history/（evolution 历史报告，按次数排序 01 开机）
```
01-evolution-report.md
02-evolution-report.md
```

### .result/（最终交付区）

### papers/ → optics_agent/papers（junction）
### reproduction_test/ → optics_agent/reproduction_test（junction）

### optics_agent/papers/SEPR/（94 篇 v3 文献审查）
```
A_prompt_engineering/{success,failure,survey}      8 篇
B_subagent_orchestration/{success,failure,survey}  8 篇
C_self_iteration/{success,failure,survey}          10 篇
D_taxonomy_knowledge_governance/{...}              8 篇
E_workflow_structure/{...}                         10 篇
F_reproduction_correctness/{...}                   10 篇
G_failure_loop_guard/{...}                         8 篇
H_memory_provenance/{...}                          9 篇
I_blueprint_parameter_scan/{...}                  9 篇
J_physical_verifier/{...}                         8 篇
K_surveys/{...}                                   6 篇
CONTEXT-for-subagent.md     子 agent 上下文（30 行）
CATEGORY-READING-NOTES.md   分类阅读笔记（45 行）
REVIEW-REPORT.md            核心风险报告（155 行，10 节）
```

---

## 5. 核心设计（完整）

### 5.1 4 agent 架构
| workflow | 编排者 | 执行者 | 步数 |
|---------|--------|--------|------|
| 复现 | main-agent | sub-agent | 10 步 + 第 11 步主 agent 报告 |
| 自迭代 | evolution-agent | sub-E-agent | 5 步 + 第 6 步 evolution-agent 报告 |

身份选择由用户第一句话决定：
- "复现 XXX.pdf" → main-agent
- "把 todo 里待迭代的任务完成" → evolution-agent
- 局部任务 → 不进 workflow

### 5.2 10 步复现 workflow
```
01-pdf_preprocessing       PDF→结构化文本
02-paper_reading           理解+参数表（gate①参数核对）
03-reproduction_design     formalization spec+拆分（gate②spec核对）
04-theory_and_implementation  推导+代码实现
05-theory_check            对抗式审查（gate③公式核对，对教材）
06-run_and_monitor         运行代码/Magnus
07-physical_verification   3 层物理检验
08-result_analysis         量化对比+归因（gate④误差核对）
09-reproducibility_selfcheck  扰动+独立重跑
10-summary_and_report      4类文档+记忆+skill草稿→toEflow
11-main_agent_report       主agent汇总定稿+run_manifest
```

### 5.3 6 步自迭代 workflow
```
01-concurrent_review       N个sub-E并行审capsule
02-cluster_and_plan        聚类+4type分流+修改计划+conflict_ledger
03-concurrent_skill_work   M个sub-E并行改skill草稿+sweep_manifest
04-validate_and_replay     selective replay 层A/B/C
05-generate_report         六维裁决+三级治理
06-evolution_agent_report  写.E-history+run_manifest
```

### 5.4 spawn 模版拼接机制
主 agent 走每步：
1. 读 workflow/0X/SKILL.md 末尾 → 拿【局部模版】（任务+输入+输出+约定+决策问题+gate+retry_budget+blocker_condition）
2. 读 references/spawn_template_global.md → 拿【全局模版】（身份+搜记忆+执行规则+forbidden_actions+max_turns=15+tools+8字段输出+重跑上限+更新记忆+中文输出）
3. 拼接：全局 + 局部 + 自己对这篇论文的具体理解/要求
4. spawn sub-agent 发完整指令
5. 等报告，校验固定头6字段+8字段，读决策性回答（含uncertainty+missing_evidence），拍板

### 5.5 subsubagent
- 用调 subagent 的标准方式调 subsubagent
- 多调防上下文过长（小活外包）
- 第 3 层不再 spawn
- W-sub/E-sub 设定复用各自 sub 身份框架

### 5.6 六维裁决 + 三级治理
**六维裁决**（每条候选经验选一）：
- Save：独特、scope 清楚 → 直接存 candidate
- Improve then Save：需打磨 → 列改进点+修订版
- Absorb (Merge)：与已有 skill 兼容 → 展示 diff+合并建议
- Fork：与已有 skill 冲突 → 创建 scope 分支，带冲突标注（不强行合并）
- Archive：有价值但不足以进 skill → 存负面知识库（带 source_artifact/evidence_type/timestamp_version/scope_applicability/confidence_result_class 五要素）
- Drop：琐碎/冗余 → 说明为什么扔

**默认流转顺序**：Save → Improve → Absorb → Archive → Drop（单 case 优先 Save/Improve，多 case+verifier+replay 后才 Absorb，禁无证据直接 Absorb）

**三级治理**（Tier = case count × 决策级别 二维）：
- Tier-1：单 case 无 verifier → Archive，不进 skill；低风险文档/摘要，agent 自主
- Tier-2：≥2 case 或 1 case+verifier → candidate pending；skill/记忆更新，必须人审
- Tier-3：≥3 case+verifier+replay 无退化 → active 升级；物理成功声明/workflow结构/蓝图口径，必须人审+verifier+replay

### 5.7 validate_and_replay（E-flow 不调 W-flow）
- 层 A（改备注/注意事项）：sub-E-agent 跑旧代码+verifier+benchmark 对比
- 层 B（改流程步骤）：sub-E-agent 重跑 step06-08 旧代码
- 层 C（改核心方法/公式）：报告"需人工开 W-flow 重跑"，human gate 决定
- 局限：只能验证不破坏旧 case 代码/验证，不能验证新 skill 推导在旧 case 也得同样代码（后者要重跑 W-flow，初期接受）

### 5.8 经验 4 type
- GUIDING：成功根因（这次为什么对）
- CAUTIONARY：失败教训（这次为什么错/险些错），立刻记
- FACT：可验证的碎片知识
- PROCEDURE：可复用执行流程，≥2 case 才升 active

### 5.9 失败防护 / 防空跑
**workflow 失败定义**：①物理 verifier 连续不通过且无新假设 ②同一步重跑达上限 5 轮 ③子 agent 报告 blocked ④wall-clock/spawn/搜索超限 ⑤evolution replay 大面积退化/human gate 拒绝

**防空跑硬性规则**：
- 节点级：同一步重跑最多 5 轮，每轮必须新证据/新假设，无新信息转 blocked，retry fingerprint 相同第二次即 blocker
- case 级：max wall-clock 4h、max spawned agents 20、max external searches 30
- evolution 级：max capsule 15、max skill 改动 8，超限分批
- 失败不是终止：step10/06 照样写报告，扔 toEflow/，进 .E-history 当 Archive 负面知识

### 5.10 result_class 7 级枚举（强制，防 LLM 把 fallback 当成功）
```
not_run                      未跑
pipeline_completed           pipeline 跑完，无物理验证
simulation_completed         仿真跑完，无物理验证
diagnostic_only              只诊断，无复现
surrogate_fallback           代用方案
partial_physical_match       部分物理匹配
physical_reproduction_success 物理复现成功
```
**硬规则**：任一适用 Layer 1 物理硬约束失败 → 默认 result_class ≤ diagnostic_only，禁声明 partial_physical_match 或 physical_reproduction_success。禁把 surrogate_fallback/diagnostic_only/pipeline_completed 当 physical_reproduction_success。

### 5.11 记忆要求（每个 agent）
- 开始前：`memory_search` 搜相关记忆，避免重复劳动
- 结束前：`memory_store`/`decisions_log`/`pitfalls_log` 更新，存前 `memory_dedup_check` 查重
- provenance 五要素：source_artifact / evidence_type / timestamp_version / scope_applicability / confidence_result_class

### 5.12 子 agent tools 控制
MCP 工具全量注入占 context，主 agent spawn 时用 allowlist：
```
tools: Read, Write, Edit, Bash, Glob, Grep, ToolSearch, Skill
```
- ToolSearch 必须显式包含（否则 MCP 工具注册了无法调用）
- tools 不支持 `mcp__*` 通配符，限 MCP 用 `disallowedTools`

### 5.13 run_manifest.yaml（每次 run 强制）
main-agent step11 / evolution-agent step06 写，记：run_id / timestamp / case或batch / spawned_agents / fan_out / max_depth_reached / result_class / retry_fingerprints

### 5.14 蓝图（blueprint ≠ script）
- **blueprint**：Magnus 负责执行的参数化任务模板，跑在 SLURM 框架，最大 973G RAM（单任务 256G）、大磁盘、128 核心
- **script**：本地 Python 跑，轻量
- 蓝图完整 schema：parameters / units / bounds / fixed_assumptions / resource_policy / expected_outputs / verifier_hooks / stop_rules / scan_parameters
- sweep_manifest.yaml：记 sweep_id / blueprint_id / 扫描参数范围步长总点数 / 每点结果路径+result_class，支持复跑单点和复现整图

### 5.15 .human/ vs .claude/ 双目录
- .human/：永远是人话版中文审查稿给用户看，现阶段是主
- .claude/：英文 prompt-engineered 执行版，agent 运行时读，后期任务 9 补全
- 双写：workflow 更新 skill 时同时写两处

### 5.16 3 层物理 verifier
- Layer 1 物理硬约束：能量守恒 / 无损吸收 / 光学定理 / 瑞利极限 / 大尺寸极限 / 球对称性（每条带适用条件/容差/失败解释/不适用）
- Layer 2 极限退化：Rayleigh 极限 / 大尺寸 extinction paradox
- Layer 3 论文图量化：数值对比，区分参数缺失/模型简化/数值错误/论文不可复现

### 5.17 conflict_ledger.yaml
evolution step02 建，冲突触发：同现象不同结论/同参数不同值/经验与已有skill冲突。字段：conflict_id / 冲突项描述 / 来源A / 来源B / 当前采用项 / 被拒项 / 裁决人/agent / 复查条件。冲突不自动调和，进 Tier-2/3 人审。

### 5.18 双系统支持（Claude Code + OpenCode）
- **Claude Code（Opus，主）**：读 `.claude/skills/` 启动时预加载完整 SKILL.md；MCP 默认继承；嵌套用 tools 省略 Agent 控制
- **OpenCode（GPT-5.5，备选）**：读 `.opencode/prompts/` + skill tool 懒加载同一份 SKILL.md；MCP 进 permission 系统；嵌套用 permission.task 控制
- **同一套 SKILL.md 正文**：.claude/skills/ 的 SKILL.md 两个系统共用，不用维护两套
- **Opus 不稳定时切 GPT-5.5 + OpenCode**，迁移成本低
- OpenCode 适配文件：AGENTS.md（隔离上级）+ opencode.json（permission/agent）+ .opencode/prompts/（4 角色 prompt）

### 5.19 三文件同步规则（强制）
SEPR 三个根配置文件改任何一个必须同步审改其它两个：
- `CLAUDE.md`（规则主源，Claude+OpenCode 都读）
- `AGENTS.md`（OpenCode 本地隔离入口）
- `opencode.json`（OpenCode permission/agent 配置）
不同步会导致 Claude Code 和 OpenCode 行为分叉。详细规则见 CLAUDE.md "三文件同步规则"节。optics_agent/AGENTS.md 也记录此要求（OA 的 CC 改 SEPR 时遵守）。

### 5.20 子 agent 深度 + 工具限制配置（2026-06-30）
Claude Code 侧新增/确认 `.claude/agents/` 四个项目级 subagent 定义：`main-agent.md`、`sub-agent.md`、`evolution-agent.md`、`sub-E-agent.md`。四个文件均使用官方 YAML frontmatter，字段含 `name`、`description`、`tools`、`disallowedTools`、`model`、`permissionMode`、`maxTurns`。

Claude Code 配置口径：
- `main-agent` / `evolution-agent`：`tools: Read, Write, Edit, Bash, Glob, Grep, ToolSearch, Skill, Agent`，`maxTurns: 50`，可分别派 `sub-agent` / `sub-e-agent`。
- `sub-agent` / `sub-e-agent`：同样保留 `Agent`，`maxTurns: 15`，但只准派第 3 层叶子 subsubagent；派叶子时必须在 prompt 中省略 `Agent` 并写明不得继续委派。
- 四个 Claude Code agent 均设 `disallowedTools: mcp__*, NotebookEdit`，默认不暴露 MCP 和 notebook 编辑。

OpenCode 配置口径：
- `sepr-main` / `sepr-evolution`：`maxTurns: 50`，`permission.task` 只允许对应执行者和 leaf 白名单，`edit/bash: ask`。
- `sepr-sub` / `sepr-sub-e`：`maxTurns: 15`，只允许分别派 `sepr-sub-leaf` / `sepr-sub-e-leaf`，禁止派其它 task，`edit/bash: ask`。
- `sepr-sub-leaf` / `sepr-sub-e-leaf`：`maxTurns: 15`，`permission.task: deny`，作为第 3 层叶子不得继续 spawn。

对齐结论：两系统都只允许 `main/evolution -> sub/sub-E -> leaf` 三层。Claude Code 用 `tools`/`disallowedTools`/`maxTurns` 控制；OpenCode 用 `permission.task`、`permission.skill`、`edit/bash` 和 `maxTurns` 控制。改任一侧时必须同步审查另一侧。

| 层级 | Claude Code | OpenCode | maxTurns | spawn 规则 |
|------|-------------|----------|----------|------------|
| 复现编排 | `main-agent.md` | `sepr-main` | 50 | 可派 `sub-agent` / `sepr-sub`，可直接派 leaf 小任务 |
| 复现执行 | `sub-agent.md` | `sepr-sub` | 15 | 只可派第 3 层 leaf |
| 复现叶子 | spawn 时省略 `Agent` | `sepr-sub-leaf` | 15 | 不再 spawn，OpenCode `task: deny` |
| 自迭代编排 | `evolution-agent.md` | `sepr-evolution` | 50 | 可派 `sub-e-agent` / `sepr-sub-e`，可直接派 leaf 小任务 |
| 自迭代执行 | `sub-E-agent.md` (`name: sub-e-agent`) | `sepr-sub-e` | 15 | 只可派第 3 层 leaf |
| 自迭代叶子 | spawn 时省略 `Agent` | `sepr-sub-e-leaf` | 15 | 不再 spawn，OpenCode `task: deny` |

工具对齐：Claude Code allowlist 为 `Read/Write/Edit/Bash/Glob/Grep/ToolSearch/Skill/Agent`，并用 `disallowedTools: mcp__*, NotebookEdit` 禁 MCP/Notebook；OpenCode 用 permission 映射同等口径，`edit/bash` 均为 `ask`，leaf 仅保留读/查/skill/受控 edit/bash，不开放 task。

---

## 6. 16 条风险落地（REVIEW-REPORT）

### P0（科学正确性核心，4 条）
1. result_class 7 级强制枚举，禁把 fallback/diagnostic/pipeline 当成功 ✅
2. verifier 适用条件（Layer 1 每条加 Applicable/Tolerance/Failure means/Not applicable）✅
3. 硬约束失败口径（step07/08/10 同步硬规则）✅
4. 自迭代 6 步每条候选带 candidate_id/evidence_ref/decision/tier/rollback_ref ✅

### P1（防污染/防冲突，4 条）
5. conflict_ledger.yaml（step02，冲突不自动调和进 Tier-2/3）✅
6. Tier 二维治理（case count × 决策级别）✅
7. uncertainty + missing_evidence（sub/sub-E 报告每条判断）✅
8. provenance 五要素字段名统一 ✅

### P2（工程规范，8 条）
9. spawn 模版 forbidden_actions + max_turns=15 ✅
10. agent 固定头 6 字段（role/task_scope/evidence_refs/confidence/blocked_by/recommended_action）✅
11. run_manifest.yaml ✅
12. 默认流转顺序 Save→Improve→Absorb→Archive→Drop ✅
13. 11 步每步 retry_budget + blocker_condition ✅
14. 蓝图完整 schema ✅
15. sweep_manifest.yaml ✅
16. prompt 变更走候选分支（先 Save/Improve/Fork，经 replay 才 Absorb）✅

---

## 7. 94 篇 v3 文献审查（5 条最高优先级）

1. **LLM-as-judge / self-bias 把 pipeline success/fallback/diagnostic 当 physical reproduction success**——AI 判断自己复现正确性不可靠，必须外部 verifier + human gate
2. **自迭代在 noisy verifier 上反复"分数涨就收"产生假进步和 reward hacking**——要 holdout + anytime-valid 接受规则 + 回归测试 + rollback
3. **子 agent/subsubagent 递归、身份漂移、工具权限过宽造成空跑或越权**——subsubagent 默认叶子化，限工具/嵌套/写权限/max turns
4. **记忆污染：失败/surrogate/旧参数/prompt injection 被未来检索为成功经验**——memory 必须带 result_class/evidence_ref/scope/confidence/supersedes
5. **参数化蓝图若无 typed schema/单位/范围/资源上限/replay 会变成不可审计随机实验**——蓝图扫描要 typed + 限资源 + 可 replay

完整报告：`optics_agent/papers/SEPR/REVIEW-REPORT.md`

---

## 8. 关键机制速查

| 机制 | 一句话 | 位置 |
|------|--------|------|
| spawn 模版拼接 | 全局+局部+主agent理解 | main-agent/evolution-agent SKILL.md |
| subsubagent | 标准方式调，防上下文，第3层不spawn | sub-agent/sub-E-agent SKILL.md |
| 六维裁决 | Save/Improve/Absorb/Fork/Archive/Drop | evolution step05 |
| 三级治理 | Tier-1/2/3 = case count × 决策级别 | evolution step05 |
| validate_and_replay | 层A/B/C，E-flow 不调 W-flow | evolution step04 |
| 经验4 type | GUIDING/CAUTIONARY/FACT/PROCEDURE | self_iteration_design-CN.md |
| toEflow 缓冲 | workflow→evolution 只增不删 | toEflow/ |
| .E-history | evolution 历史报告按次数排序 | .E-history/ |
| 失败防护 | 重跑5轮+新证据+retry fingerprint | CLAUDE.md + 各SKILL.md |
| result_class | 7级枚举，禁fallback当成功 | CLAUDE.md |
| run_manifest | 记fan_out/depth/result_class | CLAUDE.md + step11/06 |
| conflict_ledger | 冲突不自动调和进Tier-2/3 | evolution step02 |
| provenance五要素 | source_artifact等 | CLAUDE.md + 报告模板 |
| 蓝图扫描 | Annotated参数+scan_parameters+资源上限 | magnus skill |
| sweep_manifest | 扫描结果记录支持复跑 | magnus skill + step03 |

---

## 9. 给未来 agent / 新对话的快速入口

### 两个工作区的角色（重要）
- **optics_agent** = 设计 SEPR 的元工作区（设计框架 + COMSOL/Magnus 工作）
- **SEPR**（本工作区）= agent 复现论文的执行工作区
- 人工预训练循环：设计 → SEPR 复现 → 经验反馈给 OA 的 CC → OA 改进设计 → 重跑
- **给 OA 的 CC 的提醒**：你改进 SEPR 设计时，读本 WORK_LOG.md 恢复 SEPR 上下文，不要照搬 SEPR 的复现机制到 optics_agent（OA 是 Magnus+COMSOL 工作区，不是复现 agent）

### 恢复上下文顺序
1. 读 `WORK_LOG.md`（本文档）——完整工作记录
2. 读 `CLAUDE.md`——工作区路由+红线+全规范
3. 读 `.human/DESIGN.md`——项目计划主线（373 行）
4. 读 `PROJECT_STATUS.md`——状态总览
5. 身份选择：复现→main-agent，自迭代→evolution-agent
6. 子 agent 被 spawn 时先跑 `python .claude/skill-print.py`（需 `PYTHONUTF8=1`）获得技能列表
7. **CC 跑复现时读 `.claude/skills/`（中文详细版，6465 行），不读 `.human/`（大纲简略）**

### 关键约束
- 全程中文输出 + Markdown 写作（公式用 `$...$`）
- 每个 agent 开始前搜 memento，结束前更新
- 不读 secret.json / license / SSH key 内容
- 不改 active COMSOL image 除非用户明确要求
- 不 commit 除非用户要求
- quick_validate 需 `PYTHONUTF8=1`
- skill-print.py 需 `PYTHONUTF8=1`
- **三文件同步规则**：改 CLAUDE.md/AGENTS.md/opencode.json 任何一个必须同步审改其它两个
- **子 agent 深度限制**：编排层 `maxTurns=50`，执行层 `maxTurns=15`，叶子层 `task deny`/省略 `Agent`；改 `.claude/agents/` 或 `opencode.json` 要对齐另一系统
- **hardlink 维护**：optics_agent 的 AGENTS.md 和 CLAUDE.md 是 hardlink，编辑工具可能破坏，改后验证 hash 一致，破坏了用 Remove-Item + New-Item -ItemType HardLink 重建

### 待办（只剩 2 项）
1. 任务 9 残留：英文 prompt-engineered 版（.claude/skills/ 现在是中文详细版够用，英文版是后期优化）
2. Mie 第一阶段：教材在 `.paper/scattering.pdf`，说"复现 XXX.pdf"启动 main-agent → 10步workflow → 4个人工gate
3. **sub-E-agent 目录名兼容**：.claude/skills/sub-E-agent/ 目录大写 E 和 frontmatter name: sub-e-agent 不完全匹配，OpenCode 可能要求一致，列为后续验证项

### 双系统启动方式
- **Claude Code（Opus）**：直接 `claude` 启动，读 .claude/skills/ 预加载
- **OpenCode（GPT-5.5 备选）**：`pwsh scripts/start-opencode-sepr.ps1`，读 .opencode/prompts/ + skill tool 懒加载同一份 SKILL.md

---

## 10. 教训 / 踩坑

- **子 agent 空返回但标 completed**：下次多试一遍（用户指示）
- **PowerShell here-string 在中文环境报错**：改用 write 工具建文件
- **bash 数行数对中文文件不准**：用 `PYTHONUTF8=1` + python 读
- **quick_validate 要求 name lowercase hyphen-case**：sub-E-agent frontmatter name 用 `sub-e-agent`，文件夹名仍 `sub-E-agent`
- **MCP 工具全量注入占 context**：必须用 tools allowlist 控制
- **ToolSearch 必须显式包含**：否则 MCP 工具注册了无法调用
- **E-flow 不调 W-flow**：replay 用 selective 层 A/B/C，层 C 人工重跑
- **编辑工具破坏 hardlink**：edit/write 在 Windows 上可能替换文件而非原地改，导致 AGENTS.md 和 CLAUDE.md 内容分叉。每次改后验证 hash 一致，破坏了用 `Remove-Item CLAUDE.md; New-Item -ItemType HardLink -Path CLAUDE.md -Target AGENTS.md` 重建
- **三文件必须同步**：改 CLAUDE.md/AGENTS.md/opencode.json 任何一个要审改其它两个，否则 Claude Code 和 OpenCode 行为分叉
- **OpenCode skill 懒加载**：和 Claude Code 的 skills: 预加载不同，OpenCode 子 agent 要靠 .opencode/prompts/ 强制先调 skill tool 加载 SKILL.md
- **task 工具 JSON 路径反斜杠报错**：派子 agent 时 prompt 里的 Windows 路径反斜杠会触发 JSON 解析错误，改用正斜杠或让子 agent 读临时 prompt 文件
- **PowerShell grep 对 UTF-8 中文匹配不稳定**：验证 JSON 配置和中文字段时，用 `python json.load` / Python UTF-8 读取比 PowerShell grep 更可靠

---

## 11. 相关文档索引

| 文档 | 位置 | 用途 |
|------|------|------|
| WORK_LOG.md | SEPR 根 | 本文档（完整工作记录） |
| CLAUDE.md | SEPR 根 | 工作区路由+红线+全规范+三文件同步规则（规则主源） |
| AGENTS.md | SEPR 根 | OpenCode 本地规则入口（隔离上级）+ 三文件同步 |
| opencode.json | SEPR 根 | OpenCode permission/agent 配置（6 agent+leaf 防递归） |
| DESIGN.md | .human/ | 项目计划主线（14章+§15+附录） |
| PROJECT_STATUS.md | SEPR 根 | 状态总览 |
| todo.md | SEPR 根 | 全局日志（每次run填） |
| opencode-adaptation-CN.md | SEPR/notes/ | OpenCode 调研报告+迁移方案（166 行） |
| .claude/agents/*.md | SEPR/.claude/agents/ | Claude Code 4 身份 subagent 定义（tools/maxTurns） |
| sepr-*.md | SEPR/.opencode/prompts/ | OpenCode 6 角色 prompt（强制先加载 skill，含 leaf） |
| sepr-sub-leaf.md / sepr-sub-e-leaf.md | SEPR/.opencode/prompts/ | OpenCode 叶子角色 prompt（task deny，不再委派） |
| start-opencode-sepr.ps1 | SEPR/scripts/ | OpenCode 启动脚本 |
| REVIEW-REPORT.md | optics_agent/papers/SEPR/ | 94篇v3风险报告 |
| CATEGORY-READING-NOTES.md | 同上 | 分类阅读笔记 |
| CONTEXT-for-subagent.md | 同上 | 子agent上下文 |
| workflow_risk_review-CN.md | optics_agent/notes/ | R-1~R-49 风险清单 |
| mie_reproduction_plan-FINAL-CN.md | reproduction_test/mie/ | 最终版 Mie 复现计划（7阶段+启动指令） |
| self_iteration_design-CN.md | SEPR/notes/ | ECC 6改动+自迭代5步 |
| evolution_history_template.md | .claude/skills/evolution-agent/references/ | .E-history 报告模板 |
| spawn_template_global.md | .claude/skills/main-agent/ 和 evolution-agent/references/ | W/E 全局 spawn 模版 |
| main_report_template.md | .claude/skills/main-agent/references/ | 4类输出模板 |
| report_template.md | .claude/skills/sub-agent/ 和 sub-E-agent/references/ | 8字段报告+固定头 |
| verification.md | .claude/skills/optics-mie-reproduction/references/ | Layer 1 物理硬约束表 |
| optics_agent/AGENTS.md | optics_agent 根 | OA 工作区规则（= CLAUDE.md hardlink，含 SEPR 边界+三文件同步） |

---

**本文档结束。上下文压缩或新开对话后，先读本文档恢复。**
