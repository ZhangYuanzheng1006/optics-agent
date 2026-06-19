## 2606.19559 Uncertainty Decomposition for Clarification Seeking in LLM Agents
- 文件：`2606.19559_Uncertainty_Decomposition_Clarification_Seeking.pdf`
- 一句话结论：把 agent 的不确定性拆成“动作置信度”和“请求不确定性”，比单一 confidence 更适合触发澄清问题。
- 核心方法/贡献：提出 prompt-only 的不确定性分解；构造 WebShop-Clarification 与 ALFWorld-Clarification，把 50% 任务故意设为欠指定；用 clarification F1、故障检测等指标比较 ReAct+UE、UAM 和新方法。
- 可用于我们 workflow 的经验：workflow 节点不应只记录“我有多确定”，还应显式记录“用户/论文/参数是否欠指定”，并在阈值触发时进入 clarification 或 missing-info 分支。
- 警告/风险：prompt 自报不确定性容易过度自信；阈值选择会影响澄清频率和任务效率；黑盒 API 场景下不能依赖 logprob 或多采样作为默认机制。
- 可落到 optics_agent 的设计点：在 paper_reading、theory_derivation、numerical_program 节点输出 `action_confidence`、`request_uncertainty`、`missing_fields`，当论文参数、边界条件、COMSOL 模板缺失时自动生成澄清请求而非继续猜测。
- 优先级：高

## 2605.21404 What Twelve LLM Agent Benchmark Papers Disclose About Themselves: A Pilot Audit and an Open Scoring Schema
- 文件：`2605.21404_Pilot_Audit_LLM_Agent_Benchmark_Papers.pdf`
- 一句话结论：当前 agent benchmark 论文普遍没有足够披露运行细节，导致相同 benchmark 的结果不可比较。
- 核心方法/贡献：提出五字段 audit schema：benchmark identity、harness specification、inference settings、cost reporting、failure breakdown；对 12 篇 benchmark 论文打分，发现 agent benchmark 平均披露分仅 0.38，成本和环境 digest 披露尤其差。
- 可用于我们 workflow 的经验：每次复现实验都必须把“ benchmark/任务集版本、执行 harness、模型和推理设置、成本、失败分类”作为一等产物，而不是只保存最终分数或图。
- 警告/风险：披露充分不等于结果正确；单人 audit 有主观性；Docker tag、模型别名、benchmark 子集都会漂移。
- 可落到 optics_agent 的设计点：为每个 run 生成 `run_audit.json` 或 `manifest.md`，强制记录 PDF 文件、参数表来源、代码提交、容器 digest/镜像名、solver 设置、资源成本、失败类别和 task-level 失败归因。
- 优先级：高

## 2601.11903 AEMA: Verifiable Evaluation Framework for Trustworthy and Controlled Agentic LLM Systems
- 文件：`2601.11903_AEMA_Verifiable_Evaluation_Agentic_LLM_Systems.pdf`
- 一句话结论：多 agent 评估系统应从单次 LLM-as-a-Judge 转向过程级、可审计、可复核的评价流水线。
- 核心方法/贡献：AEMA 使用 Planning、Prompt-Refinement、Evaluation、Final Report 四类评估 agent，对执行轨迹进行步骤级评分、聚合和报告；强调人类监督、历史 trace、可复现评估记录。
- 可用于我们 workflow 的经验：复杂科学 workflow 的评估不能只看最终图像是否相似，还要评估每个节点的依据、工具调用、参数选择和中间失败是否合理。
- 警告/风险：LLM 评审仍可能偏置或不稳定；多 agent 评估增加开销；如果评估函数检索或分类错误，会让报告显得可审计但实际不可靠。
- 可落到 optics_agent 的设计点：在 supervisor/worker 工作流中加入 evaluator 角色，对每个节点产物输出 step score、evidence link、human-review-needed 标记，并把最终 handoff 报告从 trace 自动聚合。
- 优先级：高

