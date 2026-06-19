# Self-Evolution Frameworks 摘要

## 2606.07412 Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills
- 文件：`2606.07412.pdf`
- 一句话结论：把求解轨迹转成结构化 agent skills，再用这些 skills 反向生成针对性训练任务，是比静态合成任务更有效的 SWE 自进化闭环。
- 核心方法/贡献：从历史 solving traces 中蒸馏反复失败模式和有效修复模式，生成真实仓库中的 repair tasks；用执行验证和 solver-gradient alignment reward 过滤任务；更新后的 Solver 再产生新轨迹，形成多轮 curriculum。
- 可用于我们 workflow 的经验：失败轨迹不应只作为日志或 reward，而应进入“轨迹 -> 技能/规则 -> 新任务/新测试 -> 再执行”的闭环。
- 警告/风险：成功依赖可执行验证和大量 SWE 任务环境；科学复现任务的 ground truth、验证信号和任务生成空间更稀疏，不能直接套用 SWE-bench 式任务合成。
- 可落到 optics_agent 的设计点：在 `update_artifacts` 后增加 trace-derived skill 生成步骤，把失败的 COMSOL/解析模型轨迹转成“可复用技能”和“下轮最小验证任务”。
- 优先级：高

## 2606.03841 EvoDS: Self-Evolving Autonomous Data Science Agent with Skill Learning and Context Management
- 文件：`2606.03841.pdf`
- 一句话结论：数据科学 agent 的自进化需要同时学习可执行技能和上下文压缩策略，否则长流程会被静态动作集和上下文爆炸限制。
- 核心方法/贡献：提出 Autonomous Skill Acquisition 自动合成、验证、复用可执行技能；提出 Adaptive Context Compression，把上下文保留/压缩建模为学习控制问题；用两阶段多 agent 训练协调执行、技能获取和上下文管理。
- 可用于我们 workflow 的经验：workflow 不仅要进化节点/技能，还要进化“哪些上下文必须保留、哪些中间产物可压缩”的策略。
- 警告/风险：论文依赖强化学习和数据科学 benchmark；optics_agent 的论文复现样本量小，不宜假设可训练出稳定压缩策略。
- 可落到 optics_agent 的设计点：为每个 workflow 节点定义 `context_policy`，把论文参数、验证指标、失败原因标为高保真保留，把普通日志压缩为摘要。
- 优先级：高

## 2606.03056 SkillDAG: Self-Evolving Typed Skill Graphs for LLM Skill Selection at Scale
- 文件：`2606.03056.pdf`
- 一句话结论：大规模 skill 库的瓶颈不是向量召回，而是依赖、冲突、重复、特化等结构关系的显式管理。
- 核心方法/贡献：把技能关系建成 typed DAG，检索时返回向量匹配、邻居和冲突信号；agent 可通过 propose-then-commit 协议提交有执行证据的边；用无环、非矛盾、append-only rollback 维护图结构。
- 可用于我们 workflow 的经验：技能选择要暴露结构证据给 agent，而不是只给 top-k 文本；技能之间的前置依赖和冲突要可查询、可更新、可回滚。
- 警告/风险：需要维护高质量类型边和提交约束；如果证据不足，agent 自己写边会把错误结构固化。
- 可落到 optics_agent 的设计点：把 `.codex/skills`、workflow 节点、memory 条目之间建立 typed edges，如 `requires`、`conflicts_with`、`supersedes`、`evidence_from`。
- 优先级：高

## 2605.22148 Ratchet: A Minimal Hygiene Recipe for Self-Evolving LLM Agents
- 文件：`2605.22148.pdf`
- 一句话结论：自生成技能是否有效，关键不在生成能力，而在技能库生命周期管理。
- 核心方法/贡献：单 agent 循环中写入、检索、整理、退休自然语言技能；核心机制包括 outcome-driven retirement、bounded active cap、meta-skill authoring guidance、pattern canonicalisation；消融显示退休和 meta-skill 写作先验最关键。
- 可用于我们 workflow 的经验：技能库必须有容量上限、贡献分数、退休机制和写作规范，否则会出现 library drift。
- 警告/风险：论文主要在编程任务验证；科学 workflow 的“贡献”往往不是 pass/fail，而是减少不确定性或定位缺失信息，需要重新定义评分。
- 可落到 optics_agent 的设计点：给项目技能和 workflow 经验增加 `utility_score`、`last_used`、`retire_candidate` 字段，定期清理低贡献或过时经验。
- 优先级：高

