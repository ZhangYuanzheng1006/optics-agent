# Workflow Optimization PDF Summaries

## 2410.07869 Benchmarking Agentic Workflow Generation
- 文件：`2410.07869_Benchmarking_Agentic_Workflow_Generation.pdf`
- 一句话结论：WorfBench/WorfEval 说明 workflow 生成不能只看最终答案，必须评价线性步骤与 DAG 依赖结构是否都正确。
- 核心方法/贡献：构建覆盖 problem-solving、function calling、embodied planning、open-grounded planning 的 workflow 生成基准；把 workflow 表示为 DAG，并用 subsequence/subgraph matching 量化链式与图式生成质量。
- 可用于我们 workflow 的经验：`case_workflow` 应保存节点、边、候选 action、拓扑排序和 gold/expected structure，评测时同时检查步骤覆盖率、依赖边正确率和可并行结构。
- 警告/风险：图结构匹配比最终任务分数更严格，容易暴露 LLM 对并行依赖和细粒度动作边界的弱点；LLM-as-evaluator 不能替代结构化匹配。
- 可落到 optics_agent 的设计点：为论文复现 workflow 增加 `expected_graph`、`required_nodes`、`dependency_edges` 和 `graph_eval` 字段，用于检测阅读、参数抽取、理论推导、数值程序、验证报告之间的依赖是否缺失或误连。
- 优先级：高

## 2410.10762 AFlow: Automating Agentic Workflow Generation
- 文件：`2410.10762_AFlow_Automating_Agentic_Workflow_Generation.pdf`
- 一句话结论：把 workflow 表示为可执行代码/节点图，并用 MCTS 基于执行反馈搜索，是自动发现高性能 workflow 的有效路径。
- 核心方法/贡献：AFlow 将 LLM 调用节点和代码化边组成搜索空间，引入可复用 operators（如 ensemble、review-revise），用 MCTS 的选择、扩展、执行评估和回传经验迭代优化；六个基准上优于人工与自动 baseline。
- 可用于我们 workflow 的经验：workflow 优化需要保存每轮候选、修改 diff、执行分数和树状经验；操作单元应抽象成可组合 operator，而不是每次从自然语言重新生成全流程。
- 警告/风险：执行式搜索成本高，若 verifier 粗糙或任务分数噪声大，MCTS 会优化到表面分数；代码化 workflow 灵活但更难做安全约束和错误定位。
- 可落到 optics_agent 的设计点：在 `workflows/` 增加 workflow mutation/replay 记录：候选 YAML、节点变更、验证指标、失败原因、父候选 ID；先在 Mie/文献摘要等低成本任务上做小规模 workflow 搜索。
- 优先级：高

## 2501.17167 QualityFlow: An Agentic Workflow for Program Synthesis Controlled by LLM Quality Checks
- 文件：`2501.17167_QualityFlow_LLM_Quality_Checks.pdf`
- 一句话结论：用质量检查器动态控制 workflow，比固定“生成-测试-调试”链更能避免错误测试和自调试跑偏。
- 核心方法/贡献：QualityFlow 设置 Code Generator、Test Designer、Self-Debugger、Clarifier 和 Quality Checker；Quality Checker 通过 imagined execution 判断代码是否符合可见测试，并决定提交、继续、澄清或回滚。
- 可用于我们 workflow 的经验：verifier 不应只在终点运行，而应作为控制节点嵌入每个关键阶段；当验证失败时，workflow 要能选择继续、澄清、重启或回滚到早期产物。
- 警告/风险：LLM imagined execution 可能误判；合成测试质量低会误导调试，因此测试本身也需要 Test Quality Checker。
- 可落到 optics_agent 的设计点：为论文复现加入 `quality_gate` 节点：参数表检查、单位检查、公式维度检查、数值输出 sanity check；失败时允许 `clarify_problem`、`regenerate_tests`、`revert_to_last_valid_artifact` 三类动作。
- 优先级：高

## 2503.11301 GNNs as Predictors of Agentic Workflow Performances
- 文件：`2503.11301_GNNs_as_Predictors_of_Agentic_Workflow_Performances.pdf`
- 一句话结论：workflow 可以先被轻量预测器筛选，再决定是否执行昂贵的 LLM/仿真评估。
- 核心方法/贡献：将 agentic workflow 建模为计算图，节点是 agent/prompt，边是依赖；提出 FLORA-Bench，用 60 万 workflow-task 对训练/评估 GNN 对成功率和排序 utility 的预测能力。
- 可用于我们 workflow 的经验：优化环路不必每个候选都完整执行，可先用结构特征、节点类型、历史表现和任务特征预测候选价值，再抽样执行高潜力候选。
- 警告/风险：预测器只能近似真实执行，跨领域泛化不稳；若训练标签来自单一 benchmark，会把 benchmark 偏差固化进搜索策略。
- 可落到 optics_agent 的设计点：积累本项目 workflow runs 的结构化日志，后续训练简单 ranker（先从规则/树模型开始，不必立即 GNN）预测“本 case 是否需要 COMSOL、是否会卡在缺参、哪个节点最可能失败”。
- 优先级：中

