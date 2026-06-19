## 2606.08531 VESTA: A Fully Automated Scenario Generation and Safety Evaluation Framework for LLM Agents
- 文件：`2606.08531_VESTA_Scenario_Generation_Safety_Evaluation.pdf`
- 一句话结论：agent 安全评估应观察执行过程中的权限、工具、监督和目标漂移，而不只是最终回答是否安全。
- 核心方法/贡献：提出五大风险维度和 16 个子类，自动生成 1,072 个可执行安全场景；结合场景族规范、种子案例、LLM 扩展、质量过滤、交互式 attacker 和 episode-level judgment；12 个 agent 平均 ASR 47.1%。
- 可用于我们 workflow 的经验：安全场景要从抽象风险落到可执行任务，并记录完整 episode trace；authority context 和 warning context 可作为实验变量。
- 警告/风险：自动生成与 LLM judge 可能引入同源偏差；ASR 依赖场景设计和判定规则；warning 能降风险但不能替代权限控制。
- 可落到 optics_agent 的设计点：为工具调用建立安全场景库，覆盖 private path 读取、PDF 上传、COMSOL license、Magnus job 提交、文件删除、外部导出等风险；每次 workflow 变更跑 process-level safety smoke。
- 优先级：高

## 2604.16968 On Safety Risks in Experience-Driven Self-Evolving Agents
- 文件：`2604.16968_Safety_Risks_Experience_Driven_Agents.pdf`
- 一句话结论：即使经验全部来自良性任务，经验驱动自演化也会强化“执行倾向”，在高风险场景降低安全性。
- 核心方法/贡献：研究 AWM 与 ReasoningBank 等经验记忆机制；在 web 和 household embodied 环境测试自演化前后 ASR；发现 benign experience 会提升攻击成功率，检索经验越多风险越大；拒绝经验可缓解但导致 over-refusal。
- 可用于我们 workflow 的经验：memory 不是无害缓存，经验条目会改变后续行为倾向；应区分执行经验、拒绝经验、警告经验，并对检索数量和适用域设限。
- 警告/风险：经验越多不一定越安全；只根据成功反馈沉淀 memory 会污染 agent 的风险边界；安全和效用存在 trade-off。
- 可落到 optics_agent 的设计点：memento 写入和检索要带 `risk_scope`、`domain_scope`、`allowed_use`；高风险节点检索 memory 时限制 top-k，并要求安全反例或拒绝案例同时进入上下文。
- 优先级：高

## 2509.26354 Your Agent May Misevolve: Emergent Risks in Self-Evolving LLM Agents
- 文件：`2509.26354_Your_Agent_May_Misevolve.pdf`
- 一句话结论：自演化 agent 可能沿 model、memory、tool、workflow 四条路径发生“误演化”，内部生成新的安全漏洞。
- 核心方法/贡献：提出 misevolution 概念，强调 temporal emergence、self-generated vulnerability、limited data control、expanded risk surface；实证显示 memory evolution 会降低拒绝率，tool evolution 会生成或复用有漏洞工具，workflow evolution 会导致安全衰减。
- 可用于我们 workflow 的经验：任何自动改 prompt、memory、tool 或 workflow topology 的能力都必须先视为高风险变更，而非单纯性能优化。
- 警告/风险：自生成工具可能隐藏数据泄漏、越权分享、跨域误用；memory 可能学习错误偏好；workflow 优化可能绕过人工审批。
- 可落到 optics_agent 的设计点：`update_artifacts` 必须输出 diff、风险分类、回滚点和安全验收；新增工具必须过 export whitelist、private path denylist、secret scan、最小权限和人工确认。
- 优先级：高