## 2512.18470 SWE-EVO: Benchmarking Coding Agents in Long-Horizon Software Evolution Scenarios
- 文件：`2512.18470_SWE_EVO_Long_Horizon_Coding_Agents.pdf`
- 一句话结论：长周期、多文件的软件演化比单 issue 修复难得多，现有 coding agents 在 release 级任务上能力断崖式下降。
- 核心方法/贡献：基于 7 个成熟 Python 项目的 release transition 构造 48 个任务；平均跨 21 个文件、874 个测试；用 FAIL->PASS 与 PASS->PASS 测试验证，并提出 Fix Rate 衡量部分进展。
- 可用于我们 workflow 的经验：长 horizon workflow 需要度量“部分正确”和“无回归”，不能只用最终 pass/fail；上下文管理、需求解释和跨文件一致性是主要瓶颈。
- 警告/风险：测试套件只覆盖可执行行为，不能证明设计正确；release notes 可能欠指定；高分 agent 也可能误解细粒度需求。
- 可落到 optics_agent 的设计点：把论文复现拆成可验证增量：参数抽取、理论公式、最小数值模型、扫描脚本、图像生成、报告，每步都有局部 check；新增 `fix_rate` 风格的 partial reproduction 指标。
- 优先级：中

## 2507.21504 Evaluation and Benchmarking of LLM Agents: A Survey
- 文件：`2507.21504_Evaluation_and_Benchmarking_of_LLM_Agents_Survey.pdf`
- 一句话结论：agent 评估需要同时覆盖目标、过程、环境、工具、成本、安全和企业合规，而不是沿用静态 LLM 评测。
- 核心方法/贡献：提出二维 taxonomy：evaluation objectives 包括行为、能力、可靠性、安全与对齐；evaluation process 包括交互模式、数据/benchmark、指标计算、工具链、环境上下文；强调企业场景中的 RBAC、审计、合规、长程交互。
- 可用于我们 workflow 的经验：workflow 评估维度应分层：结果质量、过程能力、可靠性、安全治理、资源成本和人工介入点分别记录。
- 警告/风险：综述提供分类但不保证具体指标可操作；很多公开 benchmark 对真实生产安全和合规覆盖不足。
- 可落到 optics_agent 的设计点：建立 workflow evaluation matrix，把 task success、parameter fidelity、tool correctness、latency/cost、human approval、private-path access、安全事件都纳入统一报告。
- 优先级：中

## 2507.21046 A Survey of Self-Evolving Agents: What, When, How, and Where to Evolve on the Path to Artificial Super Intelligence
- 文件：`2507.21046_Survey_Self_Evolving_Agents_What_When_How_Where.pdf`
- 一句话结论：自演化 agent 的核心设计问题是演化什么、何时演化、如何演化，并且评估与 agent 必须共同演化。
- 核心方法/贡献：系统梳理 model、memory、tool、architecture/workflow 等可演化组件；按 intra-test-time、inter-test-time 等阶段归类演化时机；讨论文本反馈、标量奖励、单/多 agent 演化机制和评估挑战。
- 可用于我们 workflow 的经验：自迭代不应只改 prompt，也可以改 memory、tool registry、workflow topology、评估规则；但每类演化都要有边界、回滚和验证。
- 警告/风险：自主演化会扩大风险面，尤其在 safety、scalability、co-evolution dynamics 上；没有评估护栏的演化容易优化局部 reward。
- 可落到 optics_agent 的设计点：把 `update_artifacts` 节点拆成可审计的演化类型：prompt update、skill update、workflow topology update、memory update、tool whitelist update，并要求每次演化附带验证结果。
- 优先级：高

## 2402.11443 Benchmark Self-Evolving: A Multi-Agent Framework for Dynamic LLM Evaluation
- 文件：`2402.11443_Benchmark_Self_Evolving_Dynamic_LLM_Evaluation.pdf`
- 一句话结论：静态 benchmark 会因模型进步和数据污染失效，可通过多 agent 自动改写样本形成动态、鲁棒、细粒度评估。
- 核心方法/贡献：用 instance pre-filter、creator、verifier、candidate option formulator 生成演化样本；操作包括问题替换、问题复杂化、上下文改写、加噪、极性反转和子能力探测；在 GSM8K、CLUTRR、StrategyQA、BoolQ 上验证会拉开模型差异。
- 可用于我们 workflow 的经验：评测集可以从已有任务自动扩展，但必须有 verifier 和反例生成，避免生成无效或答案漂移样本。
- 警告/风险：LLM 生成的 benchmark 可能引入错误标签、分布偏移或被同类模型偏好；动态扩展需要版本化，否则难以复现。
- 可落到 optics_agent 的设计点：为论文复现构造 dynamic audit cases，例如对参数单位、边界条件、材料常数、扫描范围做扰动，测试 workflow 是否能发现矛盾并拒绝错误配置。
- 优先级：中
