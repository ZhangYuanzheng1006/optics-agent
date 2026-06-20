# 自演化记忆框架文献摘要与风险分析

> 处理对象：`papers/memory/self_evolving_memory/` 目录下 12 篇 PDF
> 提取方式：`pdftotext -layout`（未修改任何 PDF，未上传任何文件）
> 分析维度：(1) experience distillation 机制 (2) skill vs episodic 分离协同 (3) 膨胀/退化失败模式 (4) 有效性验证条件 (5) 对"固定 workflow + 迭代 skill/记忆"策略的启示
>
> 读取失败：`2509.25140_ReasoningBank_Scaling_Agent_Self_Evolving_Reasoning_Memory.pdf` — PDF 损坏（`Couldn't find trailer dictionary` / `Couldn't read xref table`），pdftotext 无法解析。

---

## 2509.09498 SEDM: Scalable Self-Evolving Distributed Memory for Agents

- 文件：`2509.09498_SEDM_Scalable_Self_Evolving_Distributed_Memory.pdf`
- 一句话结论：通过可验证的写入准入（A/B replay）、自调度记忆控制器和跨域知识扩散，将记忆从被动存储转变为主动自优化组件，在提升推理准确率的同时降低 token 开销。
- 核心方法/贡献：
  - **SCEC-based Verifiable Write Admission**：将每次任务执行封装为 Self-Contained Execution Context（含输入/输出/工具摘要/种子/配置哈希），在无原始环境下做并行 A/B 重放（控制组 vs 注入候选记忆组），计算 ΔReward、ΔLatency、ΔTokens 的复合准入分数 S = ΔR − λL·ΔL − λT·ΔT，仅 S ≥ η 的条目入库并获得初始权重 w₀ = max{0, S}。
  - **Self-Scheduling Memory Controller**：检索时用 s(q,m) = sim(q,m) × w(m) 排序，无需实时 LLM rerank。权重随使用更新：w_{t+1} = w_t + α·Ū(m) − β·f_use(m)，实现渐进演化（提升稳定项、衰减低频/负效用项、合并近重复、剪枝冲突项）。
  - **Cross-Domain Knowledge Diffusion**：将已准入条目抽象为通用形式，在其他任务中重新验证后安全迁移。
- 可用于我们向量记忆系统的经验：
  - **写入时 evidence gate** 是最核心的设计——不靠语义相似度判断价值，而是用可重放的 A/B 实验量化边际效用。这直接对应我们 SKILL 层的 evidence gate 理念，可以推广到向量库写入端。
  - **admission-derived weight × semantic similarity** 的检索评分公式极简但有效，避免了常驻 reranker 的延迟和方差。我们可以用 Qwen3-Reranker 做类似的事，但 SEDM 证明了即使不用 reranker，只要写入端有证据 gate，sim × w 也能工作。
  - **渐进式权重衰减**（α·Ū − β·f_use）提供了一种"实时标记不删除"的自然实现：不立即删除，而是通过权重衰减让低效条目自然沉底。
- 警告/风险：
  - A/B replay 的前提是任务可重放（SCEC 封装了所有依赖）。对于我们的论文复现/COMSOL 任务，很多执行依赖外部环境（Magnus 集群、license、GUI），难以做到 environment-free replay，准入证据的成本可能很高。
  - 准入阈值 η 和衰减率 α/β 需要调参，论文未给出敏感性的完整分析。
  - 跨域扩散的"抽象为通用形式"依赖 LLM 抽象质量，可能引入幻觉。
- 可落到 optics_agent 的设计点：
  - 向量库写入端增加 lightweight evidence gate：对于论文复现任务，可以用"复现结果是否与论文数值吻合"作为 ΔR 信号；对于 COMSOL 任务，用"求解是否成功"作为信号。
  - 检索评分用 sim × utility_weight 替代纯 sim，utility_weight 从历史使用结果中维护。
  - 定期合并近重复条目（对应我们的"定期 API 合并清理"），但保留 version trace 支持回滚。
- 优先级：高

---

## 2510.08002 MUSE: Learning on the Job — An Experience-Driven, Self-Evolving Agent for Long-Horizon Tasks

- 文件：`2510.08002_MUSE_Experience_Driven_Self_Evolving_Hierarchical_Memory.pdf`
- 一句话结论：通过分层记忆模块（Strategic/Procedural/Tool）和 Plan-Execute-Reflect-Memorize 闭环，使 agent 在不微调 LLM 的情况下从长程生产力任务中持续学习，在 TAC benchmark 上以轻量模型达到 SOTA。
- 核心方法/贡献：
  - **三层记忆分离**：Strategic Memory（<Dilemma, Strategy> 键值对，全局策略，加载到 system prompt）；Procedural Memory（SOP 库，按应用→子任务二级索引，启动时只加载索引，按需查询详情）；Tool Memory（静态描述 + 动态指令，"肌肉记忆"自动生效）。
  - **Reflect Agent 自主蒸馏**：子任务成功 → 蒸馏为 Procedural Memory；失败 → 生成诊断分析并重新规划；整个任务完成 → 蒸馏更高层的 Strategic/Tool Memory。
  - **自然语言存储**：记忆以自然语言保存，LLM 无关，可跨模型迁移。
  - **去重与泛化**：任务完成后做全局精炼（去重、泛化），保持记忆简洁。
