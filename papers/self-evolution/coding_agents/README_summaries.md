# Coding Agents 文献摘要

## 2606.07412 Socratic-SWE: Self-Evolving Coding Agents via Trace-Derived Agent Skills
- 文件：`2606.07412_Socratic_SWE.pdf`
- 一句话结论：代码 agent 的自进化可把历史求解轨迹蒸馏成技能，再用技能生成针对当前弱点的新任务，形成 trace-skill-task 闭环。
- 核心方法/贡献：提出 Socratic-SWE，从代码搜索、编辑、命令执行、测试运行等历史轨迹中提取失败模式和修复模式；技能指导真实仓库中的 repair task 生成；候选任务经过执行验证和 solver-gradient alignment 奖励筛选；迭代训练后在 SWE-bench Verified 等 benchmark 上提升。
- 可用于我们 workflow 的经验：轨迹不应只用于最终奖惩，应被结构化成可复用技能、常见失败和下一轮任务生成约束。
- 警告/风险：论文较新，结果需独立复现；梯度对齐依赖训练闭环，未必适合纯推理 agent；生成任务如果验证不足会放大错误技能。
- 可落到 optics_agent 的设计点：把每次论文复现的失败轨迹蒸馏为 `.codex/skills/` 更新候选和 `pitfalls_log`，并用这些技能生成下一轮小型回归任务。
- 优先级：高

## 2405.15793 SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering
- 文件：`2405.15793_SWE_agent.pdf`
- 一句话结论：给 LLM 设计专用 agent-computer interface 比直接暴露 Linux shell 更有效，接口质量会显著影响软件工程 agent 表现。
- 核心方法/贡献：提出 SWE-agent 和 ACI 概念；用少量简单、紧凑、可反馈的命令支持文件查看、搜索、编辑、测试执行；在 SWE-bench 和 HumanEvalFix 上达到当时领先表现；通过消融分析命令、反馈和 guardrail 的作用。
- 可用于我们 workflow 的经验：工具接口应少而强，返回应简洁但包含状态变化；编辑、搜索、测试等高频动作需要 guardrail 和错误恢复提示。
- 警告/风险：ACI 为代码仓库优化，不能直接覆盖科学仿真；强 guardrail 也可能限制专家级操作；benchmark 成功不等价于真实用户验收。
- 可落到 optics_agent 的设计点：为论文复现构建 agent-friendly 命令层，例如 `extract_parameters`、`run_case`、`validate_plot`、`summarize_failure`，每个命令返回结构化状态而非大段日志。
- 优先级：高

## 2404.05427 AutoCodeRover: Autonomous Program Improvement
- 文件：`2404.05427_AutoCodeRover.pdf`
- 一句话结论：真实 issue 修复要把代码库当作结构化程序而非文件集合，AST 级搜索和测试/故障定位能显著提高定位质量。
- 核心方法/贡献：AutoCodeRover 用 LLM 分析 GitHub issue，迭代调用结构化代码搜索 API 获取类、方法和代码片段；可结合 spectrum-based fault localization；补丁生成后用测试验证并有限重试；在 SWE-bench Lite 上报告 19% 解决率。
- 可用于我们 workflow 的经验：检索上下文应围绕结构化对象和失败信号，而不是简单全文检索；修复前先判断上下文是否足够。
- 警告/风险：依赖测试套件和 AST 支持；补丁通过测试可能仍不可接受；论文强调软件工程，迁移到 COMSOL/科学脚本时需要对应的结构化对象。
- 可落到 optics_agent 的设计点：把科学复现 artifact 结构化为“论文参数、模型对象、脚本函数、结果表、图像指标”，并在失败时优先用测试/日志定位最可疑节点。
- 优先级：中

## 2402.01030 Executable Code Actions Elicit Better LLM Agents
- 文件：`2402.01030_CodeAct.pdf`
- 一句话结论：让 agent 用可执行 Python 代码作为 action，比 JSON/文本动作更自然地支持变量、控制流、多工具组合和自调试。
- 核心方法/贡献：提出 CodeAct，把 agent 对环境的动作统一为可执行 Python；用解释器返回结果或 traceback，支持多轮修正；构建 M3 ToolEval 和 CodeActInstruct，在多工具复杂任务上相对 JSON/文本动作最高提升约 20%。
- 可用于我们 workflow 的经验：复杂工具链不要只设计单次 JSON 调用，应该允许代码式组合、循环、条件和中间变量，同时把执行错误作为反馈。
- 警告/风险：可执行代码 action 带来安全、权限和副作用风险；对非 Python 工具仍需包装；没有沙箱和资源限制会扩大破坏面。
- 可落到 optics_agent 的设计点：长程计算节点可用受限 Python runner 组合本地解析、数值检查和绘图，但写文件、网络、集群提交必须经白名单工具和显式验收。
- 优先级：高

## 2310.06770 SWE-bench: Can Language Models Resolve Real-World GitHub Issues?
- 文件：`2310.06770_SWE_bench.pdf`
- 一句话结论：真实软件工程 benchmark 的核心是“真实 issue + 代码库快照 + PR 关联测试 + 执行验收”，远比短代码生成更接近长程 agent 能力。
- 核心方法/贡献：从 12 个流行 Python 仓库中筛选 2,294 个 GitHub issue/PR 任务；要求模型基于 issue 和完整代码库生成 patch；用 fail-to-pass 测试和系统测试判定 resolved；同时发布训练集 SWE-bench-train。
- 可用于我们 workflow 的经验：评估工作流必须有可执行、可复现、自动化的验收标准；任务构造要保留输入快照、参考变更和测试。
- 警告/风险：测试覆盖不完整会导致“过测试但不正确”；真实仓库环境安装成本高；指标偏向能被测试捕捉的问题。
- 可落到 optics_agent 的设计点：将论文复现任务定义为 benchmark instance：论文/图号、代码快照、参数表、预期图像指标、运行命令、验收脚本和失败日志全部归档。
- 优先级：高