## 2505.18646 SEW: Self-Evolving Agentic Workflows for Automated Code Generation
- 文件：`2505.18646_SEW_Self_Evolving_Agentic_Workflows.pdf`
- 一句话结论：workflow 自进化应同时优化拓扑和 agent prompt，并认真选择 workflow 表示语言。
- 核心方法/贡献：SEW 自动生成初始多 agent workflow，再用 Direct Evolution 和 Hyper Evolution 演化 workflow 结构与单个 agent prompt；比较 BPMN、CoRE、Python、YAML、pseudo-code 等表示，发现不同表示的可解析性和可执行性差异明显。
- 可用于我们 workflow 的经验：workflow 表示不是中性选择；面向 LLM 修改时，应兼顾人类可读、机器可解析、可执行和可局部变异。
- 警告/风险：自进化结果强依赖任务类型和 backbone；只在代码生成上验证，迁移到科学 workflow 需要重新设计指标和约束。
- 可落到 optics_agent 的设计点：保留 YAML 作为主规范，但可为自优化生成一个更接近 CoRE 的中间表示：节点自然语言目标 + 伪代码控制流 + 明确输入输出 schema；每次自迭代只允许局部 patch 并通过 schema 校验。
- 优先级：高

## 2505.19764 Multi-View Encoders for Performance Prediction in LLM-Based Agentic Workflows
- 文件：`2505.19764_Multi_View_Encoders_for_Agentic_Workflow_Performance_Prediction.pdf`
- 一句话结论：预测 workflow 表现时，单看图结构不够，必须联合编码代码架构、prompt 语义和交互图。
- 核心方法/贡献：Agentic Predictor 使用多视图 encoder 表示 workflow 的结构、行为和语义信号，并通过跨域无监督预训练缓解标签稀缺；用于快速估计候选 workflow 成功率并减少试错执行。
- 可用于我们 workflow 的经验：workflow benchmark 数据应同时记录 DAG、prompt、工具调用、代码/脚本、输入输出和运行环境，否则后续无法建立可靠性能预测器。
- 警告/风险：当前多以二元成功率为标签，可能忽略科学复现中的物理可信度、可解释性、成本、人工可审查性等多目标指标。
- 可落到 optics_agent 的设计点：在 run state 中结构化保存 `workflow_view`、`prompt_view`、`tool_view`、`artifact_view`、`metric_view`；为候选 workflow 排序时使用多目标分数：成功、物理验证、成本、可复现性。
- 优先级：中

## 2509.13978 LLM Agents for Interactive Workflow Provenance: Reference Architecture and Evaluation Methodology
- 文件：`2509.13978_LLM_Agents_Interactive_Workflow_Provenance.pdf`
- 一句话结论：科学 workflow 的可交互 provenance 需要轻量元数据、结构化查询和模块化 agent 架构，而不是事后翻日志。
- 核心方法/贡献：提出面向 HPC/Edge/Cloud 科学 workflow 的 provenance-aware LLM agent 参考架构；用 MCP、RAG、数据库/流式 provenance 层，将自然语言问题翻译为结构化 provenance 查询，支持 what/when/who/how 等查询类。
- 可用于我们 workflow 的经验：provenance 应覆盖 prospective provenance（计划结构）和 retrospective provenance（实际执行），并记录数据流、控制流、遥测、调度位置和执行者。
- 警告/风险：LLM 对 provenance 的回答必须受 schema/RAG/查询结果约束；否则会把不存在的运行事实编造成解释。
- 可落到 optics_agent 的设计点：为每次 paper reproduction 保存 `provenance.jsonl`：节点开始/结束、输入 artifact、输出 artifact、命令、环境、资源、失败原因、人工介入；后续提供“为什么这个结果是 fallback/diagnostic”的自然语言查询。
- 优先级：高

