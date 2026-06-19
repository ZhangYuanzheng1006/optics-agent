# Planning And Reasoning 文献摘要

## 2406.11638 MASAI: Modular Architecture for Software-engineering AI Agents
- 文件：`2406.11638_Plan_Execute_Verify_Agents.pdf`
- 一句话结论：长程软件工程任务适合拆成多个目标明确的子 agent，而不是让单一 agent 扛完整上下文和完整轨迹。
- 核心方法/贡献：提出 MASAI，由 Test Template Generator、Issue Reproducer、Edit Localizer、Fixer、Ranker 五类子 agent 组成；不同子 agent 可使用不同策略如 ReAct 或 CoT；在 SWE-bench Lite 上报告 28.33% resolution rate，并分析模块设计影响。
- 可用于我们 workflow 的经验：plan-execute-verify 应细化为可组合角色：生成验收模板、复现问题、定位、修复/实现、排序/验收。
- 警告/风险：多 agent 会引入接口契约和错误传递问题；子 agent 输出若不结构化，最终 ranker 很难可靠比较；SWE-bench 结果不直接代表科学复现能力。
- 可落到 optics_agent 的设计点：论文复现 workflow 可拆为参数抽取、理论检查、数值实现、运行验证、图像/物理验收、报告更新等子 agent，每个子 agent 输出固定 schema。
- 优先级：高

## 2312.04511 An LLM Compiler for Parallel Function Calling
- 文件：`2312.04511_LLMCompiler_Parallel_Function_Calling.pdf`
- 一句话结论：多工具调用不必全走 ReAct 串行循环，可以先编译成带依赖的任务 DAG，再并行执行并在需要时重规划。
- 核心方法/贡献：提出 LLMCompiler，由 Function Calling Planner、Task Fetching Unit、Executor 组成；生成函数调用计划和依赖关系，支持并行执行、动态 replanning；在多个任务上相对 ReAct 降低延迟和成本并提升准确率。
- 可用于我们 workflow 的经验：workflow 引擎应把节点依赖显式化，能并行的检索、解析、测试、绘图不要串行；观察结果只在 join 点汇总，减少上下文污染。
- 警告/风险：计划器若错误判断依赖，会导致并行执行浪费或错误；有强反馈依赖的任务仍需动态重规划；并行会增加资源争用和日志管理复杂度。
- 可落到 optics_agent 的设计点：把 `paper_reproduction.workflow.yaml` 的 independent checks 设计成 DAG，例如 PDF 参数提取、公式复核、代码环境检查可并行，COMSOL/数值运行后再 join 验收。
- 优先级：高

## 2308.09687 Graph of Thoughts: Solving Elaborate Problems with Large Language Models
- 文件：`2308.09687_Graph_of_Thoughts.pdf`
- 一句话结论：复杂推理不只是一条链或一棵树，很多任务需要把多个思路合并、精炼、循环改进，适合用 thought graph 表示。
- 核心方法/贡献：提出 Graph of Thoughts，将 LLM 产生的信息单元建模为图节点，依赖为边；支持聚合、回溯、精炼和反馈循环；在排序、关键词统计、集合操作、文档合并等任务上展示质量和成本优势。
- 可用于我们 workflow 的经验：中间结论应允许合并和互相引用，而不是只保留线性日志；适合用于多来源证据整合和候选方案比较。
- 警告/风险：图结构设计本身需要策略；节点数量膨胀会增加成本；如果评估函数弱，图会放大错误思路。
- 可落到 optics_agent 的设计点：为论文复现建立证据图：PDF 文本、公式推导、参数表、代码结果、图像指标作为节点，报告结论只从已验证节点聚合。
- 优先级：中

## 2305.10601 Tree of Thoughts: Deliberate Problem Solving with Large Language Models
- 文件：`2305.10601_Tree_of_Thoughts.pdf`
- 一句话结论：当任务需要探索、前瞻和回溯时，维护多个 thought 分支并自评估，比单条 CoT 更可靠。
- 核心方法/贡献：提出 Tree of Thoughts，将中间推理步骤作为节点，使用 BFS/DFS 等搜索算法生成、评估和选择分支；在 Game of 24、Creative Writing、Mini Crosswords 上显著优于 CoT。
- 可用于我们 workflow 的经验：对不确定的建模选择或修复方案，应保留多个候选并用验收测试筛选，而不是过早承诺单一路径。
- 警告/风险：分支搜索成本高；自评估可能不可靠；对可直接验证的工程任务，应优先用测试而非纯 LLM 打分。
- 可落到 optics_agent 的设计点：在理论模型、数值近似、参数缺失处理上启用候选分支，分支必须带假设、运行成本和验收指标。
- 优先级：中

## 2305.04091 Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models
- 文件：`2305.04091_Plan_and_Solve_Prompting.pdf`
- 一句话结论：先生成计划再逐步执行，可以减少 Zero-shot CoT 的漏步骤问题；更详细的变量和计算要求可降低计算错误。
- 核心方法/贡献：提出 Plan-and-Solve prompting，用“先理解问题并制定计划，再按计划逐步求解”替代简单“Let's think step by step”；PS+ 增加变量提取、数值提取和中间计算注意事项，在多类推理数据集上提升零样本表现。
- 可用于我们 workflow 的经验：每个复杂节点开始前应先写最小计划和变量清单，执行后再抽取最终答案；计划本身要可检查。
- 警告/风险：prompt 层面的计划不能保证执行正确；可能产生看似完整但未经验证的步骤；对工具任务仍需外部观察和测试。
- 可落到 optics_agent 的设计点：论文复现节点模板加入“变量/参数清单、子任务计划、执行记录、验收结果”四段，避免遗漏实验条件。
- 优先级：中

## 2210.03629 ReAct: Synergizing Reasoning and Acting in Language Models
- 文件：`2210.03629_ReAct.pdf`
- 一句话结论：ReAct 是计划-行动-观察-修正循环的基础范式，适合需要外部信息和环境反馈的长程任务。
- 核心方法/贡献：将 reasoning trace 与 task-specific action 交替生成，用外部 API 或环境观察支撑推理，并让推理追踪、更新和修正行动计划；在 QA、事实验证、交互决策任务上优于只推理或只行动。
- 可用于我们 workflow 的经验：计划不能一次写完就冻结，执行观察应能触发 plan update；日志格式应支持审计每个 action 的前因后果。
- 警告/风险：纯串行 ReAct 成本高且慢；长上下文会导致无关观察干扰；没有明确停止条件时容易循环。
- 可落到 optics_agent 的设计点：每个 workflow 节点定义停止条件、失败条件和最大重试次数；用 state 文件记录 Thought/Action/Observation，但配合 DAG 并行和 acceptance tests。
- 优先级：高
