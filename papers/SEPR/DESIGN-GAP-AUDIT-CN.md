# SEPR 设计自洽性 + 落地现状 Gap 审计

> 审计日期：2026-07-02  
> 审计范围：`C:\Users\27370\Desktop\project\self-evo-paper-repro` 根配置、`.claude/agents/`、`.claude/skills/`、`.human/skills/`、`.opencode/prompts/`，并对照 `BORROWABLE-EXPERIENCE-CN.md` §4.2 / §5.7 / §6.6 与 memento 中 Claude 2026-07-02 审计结论。  
> 审计约束：只读核对；未修改 SEPR 任何文件；本报告是唯一写入产物。

## 0. 优先级总表

### 0.1 让设计自洽必须修的 bug

| 优先级 | Gap | 为什么必须修 | 建议时机 |
|---|---|---|---|
| P0 | capsule 产/消断裂 | E-flow 明确消费 `.work/.result/<case>/capsule.md`，W-flow step10/11 没有稳定生产该文件，E-flow 首跑缺输入 | 设计bug必修 |
| P0 | 路径体系三套并存 | 根目录约定、W-flow、E-flow 同时使用 `.work/.todo/...`、`.work/<case>/...`、`.work/self-iteration/...`、`.work/.result/...`，子 agent 会写错/找错 | 设计bug必修 |
| P0 | `.claude/agents` 深度上限在 Claude Code 侧只有 prompt 软约束 | Claude 执行层 agent 仍含 `Agent` 工具；OpenCode 有 leaf `task: deny` 硬约束，两系统安全强度不对称 | 设计bug必修 |
| P0 | 根配置与实际状态漂移 | `CLAUDE.md` / `PROJECT_STATUS.md` 仍说 `.claude/skills` 英文待写，但实际中文详细执行版已完成；这会误导未来 agent | 设计bug必修 |
| P0 | `opencode.json` 顶层 skill 白名单缺关键路由 | 顶层 `permission.skill` 为 `*: deny`，但缺 `pdf`、`magnus`、`optics-agent-core`；根路由表却列这些 skill | 设计bug必修 |
| P1 | evolution-agent 残留“四选一裁决” | 主体已变六维裁决，但 SKILL 表格和 gate 仍写四选一，治理口径冲突 | 设计bug必修 |
| P1 | result_class 旧口径残留 | 根规则禁止 `success / partial / fallback / blocked / failed / archived`，但主报告模板和 todo 模板仍出现旧枚举 | 设计bug必修 |
| P1 | PyMieScatt 弃用后文本残留 | SEPR 无 PyMieScatt 脚本，但 workflow 仍要求 PyMieScatt/三方叠加，和“三层验证 + 两方一致性”冲突 | 设计bug必修 |
| P1 | `pdf` / `magnus` 域 skill 为空白骨架 | step01/step06 关键路径依赖的脚本在 skill 中列出但实际未落地，首跑会靠临时实现 | 跑通前 |
| P2 | `.human` / `.claude` 文件集合与定位不同步 | `.claude` 多 `pdf`/`magnus`，`.human` 多一个 evolution `main_report_template.md`；二者已不是“镜像”关系 | 设计bug必修 |

### 0.2 跑通后才值得加的治理

| 优先级 | Gap | 当前结论 | 建议时机 |
|---|---|---|---|
| G1 | 报告 8 字段改工具 schema | 当前靠 Markdown/YAML 模板约束，未用工具 schema 强制 | 跑通后 |
| G1 | held-out / 同构扰动 / anytime-valid 接受规则 | 设计中有 replay，但无 holdout、同构扰动、e-value/置信序列 | 跑通后 |
| G1 | 记忆治理 valid_to / quarantine / forbidden_region / utility_score | 当前有 memento、dedup 和 provenance 五字段，但无这些机制 | 跑通后 |
| G2 | baseline A/B/C/D | 当前无“SEPR vs 裸 Claude Code vs 固定脚本”的评估设计 | 跑通后 |
| G2 | 执行真实性分级 | 当前 result_class 管物理成功等级，但没有 `emulated < dry-run < real execution` 正交维度 | 跑通后 |
| G2 | declared-vs-actual / template_contract / loads_memories allowed_types / candidate_benchmark | V1→V2 的四项消风险未完整继承 | 跑通后 |