- 可用于我们向量记忆系统的经验：
  - **三层记忆结构与我们高度对应**：Strategic Memory ↔ 提示词备注（≤3条/节点，简洁全局指导）；Procedural Memory ↔ SKILL（结构化 SOP，按需加载）；Tool Memory ↔ 工具使用经验；向量库 ↔ 原始轨迹的语义检索层。
  - **"启动时只加载索引，按需查详情"** 的设计直接解决了 context window 膨胀问题——对应我们 SKILL 的"先读 SKILL.md 再按需深入"。
  - **LLM 无关的自然语言记忆**意味着我们用 Qwen3-Reranker 做的向量库不会绑定到特定 embedding 模型。
- 警告/风险：
  - Reflect Agent 的蒸馏质量完全依赖 LLM 的自我反思能力，在领域专业任务（如光学物理）中可能蒸馏出错误"经验"。
  - Strategic Memory 加载到 system prompt 会占用固定 context 额度，如果 dilemma 积累过多会侵蚀任务空间——论文虽提到"保持简洁"但未给出硬上限机制。
  - Procedural Memory 的 SOP 索引需要人工或 LLM 维护分类体系，迁移到新领域时索引可能不适用。
- 可落到 optics_agent 的设计点：
  - 论文复现工作流的每个节点可以配 ≤3 条 Strategic Memory（提示词备注），记录该节点最常见的 dilemma 及策略。
  - SKILL 文件按"应用→子任务"二级索引组织，与 MUSE 的 Procedural Memory 结构对齐。
  - Reflect 阶段对应我们工作流的 `update_artifacts` 节点，但需要增加 evidence gate 防止错误经验入库。
- 优先级：高

---

## 2511.20857 Evo-Memory: Benchmarking LLM Agent Test-time Learning with Self-Evolving Memory

- 文件：`2511.20857_Evo_Memory_Benchmarking_Self_Evolving_Memory.pdf`
- 一句话结论：提出首个统一的流式自演化记忆 benchmark，将静态数据集重构为任务流，区分"对话回忆"与"经验复用"，并实现了 10+ 记忆模块的统一评估和 ReMem 基线。
- 核心方法/贡献：
  - **核心区分**：Conversational Recall（回忆过去说了什么）vs Experience Reuse（抽象推理策略用于未来任务）。指出现有 benchmark 只测前者不测后者。
  - **统一形式化**：记忆增强 agent = (F, U, R, C)，即基础 LLM、记忆更新管道、检索模块、上下文构建。Search → Synthesis → Evolve 三步循环。
  - **ExpRAG**：简单的任务级经验检索基线，用模板 S 编码经验文本，Top-k 检索后 ICL。
  - **ReMem**：Think-Act-Refine Memory 三模块管道，紧密耦合推理、动作和记忆更新。
  - **流式评估**：将数据集转为序列 τ = {(x₁,y₁),...,(x_T,y_T)}，每步处理后更新记忆状态 M_t。
- 可用于我们向量记忆系统的经验：
  - **"回忆 vs 复用"的区分**对我们至关重要：我们的向量库不应只存"上次跑了什么参数"（回忆），而应存"为什么选这些参数、什么情况下该调整"（复用）。
  - **统一的 (F, U, R, C) 形式化**可以作为我们记忆系统设计的检查清单：F（用哪个 LLM）、U（记忆怎么更新）、R（怎么检索）、C（怎么构建上下文）。
  - **流式评估思路**可以用来验证我们的 skill 自迭代是否真的在改进：把论文复现任务排成序列，看后期任务是否比前期完成得更好。
- 警告/风险：
  - 作为 benchmark 论文，它主要提供评估框架而非记忆治理策略，对膨胀/退化的失败模式分析有限。
  - ExpRAG 作为基线过于简单（直接 append），不代表生产级记忆系统。
  - 流式评估假设任务间有可复用的经验依赖，但如果我们不同论文复现任务之间差异很大，流式评估可能不适用。
- 可落到 optics_agent 的设计点：
  - 用 Evo-Memory 的流式评估思路设计我们的"skill 自迭代有效性验证"：将一系列论文复现任务排成流，检验迭代后的 skill/记忆是否提升后续任务完成率。
  - 记忆写入模板 S 应包含"策略/教训"而非"原始参数"，遵循经验复用而非对话回忆的原则。
- 优先级：中

---

## 2601.03192 MemRL: Self-Evolving Agents via Runtime Reinforcement Learning on Episodic Memory

- 文件：`2601.03192_MemRL_Self_Evolving_Runtime_Reinforcement_Learning.pdf`
- 一句话结论：通过将记忆检索建模为 MDP，用非参数强化学习在冻结 LLM 上更新记忆的 Q 值（效用），实现 Two-Phase Retrieval（相似性召回 + Q 值选择），在不修改权重的情况下持续提升 agent 性能。
- 核心方法/贡献：
  - **Intent-Experience-Utility 三元组**：每条记忆 = (意图 z, 经验 e, 效用 Q)。Q 近似在该意图下使用该经验的期望回报。
  - **Two-Phase Retrieval**：Phase A 用 cosine similarity + 稀疏阈值 δ 召回 Top-k1 候选；Phase B 用复合分数 score = (1−λ)·sim̂ + λ·Q̂ 从候选中选 Top-k2。λ=0.5 为最优平衡点。
  - **非参数 RL 更新**：用 Monte Carlo 风格规则 Q_new ← Q_old + α(r − Q_old) 更新被注入记忆的 Q 值，无需梯度。
  - **理论保证**：Q 值收敛到真实期望回报（无偏、方差有界）；整个系统建模为 Generalized EM 过程（检索=E步，效用更新=M步），单调改进保证全局稳定。
  - **失败记忆保留**：即使在高 Q 区也保留 ~12% 的"失败"记忆，因为 Q 值捕捉的是策略性效用而非二元结果。
