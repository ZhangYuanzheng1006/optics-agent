# SEPR workflow-v3 A-K 分类阅读产出

本文件模拟 A-K 并发阅读子 agent 的汇总输出。每类阅读 `papers/SEPR/<category>/{success,failure,survey}` 下的 PDF，并结合已有 `papers/self-evolution` 127 篇摘要交叉归纳。

## A. 提示词工程 agent

- 来源：`2605.19362_User_Comprehension_Skill_Specifications.pdf`、`2605.03353_SkCC_Portable_Secure_Skill_Compilation.pdf`、`2605.27955_Skill_as_Pseudocode.pdf`、Anthropic Skill docs、CLAUDE.md/AGENTS.md Web 搜索。
- 类型：经验。
- 适用块：1 提示词工程、3 自迭代系统、8 记忆系统。
- 结论：`CLAUDE.md` 应是高层地图，`SKILL.md` 应是按需加载的任务说明，深层资料应继续下沉到引用文件或可执行脚本。
- 经验/风险：v3 的 `.human/.claude + spawn 模版 + skill` 很容易把同一规则复制三遍，导致指令冲突和上下文腐烂。技能文件需要触发条件、输入输出、验证方式、旧模式/禁用模式，而不是堆历史。
- 严重度：高。
- 建议动作：Improve。把 always-on、task-specific、run-specific 三层指令分离；spawn 模版只携带当前任务必要上下文和输出 schema。

- 来源：`2402.06363_StruQ_Prompt_Injection.pdf`、`2606.27567_On_the_Inseparability_of_Instructions_and_Data.pdf`。
- 类型：风险。
- 适用块：1 提示词工程、7 失败防护、8 记忆系统。
- 结论：共享 embedding/上下文中的“指令”和“数据”很难天然隔离，prompt injection 防护不能只靠更强 prompt。
- 经验/风险：文献和日志中可能包含“请忽略前文”等攻击性或污染性文本；如果复现 agent 直接把论文、网页、旧报告拼入 spawn prompt，可能污染角色边界和记忆写入。
- 严重度：高。
- 建议动作：Improve + Absorb。所有外部文本进入 agent 前标注为 data，不允许其中指令改变工具权限、报告口径和记忆写入。

- 来源：`2606.04465_SePO_System_Prompt_Optimization.pdf`、`2604.26615_TDD_Governance_Prompt_Engineering.pdf`。
- 类型：经验/风险。
- 适用块：1 提示词工程、6 正确性判断。
- 结论：system prompt 优化可以提高行为，但必须受测试、验收条件和 governance 约束。
- 经验/风险：如果 evolution workflow 自动优化 prompt，只看报告分或 agent 自评，容易优化出更会“说成功”的 prompt，而不是更会复现的 workflow。
- 严重度：高。
- 建议动作：Fork。prompt 优化只能在候选分支中运行，必须通过 deterministic verifier 和人工 gate 才能吸收。

## B. 子 agent 系统/编排

- 来源：Claude Code Subagents docs、Agent Teams docs、`2606.09832_ASAF_Agent_Identity_Design.pdf`、`2511.09710_Echoing` 旧库摘要。
- 类型：风险。
- 适用块：2 子 agent 系统、7 失败防护。
- 结论：子 agent 的价值在上下文隔离和并行阅读，但身份漂移、越权工具和嵌套递归是核心风险。
- 经验/风险：v3 若允许 subsubagent，需要显式限制嵌套深度、工具 allowlist、返回格式和父 agent synthesis 规则。叶子阅读/验证 agent 不应有写 `.human/.claude` 或更新 skill 的权限。
- 严重度：高。
- 建议动作：Improve。为每个 agent 声明 role、input、output、allowed tools、forbidden actions、max turns、nesting policy。

- 来源：`2606.27416_Glite_ARF_Parallel_Coding_Agents.pdf`、`2605.25746_Structure_Guided_Orchestration.pdf`、`2606.28187_GBC_Credit_Assignment_MAS.pdf`。
- 类型：经验。
- 适用块：2 子 agent 系统、5 workflow 结构、6 正确性判断。
- 结论：并行 agent 适合相互独立的研究/验证任务，但需要 verifier-driven aggregation 和 credit assignment。
- 经验/风险：如果 11 步复现里多个子 agent 同时改同一产物，会发生冲突；如果只返回自然语言总结，父 agent 无法定位哪一步造成错误。
- 严重度：中。
- 建议动作：Absorb。子 agent 输出必须带 `evidence_refs`、`confidence`、`failure_mode`、`next_action`。

