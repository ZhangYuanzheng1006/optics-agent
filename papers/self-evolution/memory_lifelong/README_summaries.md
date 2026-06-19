# Memory / Lifelong Learning 文献摘要

## 2605.28224 When Does Memory Help Multi-Trajectory Inference for Tool-Use LLM Agents?
- 文件：`2605.28224_When_Does_Memory_Help_Tool_Use_Agents.pdf`
- 一句话结论：memory 是否有用取决于搜索策略、任务结构和记忆抽象层级，同一种 memory 在不同推理策略下效果可能相反。
- 核心方法/贡献：提出 scope × abstraction 框架，比较 trajectory-level reflection、atomic fact extraction、raw observation injection、within-expansion sibling transfer 等记忆形式，在 best-of-N、beam search、MCTS 和多类工具环境中评估。
- 可用于我们 workflow 的经验：失败反思、原始观测、原子事实和同层候选反馈应分开存储与检索；不要把所有“记忆”混成一个池。
- 警告/风险：反思只有在某些搜索策略下显著有效；fact extraction 可能不提准确率但能缩短轨迹；非可 fork 环境不能照搬 MCTS/beam。
- 可落到 optics_agent 的设计点：给 memory_store 增加标签约定：`reflection`、`fact`、`raw-observation`、`failed-attempt`、`sibling-feedback`，并按 workflow 节点类型选择检索层。
- 优先级：高

## 2604.15774 MemEvoBench: Benchmarking Safety Risks from Memory Misevolution in LLM Agents
- 文件：`2604.15774_MemEvoBench_Memory_Misevolution_Safety.pdf`
- 一句话结论：动态记忆不是中性日志，受污染记忆、偏置反馈和噪声工具输出会逐步演化成稳定的不安全行为模式。
- 核心方法/贡献：提出 MemEvoBench，评估 adversarial memory injection、noisy tool outputs、biased feedback 下的长期 memory misevolution，覆盖 QA 风格任务和 workflow 风格工具任务，并比较防御策略。
- 可用于我们 workflow 的经验：记忆写入必须有准入门槛、来源标注、置信度、过期机制和纠错工具；正反馈不能自动等同于高价值经验。
- 警告/风险：静态安全 prompt 防不住记忆演化；错误经验若被多次相似检索强化，会从一次事故变成系统性偏见。
- 可落到 optics_agent 的设计点：为记忆写入添加 `source`、`evidence`、`confidence`、`risk`、`supersedes` 字段习惯；对仿真失败、fallback、surrogate 结果强制标记，防止被未来误当成功经验。
- 优先级：高

## 2603.12056 XSkill: Continual Learning from Experience and Skills in Multimodal Agents
- 文件：`2603.12056_XSkill_Continual_Learning_From_Experience_and_Skills.pdf`
- 一句话结论：持续改进 agent 需要同时学习低层 experience 和高层 skill，前者指导局部决策，后者复用结构化流程。
- 核心方法/贡献：提出 XSkill 双流框架，从多路径 rollout 中提炼视觉 grounding 的经验与技能，通过跨 rollout critique 进行累积，推理时按当前上下文检索和适配。
- 可用于我们 workflow 的经验：经验和技能应分层存储；经验记录“这次哪里错/怎么选工具”，技能记录“可复用 workflow/template”。
- 警告/风险：如果经验没有上下文约束，会被错误迁移；skill 过粗会固化不适合当前任务的流程。
- 可落到 optics_agent 的设计点：把复现失败记录写成 experience，把稳定成功流程提升为 skill；只有经过多次验证的经验才合并到 workflow/skill 文件。
- 优先级：高

## 2603.07670 Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers
- 文件：`2603.07670_Memory_for_Autonomous_LLM_Agents.pdf`
- 一句话结论：agent memory 应被看作 write-manage-read 闭环，而不是简单向量库检索。
- 核心方法/贡献：综述 2022-2026 年 agent memory，形式化为写入、管理、读取循环，提出按时间范围、表示载体和控制策略的三维 taxonomy，并讨论压缩、RAG、反思、层级虚拟上下文、学习式管理和工程治理。
- 可用于我们 workflow 的经验：每次记忆操作都要区分写入过滤、去重/压缩、矛盾处理、检索策略和遗忘策略；评估应看下游任务收益而非检索命中本身。
- 警告/风险：一个错误写入会污染未来多步决策；存得越多不一定越好，还会带来隐私、延迟和过期风险。
- 可落到 optics_agent 的设计点：将 memento 使用规则从“会话结束存总结”细化为“写入前查重、写入时标注证据、定期压缩、过期/反证时 supersede”。
- 优先级：高