- 可用于我们向量记忆系统的经验：
  - **Q 值替代纯语义检索**是最直接可落地的改进：我们的向量库目前只有 embedding similarity，可以给每条记忆附加一个 utility 字段，用历史使用结果（复现成功/失败）更新，检索时用 sim × Q 排序。
  - **Two-Phase 设计与 Qwen3-Reranker 天然互补**：Phase A 的相似性召回由向量库完成，Phase B 的 Q 值选择可以由 Qwen3-Reranker 或 Q 值排序完成——但如果用 Q 值，可以省掉 reranker 的 GPU 开销。
  - **λ=0.5 的凹性峰值**说明纯语义和纯效用都不行，必须平衡——这验证了我们"向量库 + 治理"而非"纯向量库"或"纯规则"的方向。
  - **失败记忆的保留**提醒我们：失败的复现尝试也有价值（记录了什么路走不通），不应直接删除。
- 警告/风险：
  - Q 值更新依赖环境反馈 r 的质量。如果我们的"复现成功"判断不准确（如 COMSOL 求解成功但物理结果错误），Q 值会学到错误的效用。
  - 理论保证假设冻结推理策略和静态任务分布——我们的论文复现任务分布可能非静态（不同论文物理不同）。
  - λ 的最优值 0.5 是在其 benchmark 上得到的，我们的领域可能需要重新调参。
  - 随着记忆增长，Q 值估计的样本可能不足（冷启动问题），新记忆的 Q_init 如何设定论文未充分讨论。
- 可落到 optics_agent 的设计点：
  - 向量库每条记忆增加 `utility_score` 字段，初始值 0.5，每次被检索使用后根据任务结果更新。
  - 检索时用 `embedding_similarity × utility_score` 排序，替代或补充 Qwen3-Reranker。
  - 保留失败复现的记录，标记为"negative experience"，检索时降低其排序权重但不删除。
- 优先级：高

---

## 2602.02474 MemSkill: Learning and Evolving Memory Skills for Self-Evolving Agents

- 文件：`2602.02474_MemSkill_Learning_Evolving_Memory_Skills.pdf`
- 一句话结论：将记忆操作（add/update/delete/skip）重构为可学习、可进化的"记忆技能"，通过 controller RL 选择技能 + LLM executor 执行技能 + designer 从 hard cases 进化技能库的闭环，实现记忆管理本身的自演化。
- 核心方法/贡献：
  - **Memory Skill 概念**：每个 skill = (描述 + 内容规格)，内容包含 Purpose / When to use / How to apply / Constraints。初始为 4 个基本操作（INSERT/UPDATE/DELETE/SKIP），designer 逐步扩展。
  - **skill bank vs memory bank 分离**：skill bank 跨所有 trace 共享（可复用的记忆管理知识）；memory bank 每个 trace 特有（该对话的具体记忆内容）。这明确分离了"如何记忆"（skill）和"记住了什么"（episodic）。
  - **Controller RL**：用下游任务表现作为 reward 训练 skill 选择策略，支持变长 skill bank（共享 scorer 适配新 skill）。
  - **Designer 闭环进化**：维护 hard-case buffer（滑动窗口），聚类失败案例选代表，LLM 分析后修改/新增 skill。保留最佳快照，性能退化时回滚。新 skill 引入时增加探索偏置。
  - **Span-level 处理**：按 token 固定长度分段处理，而非逐 turn，支持更大提取粒度。
- 可用于我们向量记忆系统的经验：
  - **"记忆操作本身是 skill"的观点非常关键**：我们的 SKILL 系统目前只包含领域知识 skill（如 COMSOL Java API），但记忆管理策略（什么时候存、怎么存、怎么合并）本身也可以是可进化的 skill。
  - **skill bank vs memory bank 分离**直接对应我们的 SKILL vs 向量库分离：SKILL 是跨任务共享的可复用知识，向量库是任务特定的 episodic 记忆。
  - **Designer 从 hard cases 进化 skill** 的闭环与我们的 `update_artifacts` 节点理念一致：从失败案例中学习并修改 skill 定义。
  - **快照 + 回滚机制**是 skill 进化的安全保障——skill 修改后如果性能退化就回滚，这比"实时标记不删除"更激进，但更安全。
- 警告/风险：
  - Controller RL 需要大量训练数据（多轮 trace），我们的论文复现任务数量可能不足以训练有效的选择策略。
  - Designer 的 LLM 分析可能引入与领域无关的 skill，导致 skill bank 膨胀。
  - Span-level 分段对长文档（如论文 PDF）可能损失跨段上下文。
  - 回滚机制需要可靠的评估指标来判断"性能退化"，但在论文复现中评估指标本身可能不稳定。
- 可落到 optics_agent 的设计点：
  - 在 SKILL 系统中增加一类"记忆管理 skill"：定义什么类型的经验应该存入向量库、什么应该升级为 SKILL、什么应该丢弃。
  - `update_artifacts` 节点实现 MemSkill 的 Designer 逻辑：收集复现失败的 hard cases，聚类分析后修改 SKILL 定义，保留快照支持回滚。
  - SKILL 版本管理引入快照机制（对应我们工作流的 `version` 递增 + `history` 追加）。
