# SEPR workflow-v3 文献调研风险报告

## 0. 执行摘要

本轮在已有 `papers/self-evolution/` 127 篇基础上，补充检索 2025-2026 新文献与 v3 特有角度，下载并分类整理到 `papers/SEPR/`。本报告按 v3 设计十块组织风险和经验。

最重要结论：v3 的大方向（4 agent、复现/自迭代分离、6 分类法、provenance、物理 verifier）是合理的，但必须把“长期资产写入”和“物理复现成功声明”变成强证据门。最危险的不是 agent 失败，而是 agent 给出 plausible-but-wrong 的可读报告，并把失败经验沉淀成长期 skill/记忆。

最高优先级风险：

1. LLM-as-judge / self-bias 把 pipeline success、fallback、diagnostic 当作 physical reproduction success。
2. 自迭代在 noisy verifier 上反复“分数涨就收”，产生假进步和 reward hacking。
3. 子 agent / subsubagent 递归、身份漂移、工具权限过宽，造成空跑或越权写长期文件。
4. 记忆污染：失败、surrogate、旧参数或 prompt injection 被未来检索为成功经验。
5. 参数化蓝图若无 typed schema、单位、范围、资源上限和 replay，会把扫描变成不可审计的随机实验。

## 1. 提示词工程：CLAUDE.md / SKILL.md / spawn 模版

### 经验

- 来源：Anthropic Skill docs、CLAUDE.md/AGENTS.md Web 检索、`2605.19362`、`2605.03353`、`2605.27955`。
- 严重度：高。
- 发现：always-on 指令应短而稳定，任务流程应放到按需加载的 skill，深层材料应继续拆到引用文件/脚本。`SKILL.md` 的 description 是触发器，body 是可执行/可审查流程，不应塞历史和泛泛原则。
- 对 v3 的含义：`.human/.claude + CLAUDE.md + SKILL.md + spawn 模版` 必须有分层边界。spawn 只传本任务必要上下文和输出 schema，不复制全局规则。

### 风险

- 来源：`2402.06363 StruQ`、`2606.27567 On the Inseparability of Instructions and Data`、`2604.26615 TDD Governance`。
- 严重度：高。
- 发现：外部文本中的指令很难和真实系统指令完全隔离；prompt 优化若只看自评分数会优化成“更会通过 judge”。
- 对 v3 的含义：论文、网页、旧日志、旧报告进入 prompt 时必须标记为 data。任何外部文本都不能改变 tool 权限、写入长期资产或报告成功口径。

### 建议

- `CLAUDE.md/AGENTS.md`：只放跨任务硬规则、目录边界、危险操作和 skill 路由。
- `SKILL.md`：放某类任务的输入、步骤、输出、验证和失败处理。
- `spawn template`：放本轮任务上下文、允许工具、禁止动作、max turns、输出 schema。
- 所有 prompt 变更走候选分支，不直接 Absorb。

## 2. 子 agent 系统：4 agent + subsubagent + spawn 拼接

### 经验

- 来源：Claude Code Subagents docs、Agent Teams docs、`2606.27416 Glite ARF`、`2605.25746 Structure-Guided Orchestration`、`2501.06322 Multi-Agent Collaboration Survey`。
- 严重度：中-高。
- 发现：子 agent 适合隔离大规模阅读、日志分析、并行验证；不适合无边界地协作改同一产物。复杂任务中父 agent 的 synthesis 质量比单个子 agent 更关键。
- 对 v3 的含义：4 agent 架构可以保留，但每次 spawn 必须声明 role、scope、input artifact、output schema、forbidden actions、tool allowlist 和 evidence requirement。

### 风险

- 来源：`2511.09710 Echoing` 旧库摘要、`2606.09832 ASAF`、Claude nested subagent docs。
- 严重度：高。
- 发现：多 agent 长对话容易身份漂移；嵌套子 agent 若允许继续 spawn，会产生递归和成本失控；通用 subagent 默认继承过多工具会造成越权。
- 对 v3 的含义：subsubagent 只能用于叶子研究/验证；默认不允许写 `.human/.claude`、不允许改 skill、不能启动长期任务。

### 建议

- 每个 agent 输出固定头：`role`、`task_scope`、`evidence_refs`、`confidence`、`blocked_by`、`recommended_action`。
- 叶子 agent 禁用继续 spawn；只有 orchestrator 能 fan-out。
- fan-out 数量和嵌套深度进入 run manifest。

## 3. 自迭代系统：evolution workflow 6 步

### 经验

