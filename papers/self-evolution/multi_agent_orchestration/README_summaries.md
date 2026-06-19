# Multi-Agent Orchestration 文献摘要

## 2603.11445 Verified Multi-Agent Orchestration: A Plan-Execute-Verify-Replan Framework for Complex Query Resolution
- 文件：`2603.11445_Verified_Multi_Agent_Orchestration.pdf`
- 一句话结论：复杂研究型任务需要把“计划-执行-验证-重计划”做成显式闭环，而不是只依赖一次性分工。
- 核心方法/贡献：提出 VMAO，将复杂查询拆成带依赖的 DAG，调用领域 agent 并行执行，由 LLM verifier 检查完整性，再针对缺口自适应重计划，并用质量阈值和资源约束控制停止。
- 可用于我们 workflow 的经验：workflow 节点应保留依赖图、上游上下文传播、验证结果和重计划原因，验证器应评价整体目标覆盖度而非单个 agent 的回答好坏。
- 警告/风险：LLM verifier 可能把“看似完整”误判为真实完整；循环重计划会带来成本膨胀，必须设置迭代上限和证据要求。
- 可落到 optics_agent 的设计点：为论文复现 workflow 增加 `verify_gaps` 节点，输出缺失参数、缺失物理验证、缺失代码/COMSOL证据，并只对缺口生成追加任务。
- 优先级：高

## 2602.03128 Understanding Multi-Agent LLM Frameworks: A Unified Benchmark and Experimental Analysis
- 文件：`2602.03128_MAFBench_Unified_Multi_Agent_Framework_Benchmark.pdf`
- 一句话结论：多 agent 系统的成败很大程度由框架架构决定，同一模型和任务下延迟、吞吐、规划准确率和协作成功率可相差数量级。
- 核心方法/贡献：提出多 agent 框架架构分类和 MAFBench，统一评估 orchestration、memory、planning、specialization、coordination 等维度，发现架构选择可导致 100 倍以上延迟差异和显著成功率波动。
- 可用于我们 workflow 的经验：不要只评估最终正确率；每个 workflow 版本都应记录延迟、工具调用数、内存检索质量、分工收益和协调失败类型。
- 警告/风险：更多 agent 不等于更强；框架抽象可能引入巨大 coordination overhead，尤其在简单任务上会吞掉收益。
- 可落到 optics_agent 的设计点：建立 `workflow_metrics.md` 或状态字段，跟踪节点耗时、调用次数、重试次数、人工输入点、并行度和成功/失败标签。
- 优先级：高

## 2512.21309 A Plan Reuse Mechanism for LLM-Driven Agent
- 文件：`2512.21309_Plan_Reuse_Mechanism_for_LLM_Driven_Agent.pdf`
- 一句话结论：相似任务应复用结构化计划而不是复用最终答案，这能显著降低规划延迟且避免参数错用。
- 核心方法/贡献：提出 AgentReuse，基于意图分类和关键参数替换判断请求相似性，缓存并复用 LLM 生成的计划；真实数据上有效复用率约 93%，规划延迟显著下降。
- 可用于我们 workflow 的经验：历史复现实验可抽象为“计划模板 + 参数槽位 + 适用条件”，遇到同类论文/图表时复用流程而不是复制结论。
- 警告/风险：如果相似性只靠原始文本 embedding，会把参数变化误判为不可复用或错误复用；计划模板必须显式标注可替换变量和不可替换前提。
- 可落到 optics_agent 的设计点：把 Mie/COMSOL/文献摘要 workflow 保存为可检索 plan template，字段包括任务类型、输入参数槽、工具链、验证标准和禁用条件。
- 优先级：高