- 优先级：高

---

## 2602.05832 UI-Mem: Self-Evolving Experience Memory for Online RL in Mobile GUI Agents

- 文件：`2602.05832_UI_Mem_Self_Evolving_Experience_Memory_GUI.pdf`
- 一句话结论：通过分层经验记忆（高层 Workflow / 中层 Subtask Skill / 失败模式 Failure Pattern）以参数化模板形式存储，结合分层组采样和自演化循环，在 GUI 在线 RL 中实现跨任务经验迁移。
- 核心方法/贡献：
  - **三层参数化模板**：Workflow（有序子任务序列，如"打开App→搜索→选择→发送"）；Subtask Skill（原子能力，如"搜索某个项"）；Failure Pattern（失败诊断，如"日期为空时不要点搜索"）。模板用 {{变量}} 参数化，检索后用当前任务变量实例化。
  - **Stratified Group Sampling**：同一 GRPO 组内注入不同强度的引导（Strong=全层引导 / Weak=只给Workflow / No=纯探索），保持组内结果多样性以维持优势估计信号。随成功率提升动态减少引导（curriculum）。
  - **Self-Evolving Loop**：从成功轨迹抽象新 plan（替换具体值为模板变量），从失败轨迹提取 failure pattern，动态更新记忆池。
- 可用于我们向量记忆系统的经验：
  - **Failure Pattern 作为一等记忆**非常重要：我们目前只关注"成功经验"（成功的复现参数），但"什么路走不通"的记录同样关键——这与 MemRL 保留失败记忆的理念一致。
  - **参数化模板**思路可用于我们的论文复现经验：存"在 {{材料}} 的 {{结构}} 中，用 {{求解器}} 模式分析，注意 {{陷阱}}"，而非存具体值。
  - **分层组采样**的思路虽然针对 RL 训练，但其核心思想（不同强度的记忆注入保持多样性）可启发我们在不同确定性场景下选择不同记忆注入策略。
- 警告/风险：
  - GUI 领域的操作高度结构化（点击/输入/滑动），模板化容易；论文复现任务的"操作"更抽象（推导/仿真/验证），模板化难度大。
  - 在线 RL 训练场景与我们的离线 skill 迭代场景差异大，Stratified Group Sampling 不直接适用。
  - Failure Pattern 的提取依赖准确的失败诊断，但在 COMSOL 求解失败时原因可能不明确（如特征值求解矩阵分解失败）。
- 可落到 optics_agent 的设计点：
  - 向量库增加 failure pattern 类型的记忆条目，记录"Degiron v2 SU-8 模式分析在 eigensolver 矩阵分解时失败"这类教训。
  - 经验记忆用模板化存储：`在{{论文}}的{{图}}复现中，{{方法}}因为{{原因}}失败，建议{{替代方案}}`。
- 优先级：中

---

## 2602.14670 FactorMiner: A Self-Evolving Agent with Skills and Experience Memory for Financial Alpha Discovery

- 文件：`2602.14670_FactorMiner_Self_Evolving_Skills_Experience_Memory.pdf`
- 一句话结论：通过模块化因子挖掘 skill（60+ 算子 + 多阶段验证管道）和经验记忆（成功模式 + 禁区），以 Ralph Loop（retrieve-generate-evaluate-distill）实现金融因子库的正交化持续扩展。
- 核心方法/贡献：
  - **Modular Skill Architecture**：因子挖掘封装为独立 skill，包含算子层（GPU 加速）和验证管道（IC 筛选 → 相关性检查 → 去重 → 全量验证），LLM 只负责生成，skill 负责确定性评估，消除"幻觉指标"。
  - **Experience Memory 双区**：Successful Patterns（持续通过质量阈值的因子模板）+ Forbidden Regions（与现有库高度相关的因子族，ρ > θ）。记忆维持全局因子库视角：新因子须与现有库互补而非孤立优化。
  - **Ralph Loop**：检索记忆先验 → 生成候选因子 → 并行评估 → 蒸馏结果回记忆。蒸馏算子 Ψ 更新 belief，将采样质量向正交流形集中。
  - **全局库准入机制**：因子不仅要通过 IC 阈值，还要与库中已有因子的相关性低于 θ 才能入库。
- 可用于我们向量记忆系统的经验：
  - **Forbidden Regions 概念非常实用**：对应我们的"已知失败模式"记忆——记录哪些参数组合/方法路径已经被验证不可行，避免重复探索。这正是 Degiron v1/v2 的教训应该存的形式。
  - **全局库视角**：新记忆入库时不仅看自身质量，还要看与现有记忆的冗余度——这对应我们的"定期 API 合并清理"中的去重逻辑，但 FactorMiner 把它做到了写入端。
  - **skill 负责确定性评估、LLM 负责生成**的分离原则，与我们的"COMSOL Java API 做确定性求解、agent 做策略决策"一致。
- 警告/风险：
  - 金融因子有明确的量化指标（IC/ICIR/相关性），准入和蒸馏可完全自动化；论文复现的"成功"标准更模糊（物理结果是否与论文吻合），自动化难度大。
  - 算子空间是有限且类型化的（60+ 算子），而论文复现的"操作空间"是开放的，模板化难度更高。
  - 相关性度量 ρ 在金融信号上有标准定义，但我们的"记忆冗余度"没有类似的客观度量。