## 1. 已知 A-D 问题逐条验证

### A1. capsule 产/消断裂

【类别】设计bug必修  
【现状】bug  
【验证结论】Claude 旧审计准确。

【证据】

- `self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:21-26`：自迭代触发条件要求已有完成复现 capsule，并确认 `.work/.result/` 有足够 capsule。
- `self-evo-paper-repro/.claude/skills/evolution-agent/workflow/01-concurrent_review/SKILL.md:7-10`：输入是 `.work/.result/` 下的 capsule 列表、每篇 `capsule.md` 和子 agent 原始工作报告。
- `self-evo-paper-repro/.claude/skills/evolution-agent/workflow/01-concurrent_review/SKILL.md:47-56`：局部 spawn 模板再次要求 `.work/.result/` 和 `capsule.md`。
- `self-evo-paper-repro/.claude/skills/sub-E-agent/workflow/01-concurrent_review/SKILL.md:9`：sub-E 明确读 `.work/.result/<case>/capsule.md`。
- `self-evo-paper-repro/.claude/skills/main-agent/workflow/10-summary_and_report/SKILL.md:7-35`：step10 产出 `full_report_draft.md`、`brief_draft.md`、skill/blueprint suggestion、benchmark/memento，没有 `capsule.md`。
- `self-evo-paper-repro/.claude/skills/main-agent/workflow/11-main_agent_report/SKILL.md:46-64`：step11 写 `run_manifest.yaml`、`.result` 报告和 memento，也没有 `capsule.md`。
- `self-evo-paper-repro/CLAUDE.md:136-157`：目录约定只有 `.work/.todo/`、`.work/.evolution/`、`.result/`，没有 `.work/.result/`。

【建议动作】定义唯一 capsule 契约：W-flow step10 或 step11 必须产 `capsule.md`，路径与 E-flow 输入统一；同时补 `processed` / run_id / result_class / evidence_refs / provenance 五字段。标记：设计bug必修。

### A2. 路径漂移

【类别】设计bug必修  
【现状】bug  
【验证结论】Claude 旧审计准确，范围比旧结论更广。

【证据】

- 根目录约定：`self-evo-paper-repro/CLAUDE.md:142-146` 规定 `.work/.sub-report/`、`.work/.todo/<paper>/`、`.work/.evolution/<timestamp>/`。
- W-flow 旧路径：`self-evo-paper-repro/.claude/skills/main-agent/workflow/10-summary_and_report/SKILL.md:11-28` 使用 `.work/<case>/...` 与 `.work/self-iteration/...`。
- W-flow 新路径：`self-evo-paper-repro/.claude/skills/main-agent/workflow/10-summary_and_report/SKILL.md:84-95` 又要求 `.work/.todo/{paper}/{case}/{timestamp}/10-summary_and_report/`。
- step11 旧路径：`self-evo-paper-repro/.claude/skills/main-agent/workflow/11-main_agent_report/SKILL.md:13-24` 引用 `.work/<case>/full_report_draft.md`、`.result/<paper>/...`、`toEflow/...`。
- step11 新路径：`self-evo-paper-repro/.claude/skills/main-agent/workflow/11-main_agent_report/SKILL.md:85-96` 又要求 `.work/.todo/{paper}/{case}/{timestamp}/11-main_agent_report/`。
- E-flow 路径：`self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:80-90` 使用 `.work/.evolution/<timestamp>/...`；但 `workflow/01` 输入仍是 `.work/.result/`，见 A1。
- main-agent 草稿路径：`self-evo-paper-repro/.claude/skills/main-agent/SKILL.md:83-91` 使用 `.work/self-iteration/<skill-name>.skill.yaml`，与 `CLAUDE.md:210-214` 的 `.work/.todo/<paper-name>/` / `.work/.evolution/<timestamp>/` 不一致。