## 2602.05665 Graph-based Agent Memory: Taxonomy, Techniques, and Applications
- 文件：`2602.05665_Graph_based_Agent_Memory.pdf`
- 一句话结论：图结构能表达记忆之间的关系、层级和因果依赖，比线性日志或纯向量库更适合长期 agent memory。
- 核心方法/贡献：综述 graph-based agent memory，从短/长期、知识/经验、结构化/非结构化分类，按 memory lifecycle 分析 extraction、storage、retrieval、evolution，并整理库、benchmark 和应用。
- 可用于我们 workflow 的经验：科研 workflow 的记忆天然有图关系：论文参数引用实验，失败由假设或工具问题导致，决策 supersede 旧决策。
- 警告/风险：图关系自动生成会带来边错误和维护成本；图越复杂，越需要边类型、权重和审计。
- 可落到 optics_agent 的设计点：使用 memento 的 `memory_link` 建立 `caused_by`、`mitigated_by`、`references`、`implements`、`supersedes`，追踪论文复现失败链和工作流演化链。
- 优先级：中

## 2601.05960 Distilling Feedback into Memory-as-a-Tool
- 文件：`2601.05960_Distilling_Feedback_into_Memory_as_a_Tool.pdf`
- 一句话结论：把一次性反馈抽象成可检索准则，可以用低成本记忆替代每次重复的 test-time refinement。
- 核心方法/贡献：提出 memory-as-a-tool，用文件系统作为显式记忆，agent 通过 `ls/read/write/edit` 工具把 evaluator feedback 抽象成“lessons learned”，并在未来任务前主动读取。
- 可用于我们 workflow 的经验：reviewer 的反馈不应只留在聊天中，应沉淀为可检索的原则、检查清单或反例。
- 警告/风险：文件名和内容质量决定可检索性；如果没有冲突解决，旧反馈和新反馈会互相污染。
- 可落到 optics_agent 的设计点：把论文摘要/复现 review 中反复出现的规范转为 `.codex/skills` 或 memento 记忆，例如“fallback 不得报告为物理复现成功”。
- 优先级：高

## 2509.18868 Memory in Large Language Models: Mechanisms, Evaluation and Evolution
- 文件：`2509.18868_Memory_in_LLMs_Mechanisms_Evaluation_Evolution.pdf`
- 一句话结论：memory 需要统一定义、分层评估和治理闭环，尤其要区分参数记忆、上下文记忆、外部记忆和程序/情节记忆。
- 核心方法/贡献：定义 memory 为持久、可寻址、稳定影响输出的状态，提出 memory quadruple 和 write-read-inhibit/update 因果链，并给出三设置评估协议和 DMM-Gov 动态治理方案。
- 可用于我们 workflow 的经验：不同 memory 类型不能用同一指标评价；外部记忆要同时看检索质量、证据归因和生成 faithful，程序/情节记忆要看跨 session 一致性和轨迹回放。
- 警告/风险：LLM-as-judge 存在位置、顺序和自偏好；更新时间不对齐会让过期信息看似正确。
- 可落到 optics_agent 的设计点：为记忆评估增加最小卡片：类型、写入路径、读取路径、证据、时间戳、可撤销性、是否影响 workflow 输出。
- 优先级：高

## 2508.19005 Building Self-Evolving Agents via Experience-Driven Lifelong Learning: A Framework and Benchmark
- 文件：`2508.19005_Experience_Driven_Lifelong_Learning_Agents.pdf`
- 一句话结论：自演化 agent 需要主动探索、长期记忆、技能学习和知识内化四件事同时成立。
- 核心方法/贡献：提出 Experience-driven Lifelong Learning 框架和 StuLife benchmark，强调从被动到主动、从上下文到记忆、从模仿到学习，并定义 Add/Update/Delete/Combine 的知识精炼操作。
- 可用于我们 workflow 的经验：workflow 自迭代不能只靠人类要求，应在失败复盘后主动提出下一步实验、技能更新和记忆合并。
- 警告/风险：当前模型在长期记忆和主动性上差距巨大；无约束主动探索容易消耗资源或偏离目标。
- 可落到 optics_agent 的设计点：在 `update_artifacts` 节点加入四类操作：新增经验、更新规则、删除过期项、合并重复技能，并要求资源预算审查。
- 优先级：高