## 2605.17721 EXG: Self-Evolving Agents with Experience Graphs
- 文件：`2605.17721.pdf`
- 一句话结论：把成功和失败经验组织成 experience graph，比零散反思或非结构化记忆更适合跨任务复用。
- 核心方法/贡献：将每次尝试抽象为 case node，区分 golden/warning/task anchor 等节点；边表示任务关联、语义相似、错误修正；支持在线实时增长和离线复用。
- 可用于我们 workflow 的经验：经验应以 case 为单位保存，并显式区分成功路径、警告路径和修正关系。
- 警告/风险：图检索和 rerank 质量决定实际效果；如果 case 粒度过粗，会变成普通日志索引。
- 可落到 optics_agent 的设计点：将每次论文复现 run 记录为 case node，边连到论文、参数表、失败类型、最终报告和可复用修复。
- 优先级：高

## 2605.16508 The Scaling Laws of Skills in LLM Agent Systems
- 文件：`2605.16508.pdf`
- 一句话结论：技能库越大不一定越好，路由准确率会随库规模对数衰减，并出现“黑洞技能”劫持。
- 核心方法/贡献：在 15 个模型、1141 个真实技能、300 万次路由/执行决策上总结 routing law 和 execution law；指出局部竞争、跨簇漂移、过泛化技能捕获；提出审计邻居、重写混淆对、移除黑洞技能等优化。
- 可用于我们 workflow 的经验：skill exposure policy 是一等设计对象，不能把所有技能和文档都塞进上下文。
- 警告/风险：统计规律来自大规模 agent 技能集合；小型项目中样本不足，但黑洞技能和过泛化说明仍然适用。
- 可落到 optics_agent 的设计点：限制每次任务加载的技能数量，监控“过常被选但贡献低”的技能，避免 `optics-agent-core` 类通用技能压制专门技能。
- 优先级：高

## 2605.06130 Skill1: Unified Evolution of Skill-Augmented Agents via Reinforcement Learning
- 文件：`2605.06130.pdf`
- 一句话结论：技能选择、技能使用、技能蒸馏应由同一个任务结果信号共同驱动，而不是各自优化。
- 核心方法/贡献：单一 policy 生成检索 query、重排选择技能、基于技能解题、从轨迹蒸馏新技能；用任务结果的低频趋势给 selection credit，用高频变化给 distillation credit。
- 可用于我们 workflow 的经验：workflow 自进化要避免“检索器、执行器、总结器”各自局部最优；最终指标应回传到所有阶段。
- 警告/风险：RL 训练成本高，且需要大量 episode；当前 optics_agent 更适合先做显式评分和人工审计，而非端到端 RL。
- 可落到 optics_agent 的设计点：在每次 run 的最终报告里反向标注本次加载技能、执行策略和新增记忆分别是否有贡献。
- 优先级：中

## 2604.17870 GraSP: Graph-Structured Skill Compositions for LLM Agents
- 文件：`2604.17870.pdf`
- 一句话结论：在检索和执行之间增加“技能编译层”，把扁平技能集合编译成有因果依赖的可执行 DAG，可降低重规划成本。
- 核心方法/贡献：将技能转为带 precondition-effect 边的 typed DAG；节点级验证；通过五类局部修复算子做 locality-bounded repair；在多个环境中减少步骤并提升 reward。
- 可用于我们 workflow 的经验：workflow 节点不应只是线性 prompt 列表，而应有前置条件、输出契约和局部修复范围。
- 警告/风险：科学复现中的依赖条件常含隐含领域假设，自动编译可能漏掉物理约束。
- 可落到 optics_agent 的设计点：为 workflow schema 增加 `preconditions`、`effects`、`verification` 和 `repair_scope`，失败时只回滚受影响子图。
- 优先级：高

## 2604.01687 CoEvoSkills: Self-Evolving Agent Skills via Co-Evolutionary Verification
- 文件：`2604.01687.pdf`
- 一句话结论：复杂多文件技能的自生成需要一个共同进化的 verifier，否则生成器缺少可操作反馈。
- 核心方法/贡献：Skill Generator 迭代构造复杂 skill package；Surrogate Verifier 在无 ground-truth test 内容时共同进化，提供可执行、可操作反馈；在 SkillsBench 上超过多个基线。
- 可用于我们 workflow 的经验：生成 workflow/skill 时必须同步生成 verifier、smoke test 或 rubric，不能只生成说明文档。
- 警告/风险：surrogate verifier 可能过拟合或奖励错误代理指标；科学任务中 surrogate 通过不等于物理复现成功。
- 可落到 optics_agent 的设计点：每个新技能包必须附带最小可运行检查、输入输出契约和失败诊断 checklist。
- 优先级：高