【建议动作】保留一套 canonical 路径，例如 `.work/.todo/{paper}/{case}/{timestamp}/` + `.work/.evolution/{timestamp}/` + `.result/{paper}/`；删掉或迁移 `.work/<case>`、`.work/self-iteration`、`.work/.result`。标记：设计bug必修。

### B1. 根配置与项目状态过时

【类别】设计bug必修  
【现状】bug  
【验证结论】准确。

【证据】

- `self-evo-paper-repro/CLAUDE.md:100-105`：仍称 `.claude/skills/` 是英文 prompt-engineered 版、4 个 agent 身份 skill 待后期写、现阶段镜像 `.human`。
- `self-evo-paper-repro/PROJECT_STATUS.md:7-12`：仍称 `.claude/` 是英文执行版待写，等待把 `.human` 转成英文 prompt-engineered 版本。
- `self-evo-paper-repro/PROJECT_STATUS.md:68-73`：待办仍包括任务 9：把 `.human/` 设计稿转成 `.claude/skills/` 英文执行版。
- `self-evo-paper-repro/WORK_LOG.md:95-101` 与 `WORK_LOG.md:213-235`：记录 `.claude/skills/` 4 身份中文详细执行版已完成，共 6465 行；这与上述根状态冲突。

【建议动作】把 `.human` / `.claude` 定位改为“人话设计稿 vs 中文详细执行版”，英文版降级为可选后期优化；同步 `CLAUDE.md`、`AGENTS.md`、`opencode.json` 相关描述。标记：设计bug必修。

### B2. 四选一裁决残留

【类别】设计bug必修  
【现状】bug  
【验证结论】准确。

【证据】

- 旧口径：`self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:36-43` 的 step05 描述为“治理报告 + 四选一裁决”。
- 旧口径：`self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:103-112` 的 gate 表仍写“四选一裁决给用户看”。
- 新口径：`self-evo-paper-repro/.claude/skills/evolution-agent/SKILL.md:142-159` 又写 step05 用六维裁决和三级治理。
- 新口径：`self-evo-paper-repro/.claude/skills/evolution-agent/workflow/05-generate_report/SKILL.md:25-42` 完整列 Save / Improve / Absorb / Fork / Archive / Drop。

【建议动作】全局替换“四选一”为“六维裁决”，并确认 `.human` 侧同处同步。标记：设计bug必修。

### B3. result_class 旧口径残留

【类别】设计bug必修  
【现状】bug  
【验证结论】准确，并新增一个模板残留。

【证据】

- 根红线：`self-evo-paper-repro/CLAUDE.md:47-61` 定义 7 级 `result_class`，并禁止把 `surrogate_fallback` / `diagnostic_only` / `pipeline_completed` 当成功。
- 根红线：`self-evo-paper-repro/CLAUDE.md:170` 禁止写 `success / partial / fallback / blocked / failed / archived` 等旧口径。
- 旧口径：`self-evo-paper-repro/todo.md:10-18` 的日志模板仍写“物理复现成功 / partial / fallback / 失败 / N/A(Eflow)”。
- 旧口径：`self-evo-paper-repro/.claude/skills/main-agent/references/main_report_template.md:255-272` 的 `sweep_manifest.yaml` 示例仍写 `result_class: success | partial | fallback | blocked | failed | archived`。
- 辅助状态字段：`self-evo-paper-repro/.claude/skills/sub-agent/references/report_template.md:63-72` 与 `sub-E-agent/references/report_template.md:63-72` 仍有 `status: completed | blocked | failed`。这可以作为任务状态，但必须明确不是 `result_class`。