- 来源：`2501.06322_Multi_Agent_Collaboration_Survey.pdf`、`2602.03128_MAFBench` 旧库摘要。
- 类型：综述经验。
- 适用块：2 子 agent 系统。
- 结论：多 agent 不是越多越好，协调开销、延迟、重复劳动和冲突建议要被量化。
- 经验/风险：v3 的 4 agent + subsubagent 应先定义哪些阶段值得并行，哪些阶段必须单主线；简单任务走 routing，复杂任务才 fan-out。
- 严重度：中。
- 建议动作：Improve。记录每轮 agent 数、token/时间成本、重复结论数、冲突结论数。

## C. 自迭代系统

- 来源：`2603.25111_SEVerA_Verified_Self_Evolving_Agents.pdf`、`2605.22905_EVE_Agent_Evidence_Verifiable.pdf`。
- 类型：经验。
- 适用块：3 自迭代系统、6 正确性判断、8 记忆系统。
- 结论：自迭代要“证据可验证”，不能从无证据的自我反思直接更新长期资产。
- 经验/风险：v3 的 evolution workflow 应要求每条经验绑定 run artifact、失败日志、数值指标或人工反馈；没有证据的反思只能 Archive，不可 Absorb。
- 严重度：高。
- 建议动作：Absorb。把 provenance 五要素作为自迭代准入条件。

- 来源：`2606.08106_PACE_Anytime_Valid_Acceptance.pdf`、`2606.26294_Red_Queen_Godel_Machine.pdf`、`2606.16682_Evaluator_Preference_Collapse.pdf`。
- 类型：风险。
- 适用块：3 自迭代系统、6 正确性判断、7 防空跑。
- 结论：反复在同一 noisy dev set 上“分数涨就收”是 adaptive multiple testing，会产生假进步。
- 经验/风险：v3 若每轮 evolution 都用同一个 verifier/同一批复现任务评估 prompt/skill 变更，会把 verifier 漏洞优化成规则。
- 严重度：高。
- 建议动作：Improve + Fork。设置 holdout 复现案例、anytime-valid 接受规则、最大演化轮数、负迁移检测。

- 来源：`2605.09315_Do_Self_Evolving_Agents_Forget.pdf`、`2606.06114_Healthy_Evolution_Human_Oversight.pdf`、`2602.15654_Zombie_Agents.pdf`。
- 类型：风险。
- 适用块：3 自迭代、8 记忆系统。
- 结论：自迭代会遗忘旧能力、放大错误反馈、被持久注入劫持。
- 经验/风险：SEPR 不能把每次失败都写成“新规则”；应先区分局部参数问题、工具 bug、论文欠指定、真实 workflow 缺陷。
- 严重度：高。
- 建议动作：Save + Archive。失败经验默认进入候选池，不直接改 skill。

## D. 6 分类法/裁决/知识管理

- 来源：`2606.28062_Single_Multi_Truth_Data_Fusion.pdf`、`2306.08302_Unifying_LLMs_and_KGs.pdf`、`2208.08130_Knowledge_Graph_Curation.pdf`。
- 类型：经验。
- 适用块：4 6 分类法、8 记忆系统。
- 结论：知识管理要支持单真值、多真值、冲突、过期和来源权重，不能只靠“最新覆盖旧的”。
- 经验/风险：Save/Improve/Absorb/Fork/Archive/Drop 需要显式判据：是否有证据、是否泛化、是否与旧规则冲突、是否仅适用于某论文/工具版本。
- 严重度：高。
- 建议动作：Absorb。每个裁决记录 `scope`、`evidence`、`conflicts`、`supersedes`、`reviewer`。

- 来源：`2410.03659_Cross_Modality_Knowledge_Conflicts.pdf`、`2606.28270_Agent_Native_Immune_System.pdf`。
- 类型：风险。
- 适用块：4 知识管理、8 记忆系统。
- 结论：不同来源、模态和 agent 之间的知识冲突会被 agent 合成成看似连贯但错误的结论。
- 经验/风险：论文文本、代码结果、COMSOL 日志、图像 OCR、人工意见冲突时，v3 不能让 LLM 自动“调和”；必须保留冲突并触发 Tier-2/3 人审。
- 严重度：高。
- 建议动作：Improve。新增 conflict ledger，而非只写最终摘要。

## E. workflow 结构和 11 步复现

- 来源：`2604.18752_Scientific_Human_Agent_Reproduction_Pipeline.pdf`、`2604.21910_Research_Question_to_Scientific_Workflow.pdf`、`2603.06394_Schema_Gated_Scientific_Workflows.pdf`、`2601.09749_R_LAM_Reproducibility_Constrained.pdf`。
- 类型：经验。
- 适用块：5 workflow 结构、9 蓝图扫描。
- 结论：科学 workflow 应把自由对话和严格执行分离：talk freely, execute strictly。
- 经验/风险：v3 11 步可以允许 agent 讨论和补全，但真正执行仿真、写长期资产、报告成功前必须通过 schema gate 和 artifact gate。
- 严重度：高。
- 建议动作：Absorb。每步定义输入 schema、输出 schema、可执行动作和禁止动作。