- 来源：`2603.25111 SEVerA`、`2605.22905 EVE-Agent`、`2510.16079 EvolveR`、`2605.17721 EXG`。
- 严重度：高。
- 发现：自迭代需要证据可验证、经验图、生命周期和版本化，不应从一次自然语言反思直接更新长期规则。
- 对 v3 的含义：evolution workflow 的每条候选经验必须绑定具体 run、artifact、日志、数值指标或人工评审。

### 风险

- 来源：`2606.08106 PACE`、`2606.26294 Red Queen Gödel Machine`、`2606.16682 Evaluator Preference Collapse`、`2605.09315 Do Self-Evolving Agents Forget`、`2602.15654 Zombie Agents`。
- 严重度：高。
- 发现：自迭代会产生 adaptive multiple testing、evaluator reward hacking、能力遗忘和持久注入。反复使用同一 verifier 会把 verifier 漏洞优化成规则。
- 对 v3 的含义：不能“分数涨就吸收”；必须有 holdout、回归测试、人工 gate、supersede/rollback 和负迁移检测。

### 建议

- 默认流转：失败观察 Save -> 候选经验 Improve -> 多次证据通过 Absorb -> 过期/局部 Archive -> 有害 Drop。
- 每轮 evolution 设置最大候选数、最大接受数、最大重试数。
- 被 Absorb 的规则必须有反例检查和旧能力回归检查。

## 4. 6 分类法：Save / Improve / Absorb / Fork / Archive / Drop + Tier 治理

### 经验

- 来源：`2606.28062 Single/Multi Truth Data Fusion`、`2306.08302 Unifying LLMs and KGs`、`2208.08130 Knowledge Graph Curation`。
- 严重度：高。
- 发现：知识管理要处理单真值、多真值、冲突、过期和来源权重，不能只有“保留/删除”。
- 对 v3 的含义：六分类法可行，但每个裁决必须记录 scope、evidence、conflicts、supersedes 和 review tier。

### 风险

- 来源：`2410.03659 Cross-Modality Knowledge Conflicts`、`2606.28270 Agent-Native Immune System`。
- 严重度：高。
- 发现：多来源冲突会被 LLM 合成成连贯但错误的结论；agent-native 防御必须在执行环中，而非外部静态说明。
- 对 v3 的含义：论文、代码、仿真日志、图像、人工意见冲突时，不允许 LLM 自动调和；必须触发 Tier-2/3。

### 建议

- 新增 `conflict ledger`：记录冲突项、来源、当前采用项、被拒项、裁决人/agent、复查条件。
- Tier-1 只处理低风险文档/摘要；Tier-2 处理 skill/记忆更新；Tier-3 处理物理成功声明、workflow 结构、蓝图执行口径。

## 5. workflow 结构：11 步复现 + 6 步自迭代

### 经验

- 来源：`2604.18752 Scientific Human-Agent Reproduction Pipeline`、`2604.21910 From Research Question to Scientific Workflow`、`2603.06394 Schema-Gated Scientific Workflows`、`2601.09749 R-LAM`。
- 严重度：高。
- 发现：科学 workflow 最关键是把自由语言协商与严格执行分离。schema gate、deterministic execution、logged-only execution、replay/fork 是科学 agent 的底线。
- 对 v3 的含义：11 步可以由 agent 协助，但执行和验收必须由 schema、artifact 和 verifier 约束。

### 风险

- 来源：`2604.25345 Plausible but Wrong`、`2509.23735 Lifecycle Failures`。
- 严重度：高。
- 发现：科学 agent 的高危失败是“看起来合理但错”，不是显式报错。
- 对 v3 的含义：每步产物必须独立可审查；最终报告必须先声明 result class。

### 建议

- 复现 11 步每步都要有 `input_artifacts`、`output_artifacts`、`quality_gate`、`retry_budget`、`blocker_condition`。
- 自迭代 6 步每步都要有 `candidate_id`、`evidence_ref`、`decision`、`tier`、`rollback_ref`。

## 6. AI 判断自己复现结果是否正确

### 经验

- 来源：`2312.15640 Correctness in Scientific Computing`、`2606.27416 Glite ARF`、`2606.28277 Automating Scientific Review`。
- 严重度：高。
- 发现：科学正确性需要可复现执行、过程 provenance、外部 verifier 和人工/领域审查。AI 可以帮助组织审查，但不能替代物理判定。
- 对 v3 的含义：AI 的职责是列证据、解释 verifier、指出缺口；最终“物理复现成功”由 deterministic/physical verifier + 人审 gate 决定。