【建议动作】`todo.md` 和 `main_report_template.md` 全部改用 7 级枚举；报告模板中的 `status` 改名为 `execution_status` 或注明“非 result_class”。标记：设计bug必修。

### B4. OpenCode skill permission 与路由表不一致

【类别】设计bug必修  
【现状】bug  
【验证结论】准确。

【证据】

- `self-evo-paper-repro/CLAUDE.md:229-243` 路由表列出 `pdf`、`magnus`、`optics-agent-core`。
- `self-evo-paper-repro/opencode.json:15-25` 顶层 `permission.skill` 为 `*: deny`，只 allow `main-agent`、`sub-agent`、`evolution-agent`、`sub-e-agent`、`optics-mie-reproduction`、`optics-magnus-platform`、`optics-magnus-artifacts`，缺 `pdf`、`magnus`、`optics-agent-core`。
- `self-evo-paper-repro/opencode.json:51-58`、`76-82`、`149-155` 的 per-agent skill 规则使用 `*: ask`，意味着缺失 skill 不是 deny，但会在关键路径上反复 ask；顶层仍与根路由不一致。

【建议动作】若保留 `pdf`/`magnus` 作为域 skill，顶层和相关 agent permission 必须显式 allow；若不用，则从根路由表移除并改用 `optics-magnus-platform` / `optics-magnus-artifacts`。标记：设计bug必修。

### C1. 深度上限两系统不对称

【类别】设计bug必修  
【现状】bug  
【验证结论】准确。

【证据】

- Claude 执行层仍含 Agent：`self-evo-paper-repro/.claude/agents/sub-agent.md:1-8` 与 `sub-E-agent.md:1-8` 的 `tools` 均包含 `Agent`。
- Claude 叶子化靠 prompt：`self-evo-paper-repro/.claude/agents/sub-agent.md:17-20` 要求 spawn 叶子时省略 Agent；`sub-E-agent.md:17-20` 同理。
- sub-agent skill 仍说 subsubagent 读同一个 `sub-agent` skill：`self-evo-paper-repro/.claude/skills/sub-agent/SKILL.md:48-65`。
- OpenCode 硬约束：`self-evo-paper-repro/opencode.json:139-159` 定义 `sepr-sub-leaf` 且 `task: deny`；`opencode.json:161-179` 定义 `sepr-sub-e-leaf` 且 `task: deny`。
- OpenCode prompt 明确叶子不得再 spawn：`self-evo-paper-repro/.opencode/prompts/sepr-sub-leaf.md:11-16`。

【建议动作】Claude 侧也新增 `sub-leaf` / `sub-e-leaf` agent 定义，tools 去掉 `Agent`；执行层只允许派 leaf agent，不再复用带 Agent 的 sub 身份。标记：设计bug必修。

### C2. PyMieScatt 弃用后残留

【类别】设计bug必修  
【现状】部分准确：文本残留准确，脚本残留未在 SEPR/optics_agent 当前工作树发现。  

【证据】

- 弃用决策：`self-evo-paper-repro/WORK_LOG.md:52-53` 写“三方一致性→两方一致性”和“PyMieScatt 弃用”；`PROJECT_STATUS.md:82` 也写 PyMieScatt 已弃用。
- 文本残留：`self-evo-paper-repro/.claude/skills/main-agent/workflow/08-result_analysis/SKILL.md:14` 仍要求“我们的+论文+PyMieScatt 三方叠加”。
- 文本残留：`self-evo-paper-repro/.claude/skills/main-agent/workflow/09-reproducibility_selfcheck/SKILL.md:12` 仍要求 PyMieScatt 独立验证。
- 文本残留：`self-evo-paper-repro/.claude/skills/sub-agent/workflow/09-reproducibility_selfcheck/SKILL.md:8` 仍要求 PyMieScatt 独立验证。
- 文本残留：`self-evo-paper-repro/.claude/skills/optics-mie-reproduction/agents/openai.yaml:2` 仍写 PyMieScatt cross-check。
- 同类残留在 `.human/skills/main-agent/workflow/08-result_analysis/SKILL.md:14`、`.human/skills/main-agent/workflow/09-reproducibility_selfcheck/SKILL.md:12`、`.human/skills/sub-agent/workflow/09-reproducibility_selfcheck/SKILL.md:8`。
- 文件复核：当前 SEPR 与 optics_agent 工作树未发现 `compare_pymiessatt.py` 或 `*pymie*` 文件。