- 可落到 optics_agent 的设计点：
  - 向量库写入端增加 forbidden regions 检查：新记忆如果与已有的 failure pattern 语义高度相似，标记为"已知失败路径"而非新建条目。
  - 经验记忆分两区：success patterns（成功复现的参数/方法模式）+ forbidden regions（已验证不可行的路径）。
  - skill 的评估部分（如 COMSOL 求解验证）应该是确定性代码，不应依赖 LLM 判断。
- 优先级：中

---

## 2603.10291 HyMEM: Hybrid Self-Evolving Structured Memory for GUI Agents

- 文件：`2603.10291_HyMEM_Hybrid_Self_Evolving_Structured_Memory_GUI.pdf`
- 一句话结论：通过图结构混合记忆（离散高层策略节点 + 连续轨迹嵌入），支持多跳检索、自演化节点更新（ADD/MERGE/REPLACE）和推理时工作记忆刷新，使 7B/8B 模型超越 GPT-4o 和 Gemini2.5-Pro。
- 核心方法/贡献：
  - **混合表示**：每个节点 = (高层策略 c_i, 中层属性 A_i, 低层轨迹嵌入 m_i)。离散策略/属性用 VLM 生成文本 token，连续轨迹嵌入用 CoMEM 压缩为 8 个 embedding。边连接共享属性的节点，形成关联拓扑支持多跳搜索。
  - **自演化三操作**：ADD（新策略/属性 → 创建节点）；MERGE（同策略但互补证据 → 挂接新轨迹并更新策略）；REPLACE（同策略但更优 → 替换旧轨迹）。VLM judge 做冗余检查判断执行哪个操作。
  - **On-the-fly Working Memory Refresh**：推理中每步动作后，VLM 检测执行阶段变化（如从"搜索"到"结账"），保留长期目标、丢弃过时上下文，重新检索并刷新引导指令和嵌入。
  - **多跳结构化检索**：先语义匹配找种子节点，再沿图扩展 1-hop 邻居并重排，迭代 t 轮获得多样且相关的候选集。
- 可用于我们向量记忆系统的经验：
  - **混合表示兼顾抽象和细节**：离散策略节点对应我们的 SKILL（高层指导），连续嵌入对应向量库（底层证据）。两者通过属性关联，支持从 SKILL 出发多跳找到相关 episodic 记忆。
  - **ADD/MERGE/REPLACE 三操作**比简单的"添加/删除"更精细，直接对应我们记忆治理的需求：新增（ADD）、合并冗余（MERGE）、替换过时（REPLACE）。
  - **VLM judge 做冗余检查**可以用 LLM-as-judge 实现：新记忆入库前让 LLM 判断它与现有记忆是 ADD/MERGE/REPLACE 关系。
  - **On-the-fly refresh**对长程任务（如多步 COMSOL 仿真）很有价值：不同阶段需要不同的记忆上下文。
- 警告/风险：
  - 图结构维护成本高（节点/边/嵌入都要更新），对于我们的记忆规模（几十万条）可能不实际。
  - VLM judge 的判断质量直接影响记忆质量，错误判断会导致错误 MERGE/REPLACE。
  - 多跳检索的 t 轮迭代增加延迟，对实时性要求高的场景可能不适用。
  - CoMEM 压缩为 8 个 embedding 是针对 GUI 轨迹的，我们的文本记忆可能不需要这种压缩。
- 可落到 optics_agent 的设计点：
  - 记忆治理 API 实现 ADD/MERGE/REPLACE 三操作而非简单 CRUD。
  - 新记忆入库前用 LLM-as-judge 判断与现有记忆的关系（新增/合并/替换），自动化记忆治理。
  - 长程任务（如完整论文复现工作流）中，不同节点加载不同记忆子集，而非全程加载全部记忆。
- 优先级：中

---

## 2604.10923 Mem2Evolve: Towards Self-Evolving Agents via Co-Evolutionary Capability Expansion and Experience Distillation

- 文件：`2604.10923_Mem2Evolve_Co_Evolutionary_Capability_Experience.pdf`
- 一句话结论：提出能力扩展与经验蒸馏的共进化范式，通过双记忆（Asset Memory 存工具/agent + Experience Memory 存策略经验），用经验指导新资产创建、用新资产产出新经验，实现稳定持续进化。
- 核心方法/贡献：
  - **双记忆机制**：Asset Memory M_A = Agent Bank ∪ Tool Bank（持久化能力仓库）；Experience Memory M_E = Agent Experience ∪ Tool Experience（蒸馏的策略教训）。每条经验 = (标题, 描述, 适用场景, 核心内容)。
  - **Forward Inference（"先复用，按需创建"）**：子任务先与 Asset Memory 做相似度匹配，超过阈值 δ 直接复用；否则用 Experience Memory 引导动态创建新工具/agent。
  - **Backward Evolution**：任务完成后，新创建的资产经 unit test 验证后存入 Asset Memory（能力扩展）；执行轨迹蒸馏为经验存入 Experience Memory（经验蒸馏）。LLM-as-judge 评估轨迹成功/失败。
  - **经验引导创建**：创建新资产时检索相关经验（成功策略 + 已知陷阱），避免从零开始。
- 可用于我们向量记忆系统的经验：
  - **能力与经验的共进化**是一个更高层的视角：我们的 SKILL（能力）和向量库（经验）也应该共进化——新 SKILL 的创建应该参考已有经验，新经验应该能催生新 SKILL。
  - **"先复用，按需创建"策略**完美匹配我们的固定 workflow + 按需迭代 skill：workflow 节点先尝试用现有 SKILL，能力不足时才创建新 SKILL。
  - **Asset Memory 的 Tool Bank 用 MCP 标准存储**——与我们的 MCP 工具生态直接兼容。
  - **经验引导创建**意味着我们写新 SKILL 时应该先搜向量库中的相关经验（成功模式和失败教训），而非凭空编写。
