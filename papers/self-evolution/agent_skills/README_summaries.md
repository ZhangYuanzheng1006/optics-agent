# Agent Skills 文献摘要

## 2606.16523 SkillWiki: A Living Knowledge Infrastructure for Agent Skills
- 文件：`2606.16523_SkillWiki_Living_Knowledge_Infrastructure.pdf`
- 一句话结论：agent skill 需要像 Wikipedia/GitHub 一样的长期知识基础设施，而不是零散 markdown 文件。
- 核心方法/贡献：提出 SkillWiki，将轨迹、文档、API 规格、脚本、历史 skill 和执行经验转成可复用、可验证、可维护、带版本和溯源的 skill 资产，并提供知识到 skill、治理、溯源图和执行反馈闭环。
- 可用于我们 workflow 的经验：workflow 产物应保存证据来源、执行日志、失败反馈和版本关系，让 skill 与知识、工具、案例共同演化。
- 警告/风险：只做知识摄取会导致技能库膨胀；如果没有治理、验证和溯源，skill 会变成不可审计的提示堆。
- 可落到 optics_agent 的设计点：为每个 skill 增加 `source/evidence/provenance/status/version/execution_feedback` 字段，并将 `candidate/active/deprecated` 生命周期写入 workflow。
- 优先级：高

## 2606.15899 SkillVetBench: LLM-as-Judge for Multi-Dimensional Security Risk Evaluation in Open-Source LLM Agent Skills
- 文件：`2606.15899_SkillVetBench_Security_Risk_Evaluation_Open_Source_Skills.pdf`
- 一句话结论：开放 skill 生态必须在安装前做语义级、多维安全评分，传统代码扫描不足以覆盖 instruction-layer 风险。
- 核心方法/贡献：提出 SkillVetBench 和 SARS 风险分数，结合 LLM-as-Judge、CVSS v4.0、三档 verdict、SKV finding 与公开 leaderboard，对 skill 的指令、代码、配置和工具声明做静态语义评估。
- 可用于我们 workflow 的经验：skill 进入 active 前应经过结构化安全报告，记录评估模型、时间戳、风险维度、证据片段和置信度。
- 警告/风险：该方法不执行 skill，也不做动态污点追踪；模型间检测率差异大，分数只在相同 evaluator 下可比。
- 可落到 optics_agent 的设计点：新增 `security_review` gate，对候选 skill 输出 `risk_level/SARS-like dimensions/CVSS-like vector/verdict/evaluator_id`，高风险禁止自动启用。
- 优先级：高

## 2606.14154 SkillMutator: Benchmarking and Defending Language-and-Code Cross-modal Attacks on LLM Agent Skills
- 文件：`2606.14154_SkillMutator_Cross_modal_Attacks_on_Agent_Skills.pdf`
- 一句话结论：skill 的真实风险常来自 SKILL.md 语义与辅助脚本行为的组合，单看文本或单看代码都会漏检。
- 核心方法/贡献：提出 SkillMutator，构造 13 类语言-代码跨模态攻击；用四阶段推理轨迹蒸馏训练本地小模型扫描器，检测率从 17.1% 提升到 88.2%。
- 可用于我们 workflow 的经验：安全审计要比较“声明目的”和“实际脚本/资源行为”是否越界，而不只是查危险 API。
- 警告/风险：攻击可通过合法工作流伪装，如缓存、备份、兼容性处理；第三方扫描会泄露本地路径和私有上下文。
- 可落到 optics_agent 的设计点：安装或修改 skill 时运行本地 cross-modal 检查，要求每个脚本调用都能回溯到 SKILL.md 中明确的任务目的和权限边界。
- 优先级：高

## 2606.01139 SkillRevise: Improving LLM-Authored Agent Skills via Trace-Conditioned Skill Revision
- 文件：`2606.01139_SkillRevise_Trace_Conditioned_Skill_Revision.pdf`
- 一句话结论：冷启动 skill 不应一次生成后直接使用，而应通过执行轨迹、诊断和 verifier 进行有界修订。
- 核心方法/贡献：提出 SkillRevise，基于执行失败诊断、通用修复原则记忆、执行锚定编辑和 verifier-first 选择迭代修订 skill；在 SkillsBench 上将成功率从 36.05% 提升到 61.63%。
- 可用于我们 workflow 的经验：skill revision 应先定位失败与保留约束，再改 skill，并以 verifier 通过为首选，经验 utility 只作兜底。
- 警告/风险：过度实例化会把偶然路径写进 skill；过度抽象又无法指导执行，需要 trace-conditioned principles。
- 可落到 optics_agent 的设计点：为 paper reproduction workflow 增加 `diagnose -> retrieve_principle -> revise_candidate -> reexecute -> promote` 的候选 skill 修订回路。
- 优先级：高