## 2603.13258 Your Code Agent Can Grow Alongside You with Structured Memory
- 文件：`2603.13258.pdf`
- 一句话结论：代码 agent 应从项目提交历史和人类验证结果中学习 intent-to-code 映射，而不是只看静态仓库快照。
- 核心方法/贡献：MemCoder 从历史 commits 结构化人类经验，蒸馏意图到实现的映射；用验证反馈做实时 self-refinement；把人类确认的解法内化为长期记忆。
- 可用于我们 workflow 的经验：项目演化历史本身是 agent 的训练语料，特别适合提取“用户如何修正 agent 输出”的偏好和规范。
- 警告/风险：依赖高质量 commit 历史和明确验证信号；混乱提交会污染记忆。
- 可落到 optics_agent 的设计点：从 `notes/`、`workflows/`、历史 final reports 和用户修正中抽取“论文复现意图 -> 具体动作”的案例记忆。
- 优先级：中

## 2602.08234 SkillRL: Evolving Agents via Recursive Skill-Augmented Reinforcement Learning
- 文件：`2602.08234.pdf`
- 一句话结论：原始轨迹需要被蒸馏成层级技能库，并在策略训练中递归演化，才能减少 token 噪声并提升泛化。
- 核心方法/贡献：通过经验蒸馏构建 SkillBank；区分通用和任务特定启发式的 adaptive retrieval；技能库与 agent policy 在 RL 中共同演化。
- 可用于我们 workflow 的经验：长日志应压缩为高层技能和启发式，并区分“通用工作流规则”和“论文/案例专属规则”。
- 警告/风险：RL 和 benchmark 环境与本项目差异大；没有大量自动评分任务时，递归演化容易自我强化错误经验。
- 可落到 optics_agent 的设计点：把 memory scope 分成方向级、项目级、案例级，并在检索时明确优先级和适用范围。
- 优先级：中

## 2602.04837 Group-Evolving Agents: Open-Ended Self-Improvement via Experience Sharing
- 文件：`2602.04837.pdf`
- 一句话结论：以 agent group 而非单个 agent 为进化单位，可以把探索多样性转化为长期累计进步。
- 核心方法/贡献：GEA 用 performance-novelty 选择 parent group；组内共享轨迹、工具和 learned artifacts；通过 offspring group 继承聚合经验，优于孤立树状分支演化。
- 可用于我们 workflow 的经验：多分支探索后需要共享和合并，而不是保留互不交流的试验分支。
- 警告/风险：适用于可并行评估的大量 coding agent 变体；科学计算任务资源昂贵，不能无约束扩大群体搜索。
- 可落到 optics_agent 的设计点：在参数扫描或多方案复现时，用小规模 parent group 汇总“解析模型、COMSOL、文献查证”三类经验，再生成下一轮方案。
- 优先级：中

## 2601.22758 AutoRefine: From Trajectories to Reusable Expertise for Continual LLM Agent Refinement
- 文件：`2601.22758.pdf`
- 一句话结论：经验模式应分成程序性 subagent 和静态 skill pattern，并持续评分、剪枝、合并。
- 核心方法/贡献：从执行历史提取 dual-form Experience Patterns；复杂程序性子任务封装为有独立推理和记忆的 subagent；静态知识保存为指南或代码片段；维护机制根据经验效用评分、剪枝、合并。
- 可用于我们 workflow 的经验：不是所有经验都应写成同一种记忆；可重复流程适合变成子 agent，简单规则适合变成 skill/pitfall。
- 警告/风险：自动识别“程序性子任务”需要足够多相似轨迹；少样本下容易过早抽象。
- 可落到 optics_agent 的设计点：把“论文参数提取”“Mie 解析复现”“COMSOL job 提交”“最终报告生成”拆成可独立维护的 subagent pattern。
- 优先级：高