- 警告/风险：
  - 动态创建工具/agent 的质量控制是开放性问题——创建的资产可能不可靠。
  - 双记忆的同步和一致性维护比单记忆复杂。
  - 共进化的"正反馈循环"如果经验质量不高，可能同时退化能力和经验。
  - 实验中 6.46% 的提升 over 纯资产创建、11.80% over 纯经验积累，说明共进化确实更优但增量不是压倒性的。
- 可落到 optics_agent 的设计点：
  - SKILL 创建/更新前强制检索向量库中的相关经验（success patterns + forbidden regions），形成"经验引导的 skill 编写"流程。
  - `update_artifacts` 节点同时更新 SKILL（能力扩展）和向量库（经验蒸馏），实现共进化。
  - 新 SKILL 入库前需要通过 evidence gate（类似 unit test），防止低质量 skill 污染系统。
- 优先级：高

---

## 2605.22721 DecentMem: Self-Evolving Multi-Agent Systems via Decentralized Memory

- 文件：`2605.22721_DecentMem_Decentralized_Memory_Multi_Agent.pdf`
- 一句话结论：提出去中心化双池记忆框架（exploitation pool + exploration pool），每个 agent 维护私有记忆，LLM-as-judge 按阶段反馈在线重加权两池，理论保证全局可达性和 O(log T) 累积 regret，在多 agent 系统中显著优于中心化记忆。
- 核心方法/贡献：
  - **去中心化设计**：每个 agent 维护私有 M = E-pool ∪ X-pool，避免中心化记忆导致的 agent 行为同质化、通信开销和隐私风险。
  - **双池机制**：E-pool 存过去任务的固化轨迹（相似度检索做局部利用）；X-pool 由 LLM 生成新候选（启发式teleportation做全局探索）。两池互补，避免纯利用陷入局部最优。
  - **在线路由**：按权重 α = w_E / (w_E + w_X) 选择池，阶段反馈 Δt = I[q_curr > q_prev] 更新权重（成功增 α，否则衰减）。
  - **理论保证**：建模为图结构随机游走 + 启发式teleportation，证明全局可达性（无 agent 永久困于局部次优）和 O(log T) 累积 regret（匹配随机bandit下界）。
  - **记忆条目记录协作轨迹**：不仅存"解决了什么"，还存"怎么解决的"和"谁执行的"，可作为动作先验和协作先验。
- 可用于我们向量记忆系统的经验：
  - **exploitation vs exploration 双池**对我们有启发：向量库（E-pool，固化经验）+ LLM 实时生成（X-pool，探索新策略）。当向量库检索不到高相似度记忆时，让 LLM 生成新的策略候选，而非强行用不相关的记忆。
  - **在线权重更新**提供了一种轻量的记忆治理方式：不需要复杂的合并/删除，通过权重调整让低效记忆自然被边缘化。
  - **O(log T) regret 保证**说明这种双池设计在理论上是最优的——这给我们"实时标记不删除"策略提供了理论支撑：不删除但通过权重衰减让低效记忆退出竞争。
- 警告/风险：
  - 去中心化设计针对多 agent 场景，我们是单 agent（或少量 agent）场景，中心化记忆可能更合适。
  - X-pool 的 LLM 生成质量依赖 LLM 能力，可能生成无效策略。
  - 理论保证假设阶段反馈可靠，但我们的任务反馈可能延迟或不准确。
  - 相似度阈值 τ 的设定对效果影响大：太高则 E-pool 总是 fallback 到 X-pool，太低则误用不相关记忆。
- 可落到 optics_agent 的设计点：
  - 向量库检索增加 fallback 机制：当最高相似度低于阈值 τ 时，不注入记忆而是让 LLM 自主推理（相当于 X-pool），避免误用不相关记忆。
  - 记忆权重用在线更新而非批量清理：每次使用后根据结果微调权重，实现"实时标记"。
  - 记忆条目记录"怎么复现的"而不仅是"复现了什么"，作为后续任务的执行先验。
- 优先级：中

---

## 2606.09365 SkeMex: Experience Makes Skillful — Enabling Generalizable Medical Agent Reasoning via Self-Evolving Skill Memory