## 2605.27955 Skill-as-Pseudocode: Refactoring Skill Libraries to Pseudocode for LLM Agents
- 文件：`2605.27955_Skill_as_Pseudocode.pdf`
- 一句话结论：自由文本 skill 会诱发反复检索和错误动作，typed pseudocode 能降低歧义与 token 成本。
- 核心方法/贡献：提出 SaP，将 markdown skill 聚类为 typed contract 和 concrete action template，通过 coverage、binding、replacement、risk 四类确定性检查后重写成伪代码化 skill。
- 可用于我们 workflow 的经验：skill 应同时给出“做什么”的 typed contract 和“怎么调用”的具体动作模板，避免让 agent 每次从散文中重新推导 schema。
- 警告/风险：自动改写可能丢失上下文或引入错误绑定；需要确定性校验和风险过滤。
- 可落到 optics_agent 的设计点：将 `.codex/skills` 中关键 workflow skill 拆成 `trigger/input/output/preconditions/postconditions/action_templates/validators`。
- 优先级：高

## 2605.27760 SkillGrad: Optimizing Agent Skills Like Gradient Descent
- 文件：`2605.27760_SkillGrad_Optimizing_Agent_Skills.pdf`
- 一句话结论：skill 可以被视作可优化参数，用轨迹损失、文本梯度和动量记忆系统性改进。
- 核心方法/贡献：提出 SkillGrad，将任务执行结果转为诊断梯度，使用 momentum agent 累积反复出现的问题，并由 patcher 对 skill package 做分层编辑。
- 可用于我们 workflow 的经验：多轮 reproduction 中重复失败模式应进入持久 memory overlay，而不是每次只写一次性反思。
- 警告/风险：训练式优化可能过拟合当前任务分布；patch 需要区分元数据、SKILL.md、脚本和资源层。
- 可落到 optics_agent 的设计点：在 workflow 结束节点生成 `skill_gradient`，记录失败证据、保留行为、建议 patch 层级和是否进入 active。
- 优先级：中

## 2605.17734 Harnessing LLM Agents with Skill Programs
- 文件：`2605.17734_Harnessing_LLM_Agents_with_Skill_Programs.pdf`
- 一句话结论：重要 skill 不应只是提示建议，而应升级为可执行的状态-动作干预函数。
- 核心方法/贡献：提出 HASP，把技能转成 Program Functions，含 `should_activate()`、`intervention()`、`emit_signals()`，可在推理时改写动作或注入纠错上下文，也可用于训练和自演化。
- 可用于我们 workflow 的经验：高价值 workflow guardrail 应在 agent loop 内有明确触发条件和干预方式，而不是只放在长说明中。
- 警告/风险：可执行干预会扩大权限和复杂度；未验证的 PF 可能比文本提示更危险。
- 可落到 optics_agent 的设计点：把“不要把 surrogate 报成物理复现成功”等强约束做成 runtime guardrail：检查状态、拦截 final_report、注入纠正要求。
- 优先级：高

## 2605.13716 SkillOps: Managing LLM Agent Skill Libraries as Self-Maintaining Software Ecosystems
- 文件：`2605.13716_SkillOps_Self_Maintaining_Skill_Libraries.pdf`
- 一句话结论：skill library 会积累技术债，必须有库级维护层，而不是只在任务执行时临时修补。
- 核心方法/贡献：提出 SkillOps，用 Skill Contract `(P,O,A,V,F)` 和 HSEG 图表示技能库，诊断 utility、compatibility、risk、validation gap，并执行 merge、repair、retire、add_validator、add_adapter。
- 可用于我们 workflow 的经验：技能治理应定期发现冗余、接口漂移、缺 validator、失败风险和兼容性问题。
- 警告/风险：库级清理对 retrieval-heavy agent 有益，但可能与任务时自修复策略冲突。
- 可落到 optics_agent 的设计点：建立 skill maintenance job，按 `candidate/active/deprecated` 管理，并为每个 active skill 强制配置 validator 和 failure modes。
- 优先级：高