### 风险

- 来源：`2604.18805 AI Agents Lack Scientific Reasoning`、`2410.10934 Agent-as-a-Judge`、`2502.06193 LLM-as-Judge in SE`、`2509.18658 Uncertainty of LLM-as-Judge`。
- 严重度：高。
- 发现：LLM judge 有自偏好、顺序偏差、不确定性和过程遗漏；agent 可执行 workflow 但科学推理弱。
- 对 v3 的含义：LLM 不能单独判断“图像像不像”“趋势对不对”。必须使用数值指标、物理约束、极限退化、论文图量化比较。

### 建议

- 报告状态必须分为：`not_run`、`pipeline_completed`、`simulation_completed`、`diagnostic_only`、`surrogate_fallback`、`partial_physical_match`、`physical_reproduction_success`。
- LLM reviewer 输出必须包含 uncertainty 和 missing evidence。

## 7. 失败防护/防空跑：重跑上限、终止判断、LoopTrap

### 经验

- 来源：`2606.06324 Harness Flaws`、`2509.23735 Lifecycle Failures`、Web 搜索 agent loop prevention。
- 严重度：高。
- 发现：空跑通常不是显式死循环，而是相同错误、相同工具调用、相同修复建议不断重复。
- 对 v3 的含义：LoopTrap 不能只靠 prompt 说“不要循环”，必须记录 retry fingerprint。

### 风险

- 来源：`2606.08106 PACE`、`2606.06114 Healthy Evolution`、`2606.28235 Govern the Repository, Not the Agent`。
- 严重度：高。
- 发现：局部 agent 看似有进展，系统层面可能积累 integration friction、成本和错误资产。
- 对 v3 的含义：防空跑要在节点级、case 级、evolution 级和仓库级同时计数。

### 建议

- 每个节点：`max_attempts=2-3`，同 fingerprint 第二次失败即 blocker。
- 每个 case：设置 max wall-clock、max spawned agents、max external searches、max simulation retries。
- 每次 retry 必须有新证据或新假设；没有新信息的 retry 直接 Drop/Archive。

## 8. 记忆系统：memento + provenance 五要素

### 经验

- 来源：`2508.02866 PROV-AGENT`、`2509.13978 Interactive Workflow Provenance`、`2601.18204 MemWeaver`、`2603.17787 Governed Memory`。
- 严重度：高。
- 发现：provenance 是证据层，memory 是经验层。二者不能混同。
- 对 v3 的含义：memento 中的“经验”必须引用 run provenance；不能只写“某次成功了”。

### 风险

- 来源：`2604.15774 MemEvoBench`、`2605.09033 ShadowMerge`、`2605.27825 MRMMIA`、`2602.15654 Zombie Agents`。
- 严重度：高。
- 发现：长期记忆可能被污染、攻击、错误合并或泄漏。错误成功声明会长期毒化后续任务。
- 对 v3 的含义：所有失败、fallback、diagnostic、surrogate 结果必须强制写 result_class。

### 建议

- provenance 五要素建议为：`source_artifact`、`evidence_type`、`timestamp/version`、`scope/applicability`、`confidence/result_class`。
- 记忆写入前查重；写入后支持 supersede；Archive 旧规则但保留审计。

## 9. 蓝图扫描泛用：参数化蓝图/参数扫描

### 经验

- 来源：`2601.09749 R-LAM`、`2603.06394 Schema-Gated Workflows`、`1611.03543 signac`、`2105.00129 WfChef`、Magnus GitHub 检索。
- 严重度：高。
- 发现：可复用蓝图应是 typed executable primitive，而不是脚本加说明。参数、单位、合法范围、资源、输出指标和 replay/fork 都应机器可读。
- 对 v3 的含义：蓝图扫描必须把 sweep 变量和固定假设分开；每个参数有单位、范围、物理约束和默认值。

### 风险

- 来源：`2509.09915 Scientific Workflows in Agentic Era`、`2505.05428 Federated Agents`、`2605.20819 DynaMate2`。
- 严重度：中-高。
- 发现：agentic workflow 正走向 adaptive/swarm，但真正自治组合仍实验性强；科学场景更重视 replay 和 audit。
- 对 v3 的含义：SEPR 现阶段应允许参数扫描 adaptive fork，但不允许 agent 自动改 workflow 拓扑。

### 建议

- 蓝图 schema 至少包含：`parameters`、`units`、`bounds`、`fixed_assumptions`、`resource_policy`、`expected_outputs`、`verifier_hooks`、`stop_rules`。
- 参数扫描结果必须写 sweep manifest，支持复跑单点和复现图。