## 2511.09710 Echoing: Identity Failures When LLM Agents Talk to Each Other
- 文件：`2511.09710_Echoing_Identity_Failures_Agent_to_Agent.pdf`
- 一句话结论：agent-agent 长对话会诱发身份漂移，agent 可能镜像对方角色，即使任务完成指标看起来成功也可能目标已偏移。
- 核心方法/贡献：系统研究 AxA 中的 echoing 失败，覆盖 66 种配置、4 个领域、2500+ 对话；发现 echoing 可高达 70%，7 轮以上更易出现，结构化响应协议可显著降低但不能根除。
- 可用于我们 workflow 的经验：worker/reviewer/expert 的身份和目标不能只写在初始 prompt；每轮交接需要短格式协议，强制声明角色、目标、不可越权事项和输出类型。
- 警告/风险：单看“是否完成任务”会掩盖身份漂移；多 agent 互评若缺少外部 grounding，可能互相迎合并强化错误。
- 可落到 optics_agent 的设计点：为 reviewer/expert 输出添加固定头部：`角色`、`检查对象`、`拒绝做的事`、`结论置信度`，并在状态文件记录 identity drift 检查。
- 优先级：高

## 2506.15451 Agent Group Chat-V2: Divide-and-Conquer Is What LLM-Based Multi-Agent System Need
- 文件：`2506.15451_Divide_and_Conquer_Multi_Agent.pdf`
- 一句话结论：多 agent 的有效性来自任务层、执行层和系统层的 divide-and-conquer，而不是简单群聊。
- 核心方法/贡献：提出 AgentGroupChat-V2，以 Query Manager、Task Manager、Group Manager 组织任务森林，动态选择异构 LLM 和交互模式，并行处理子任务，在数学、代码和复杂推理任务上优于基线。
- 可用于我们 workflow 的经验：复杂科研任务适合拆成任务森林，每个子树有独立 agent 组和局部上下文，最终由上层节点汇总。
- 警告/风险：任务拆解质量决定上限；如果子任务依赖没有建模，盲目并行会造成重复、冲突或缺失前提。
- 可落到 optics_agent 的设计点：在 paper reproduction workflow 中把“读论文、提参数、推导、数值实现、验证、报告”作为可并行但有依赖的任务森林。
- 优先级：中

## 2506.12508 AgentOrchestra: Orchestrating Multi-Agent Intelligence with the Tool-Environment-Agent (TEA) Protocol
- 文件：`2506.12508_AgentOrchestra.pdf`
- 一句话结论：agent、tool、environment 都应作为带生命周期和版本的资源管理，才能支持可追溯的自演化。
- 核心方法/贡献：提出 TEA 协议，把工具、环境、agent 建模为一等、可版本化组件，并在 AgentOrchestra 中用中心 planner 协调 research/web/analysis/tool synthesis/reporting 等专门 agent，支持反馈驱动的组件演化。
- 可用于我们 workflow 的经验：workflow 不应只保存 prompt，还要保存环境、工具版本、输入输出 artifact、运行上下文和自演化补丁。
- 警告/风险：协议层复杂度较高；如果没有版本锁定和回滚，自演化会让结果不可复现。
- 可落到 optics_agent 的设计点：将 workflow 节点状态扩展为 TEA 风格：`agent_version`、`tool_version`、`environment`、`artifact_refs`、`evolution_patch`、`rollback_ref`。
- 优先级：高

## 2501.06322 Multi-Agent Collaboration Mechanisms: A Survey of LLMs
- 文件：`2501.06322_Multi_Agent_Collaboration_Survey.pdf`
- 一句话结论：多 agent 协作机制可按参与者、协作类型、结构、策略和协调协议系统分类，设计时应先选机制而非先堆角色。
- 核心方法/贡献：综述 LLM 多 agent 协作，提出覆盖 actors、cooperation/competition/coopetition、centralized/distributed、role/model-based strategy、coordination protocol 的框架，并总结应用和开放挑战。
- 可用于我们 workflow 的经验：不同任务阶段应使用不同协作机制；参数抽取适合并行专家，物理一致性审查适合 reviewer，路线选择适合 supervisor 集中决策。
- 警告/风险：综述层面给出分类但缺少统一工程指标；协作结构若不随任务调整，会把简单流程复杂化。
- 可落到 optics_agent 的设计点：在每个 workflow 节点声明协作模式：`single`、`supervisor_worker`、`reviewer_gate`、`parallel_experts` 或 `debate`。
- 优先级：中