## 2605.11770 Behavioral Integrity Verification for AI Agent Skills
- 文件：`2605.11770_Behavioral_Integrity_Verification_for_AI_Agent_Skills.pdf`
- 一句话结论：skill 安全的核心审计问题是“声明能力”和“实际能力”是否一致。
- 核心方法/贡献：提出 BIV，用 29 类 capability taxonomy 比较 metadata 声明行为与 code/instructions 实际行为；在 49,943 个 OpenClaw skills 上发现 80.0% 有偏差，并在恶意检测中达到 F1 0.946。
- 可用于我们 workflow 的经验：偏差证据可同时服务生态测量、根因分类和恶意检测；不应只给二元安全结论。
- 警告/风险：很多偏差来自开发者疏忽而非恶意；治理流程要区分 oversight、stale docs 和 adversarial intent。
- 可落到 optics_agent 的设计点：为每个 skill 维护 declared/actual capability 表，若实际触及文件、网络、shell、凭据或外部服务但声明缺失，则阻断 promotion。
- 优先级：高

## 2605.10990 Skill Drift Is Contract Violation: Proactive Maintenance for LLM Agent Skill Libraries
- 文件：`2605.10990_Skill_Drift_Is_Contract_Violation.pdf`
- 一句话结论：skill drift 本质是环境契约违约，监控应关注有角色意义的操作假设，而不是所有外部变化。
- 核心方法/贡献：提出 SkillGuard，从 skill 文档抽取可执行环境契约并验证依赖、API、URL、配置、schema、认证等 role-bearing assumptions；在 DriftBench 上实现高精度漂移检测和本地化修复。
- 可用于我们 workflow 的经验：依赖版本、COMSOL/Magnus 路径、许可证挂载、API URL 等应被标为 operational contract，并定期验证。
- 警告/风险：原始 CI 探针会产生大量误报；契约抽取不完整会漏检真实 drift。
- 可落到 optics_agent 的设计点：把 skills 与 workflow 中的外部假设写成 `environment_contracts`，对 active skill 做 proactive check，违约时转入 candidate/needs-repair。
- 优先级：高

## 2605.05846 LoopTrap: Termination Poisoning Attacks on LLM Agents
- 文件：`2605.05846_LoopTrap_Termination_Poisoning_Attacks.pdf`
- 一句话结论：攻击者可污染 agent 的终止判断，让任务明明完成却持续执行并消耗成本。
- 核心方法/贡献：定义 Termination Poisoning，提出 LoopTrap，通过四类脆弱性画像和自适应陷阱合成，在 8 个 agent、60 个任务上造成平均 3.57 倍步骤放大。
- 可用于我们 workflow 的经验：workflow 节点必须有外部 verifier、预算和硬停止条件，不能完全依赖 LLM 自评“是否完成”。
- 警告/风险：开放式、完成边界模糊的任务尤其易受攻击；恶意内容可能来自网页、文档、API 响应或 skill。
- 可落到 optics_agent 的设计点：所有长流程节点加 `max_steps/max_tokens/deadline/completion_verifier`，并在连续无新证据时强制转入诊断而非继续循环。
- 优先级：高

## 2605.00314 Semia: Auditing Agent Skills via Constraint-Guided Representation Synthesis
- 文件：`2605.00314_Semia_Auditing_Agent_Skills.pdf`
- 一句话结论：要静态审计 skill，需要把自然语言策略提升为可查询的结构化表示，而非让 LLM 直接给主观 verdict。
- 核心方法/贡献：提出 Semia，用 Skill Description Language 将 skill 转成 Datalog fact base，再用 Constraint-Guided Representation Synthesis 迭代生成、验证和评分，最终用 reachability query 检测风险。
- 可用于我们 workflow 的经验：安全属性可被表达为“污染输入是否绕过显式 safeguard 到达高影响 sink”的确定性查询。
- 警告/风险：LLM 一次性抽取 IR 容易漏掉关键 guard；必须有结构验证、语义回译评分和 witness path。
- 可落到 optics_agent 的设计点：为高权限 skill 生成简化 SDL：actions、sources、sinks、guards、human checkpoints，并用规则查询阻断无保护路径。
- 优先级：高