## 10. 物理 verifier：硬约束 / 极限退化 / 论文图量化

### 经验

- 来源：`2312.15640 Correctness in Scientific Computing`、`2103.09899 V&V Turbulence`、`2601.19818 Learn and Verify PINNs`、`2401.04146 Mie Scattering Review`。
- 严重度：高。
- 发现：verification 与 validation 要分开。硬约束验证代码/数值是否自洽；极限退化验证模型在已知极限是否正确；论文图量化验证目标现象是否匹配。
- 对 v3 的含义：三层 verifier 是 v3 最关键的科学防线，应高于 LLM reviewer。

### 风险

- 来源：`2512.22261 Physics Constraint Paradox`、Mie scattering review。
- 严重度：中。
- 发现：物理约束不应乱加；约束适用域、数值容差和模型假设不匹配时会误判。
- 对 v3 的含义：每个 verifier 必须写适用条件、容差、失败解释和“不适用”条件。

### 建议

- 硬约束失败：默认不可报告物理复现成功。
- 极限退化失败：默认回到模型/数值设置排查。
- 论文图量化失败：区分参数缺失、模型简化、数值错误和论文不可复现。

## 附录 A. 本轮目录与下载统计

本轮创建目录：

```text
papers/SEPR/A_prompt_engineering/{success,failure,survey}
papers/SEPR/B_subagent_orchestration/{success,failure,survey}
papers/SEPR/C_self_iteration/{success,failure,survey}
papers/SEPR/D_taxonomy_knowledge_governance/{success,failure,survey}
papers/SEPR/E_workflow_structure/{success,failure,survey}
papers/SEPR/F_reproduction_correctness/{success,failure,survey}
papers/SEPR/G_failure_loop_guard/{success,failure,survey}
papers/SEPR/H_memory_provenance/{success,failure,survey}
papers/SEPR/I_blueprint_parameter_scan/{success,failure,survey}
papers/SEPR/J_physical_verifier/{success,failure,survey}
papers/SEPR/K_surveys/{success,failure,survey}
```

下载统计（含少量跨类重复 PDF，用于不同子 agent 独立阅读）：

| 类别 | 篇数 | 重点 |
|---|---:|---|
| A 提示词工程 | 8 | SKILL.md、prompt injection、system prompt optimization |
| B 子 agent 编排 | 8 | identity、orchestration、parallel agents、credit assignment |
| C 自迭代 | 10 | verified self-evolution、PACE、Red Queen、forgetting、zombie agents |
| D 分类/知识治理 | 8 | KG、truth fusion、conflict、agent immune system |
| E workflow 结构 | 10 | scientific reproduction pipeline、schema-gated workflow、R-LAM、plausible-but-wrong |
| F 正确性判断 | 10 | scientific review、LLM-as-judge、AI science reasoning、scientific correctness |
| G 失败/空跑防护 | 8 | harness flaws、lifecycle failures、PACE、loop/evaluator collapse |
| H 记忆/provenance | 9 | PROV-AGENT、MemWeaver、memory poisoning、memory inference |
| I 蓝图/参数扫描 | 9 | R-LAM、schema gate、signac、WfChef、federated agents |
| J 物理 verifier | 8 | V&V、PINN verifier、Mie、physics constraints |
| K 综述 | 6 | self-evolving agents、trustworthy agentic AI、agentic science |
| 合计 | 94 | 2025-2026 为主，兼收基础 V&V/工作流论文 |

## 附录 B. 搜索覆盖

使用过的检索源：

- `academic-research_search_papers`：arXiv 2025-2026 多关键词检索。
- `arxiv-mcp_search_arxiv`：按 self-evolving、skill、multi-agent、scientific workflow、verifier 等补充检索。
- `exa_web_search_exa`：CLAUDE.md/SKILL.md、subagent、科学复现验证、参数化 workflow 等 Web 搜索；后续触发免费额度限制。
- `firecrawl_search`：补充 AI scientific verification、loop prevention、progressive disclosure、parameterized scientific workflow。
- `github_search_repositories`：补充 agent skills/AGENTS.md/linter 和 multi-agent framework 相关仓库。

## 附录 C. 并发阅读子 agent 产出位置

- 子 agent 上下文：`papers/SEPR/CONTEXT-for-subagent.md`。
- A-K 分类阅读产出：`papers/SEPR/CATEGORY-READING-NOTES.md`。
- 总报告：`papers/SEPR/REVIEW-REPORT.md`。