## 2505.18646 SEW: Self-Evolving Agentic Workflows for Automated Code Generation
- 文件：`2505.18646.pdf`
- 一句话结论：workflow 的拓扑和 agent prompt 可以作为文本对象被自动生成、评估和进化。
- 核心方法/贡献：Self-Evolving Workflow 自动生成并优化多 agent workflow；同时演化 agent 拓扑和 prompt；比较 BPMN、CoRE、Python、YAML、伪代码等 workflow 表示形式。
- 可用于我们 workflow 的经验：workflow 定义应选择 LLM 易读、可 diff、可验证的表示；YAML/伪代码比隐式聊天流程更适合自迭代。
- 警告/风险：实验集中在代码生成；科学 workflow 的评价函数更复杂，拓扑变更需要防止破坏安全约束和资源约束。
- 可落到 optics_agent 的设计点：继续把 workflow 放在 `.workflow.yaml`，并要求每次拓扑修改递增版本、写 history、附验证结果。
- 优先级：高

## 2406.18532 Symbolic Learning Enables Self-Evolving Agents
- 文件：`2406.18532.pdf`
- 一句话结论：把 agent pipeline 视为由 prompts、tools 和连接方式组成的 symbolic network，可以用自然语言“梯度”做自优化。
- 核心方法/贡献：提出 agent symbolic learning，将 prompt、tool、pipeline 连接视为可学习符号权重；用语言形式的 loss、gradient、optimizer 模拟反向传播和梯度下降。
- 可用于我们 workflow 的经验：失败报告可以转成针对节点 prompt、工具选择和连接关系的结构化“语言梯度”。
- 警告/风险：概念框架强、形式化吸引人，但证明和稳定性有限；语言梯度可能听起来合理却不可执行。
- 可落到 optics_agent 的设计点：在 `update_artifacts` 中区分三类更新建议：prompt gradient、tool gradient、topology gradient，并要求每条建议绑定证据。
- 优先级：中

## 2305.16291 Voyager: An Open-Ended Embodied Agent with Large Language Models
- 文件：`2305.16291.pdf`
- 一句话结论：自动课程、可执行技能库和基于环境反馈的迭代提示构成了早期成功的开放式 lifelong agent 模式。
- 核心方法/贡献：在 Minecraft 中使用 automatic curriculum 最大化探索；用 executable code skill library 存储复杂行为；用环境反馈、执行错误和 self-verification 迭代改进程序。
- 可用于我们 workflow 的经验：开放式探索需要 curriculum，而技能最好是可执行、可组合、可验证的 artifact。
- 警告/风险：Minecraft 环境反馈密集且安全，科学复现反馈稀疏且计算昂贵；“ever-growing skill library” 后续论文已证明会带来维护问题。
- 可落到 optics_agent 的设计点：采用 Voyager 的 executable skill 思路，但必须结合 Ratchet/SkillDAG 的技能治理和结构化检索。
- 优先级：中

## 2303.17651 Self-Refine: Iterative Refinement with Self-Feedback
- 文件：`2303.17651.pdf`
- 一句话结论：单个 LLM 可以通过生成、反馈、修订的测试时循环提升输出质量，是最简单的反思基线。
- 核心方法/贡献：同一模型扮演 generator、feedback provider、refiner；不需要训练数据或权重更新；在多类生成任务上相对一次性生成有提升。
- 可用于我们 workflow 的经验：每个 report、参数表、代码片段都可以先生成再自评再修订，作为低成本质量门。
- 警告/风险：自反馈依赖模型自评能力，容易确认偏误；对物理正确性、数值稳定性等问题必须引入外部验证。
- 可落到 optics_agent 的设计点：将 self-refine 作为文档/摘要/计划节点的默认局部循环，但 COMSOL/数值结论必须由可执行检查或人工领域输入确认。
- 优先级：中

## 2303.11366 Reflexion: Language Agents with Verbal Reinforcement Learning
- 文件：`2303.11366.pdf`
- 一句话结论：把环境反馈转成语言反思并写入 episodic memory，可在不更新权重的情况下改进下一次尝试。
- 核心方法/贡献：将二值/标量/自由文本反馈放大为 verbal reflection；维护反思文本缓冲区；支持外部反馈、启发式反馈和 LLM 自评反馈。
- 可用于我们 workflow 的经验：失败后必须生成行动导向的反思，而不是只记录错误栈；反思应进入下一轮上下文。
- 警告/风险：反思质量和 credit assignment 是瓶颈；没有形式化成功保证，且错误反思会污染后续尝试。
- 可落到 optics_agent 的设计点：每次失败 run 生成固定格式 `reflection`：失败信号、可能原因、下一步最小动作、禁止重复动作，并存入 memento/pitfalls。
- 优先级：高