【建议动作】删掉 PyMieScatt / 三方叠加文本，改成“独立实现/物理硬约束/教材公式/论文图量化”交叉验证；`agents/openai.yaml` 同步更新。标记：设计bug必修。

### D. pdf / magnus 域 skill 为空白骨架

【类别】跑通前  
【现状】bug / 缺失  
【验证结论】准确。

【证据】

- `self-evo-paper-repro/.claude/skills/pdf/SKILL.md:6-11` 明确“空白，待后期英文 prompt-engineered”“职责待填”。
- `self-evo-paper-repro/.claude/skills/pdf/SKILL.md:20-34` 列 `scripts/extract_pdf.py`、`classify_figures.py`、`extract_tables.py`、`digitize_figure.py`，但标注“预制脚本待填 / 输出约定待填 / 常见坑待填”。
- `self-evo-paper-repro/.claude/skills/magnus/SKILL.md:6-19` 明确“空白，待后期英文 prompt-engineered”“职责待填”。
- `self-evo-paper-repro/.claude/skills/magnus/SKILL.md:52-58` 列 `submit_magnus.py`、`monitor_job.py`、`collect_results.py`，但标注“预制脚本待填 / 安全红线待填”。
- 当前 SEPR 工作树未发现 `scripts/*.py`。

【建议动作】若首轮 Mie 需要 PDF/图数字化或 Magnus，先补最小可执行脚本或明确改成“用现有工具临时执行，不承诺脚本存在”；不要让 workflow 误以为脚本已就位。标记：跑通前。

## 2. 23 条落地清单逐条状态