## 2507.22925 H-MEM: Hierarchical Memory for High-Efficiency Long-Term Reasoning in LLM Agents
- 文件：`2507.22925_Hierarchical_Memory_Long_Term_Reasoning.pdf`
- 一句话结论：层级记忆通过先粗后细检索减少无关记忆干扰，比全库 top-k 相似度更高效。
- 核心方法/贡献：提出 H-MEM，将记忆按 Domain、Category、Memory Trace、Episode 四层组织，并用位置索引指向下级记忆，推理时逐层路由检索。
- 可用于我们 workflow 的经验：先按方向/项目/任务类型过滤，再按具体问题检索，通常比全库语义搜索更稳定。
- 警告/风险：层级分类错误会导致相关记忆根本进不了候选集；需要允许跨层补救搜索。
- 可落到 optics_agent 的设计点：延续现有 memento 三层架构：`direction:phybench`、project_path、任务标签；再为论文复现、COMSOL、Mie、workflow 分别设子标签。
- 优先级：中

## 2507.05257 Evaluating Memory in LLM Agents via Incremental Multi-Turn Interactions
- 文件：`2507.05257_Evaluating_Memory_in_LLM_Agents_Incremental_Multi_Turn.pdf`
- 一句话结论：memory agent 评估必须模拟增量多轮积累，而不是把长上下文一次性塞进去。
- 核心方法/贡献：提出 MemoryAgentBench，基于认知科学定义四项能力：accurate retrieval、test-time learning、long-range understanding、selective forgetting，并把长上下文数据改造成多轮增量输入。
- 可用于我们 workflow 的经验：评估 optics_agent 记忆时应看它是否能在多次会话中正确召回、学习新规则、整合长链信息并覆盖/遗忘旧错误。
- 警告/风险：长上下文 benchmark 不等价于 memory benchmark；只测召回会漏掉选择性遗忘和测试时学习。
- 可落到 optics_agent 的设计点：建立小型 memory regression：给定旧错误记忆、新纠正记忆和新任务，检查 agent 是否引用新规则并避免旧结论。
- 优先级：高

## 2503.21760 MemInsight: Autonomous Memory Augmentation for LLM Agents
- 文件：`2503.21760_MemInsight_Autonomous_Memory_Augmentation.pdf`
- 一句话结论：记忆条目需要自动补充结构化属性，才能在规模增长后保持可检索和可用。
- 核心方法/贡献：提出 MemInsight，通过 attribute mining、annotation 和 memory retrieval 为历史交互生成实体中心或会话中心属性，在推荐、QA、事件总结等任务上提升检索与上下文效果。
- 可用于我们 workflow 的经验：每条记忆不能只有自然语言正文，还应有领域、任务、实体、失败类型、证据类型、时间等属性。
- 警告/风险：自动属性抽取可能错标或过拟合任务；人工定义 schema 太死也会限制新任务。
- 可落到 optics_agent 的设计点：写入记忆时固定补充 tags：`paper-id`、`figure`、`method`、`failure-mode`、`artifact-type`、`confidence`，便于后续过滤。
- 优先级：中

## 2501.07278 Lifelong Learning of Large Language Model based Agents: A Roadmap
- 文件：`2501.07278_Lifelong_Learning_of_LLM_Agents.pdf`
- 一句话结论：LLM agent 的 lifelong learning 需要围绕 perception、memory、action 三模块解决稳定性-可塑性困境。
- 核心方法/贡献：系统综述 LLM agent lifelong learning，将核心模块归纳为感知、多模态输入整合、记忆存取演化知识、行动与环境交互，并讨论灾难性遗忘、可塑性丧失、评估指标和应用场景。
- 可用于我们 workflow 的经验：workflow 自演化要在“保留可靠旧知识”和“吸收新经验”之间做版本化权衡，而不是每次失败都直接覆盖规则。
- 警告/风险：过强稳定性导致不学习，过强可塑性导致遗忘或漂移；多模态/工具环境会放大这种权衡。
- 可落到 optics_agent 的设计点：所有重要 workflow/skill 更新都应有版本、历史、supersede 关系和回滚路径，失败经验先进入记忆，验证后再升格为规则。
- 优先级：高