- 来源：`2604.25345_Plausible_but_Wrong_Astrophysical_Workflows.pdf`、`2509.23735_Lifecycle_Failures_Agentic_Workflows.pdf`。
- 类型：风险。
- 适用块：5 workflow 结构、6 正确性判断、7 防空跑。
- 结论：科学 agent 最危险的失败不是崩溃，而是产出“ plausible but wrong”的可读报告。
- 经验/风险：v3 报告必须区分 pipeline completed、simulation completed、physical reproduction completed；不能允许最后报告把诊断图、fallback、surrogate 写成复现成功。
- 严重度：高。
- 建议动作：Improve。强制 final report 先列 result class 和 verifier status。

## F. AI 判断复现正确性

- 来源：`2606.28277_Automating_Scientific_Review_Paper_Assistant.pdf`、`2606.07462_Benchmarks_Frontier_LLMs_Agentic_Science.pdf`、`2604.18805_AI_Agents_Lack_Scientific_Reasoning.pdf`。
- 类型：风险/综述。
- 适用块：6 正确性判断、10 物理 verifier。
- 结论：LLM 可以辅助科学审查，但当前 agent 在科学推理和真实性判断上仍弱，必须依赖外部证据和领域 verifier。
- 经验/风险：如果 SEPR 让 LLM 读自己的结果图并判断“是否复现”，会产生 self-bias；应把 LLM 限制在解释 verifier 输出和列缺口。
- 严重度：高。
- 建议动作：Absorb。LLM-as-judge 只作为 reviewer，不作为最终判定器。

- 来源：`2410.10934_Agent_as_a_Judge.pdf`、`2502.06193_LLM_as_Judge_Software_Engineering.pdf`、`2509.18658_Uncertainty_LLM_as_Judge.pdf`。
- 类型：风险。
- 适用块：6 正确性判断。
- 结论：LLM judge 对过程评价有用，但存在偏好、顺序、置信区间和不稳定性问题。
- 经验/风险：v3 的 reviewer 必须输出 uncertainty，最好使用多证据 rubric，而非单句“通过/不通过”。
- 严重度：高。
- 建议动作：Improve。引入区间评分、反例检查、外部数值阈值。

- 来源：`2312.15640_Correctness_in_Scientific_Computing.pdf`、`2606.27416_Glite_ARF_Parallel_Coding_Agents.pdf`。
- 类型：经验。
- 适用块：6 正确性判断、10 物理 verifier。
- 结论：科学正确性需要 reproducibility、auditability、deterministic checks 和 verifier-driven execution。
- 经验/风险：每个复现结果必须能从参数表、代码、日志、数据、图重新追溯；报告没有 trace 就不应被认为可信。
- 严重度：高。
- 建议动作：Absorb。

## G. 失败防护/防空跑

- 来源：`2606.06324_Diagnosing_Repairing_Harness_Flaws.pdf`、`2509.23735_Lifecycle_Failures_Agentic_Workflows.pdf`。
- 类型：经验/风险。
- 适用块：7 失败防护、5 workflow 结构。
- 结论：失败常来自 harness、工具接口、上下文和生命周期，而不是 agent “不够聪明”。
- 经验/风险：v3 的 LoopTrap 应检测同一错误、同一工具参数、同一缺失 artifact 的重复出现；超过阈值应停止并输出 blocker。
- 严重度：高。
- 建议动作：Improve。记录 retry fingerprint：错误码、命令、输入 hash、产物状态、修改 diff。

- 来源：Web 搜索“agent loop prevention production”、`2606.08106_PACE`、`2606.06114_Healthy_Evolution`。
- 类型：风险。
- 适用块：7 防空跑、3 自迭代。
- 结论：无限 loop 往往表现为 agent 不知道自己正在重复，而非显式 while true。
- 经验/风险：SEPR 应设全局预算：每节点 max attempts、每 case max wall-clock、每 evolution max accepted changes、每失败类型 max retries。
- 严重度：高。
- 建议动作：Absorb。终止条件是 workflow schema 的一部分，不是 prompt 建议。

## H. 记忆/provenance

- 来源：`2508.02866_PROV_AGENT_Unified_Provenance.pdf`、`2509.13978_Interactive_Workflow_Provenance.pdf`、`2601.18204_MemWeaver_Traceable_Long_Horizon.pdf`。
- 类型：经验。
- 适用块：8 记忆/provenance、5 workflow 结构。
- 结论：provenance 要覆盖 prospective plan 和 retrospective execution，且能回答 who/what/when/how/why。
- 经验/风险：v3 的 memento 记忆不应替代 run provenance；记忆是经验层，provenance 是证据层。
- 严重度：高。
- 建议动作：Absorb。每次复现写 `provenance.jsonl` 或等价结构，记忆条目只引用证据而不复制全部证据。