| # | 来源 | 落地项 | 状态 | 证据 | 建议动作 |
|---|---|---|---|---|---|
| 1 | §4.2 | 报告 8 字段改工具 schema 强约束 | 缺失 | 当前是 Markdown/YAML 模板：`sub-agent/references/report_template.md:61-108`；spawn 只说“报告必须有字段”：`main-agent/references/spawn_template_global.md:73-78` | 跑通后：做 report submission tool / JSON schema，`result_class` 用 enum |
| 2 | §4.2 | 红线三明治 + 显式优先级 | 部分 | 有 forbidden/result_class：`spawn_template_global.md:38-53`；但未见“全局 > 局部 > 主 agent 理解，下游不得放宽红线”的统一优先级文本 | 设计bug必修：先补优先级；三明治可跑通后优化 |
| 3 | §4.2 | 外部内容一律当数据 | 部分 | `main-agent/SKILL.md:193`、`sub-agent/SKILL.md:188`、`evolution-agent/SKILL.md:206`、`sub-E-agent/SKILL.md:191` 有 prompt injection 数据化规则 | 跑通前：把该规则放入全局 spawn 模板首尾，尤其 PDF/网页步骤 |
| 4 | §4.2 | result_class 补机理维 / 诚实维 | 部分 | 7 级 result_class 已落地：`CLAUDE.md:47-61`；但无独立“机理维/诚实维”字段，报告主要写 result_class 和 evidence | 跑通后：增加 mechanism_validity / evidence_honesty 正交字段 |
| 5 | §4.2 | verifier 加同构扰动 / held-out 参数点 | 缺失 | 定向搜索未见 held-out / 同构扰动；现有三层验证见 `optics-mie-reproduction/SKILL.md:16-20` | 跑通后：在 benchmark 加留出点和扰动点 |
| 6 | §4.2 | 记忆 valid_to / trace / quarantine / 禁止全库重压 | 部分 | 有 memento + dedup + provenance：`CLAUDE.md:175-194`；无 `valid_to` / quarantine / trace 指针规则 | 跑通后：扩展 memory 写入元数据和作废规则 |
| 7 | §4.2 | 自迭代接受规则换 anytime-valid | 缺失 | 定向搜索未见 anytime / e-value / 置信序列；replay 只做新旧对比：`evolution-agent/workflow/04-validate_and_replay/SKILL.md:16-31` | 跑通后：再引入统计接受规则 |
| 8 | §4.2 | 失败防护硬化：限制和 verifier 对 agent 只读隔离 | 部分 | 有 prompt 级上限：`CLAUDE.md:118-134`；蓝图 schema 有 `resource_policy` / `stop_rules`：`magnus/SKILL.md:31-40`；但无框架级强制 | 跑通前保留 prompt；跑通后考虑 hook/runner 强制 |
| 9 | §4.2 | 子 agent 产物落盘 + spawn 四要素 | 已落地 | `spawn_template_global.md:23-30` 有 paper/case/timestamp/task/input/output/report_path；`main-agent/SKILL.md:58-67` 要求子 agent 各自落盘 | 保持，顺带修路径漂移 |
| 10 | §4.2 | 蓝图 verifier_hooks 加物理契约反推 / 树状 rubric | 部分 | 蓝图 schema 有 `verifier_hooks`：`main_report_template.md:210-253`；`magnus/SKILL.md:31-40`；无“反推实际求解方程”或树状 rubric | 跑通后，优先在 COMSOL/Magnus case 加 |
| 11 | §4.2 | 每轮自迭代注入外部真实锚 | 部分 | Mie skill 强调教材主源：`optics-mie-reproduction/SKILL.md:83-90`；但 E-flow 未强制每轮注入论文原图/教材锚 | 跑通后：加到 E-flow step01/04 |
| 12 | §5.7 | 蓝图 typed schema + sweep_manifest | 已落地 | `main_report_template.md:210-253` 完整 schema；`main_report_template.md:255-275` 有 `sweep_manifest.yaml`；`magnus/SKILL.md:31-50` 同步 | 保持，但修 `result_class` 旧枚举 |
| 13 | §5.7 | verifier V&V 分离 + 每层失败含义 | 部分 | 有三层验证：`verification.md:5-45`；有“Layer 1 passing only means no big mistake”：`verification.md:18`；但未显式区分 verification / validation，也没有每条 Applicable/Failure means/Not applicable | 跑通后补 V&V 和适用条件矩阵 |
| 14 | §5.7 | conflict_ledger 六字段 + Tier 人审 | 已落地 | `evolution-agent/workflow/02-cluster_and_plan/SKILL.md:25-29`、`58`、`83-84` 明确冲突台账字段和不自动调和 | 保持 |
| 15 | §5.7 | holdout + 负迁移检测 + 每轮 max 候选/接受/重试 | 部分 | 有 max capsule / max skill：`CLAUDE.md:127-132`；有 replay 退化检查：`evolution-agent/workflow/04-validate_and_replay/SKILL.md:16-31`；无 holdout / max accept | 跑通后补 holdout 与 max accept |
| 16 | §5.7 | provenance.jsonl 与 memento 分离 | 缺失 | 只有 provenance 五字段：`CLAUDE.md:183-194`；未见 `provenance.jsonl` | 跑通后：每个 run 落证据层 `provenance.jsonl`，memento 只引用 |
| 17 | §6.6 | 先跑通再加治理 | 部分 | `notes/self_iteration_design-CN.md:114` 写初期 replay set 小，先跑通流程；但根 `CLAUDE.md` 未把它作为战略排序 | 跑通前：在根状态/启动说明中置顶“先跑 Akimov 最小 case” |
| 18 | §6.6 | baseline A/B/C/D | 缺失 | 定向搜索未见 baseline A/B/C/D | 跑通后：建立对照实验，不阻塞首跑 |
| 19 | §6.6 | uncertainty routing 双维度 | 部分 | 报告要求 `uncertainty` / `missing_evidence`：`sub-agent/references/report_template.md:39-46`；无 action_confidence / request_uncertainty 路由 | 跑通后：缺参走 clarification 而非 retry |
| 20 | §6.6 | physics_formalization 九字段 + 代码强制消费 | 部分 | 九字段在 Mie skill：`optics-mie-reproduction/SKILL.md:37-40`；step03 要 spec 字段和 missing_fields：`main-agent/workflow/03-reproduction_design/SKILL.md:50-54`；无代码生成必须消费 spec 的机制 | 跑通前可先靠 gate；跑通后加 spec-to-code check |
| 21 | §6.6 | 执行真实性分级 | 缺失 | 定向搜索只见 opencode dry-run 调研，不在 workflow/result 里；无 `emulated < dry-run < real execution` 字段 | 跑通后：与 result_class 正交加入 run_manifest |
| 22 | §6.6 | capsule 100% fire + processed | 缺失 | 见 A1：只有消费无生产；未见 `processed` 字段 | 设计bug必修：补 capsule 契约 |
| 23 | §6.6 | 记忆 utility_score + store routing + forbidden_region + observation 存储 | 缺失 | 当前只有 memento 搜索/写入与 dedup：`CLAUDE.md:175-194`；未见这些字段/路由 | 跑通后：不要阻塞首跑，等有真实失败样本再加 |

