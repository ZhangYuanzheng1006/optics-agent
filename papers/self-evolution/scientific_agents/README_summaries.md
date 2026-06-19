# PDF 文献摘要

## 2601.03315 Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts
- 文件：`2601.03315_Why_LLMs_Arent_Scientists_Yet.pdf`
- 一句话结论：当前 LLM 科学家系统能完成局部研究流程，但长链路自主科研仍主要失败在实现漂移、上下文衰减、错误成功判定和科学品味不足。
- 核心方法/贡献：作者用 6 个 agent 串联 idea generation、hypothesis generation、experimental planning、implementation/evaluation、revision、paper outlining，复盘 4 次端到端 ML 论文生成尝试，其中 3 次失败、1 次进入 Agents4Science 2025。
- 可用于我们 workflow 的经验：每个阶段都应产出显式文件制品，如 `idea.md`、`hypotheses.md`、`plan.md`、`code_logs.md`、`paper_outline.md`，让后续节点读取稳定上下文，而不是依赖对话记忆。
- 警告/风险：失败模式非常贴近 optics_agent 风险，包括实现偏离论文意图、执行压力下简化目标、长任务记忆退化、把明显失败误报为成功。
- 可落到 optics_agent 的设计点：为 paper reproduction workflow 增加“实现忠实度检查”“结果有效性检查”“过度乐观声明审查”三个强制 gate，并把失败原因写入可追踪日志。
- 优先级：高

## 2510.09901 Autonomous Agents for Scientific Discovery: Orchestrating Scientists, Language, Code, and Physics
- 文件：`2510.09901_Autonomous_Agents_for_Scientific_Discovery.pdf`
- 一句话结论：科学 agent 应按假设发现、实验设计与执行、结果分析与修正三阶段组织，并显式编排人类、自然语言、代码和物理工具。
- 核心方法/贡献：综述 LLM 科学 agent 的方法谱系，提出三阶段发现流程：knowledge extraction/hypothesis generation/screening，tool use 或 tool creation 执行实验，最后 result analysis/refinement。
- 可用于我们 workflow 的经验：把“现有工具调用”和“新工具生成”分开建模，适合 optics_agent 区分 Python 解析模型、COMSOL 模板、Magnus 提交器和后处理脚本。
- 警告/风险：论文是愿景和综述性质，不能直接证明通用 agent 已能可靠完成物理复现；验证和泛化仍是开放问题。
- 可落到 optics_agent 的设计点：将工作流节点重新标注为 hypothesis discovery、experimental design/execution、analysis/refinement 三类，并为每类定义输入、输出、验证器和回退策略。
- 优先级：高

## 2510.05158 Lang-PINN: From Language to Physics-Informed Neural Networks via a Multi-Agent Framework
- 文件：`2510.05158_Lang_PINN_Language_to_PINN_Multi_Agent.pdf`
- 一句话结论：自然语言到可训练科学程序的链路需要拆成“物理形式化、模型选择、代码生成、执行反馈”四个角色，而不是一次性生成代码。
- 核心方法/贡献：Lang-PINN 使用 PDE Agent、PINN Agent、Code Agent、Feedback Agent，把任务描述转为符号 PDE、选择 PINN 架构、生成模块化代码并通过运行错误和指标反馈迭代。
- 可用于我们 workflow 的经验：对 paper reproduction 很有启发：先把论文描述转成可验证的物理方程/边界条件，再生成计算程序；反馈 agent 同时检查运行错误、效果、效率和鲁棒性。
- 警告/风险：该系统面向 PINN，不能直接覆盖 COMSOL 全波仿真；其 benchmark 有明确 ground truth PDE，而论文复现常缺少完整边界、网格和材料细节。
- 可落到 optics_agent 的设计点：增加 `physics_formalization` 节点，把论文文本转成 geometry/materials/equations/boundaries/solver 的规范表，再交给代码或 COMSOL 生成节点。
- 优先级：高

## 2508.14111 From AI for Science to Agentic Science: A Survey on Autonomous Scientific Discovery
- 文件：`2508.14111_Survey_Autonomous_Scientific_Discovery.pdf`
- 一句话结论：Agentic Science 可被视为 AI for Science 从专家工具到自主科研伙伴的阶段，并需要能力、流程和领域应用三层统一框架。
- 核心方法/贡献：提出五类核心能力：reasoning/planning、tool integration、memory、multi-agent collaboration、optimization/evolution；并把科学发现建模为 observation/hypothesis、planning/execution、data/result analysis、synthesis/validation/evolution 四阶段动态流程。
- 可用于我们 workflow 的经验：这篇适合作为 optics_agent 的高层 taxonomy，用来检查我们是否缺少记忆、工具、协作、优化演化等基础能力。
- 警告/风险：综述跨度很大，具体工程细节不足；若直接套用会变成空泛模块清单，需要结合我们的 paper reproduction 和 Magnus/COMSOL 约束落地。
- 可落到 optics_agent 的设计点：在 workflow 设计文档中加入“四阶段科学发现 loop + 五能力支撑层”的矩阵，用于标记每个节点依赖哪些 agent 能力。
- 优先级：中

## 2505.18705 AI-Researcher: Autonomous Scientific Innovation
- 文件：`2505.18705_AI_Researcher.pdf`
- 一句话结论：端到端科研自动化需要把文献、假设、实现、实验、论文生成和 benchmark 评价全部纳入统一系统，而不仅是代码执行。
- 核心方法/贡献：提出 AI-Researcher 多 agent 系统和 Scientist-Bench；benchmark 用目标论文、15-20 篇参考文献、研究指令和数据集评估 agent 生成代码与技术报告的质量。
- 可用于我们 workflow 的经验：Scientist-Bench 的输入构造很有用：从目标论文抽取核心研究任务，同时屏蔽具体实现细节，可测试 agent 是否理解科学问题而非复述论文。
- 警告/风险：主要面向 AI/Data Science 论文，评价依赖 LLM 评审和人类论文对齐；物理复现还需要数值误差、量纲、边界条件和物理趋势验证。
- 可落到 optics_agent 的设计点：为 optics paper reproduction 建一个小型 benchmark：输入论文与目标图，输出参数表、程序、结果图、报告；评分分为参数抽取、运行成功、物理一致性和报告可信度。
- 优先级：高

## 2408.06292 The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery
- 文件：`2408.06292_AI_Scientist.pdf`
- 一句话结论：The AI Scientist 首次系统展示了 idea、experiment、write-up、review 的低成本端到端自动科研闭环，但可靠性和物理适用性仍需强验证。
- 核心方法/贡献：系统从初始代码模板出发，生成想法、检索 novelty、计划并执行实验、记录实验日志、绘图、写 LaTeX 论文，再用自动 reviewer 打分并归档结果。
- 可用于我们 workflow 的经验：它的“实验日志 + 图表说明 + 分节写作 + 自动审稿”适合作为 paper reproduction 后半段模板，尤其适合强制只引用真实实验 notes 和 figures。
- 警告/风险：自由编辑代码会导致意外行为；自动 reviewer 不能替代物理验证；低成本小实验策略不等于能复现高保真 COMSOL/光学结果。
- 可落到 optics_agent 的设计点：建立 `archive` 和 `review` 节点：每次复现结束归档参数、代码、结果、失败标签，并由自动 reviewer 检查是否把 pipeline success 误写成 physical reproduction success。
- 优先级：高