- 文件：`2606.09365_SkeMex_Self_Evolving_Skill_Memory_Medical.pdf`
- 一句话结论：通过 Read-Write-Assess-Govern 闭环和多分支 skill 仓库（general/task/action），用环境反馈估计 skill 效用指导值感知检索和仓库治理，在不更新模型权重的情况下实现医疗 agent 的持续自进化。
- 核心方法/贡献：
  - **多分支 skill 仓库**：M = M_gen ∪ M_task ∪ M_act。General（可迁移推理策略和广泛临床原则）；Task-level（特定任务族的模式）；Action-level（工具使用的操作知识）。三分支独立管理，防止不同抽象层的 skill 在同一池中竞争。
  - **Read（值感知检索）**：Score = λ_sim·Sim + λ_u·U(κ) + λ_h·h(m)。语义相似度 + category-conditioned 效用 + Ebbinghaus 遗忘曲线衰减的记忆强度。分支感知 Top-K 平衡三分支。
  - **Write（轨迹到 skill 蒸馏）**：Gated trajectory buffer 过滤基础设施错误/机械重复/平凡成功 → Two-pass distillation（分析 pass 提取可复用模式 + 判断 CREATE/PATCH/NONE；变异 pass 生成 skill 草稿或局部更新）→ Novelty gate + Quality gate 审查。
  - **Assess（效用估值）**：窗口级聚合反馈（非逐样本），用相对优势 A = r − r̄(κ) 而非绝对奖励做 credit assignment。贡献函数区分正向/负向/忽略采用，含风险敏感正则化 ρ_i = ε·u_i 防止高效用 skill 累积不安全行为。cosine warmup schedule 让新 skill 快速调整、成熟 skill 稳定更新。
  - **Govern（仓库治理）**：每 N 窗口执行——合并冗余 skill、降级低效 skill、晋升稳定高效 skill 为 mature、分支超容量时移除最低效用 skill。治理后清空 buffer 进入下一窗口。
  - **M-MDP 形式化**：将 skill 记忆演化建模为非参数强化过程，环境反馈提供 reward 信号估计 context-dependent utility。
- 可用于我们向量记忆系统的经验：
  - **Read-Write-Assess-Govern 闭环与我们完全对齐**：Read=检索记忆；Write=蒸馏新经验；Assess=评估效用；Govern=定期清理。特别是 Govern 操作直接实现我们的"定期 API 合并清理"。
  - **多分支 skill 仓库**的三层抽象（general/task/action）可以映射到我们：general=跨论文的通用复现策略；task=特定论文类型的复现方法；action=特定工具（COMSOL/Python）的操作知识。
  - **Gated trajectory buffer** 过滤低价值轨迹（基础设施错误/机械重复/平凡成功）——我们的复现尝试也需要类似过滤：COMSOL license 超时不算经验，成功跑通 smoke test 不算物理复现成功。
  - **窗口级聚合 + 相对优势**的 credit assignment 比逐样本更稳定，适合我们任务难度差异大的场景。
  - **Novelty gate + Quality gate** 是 skill 入库的双重保障：Novelty 防止冗余（与已有 skill 重叠则转 PATCH），Quality 要求有明确的情境触发器和具体步骤——这直接对应我们 SKILL 的 evidence gate。
  - **风险敏感正则化** ρ_i = ε·u_i 防止高效用 skill 累积不安全行为——对我们的安全约束（如不删除 active COMSOL image）很有价值。
- 警告/风险：
  - 医疗领域有明确的对错标准（诊断是否正确），论文复现的"成功"标准更模糊（物理结果是否吻合），效用估计可能更噪声。
  - 窗口大小（30 trajectories）是经验值，我们的任务密度可能更低，窗口可能需要更大。
  - skill 蒸馏依赖 LLM 分析质量，在领域专业任务中可能蒸馏出错误"可复用模式"。
  - 容量限制 C_gen/C_task/C_act 需要人工设定，太小则频繁驱逐有用 skill，太大则治理失效。
  - Ebbinghaus 遗忘曲线衰减可能不适合我们的场景——某些物理知识不会"遗忘"。
- 可落到 optics_agent 的设计点：
  - SKILL 仓库按 general/task/action 三分支组织，对应跨论文通用策略/特定论文类型方法/工具操作知识。
  - `update_artifacts` 节点实现完整的 Read-Write-Assess-Govern 闭环：检索相关 skill → 蒸馏新经验 → 评估效用 → 定期治理（合并/降级/晋升/驱逐）。
  - skill 入库增加 Novelty gate（与现有 SKILL 语义去重）+ Quality gate（要求有明确触发条件和具体步骤）。
  - 效用估计用窗口级相对优势而非逐任务绝对结果，适应任务难度差异。
  - 安全约束（如 COMSOL image 不可变）用风险敏感正则化保护，防止高效用但危险的 skill 积累。
- 优先级：高

---

## 横向分析：对我们"固定 workflow + 迭代 skill/记忆"策略的综合启示

### 1. 哪些 experience distillation 机制适合我们

| 机制 | 来源 | 适用性 | 理由 |
|------|------|--------|------|
| **A/B replay 准入** | SEDM | 中 | 理念完美但 COMSOL 任务难重放；可用于可重放的 Python 分析任务 |
| **环境反馈 Q 值更新** | MemRL | 高 | 轻量、无需重放，用任务结果更新记忆效用值即可 |
| **Reflect Agent 蒸馏** | MUSE | 高 | 已有 `update_artifacts` 节点，只需增加蒸馏逻辑 |
| **窗口级相对优势** | SkeMex | 高 | 适应我们任务难度差异大的特点 |
| **Hard case → skill 进化** | MemSkill | 高 | 从失败案例学习并修改 SKILL，与我们自迭代目标完全一致 |
| **Gated buffer 过滤** | SkeMex | 高 | 过滤基础设施错误/平凡成功，只保留有信息量的轨迹 |
| **Forbidden regions** | FactorMiner | 高 | 记录已验证不可行的路径，避免重复探索 |

### 2. skill memory 和 episodic memory 如何分离或协同

论文们呈现了三种分离模式：
- **MUSE 模式**：按抽象层级分离（Strategic=全局策略 / Procedural=SOP / Tool=操作）——对应我们的 prompt备注 / SKILL / 工具经验。
- **MemSkill 模式**：按共享性分离（skill bank=跨trace共享的管理知识 / memory bank=trace特定的内容）——对应我们的 SKILL（跨任务共享）/ 向量库（任务特定）。
- **SkeMex 模式**：按抽象层级 + 独立管理分离（general/task/action 三分支独立治理）——最精细的分离。