## 2601.07477 JudgeFlow: Agentic Workflow Optimization via Block Judge
- 文件：`2601.07477_JudgeFlow_Block_Judge_Workflow_Optimization.pdf`
- 一句话结论：优化 workflow 时，最有价值的反馈不是“整体失败”，而是“哪个逻辑块最该改”。
- 核心方法/贡献：JudgeFlow 将 workflow 分解为 Sequence、Loop、Conditional 等 reusable logic blocks；Judge 模块分析失败执行 trace，为问题块分配 rank-based responsibility score，再让优化器定向修改最弱块。
- 可用于我们 workflow 的经验：workflow schema 应显式表达块级边界和控制结构，便于失败归因、局部修改和 replay；verifier 输出应包含责任排序而非单个 pass/fail。
- 警告/风险：Judge 本身可能有偏差，复杂失败常由多个块共同导致；如果 trace 不完整，块级归因会误导优化。
- 可落到 optics_agent 的设计点：把论文复现 workflow 节点归并为 blocks（reading、parameterization、theory、implementation、validation、reporting），失败时生成 `block_blame` 排名和证据，再只允许修改排名最高的 block。
- 优先级：高

## 2601.15808 Inference-Time Scaling of Verification: Self-Evolving Deep Research Agents via Test-Time Rubric-Guided Verification
- 文件：`2601.15808_Deep_Research_Agents_Rubric_Verification.pdf`
- 一句话结论：深度研究 agent 的可靠性提升可以来自测试时 verifier 扩展：用失败分类和 rubric 生成可执行反馈，反复修正答案。
- 核心方法/贡献：构建 DRA Failure Taxonomy（五大类、十三子类），据此生成 rubric；DeepVerifier 将复杂验证拆成更易检查的检索/证据子问题，输出 rubric-based feedback，测试时迭代提升 GAIA/XBench-DeepResearch 表现。
- 可用于我们 workflow 的经验：verifier 应先有 failure taxonomy，再有 rubric；反馈要指向具体证据缺口、推理错误、工具错误或格式错误，而不是泛泛要求“重试”。
- 警告/风险：验证不等于生成，rubric 若覆盖不全会给错误安全感；多轮反馈存在成本和收敛风险。
- 可落到 optics_agent 的设计点：建立 optics_agent 论文复现失败 taxonomy：缺参数、单位/坐标系错误、理论假设不匹配、仿真未收敛、结果物理量错误、报告夸大；每类绑定检查问题和修复建议。
- 优先级：高

## 2604.08224 Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering
- 文件：`2604.08224_Externalization_Memory_Skills_Protocols_Harness_Engineering.pdf`
- 一句话结论：agent 能力提升越来越来自把状态、技能、交互结构和治理机制外部化到 harness，而不是只依赖模型权重。
- 核心方法/贡献：综述 externalization 视角：memory 外部化跨时间状态，skills 外部化程序性专长，protocols 外部化交互结构，harness engineering 统一执行、权限、上下文、观测和反馈。
- 可用于我们 workflow 的经验：workflow 不是 prompt 列表，而是外部认知基础设施；应把可复用知识、约束、状态、协议和审批门都做成可检查 artifact。
- 警告/风险：外部化会带来治理、权限、上下文预算、组件耦合和评测难题；共享基础设施若缺少版本控制会污染后续任务。
- 可落到 optics_agent 的设计点：把 `AGENTS.md`、skills、workflow YAML、state、provenance、memory 视为同一 harness；新增 workflow 设计时必须声明 externalized state、externalized expertise、protocol 和 guardrail，而不是只写节点顺序。
- 优先级：高

## 2604.19572 A Self-Evolving Framework for Efficient Terminal Agents via Observational Context Compression
- 文件：`2604.19572_Terminal_Agents_Observation_Context_Compression.pdf`
- 一句话结论：长程终端 agent 的上下文压缩应保留精确证据，并让压缩规则从交互轨迹中自进化。
- 核心方法/贡献：TACO 将终端观察压缩建模为 preservation-aware rule learning；通过任务内规则演化和全局规则池，在不训练专用压缩器的情况下减少冗余日志，同时保留错误信息、文件路径、测试名等关键证据。
- 可用于我们 workflow 的经验：replay 和 provenance 日志要区分“可压缩冗余”和“必须逐字保留证据”；上下文压缩规则应可解释、可触发、可回退，并能跨任务复用。
- 警告/风险：过度压缩会丢失后续调试所需的精确字符串；LLM 摘要会改写证据，不适合替代原始错误片段。
- 可落到 optics_agent 的设计点：为 COMSOL/Magnus/pytest 输出建立 evidence-preserving compressor：保留命令、退出码、错误栈、文件路径、关键 stdout markers、指标表；冗长安装日志和重复进度条进入可折叠摘要。
- 优先级：高