## 2604.23853 ClawTrace: Cost-Aware Tracing for LLM Agent Skill Distillation
- 文件：`2604.23853_ClawTrace_Cost_Aware_Tracing_for_Skill_Distillation.pdf`
- 一句话结论：从轨迹蒸馏 skill 时，必须把成本归因到步骤级，否则无法区分修 bug 和剪冗余。
- 核心方法/贡献：提出 ClawTrace 和 TraceCard，记录 LLM 调用、工具调用、子 agent、token/USD 成本、冗余工具簇和失败步骤；CostCraft 输出 preserve、prune、repair 三类 patch。
- 可用于我们 workflow 的经验：评估 skill 不应只看整体成功率，还要看不同规则类型的迁移行为和成本影响。
- 警告/风险：preserve 规则可能过拟合并导致质量回归；prune 规则反而可能是质量 guardrail。
- 可落到 optics_agent 的设计点：为 workflow run 生成小型 TraceCard，包含每步成本、产物、失败/修复标记，并把 skill patch 分为 preserve/prune/repair。
- 优先级：中

## 2604.03081 Supply-Chain Poisoning Attacks Against LLM Coding Agent Skill Ecosystems
- 文件：`2604.03081_Supply_Chain_Poisoning_Agent_Skill_Ecosystems.pdf`
- 一句话结论：恶意 skill 可把 payload 藏在文档示例和配置模板中，使 coding agent 在正常任务中复制并执行。
- 核心方法/贡献：提出 DDIPE 和 PoisonedSkills，用 LLM seed-mutation-validation 生成 1,070 个 adversarial skills，覆盖 15 类 MITRE ATT&CK；在多框架多模型下仍有 11.6% 到 33.5% 绕过率。
- 可用于我们 workflow 的经验：文档代码块、模板、示例脚本都应纳入供应链审查，不能只审 SKILL.md 主体。
- 警告/风险：显式恶意请求可被防住，但“备份、日志、兼容性、配置初始化”等伪装路径更危险。
- 可落到 optics_agent 的设计点：禁止 candidate skill 自动执行外部网络/文件外传/credential 访问；示例代码需经过同等审计和最小权限运行。
- 优先级：高

## 2604.02837 Towards Secure Agent Skills: Architecture, Threat Taxonomy, and Security Analysis
- 文件：`2604.02837_Towards_Secure_Agent_Skills.pdf`
- 一句话结论：Agent Skills 的严重风险来自架构性属性，不能只靠增量补丁解决。
- 核心方法/贡献：系统分析 Agent Skill 的 Creation、Distribution、Deployment、Execution 生命周期，提出 7 类威胁、17 个场景和 3 层攻击面，并总结真实安全事件和防御方向。
- 可用于我们 workflow 的经验：skill governance 要覆盖创建、分发、部署和执行全生命周期，而不是只在运行时做防护。
- 警告/风险：自然语言指令无 data-instruction 边界、一次批准长期信任、市场无强制审查、脚本以用户权限执行，是结构性缺陷。
- 可落到 optics_agent 的设计点：按生命周期定义 gate：authoring lint、distribution provenance、deployment permission tier、execution sandbox/approval。
- 优先级：高

## 2603.28815 SkillTester: Benchmarking Utility and Security of Agent Skills
- 文件：`2603.28815_SkillTester_Utility_and_Security_of_Agent_Skills.pdf`
- 一句话结论：skill 评估要同时比较 utility 和 security，且 utility 必须相对 no-skill 基线衡量。
- 核心方法/贡献：提出 SkillTester，通过 paired baseline/with-skill execution、实际 skill invocation 记录和独立安全 probe suite，输出 utility score、security score 和三档安全状态。
- 可用于我们 workflow 的经验：技能是否有用不能看单次成功，必须回答“相比不用 skill 改变了什么”。
- 警告/风险：该框架不是完整形式化认证，也不覆盖 runtime adaptation；公开输出需简洁，内部证据需可追溯。
- 可落到 optics_agent 的设计点：新增 skill benchmark harness：同一论文复现子任务分别跑 no-skill 与 with-skill，记录成功率、步骤、token、风险探针结果。
- 优先级：高

## 2603.25111 SEVerA: Verified Self-Evolving Agents
- 文件：`2603.25111_SEVerA_Verified_Synthesis_Self_Evolving_Agents.pdf`
- 一句话结论：自演化 agent 需要硬形式约束，否则优化性能会诱导违规、作弊或绕过安全规则。
- 核心方法/贡献：提出 Formally Guarded Generative Models 和 SEVerA，用一阶逻辑为每次生成模型调用指定输出契约，通过 rejection sampler 和 verified fallback 保证硬约束，再优化软目标。
- 可用于我们 workflow 的经验：critical workflow 节点应把不可违反的行为写成机器可检验 hard constraints，而不是自然语言建议。
- 警告/风险：形式约束覆盖不到的行为仍可能出错；fallback 与拒绝采样会增加成本并可能影响输出多样性。
- 可落到 optics_agent 的设计点：对报告生成、结果标注、文件写入路径、私有数据边界设置硬约束 verifier，例如禁止把 diagnostic/surrogate 标为 physical reproduction。
- 优先级：中