## 3. §6.5 V1→V2 消除风险清单核对

| 项 | SEPR 现状 | 状态 | 证据 | 建议动作 |
|---|---|---|---|---|
| declared-vs-actual capability | 没有“skill 声称能力 vs 脚本实际存在/行为”的检查；`pdf`/`magnus` 声称脚本但 `scripts/*.py` 不存在 | 缺失 | `pdf/SKILL.md:20-25`、`magnus/SKILL.md:52-56` 列脚本；当前工作树未发现 `scripts/*.py` | 跑通前：至少把不存在脚本标为“待实现，不可依赖” |
| template_contract | 蓝图 schema 和 spawn 输入有局部契约，但没有统一 `template_contract` 字段防止复用旧假设 | 部分 | `main_report_template.md:210-253` 有 blueprint schema；`spawn_template_global.md:23-30` 有 task boundary | 跑通后：给复用模板加 `assumptions / invalid_when / provenance / consumed_by` |
| loads_memories allowed_types | 只有“开始前搜 memento”，没有每步 allowed memory type 过滤 | 缺失 | `CLAUDE.md:175-181`、`main-agent/SKILL.md:166-173` 要求搜/存 memento，但无 allowed_types | 跑通后：按 step 限制 FACT / PROCEDURE / CAUTIONARY 等 |
| candidate_benchmark | benchmark 是 frozen standard-answer，但没有 candidate benchmark 标记；动态 case 可能直接进入正式 benchmark | 部分 | `benchmark_format.md:3` 写 frozen standard-answer；`benchmark_format.md:85-90` 写 append-only 和 human gate；无 candidate 标记 | 跑通后：新增 candidate/pending/active benchmark 生命周期 |

## 4. 内部一致性审计

### 4.1 workflow step 编号与角色边界

【现状】部分自洽。

- 复现 workflow 根表是 10 步 + 第 11 步：`main-agent/SKILL.md:23-41`。
- 自迭代 workflow 根表是 6 步：`evolution-agent/SKILL.md:30-43`。
- 但 `main-agent/workflow/11-main_agent_report/SKILL.md:70-72` 写“本步由主 agent 自己执行，不 spawn sub-agent”，随后 `11-main_agent_report/SKILL.md:123-140` 又生成“你是 sub-agent”的完整 spawn 指令。这是自动详细化模板遗留，属于内部矛盾。