**协同方式**：Mem2Evolve 的共进化范式最适合我们——skill 创建时检索 episodic 经验引导，episodic 经验积累到一定程度蒸馏为新 skill。DecentMem 的双池机制提供了 fallback：episodic 不够用时让 LLM 自主推理。

### 3. 自演化过程中记忆膨胀/退化的失败模式

| 失败模式 | 来源论文的应对 | 我们的应对建议 |
|----------|---------------|---------------|
| **噪声积累** | SEDM: A/B 准入过滤；MemRL: Q 值过滤 distractor | 向量库写入端增加 evidence gate |
| **冗余膨胀** | HyMEM: MERGE 操作；SkeMex: Novelty gate + 定期合并 | 定期 API 合并 + 入库时 LLM-as-judge 去重 |
| **效用退化** | SEDM: 权重衰减；SkeMex: Ebbinghaus 衰减 + 容量驱逐 | utility_score 衰减 + 分支容量限制 |
| **冲突记忆** | SEDM: 冲突检测 + 渐进降权 | 检测矛盾记忆并标记，降低权重 |
| **局部最优困陷** | DecentMem: X-pool teleportation；UI-Mem: 探索组 | 相似度低于阈值时 fallback 到 LLM 自主推理 |
| **能力-经验共同退化** | Mem2Evolve: 共进化但需质量gate | skill 入库需 Novelty + Quality 双 gate |
| **危险行为积累** | SkeMex: 风险敏感正则化 | 安全约束 skill 用高正则化保护 |
| **回滚缺失** | MemSkill: 快照 + 回滚 | SKILL 版本管理保留快照 |

### 4. 哪些框架验证了"记忆驱动的 agent 进化"确实有效，在什么条件下有效

| 框架 | 有效性证据 | 有效条件 |
|------|-----------|---------|
| **SEDM** | FEVER+HotpotQA 准确率提升 + token 降低 | 任务可重放（SCEC 封装）；A/B 实验有明确 reward |
| **MUSE** | TAC SOTA 51.78%（+20% relative） | 长程多步骤任务；有 Reflect 闭环 |
| **MemRL** | 4 benchmark CSR +3.8%；Q 值与成功率 r=0.861 | 冻结 LLM；环境反馈可靠；任务间有语义相似性 |
| **MemSkill** | 4 benchmark 一致提升 + 跨设置泛化 | 有足够训练 trace 训练 controller |
| **SkeMex** | 9 医疗 benchmark 平均 +7.88%；跨模型迁移有效 | 有明确对错标准；窗口级聚合稳定效用估计 |
| **DecentMem** | +23.8% over 中心化；-49% token | 多 agent 协作场景；阶段反馈可靠 |
| **Mem2Evolve** | +11.80% over 纯经验；+6.46% over 纯资产 | 共进化正反馈；新资产有 unit test |
| **HyMEM** | 7B 超越 GPT-4o (+15.3%) | GUI 轨迹；VLM judge 可靠 |

**共同有效条件**：(1) 环境反馈/任务结果可获取且相对可靠；(2) 任务间存在可复用的模式（非完全独立）；(3) 有某种准入/gate 机制防止噪声入库；(4) 有治理机制防止无限膨胀。

### 5. 对我们"固定 workflow + 迭代 skill/记忆"策略的启示

1. **固定 workflow 是正确选择**：多篇论文（MUSE、MemSkill、SkeMex）的闭环都是在固定拓扑上迭代内容，而非频繁改变拓扑。DecentMem 的理论证明也表明，在固定框架上做记忆权重的在线优化可以达到 O(log T) 最优 regret。

2. **三层记忆对应关系已验证**：MUSE 的三层（Strategic/Procedural/Tool）和 SkeMex 的三分支（general/task/action）都验证了按抽象层级分离记忆的有效性。我们的 prompt备注/SKILL/向量库三层结构有充分文献支撑。

3. **迭代重点是 skill 和记忆治理，不是 workflow**：MemSkill 明确指出"skill bank 本身可以进化"，Mem2Evolve 验证了"能力扩展 + 经验蒸馏共进化"优于单独进化任一方。我们的 `update_artifacts` 节点应该同时更新 SKILL 和向量库。

4. **evidence gate 是防止退化的关键**：SEDM 的 A/B 准入、SkeMex 的 Novelty+Quality gate、Mem2Evolve 的 unit test 都表明：没有 gate 的自演化会退化。我们的 SKILL evidence gate 必须坚持。

5. **"实时标记不删除，定期合并清理"策略有支撑**：SEDM 的渐进权重衰减、DecentMem 的在线权重更新、SkeMex 的窗口级治理都是"实时标记 + 定期清理"的变体。不需要实时删除，但必须有权重/效用机制让低效记忆退出竞争。

6. **Qwen3-Reranker 的定位应重新考虑**：MemRL 证明了 sim × Q 的检索评分可以在没有 reranker 的情况下工作（λ=0.5 最优）。如果我们在写入端有 evidence gate + 运行时 Q 值更新，reranker 可以作为可选的精排而非必选组件，降低 GPU 常驻成本。

7. **失败记忆是重要资产**：MemRL（保留12%失败记忆）、UI-Mem（Failure Pattern）、FactorMiner（Forbidden Regions）都强调失败经验的价值。我们的向量库应该主动存储和管理失败复现的教训。