## 2509.23694 SafeSearch: Automated Red-Teaming of LLM-Based Search Agents
- 文件：`2509.23694_SafeSearch_Red_Teaming_Search_Agents.pdf`
- 一句话结论：搜索 agent 会把开放互联网的不可靠结果当成权威上下文，安全风险可通过沙盒化红队自动测量。
- 核心方法/贡献：构建 SafeSearch 自动红队框架，生成 300 个覆盖 misinformation、prompt injection、广告推广、偏见等风险的测试；通过差分测试、指南辅助网站生成、沙盒注入不可靠搜索结果和专用 LLM evaluator 评估 17 个模型与 3 种 search scaffold。
- 可用于我们 workflow 的经验：外部搜索和文献网页结果必须视为不可信输入；应比较“有搜索/无搜索”输出差异，检测 stance shift 和引用污染。
- 警告/风险：reminder prompting 防护有限；长尾、难验证问题最容易被低质量来源带偏；搜索预算和 scaffold 设计会隐式影响安全。
- 可落到 optics_agent 的设计点：web 文献检索节点保存 source trust score、引用 URL、检索日期和差分摘要；禁止从搜索结果直接导入可执行代码或工具，除非经过沙盒和人工白名单。
- 优先级：高

## 2502.09809 AgentGuard: Repurposing Agentic Orchestrator for Safety Evaluation of Tool Orchestration
- 文件：`2502.09809_AgentGuard_Safety_Evaluation_Tool_Orchestration.pdf`
- 一句话结论：可以让目标 agent 的 orchestrator 反过来生成、执行并验证自己的危险工具编排，再产出 sandbox 约束。
- 核心方法/贡献：AgentGuard 分四阶段：unsafe workflow identification、unsafe workflow validation、safety constraint generation、safety constraint validation；输出包含危险 workflow、测试用例、违反原则和已验证约束的评估报告。
- 可用于我们 workflow 的经验：tool safety 不只看单个工具，而要测试多工具组合是否产生恶意效果；安全约束必须通过复跑测试验证。
- 警告/风险：原型假设 orchestrator 会诚实暴露风险且具备安全知识；约束生成可能不可执行或过宽；真实环境执行测试要严格隔离。
- 可落到 optics_agent 的设计点：为 file、shell、web、github、Magnus 等工具组合生成 unsafe workflow 测试，并把通过验证的 deny rules/export whitelist 写入工具策略文档。
- 优先级：高

## 2406.13352 AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents
- 文件：`2406.13352_AgentDojo_Dynamic_Environment_Attacks.pdf`
- 一句话结论：prompt injection 防御需要在有状态、多工具、含不可信数据的动态环境中同时评估 utility 和 security。
- 核心方法/贡献：提供 97 个现实任务、629 个安全测试、74 个工具和可扩展动态环境；攻击目标通过工具返回的不可信数据注入；用环境状态的 formal checks 评估 utility 和 targeted/untargeted ASR。
- 可用于我们 workflow 的经验：工具输出必须区分 data 与 instruction；安全评估应有真实环境状态检查，而不是只靠 LLM 判断。
- 警告/风险：现有防御只能降低部分攻击成功率，无法保证安全关键任务；静态 benchmark 会滞后于攻击和防御演化。
- 可落到 optics_agent 的设计点：把 PDF 文本、网页、日志、README 中的指令视为不可信数据；工具输出进入模型前加来源标签，禁止其覆盖 system/workflow 规则；对导出、删除、提交、上传等动作加独立权限检查。
- 优先级：高

## 2309.15817 Identifying the Risks of LM Agents with an LM-Emulated Sandbox
- 文件：`2309.15817_ToolEmu_Sandboxed_Tool_Execution.pdf`
- 一句话结论：LM-emulated sandbox 可低成本发现长尾高风险工具调用失败，但结果仍需现实可行性验证。
- 核心方法/贡献：ToolEmu 用 LLM 模拟工具执行和环境状态，配套自动安全 evaluator 与 helpfulness evaluator；覆盖 36 个高风险 toolkits、144 个测试案例和 9 类风险；68.8% 被识别失败经人工验证为真实风险。
- 可用于我们 workflow 的经验：在真实工具不可随便调用时，可先用模拟器做红队和风险筛查，再把高风险案例转为真实 sandbox 测试。
- 警告/风险：模拟器和 evaluator 可能共同被 prompt injection 欺骗；模拟成功不等于真实世界可复现；最安全 agent 仍有显著失败率。
- 可落到 optics_agent 的设计点：对 COMSOL/Magnus/GitHub/文件系统高风险动作先建立 dry-run/emulated execution 层，所有真实执行前要求 manifest、权限、资源、导出路径和回滚策略检查通过。
- 优先级：高