【建议动作】删除 step11 的 sub-agent spawn 指令块，或明确它是通用模板误插入且不可执行。标记：设计bug必修。

### 4.2 `.human` vs `.claude` 同步

【现状】不同步，但这是“执行版更详细”的合理演化；问题在根文件仍称镜像。

【证据】

- `.claude/skills` 多 `pdf/SKILL.md` 与 `magnus/SKILL.md`；`.human/skills` 无对应文件。
- `.human/skills` 多 `evolution-agent/references/main_report_template.md`；`.claude/skills` 无对应文件。
- 行数差异显著：`.claude/skills/main-agent/SKILL.md` 194 行 vs `.human/skills/main-agent/SKILL.md` 91 行；`.claude/skills/evolution-agent/SKILL.md` 207 行 vs `.human/skills/evolution-agent/SKILL.md` 101 行；`.claude/skills/evolution-agent/references/spawn_template_global.md` 84 行 vs `.human/.../spawn_template_global.md` 4 行。

【建议动作】不要再声明“镜像”；改为“.human 是审查稿，.claude 是执行版，关键协议字段必须双写同步”。标记：设计bug必修。

### 4.3 域 skill 名称与路由

【现状】部分漂移。

- `CLAUDE.md:237-242` 路由列 `optics-mie-reproduction`、`optics-magnus-platform`、`optics-magnus-artifacts`、`pdf`、`magnus`、`optics-agent-core`。
- `opencode.json:15-25` 顶层未 allow `pdf`、`magnus`、`optics-agent-core`。
- `optics-mie-reproduction/SKILL.md:91-93` 建议 COMSOL/Magnus 时切到 `optics-comsol-runtime` + `optics-comsol-batch` + `optics-magnus-platform`，但 SEPR skill 路由没有 `optics-comsol-runtime` / `optics-comsol-batch`。

【建议动作】SEPR 如果只做 Mie Python，去掉 COMSOL runtime 路由提示；如果要支持 COMSOL/Magnus，则补齐对应 skill 或改为指向 optics_agent 侧。标记：跑通后，除非首跑需要 COMSOL。

## 5. 统计

### 5.1 对 Claude 旧审计的验证/修正/扩展

- 验证准确：A1 capsule 断裂、A2 路径漂移、B 根状态过时、B 四选一残留、B todo 旧口径、B OpenCode skill 缺口、C1 深度不对称、D pdf/magnus 空白骨架，共 8 类。
- 部分修正：C2 PyMieScatt。文本残留准确；但当前 SEPR/optics_agent 工作树未发现 `compare_pymiessatt.py` 脚本文件。
- 扩展发现：`main_report_template.md` 的 `sweep_manifest` 旧 `result_class` 枚举；step11 “主 agent 自己做”与后续 sub-agent spawn 指令矛盾；`.human`/`.claude` 文件集合差异；`optics-mie-reproduction` 的 COMSOL skill 路由提示与 SEPR 实际 skill 集不一致。

### 5.2 23 条清单统计

- 已落地：3 条。
- 部分落地：12 条。
- 缺失：8 条。

### 5.3 总体判断

SEPR 的核心方向仍成立：固定拓扑、human gate、result_class、三层 verifier、六维裁决、冲突台账、provenance 五字段都已有骨架。当前最大问题不是“治理不够多”，而是若干设计契约未闭环：capsule 没有生产者、路径不统一、根状态过时、Claude/OpenCode 深度约束不对称、关键域 skill 空壳。建议先修这些自洽 bug，再用最小 Akimov Mie case 跑通一次；其余治理项（schema 工具、holdout、anytime-valid、记忆 utility）放到跑通后按真实断点增量添加。

## 6. 记忆记录

本次审计结论已存入 memento。

- 记忆 ID：`82893d40-e6d1-4c7b-8bd5-8f160cf964f8`