## 2602.12430 Agent Skills for Large Language Models: Architecture, Acquisition, Security, and the Path Forward
- 文件：`2602.12430_Agent_Skills_Architecture_Acquisition_Security_Path_Forward.pdf`
- 一句话结论：这是 agent skills 体系综述，强调架构、获取、部署、安全和生命周期治理要一起设计。
- 核心方法/贡献：梳理 SKILL.md、progressive disclosure、MCP 关系、skill acquisition、computer-use 部署和安全研究，并提出 Skill Trust and Lifecycle Governance Framework 与四层 gate-based permission model。
- 可用于我们 workflow 的经验：skill 不只是提示文件，而是可分发、可版本化、可权限化的能力包。
- 警告/风险：社区 skill 漏洞比例高；跨平台可移植性、权限模型、评测和自改进治理仍是开放问题。
- 可落到 optics_agent 的设计点：建立 permission tier：read-only notes、workspace write、local tool execution、network/cluster execution，并按 provenance 和验证结果授予。
- 优先级：高

## 2512.18950 Learning Hierarchical Procedural Memory for LLM Agents through Bayesian Selection and Contrastive Refinement
- 文件：`2512.18950_MACLA_Hierarchical_Procedural_Memory.pdf`
- 一句话结论：过程性记忆应外置、层次化，并用成功率不确定性和成功/失败对比持续更新。
- 核心方法/贡献：提出 MACLA，用冻结 LLM 抽取 trajectory segment，形成带前置条件、动作序列、后置条件的 procedures；用 Bayesian posterior 做选择，用 contrastive refinement 改进，并组合成 meta-procedural playbooks。
- 可用于我们 workflow 的经验：技能库可以从执行轨迹中抽取 procedure，再用贝叶斯置信度管理 active 程度。
- 警告/风险：若 procedure 只是大段文本，会出现检索漂移和弱组合性；合并阈值与前置条件错误会污染记忆库。
- 可落到 optics_agent 的设计点：将 paper reproduction 的成功/失败片段抽象为 `procedure`，维护 `alpha/beta/reliability/preconditions`，低置信度保持 candidate。
- 优先级：中

## 2512.17102 Reinforcement Learning for Self-Improving Agent with Skill Library
- 文件：`2512.17102_RL_for_Self_Improving_Agent_with_Skill_Library.pdf`
- 一句话结论：RL 可把 skill 生成与使用纳入训练目标，使 agent 在任务链中持续积累可复用程序化 skill。
- 核心方法/贡献：提出 SAGE，即 Skill Augmented GRPO，通过 Sequential Rollout 让前序任务产生的 skill 在后续相似任务中可用，并用 Skill-integrated Reward 同时奖励任务结果、skill 生成和 skill 使用。
- 可用于我们 workflow 的经验：自改进不应只奖励当前任务成功，还应奖励产生高质量、可复用、能被后续任务调用的 skill。
- 警告/风险：依赖可验证 reward 和相似任务链；prompt-only skill 生成不稳定，通常需 SFT/RL 支撑。
- 可落到 optics_agent 的设计点：在 reproduction benchmark 中加入跨论文/跨图复用指标：后续任务是否调用前序生成的 skill、是否减少步骤和 token。
- 优先级：低

## 2510.26328 Agent Skills Enable a New Class of Realistic and Trivially Simple Prompt Injections
- 文件：`2510.26328_Agent_Skills_Prompt_Injections.pdf`
- 一句话结论：Agent Skills 让真实 prompt injection 变得极其简单，因为 skill 文件本身全是会被 agent 执行的指令。
- 核心方法/贡献：展示在长 SKILL.md 或引用脚本中隐藏恶意备份/外传指令，可借助“Don't ask again”授权继承执行敏感操作；Claude Web 中也可通过输出恶意 URL 泄露敏感信息。
- 可用于我们 workflow 的经验：skill 文件不能因“看起来是说明文档”而被信任；引用脚本、长文本和权限批准继承都要审计。
- 警告/风险：非技术用户难以逐行审查；基于“检测数据中是否有指令”的 prompt injection 防御对 skill 无效，因为 skill 天生就是指令。
- 可落到 optics_agent 的设计点：默认不信任第三方 skill；禁止一键永久授权高风险动作；对 skill 引用的脚本和资源做同目录完整扫描。
- 优先级：高