## 2412.05449 Towards Effective GenAI Multi-Agent Collaboration: Design and Evaluation for Enterprise Applications
- 文件：`2412.05449_Enterprise_Multi_Agent_Collaboration_Design_Evaluation.pdf`
- 一句话结论：企业级多 agent 应优先采用层级 supervisor/specialist，并用断言式 benchmark、payload referencing 和路由模式控制质量与延迟。
- 核心方法/贡献：评估层级多 agent 框架的 coordination 和 routing 两种模式；在企业场景中多 agent 最高提升 70% 成功率，payload referencing 改善代码密集任务，routing 可绕过不必要编排降低延迟。
- 可用于我们 workflow 的经验：不是所有请求都要进完整 workflow；简单查找或固定格式任务应由 routing 直接分派，复杂任务才进入 supervisor 协调。
- 警告/风险：同步消息传递会阻塞；payload 引用需要稳定 artifact ID，否则 specialist 容易拿错上下文。
- 可落到 optics_agent 的设计点：为工作流引擎增加 routing 前置判断，并用 artifact 引用而非复制长上下文传递 PDF 摘要、参数表、日志和图表。
- 优先级：高

## 2410.21784 MARCO: Multi-Agent Real-time Chat Orchestration
- 文件：`2410.21784_MARCO_Multi_Agent_Real_time_Chat_Orchestration.pdf`
- 一句话结论：实时任务型 agent 需要确定性任务执行过程、混合共享记忆和 guardrails，而不是完全自由规划。
- 核心方法/贡献：提出 MARCO，用自然语言 Task Execution Procedure 指导 agent，通过共享混合记忆记录完整上下文、工具更新和对话轮次，并用 guardrails 修复格式、函数、参数和安全错误。
- 可用于我们 workflow 的经验：科研复现节点可以用 TEP/SOP 限制 agent 行为，将 LLM 只放在需要判断、补全和解释的位置，确定性步骤交给脚本。
- 警告/风险：过度依赖预定义 TEP 会降低开放探索能力；guardrails 需要覆盖工具参数幻觉和格式漂移。
- 可落到 optics_agent 的设计点：为每类节点写 TEP：输入、允许工具、参数检查、失败恢复、输出 schema；把共享记忆限定为当前任务相关 artifact。
- 优先级：中

## 2401.07324 Small LLMs Are Weak Tool Learners: A Multi-LLM Agent
- 文件：`2401.07324_Small_LLMs_Are_Weak_Tool_Learners_Multi_LLM_Agent.pdf`
- 一句话结论：工具使用可拆成 planner、caller、summarizer 三种能力，模块化小模型/agent 比单模型全包更易训练和维护。
- 核心方法/贡献：提出 α-UMi，把工具学习分解为规划、工具调用、结果总结，并用 global-to-local progressive fine-tuning 分别强化角色，在多个工具学习 benchmark 上优于单 LLM agent。
- 可用于我们 workflow 的经验：工具调用失败常来自“规划、调用、总结”混在一起；拆角色能让 reviewer 精确定位是计划错、参数错还是总结错。
- 警告/风险：多模型拆分增加接口和状态传递成本；caller 必须有严格参数 schema，否则小模型更易产生非法调用。
- 可落到 optics_agent 的设计点：将节点内部拆为 `planner`、`tool_caller`、`summarizer/reporter` 三段日志，便于失败复盘和记忆写入。
- 优先级：中