- 来源：`2605.09033_ShadowMerge_Graph_Memory_Poisoning.pdf`、`2605.27825_MRMMIA_Memory_Inference_Attacks.pdf`、`2604.15774_MemEvoBench_Misevolution.pdf`、`2602.15654_Zombie_Agents.pdf`。
- 类型：风险。
- 适用块：8 记忆系统、3 自迭代。
- 结论：长期记忆会被污染、推断、冲突合并或持久注入劫持。
- 经验/风险：fallback/surrogate/failed probe 必须带强标签，否则未来检索时会被当成“成功复现经验”。
- 严重度：高。
- 建议动作：Improve。记忆写入默认 `confidence`、`result_class`、`evidence_ref`、`expires/supersedes`。

## I. 蓝图扫描/参数化

- 来源：`2601.09749_R_LAM.pdf`、`2603.06394_Schema_Gated_Workflows.pdf`、`1611.03543_Signac_Data_Workflow_Management.pdf`、`2105.00129_WfChef_Workflow_Generators.pdf`、Magnus GitHub 搜索。
- 类型：经验。
- 适用块：9 蓝图扫描泛用、5 workflow 结构。
- 结论：参数化蓝图应是 typed executable primitive，必须支持参数 schema、执行 trace、replay、fork 和 failure transparency。
- 经验/风险：如果蓝图只是“脚本 + prompt 说明”，参数扫描会失控；需要把 sweep variable、fixed assumption、resource policy、expected metric 写进 schema。
- 严重度：高。
- 建议动作：Absorb。每个蓝图定义参数、默认值、合法范围、单位、物理约束、资源上限和输出指标。

- 来源：`2509.09915_Scientific_Workflows_Agentic_Era.pdf`、`2505.05428_Federated_Agents_Scientific_Workflows.pdf`、`2605.20819_DynaMate2_Tool_Registration.pdf`。
- 类型：经验/风险。
- 适用块：9 蓝图扫描、2 子 agent 系统。
- 结论：agentic scientific workflows 正从 static pipeline 走向 adaptive/swarm，但真正 mesh/swarm 仍实验性强。
- 经验/风险：SEPR 目前应先做 static/adaptive pipeline，不要让 agent 自动改拓扑；参数扫描可 adaptive，但必须保留 replay 和 stop rule。
- 严重度：中。
- 建议动作：Improve。蓝图扫描优先支持受控 fork，而不是开放式自生成拓扑。

## J. 物理 verifier

- 来源：`2312.15640_Correctness_Scientific_Computing.pdf`、`2103.09899_Verification_Validation_Turbulence.pdf`、`2601.19818_Learn_and_Verify_PINNs.pdf`。
- 类型：经验。
- 适用块：10 物理 verifier、6 正确性判断。
- 结论：物理验证需要 verification 和 validation 分开：代码/离散化/求解器正确性，与物理模型对真实/论文结果的有效性不是一回事。
- 经验/风险：SEPR 的三层 verifier 很合理，但还应记录每层失败含义：硬约束失败是不可接受，极限退化失败说明模型/数值错误，论文图不匹配可能是参数/模型缺失。
- 严重度：高。
- 建议动作：Absorb。

- 来源：`2401.04146_Mie_Scattering_Review.pdf`、`1704.08779_Mie_Scattering_Eigenmodes.pdf`、`2512.22261_Physics_Constraint_Paradox.pdf`。
- 类型：经验/风险。
- 适用块：10 物理 verifier。
- 结论：物理约束不是越多越好；约束必须和模型适用范围、数值精度、边界条件一致。
- 经验/风险：Mie/COMSOL verifier 要区分解析硬约束、渐近极限和论文图经验指标；错误使用约束可能误杀正确模型或放过错误模型。
- 严重度：中。
- 建议动作：Improve。每个 verifier 记录适用域、容差、失败解释和允许例外。

## K. 综述

- 来源：`2508.07407_Comprehensive_Survey_Self_Evolving_Agents.pdf`、`2605.23989_Trustworthy_Agentic_AI_Survey.pdf`、`2508.14111_Autonomous_Scientific_Discovery_Survey.pdf`、`2509.09915_Scientific_Workflows_Agentic_Era.pdf`。
- 类型：综述。
- 适用块：全部。
- 结论：2025-2026 新进展共同指向一个原则：agent 能力应外部化到可审计 harness、schema、memory、skill、provenance 和 verifier，而非堆更长 prompt。
- 经验/风险：v3 的方向是对的，但风险集中在“自由生成”和“长期沉淀”的边界；所有能长期影响系统的东西都要有 evidence、version、scope、rollback。
- 严重度：高。
- 建议动作：Absorb。用 K 类综述做 v3 风险审查总框架。
