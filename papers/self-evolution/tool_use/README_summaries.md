# Tool Use 文献摘要

## 2307.16789 ToolLLM: Facilitating Large Language Models to Master 16000+ Real-world APIs
- 文件：`2307.16789_ToolLLM_ToolBench.pdf`
- 一句话结论：大规模真实 API 工具使用需要“API 检索 + 轨迹生成 + 可执行评估”三件事同时设计，不能只靠把工具说明塞进 prompt。
- 核心方法/贡献：构建 ToolBench，覆盖 RapidAPI 上 16,464 个 REST API；用 ChatGPT 自动生成单工具、多工具、跨类别任务，并用 DFS decision tree 标注可行调用路径；训练 ToolLLaMA，并用 ToolEval 自动评估工具调用过程。
- 可用于我们 workflow 的经验：workflow 节点应显式区分“候选工具检索”“调用路径规划”“执行反馈评估”，并保留多分支尝试而非单一路径贪心执行。
- 警告/风险：自动生成的调用路径和评估器会继承强模型偏差；真实 API 的副作用、权限、速率限制和返回格式漂移不容易被 benchmark 覆盖。
- 可落到 optics_agent 的设计点：为 `workflows/` 增加工具注册表与检索层，节点执行记录应包含候选工具、被选工具、参数、返回、失败分支和最终评估。
- 优先级：高

## 2305.15334 Gorilla: Large Language Model Connected with Massive APIs
- 文件：`2305.15334_Gorilla_APIs.pdf`
- 一句话结论：API 使用的关键失败不是“不会写代码”，而是 API 名称、参数和版本文档幻觉，因此检索增强的文档绑定很重要。
- 核心方法/贡献：提出 Gorilla，基于 LLaMA 微调用于生成 API 调用；构建 APIBench，覆盖 HuggingFace、TorchHub、TensorHub API；结合文档检索，在测试时适应 API 文档变化，并用 AST 子树匹配评估函数调用正确性和幻觉。
- 可用于我们 workflow 的经验：工具接口必须绑定当前文档版本；评估工具调用时应解析结构化调用而不是只看自然语言答案。
- 警告/风险：论文重点是机器学习 API 调用，很多任务没有外部副作用；AST 匹配适合代码/API 片段，不等价于真实执行成功或科学结果正确。
- 可落到 optics_agent 的设计点：COMSOL、Magnus、arXiv、firecrawl 等工具说明应有版本化 schema；workflow 验证可增加“参数 schema 校验 + dry-run/帮助命令 + 执行后 artifact 检查”。
- 优先级：高

## 2304.08244 API-Bank: A Comprehensive Benchmark for Tool-Augmented LLMs
- 文件：`2304.08244_APIBank.pdf`
- 一句话结论：工具增强 LLM 评测应拆成 planning、retrieving、calling 三种能力，并覆盖少/多 API、单/多调用四类场景。
- 核心方法/贡献：提出 API-Bank，包含 73 个可运行 API、314 条人工标注对话和 753 次 API 调用；构造 2,138 个 API 与 1,888 条训练对话；用多 agent 自动生成领域、API、用户请求、调用和响应，降低标注成本。
- 可用于我们 workflow 的经验：benchmark 需要按能力分层，而不是只给端到端成功率；多工具任务要显式测试检索错、规划错、参数错、调用错。
- 警告/风险：自动合成 API 和对话可能过于规则化；工具调用正确不代表用户目标完成，尤其是长程科学任务。
- 可落到 optics_agent 的设计点：为论文复现 workflow 建立分层验收：信息检索正确、参数表完整、代码可运行、测试通过、物理结果可信分别评分。
- 优先级：高

## 2303.17580 HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in Hugging Face
- 文件：`2303.17580_HuggingGPT.pdf`
- 一句话结论：LLM 可以作为控制器，把复杂请求拆成子任务、选择专家模型、执行并汇总，但成败取决于子任务依赖和模型描述质量。
- 核心方法/贡献：提出四阶段框架：任务规划、模型选择、任务执行、响应生成；用自然语言模型卡作为通用接口，让 ChatGPT 调度 Hugging Face 上的多模态模型。
- 可用于我们 workflow 的经验：复杂工作流应把“计划图”和“资源/模型选择”分开记录；每个子任务需要输入输出资源 ID 与依赖关系。
- 警告/风险：模型选择依赖文本描述，容易误选；外部模型执行成本高且失败模式多；最终汇总可能掩盖中间错误。
- 可落到 optics_agent 的设计点：论文复现节点应保存资源句柄，例如 PDF 摘要、参数表、脚本、图像、日志，并在最终报告中引用这些中间 artifact 而非只给自然语言结论。
- 优先级：中

## 2302.04761 Toolformer: Language Models Can Teach Themselves to Use Tools
- 文件：`2302.04761_Toolformer.pdf`
- 一句话结论：工具使用数据可以用“候选调用生成、真实执行、基于损失改进过滤”自监督构造，降低人工标注依赖。
- 核心方法/贡献：用少量示例让语言模型在普通文本中插入 API 调用，执行后只保留能降低后续 token 预测损失的调用；覆盖计算器、QA、搜索、翻译、日历等工具。
- 可用于我们 workflow 的经验：不是所有工具调用都值得保留，应该用执行后收益过滤；历史轨迹可转化为训练/提示样例。
- 警告/风险：损失下降不一定对应任务目标成功；该方法偏离线训练，不能直接解决真实工具权限、副作用和长程回滚问题。
- 可落到 optics_agent 的设计点：对 agent 轨迹做离线复盘，标记哪些工具调用实际减少不确定性或推进验收，并沉淀为技能示例。
- 优先级：中

## 2210.03629 ReAct: Synergizing Reasoning and Acting in Language Models
- 文件：`2210.03629_ReAct.pdf`
- 一句话结论：交替生成 Thought、Action、Observation 能让 agent 在外部反馈中修正计划，是长程工具工作流的基本执行循环。
- 核心方法/贡献：提出 ReAct，将语言推理轨迹和环境动作交织；在 HotpotQA、Fever、ALFWorld、WebShop 中用少量示例提升准确率、可解释性和交互任务成功率。
- 可用于我们 workflow 的经验：每步执行都应记录“为什么行动、调用什么、观察到什么、如何改计划”；静态 CoT 不足以处理检索失败、文件缺失和测试失败。
- 警告/风险：顺序 ReAct 延迟和成本高；长轨迹会累积错误并污染上下文；没有外部验收时容易把观察解释错。
- 可落到 optics_agent 的设计点：workflow state 采用 ReAct 风格日志，但在可并行任务上不要盲目串行，关键节点必须接 acceptance test。
- 优先级：高