## 2308.08155 AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation
- 文件：`2308.08155_AutoGen_Multi_Agent_Conversation_Framework.pdf`
- 一句话结论：可对话、可定制 agent 和可编程 conversation pattern 是通用多 agent 应用的基础抽象。
- 核心方法/贡献：提出 AutoGen，支持 LLM、工具、人类输入组合成 conversable agent，并允许用自然语言或代码定义 joint/hierarchical 等对话模式，覆盖数学、代码、问答和决策等场景。
- 可用于我们 workflow 的经验：human-in-the-loop、tool executor、critic、domain expert 都可以统一成消息节点，但必须有清晰的终止条件和发言规则。
- 警告/风险：自由对话模式容易产生冗余轮次、闲聊和上下文污染；缺少结构化交接时难以审计。
- 可落到 optics_agent 的设计点：保留 AutoGen 式灵活角色，但在 workflow 层强制每轮消息写入结构化 state 和 artifact，而不是只留聊天记录。
- 优先级：中

## 2308.00352 MetaGPT: Meta Programming for a Multi-Agent Collaborative Framework
- 文件：`2308.00352_MetaGPT_Multi_Agent_Collaborative_Framework.pdf`
- 一句话结论：把人类 SOP 编码进 agent 协作流程，比开放式角色扮演更能减少级联幻觉和交付不一致。
- 核心方法/贡献：提出 MetaGPT，用软件工程 SOP 和装配线式角色分工生成结构化中间产物，如需求文档、设计、流程图、接口和代码；在软件工程 benchmark 上表现更稳定。
- 可用于我们 workflow 的经验：每个科研 workflow 节点都应产生可审查中间件，而不是直接跳到最终报告。
- 警告/风险：SOP 依赖领域知识；错误 SOP 会稳定地产生错误流程，必须允许 reviewer 更新 SOP。
- 可落到 optics_agent 的设计点：把论文复现 SOP 固化为“论文事实表、参数表、理论假设表、数值配置、验证表、失败报告”六类中间 artifact。
- 优先级：高

## 2307.07924 ChatDev: Communicative Agents for Software Development
- 文件：`2307.07924_ChatDev_Communicative_Agents_for_Software.pdf`
- 一句话结论：chat chain 和 communicative dehallucination 可以把多 agent 软件开发过程拆成受控对话链，降低代码幻觉。
- 核心方法/贡献：提出 ChatDev，让设计、编码、测试等角色通过自然语言和编程语言协作；用 chat chain 规定“交流什么”，用 dehallucination 机制让 agent 在信息不足时主动追问而非编造。
- 可用于我们 workflow 的经验：科学计算代码生成也应有“需求澄清-实现-执行-测试-修正”的链式协议，信息不足时必须显式停下请求参数或模板。
- 警告/风险：对话链仍可能在前置错误上级联；如果没有执行测试，沟通本身不能保证代码正确。
- 可落到 optics_agent 的设计点：给数值程序节点加入“缺失信息检查”和“必须运行最小测试”门槛，失败时输出 blocker 而非虚构结果。
- 优先级：中

## 2303.17760 CAMEL: Communicative Agents for Mind Exploration of Large Language Model Society
- 文件：`2303.17760_CAMEL_Communicative_Agents.pdf`
- 一句话结论：角色扮演能自动生成协作数据和推动任务完成，但早期系统已暴露 role flipping、重复指令和无限循环等风险。
- 核心方法/贡献：提出 CAMEL role-playing 和 inception prompting，用少量人类任务想法驱动两个或多个 agent 自主协作，并生成 AI Society、Code、Math、Science、Misalignment 等数据集。
- 可用于我们 workflow 的经验：角色初始化要包含任务、身份、对话边界、停止信号和反循环机制；对话记录可用于后续经验抽取。
- 警告/风险：role-playing 容易身份翻转、空回复、重复和循环；生成数据可放大未对齐行为。
- 可落到 optics_agent 的设计点：把多 agent 交互的每次异常标成 `role_flip`、`loop`、`irrelevant_reply`、`missing_stop`，进入 memory/pitfall 评估。
- 优先级：中
