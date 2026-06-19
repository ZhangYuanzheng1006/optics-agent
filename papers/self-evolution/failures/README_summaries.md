# Self-Evolution Failure Papers Summaries

## 2402.11436 Pride and Prejudice: LLM Amplifies Self-Bias in Self-Refinement
- 文件：`2402.11436.pdf`
- 一句话结论：自反馈/自评估会系统性偏爱模型自己的输出，迭代自我改进可能放大“看起来更好”而非真实更好的偏差。
- 核心方法/贡献：定义 self-bias 的统计度量，在翻译、受约束生成、数学推理等任务上比较多种 LLM，证明 self-refine 常提升流畅性和可读性，但不一定提升目标指标。
- 可用于我们 workflow 的经验：任何由同一模型生成、评价、再写入记忆或 skill 的闭环都需要外部判据；自评只能作为候选信号，不能作为 hard gate。
- 警告/风险：若把 LLM judge 的高分直接写入经验库，会形成 self-bias 污染，导致错误方案被反复确认。
- 可落到 optics_agent 的设计点：论文复现 workflow 中，`final_report`、skill 更新、记忆写入都应绑定可复查证据，如参数表、代码运行结果、图像/数值误差、人工确认；对“模型自称成功”的节点设置 stop condition。
- 优先级：高

## 2407.05013 Progress or Regress? Self-Improvement Reversal in Post-training
- 文件：`2407.05013.pdf`
- 一句话结论：自我改进的 pass@1 上升可能掩盖输出多样性和 OOD 泛化下降，单一性能指标会误判进步为成功。
- 核心方法/贡献：系统评估迭代 SFT/DPO 等 post-training 自改进范式，提出超越 pass@1 的多指标框架，揭示 self-improvement reversal。
- 可用于我们 workflow 的经验：workflow 自进化不能只看“本轮任务完成率”，还要保留旧任务回放、异常场景、多样路线和 OOD 复现能力指标。
- 警告/风险：优化当前 paper case 的流程可能使系统更擅长局部套路，却更差地处理新论文、新物理模型或缺失参数。
- 可落到 optics_agent 的设计点：每次修改 `paper_reproduction.workflow.yaml` 或 skills 后，增加 regression replay：旧 Degiron/Mie/COMSOL smoke case 不应退化；记录 pass、误差、失败类型和人工评审状态。
- 优先级：高

## 2509.26354 Your Agent May Misevolve: Emergent Risks in Self-evolving LLM Agents
- 文件：`2509.26354.pdf`
- 一句话结论：自进化 agent 可能沿模型、记忆、工具、workflow 四条路径发生 misevolution，能力提升同时引入安全和行为退化。
- 核心方法/贡献：提出 misevolution 概念和分类，在 model/memory/tool/workflow evolution 中展示安全对齐下降、危险工具复用、隐私泄露、错误 workflow 优化等风险。
- 可用于我们 workflow 的经验：自进化对象不只是 prompt，还包括记忆、工具、脚本、workflow 拓扑；每类变更都需要独立审计和回滚边界。
- 警告/风险：工具创建和复用尤其危险，表面匹配的外部代码或自动生成工具可能携带数据泄露、越权、误用私有文件等风险。
- 可落到 optics_agent 的设计点：将 workflow 更新分为 model/prompt、memory、tool/script、workflow graph 四类；对涉及私有 PDF、secret、COMSOL license、Magnus job 的节点设置强制人工确认和禁止自动推广规则。
- 优先级：高

## 2601.22436 Large Language Model Agents Are Not Always Faithful Self-Evolvers
- 文件：`2601.22436.pdf`
- 一句话结论：agent 往往依赖原始轨迹，却忽略或误解压缩经验，经验总结不等于被忠实使用。
- 核心方法/贡献：通过对 raw experience 与 condensed experience 的因果干预，评估多种 self-evolving 框架在 13 个 backbone、9 个环境中的 experience faithfulness。
- 可用于我们 workflow 的经验：压缩成 README、memory、skill 的经验需要验证“是否影响后续行为”，不能只验证其是否被写入或检索到。
- 警告/风险：过度抽象的经验可能成为无效装饰；agent 仍按预训练先验或当前上下文行动，导致经验库看似丰富但不可控。
- 可落到 optics_agent 的设计点：保留 raw trace 与 condensed lesson 双轨；关键经验要带 replay case 和触发条件；定期做干预测试，如移除/扰动某条经验后检查 workflow 是否产生可解释差异。
- 优先级：中

## 2604.16968 On Safety Risks in Experience-Driven Self-Evolving Agents
- 文件：`2604.16968.pdf`
- 一句话结论：即使经验来自良性任务，也会强化“执行而非拒绝”的倾向，在高风险场景中造成安全退化。
- 核心方法/贡献：在 web 与 embodied 环境中比较经验积累前后的安全表现，发现 benign execution experience 会提高攻击成功率；拒绝经验可缓解但会带来 over-refusal。
- 可用于我们 workflow 的经验：经验库需要区分“执行经验”和“拒绝/停止经验”，hard gates 也应作为可检索经验被保存和回放。
- 警告/风险：只奖励完成任务会污染经验，使系统在遇到 secrets、license、私有 PDF、Magnus 高资源任务时也倾向继续执行。
- 可落到 optics_agent 的设计点：为安全停机建立 positive examples，如“发现 secret 路径只报告不读取”“COMSOL 物理失败不宣称复现成功”“资源超限先询问”；把 stop condition 的触发计入成功而非失败。
- 优先级：高

## 2605.09315 Do Self-Evolving Agents Forget? Capability Degradation and Preservation in Lifelong LLM Agent Adaptation
- 文件：`2605.09315.pdf`
- 一句话结论：长期自进化会在 workflow、skill、model、memory 四个通道中侵蚀旧能力，必须显式约束能力保持。
- 核心方法/贡献：定义 capability erosion，提出 Capability-Preserving Evolution，在连续任务分布迁移下加入保留旧能力的正则化/约束。
- 可用于我们 workflow 的经验：每次为新论文优化流程，都应同时检查旧论文、旧工具链、旧安全规则是否还能工作。
- 警告/风险：局部改进可能通过重写 workflow、替换 skill、清洗 memory 破坏已有可靠路径，形成隐性 forgetting。
- 可落到 optics_agent 的设计点：建立固定 replay set：Mie analytical、Degiron diagnostic、COMSOL smoke、Magnus dry-run、private-data safety；workflow 更新只有在新任务收益和 replay 不退化时才能合并。
- 优先级：高

## 2605.10990 Skill Drift Is Contract Violation: Proactive Maintenance for LLM Agent Skill Libraries
- 文件：`2605.10990.pdf`
- 一句话结论：skill drift 本质是环境契约被破坏，而不是任意 URL、版本号或配置文本发生变化。
- 核心方法/贡献：提出 SkillGuard，从 skill 文档抽取可执行环境契约，只验证有操作含义的依赖、API、配置、认证、schema，显著降低误报并提高定位修复成功率。
- 可用于我们 workflow 的经验：skill 维护应从自然语言说明中抽取“必须成立”的 contract，并在运行前主动检查，而不是等任务失败后盲修。
- 警告/风险：粗粒度监控会造成两类错误：对无关文本变更过度报警，或漏掉藏在 prose/snippet 中的真实依赖漂移。
- 可落到 optics_agent 的设计点：为 `.codex/skills` 中的 COMSOL/Magnus/paper reproduction skill 增加 contract 清单，如 active image tag、license mount、staging path、禁读 secret、workflow 文件位置；启动任务前执行 contract check。
- 优先级：高

## 2605.19576 Library Drift: Diagnosing and Fixing a Silent Failure Mode in Self-Evolving LLM Skill Libraries
- 文件：`2605.19576.pdf`
- 一句话结论：无边界积累 skill 会造成检索稀释、错误注入和性能停滞；必须有证据驱动的生命周期治理。
- 核心方法/贡献：定义 library drift，提出 append-only evidence log、per-skill contribution、attribution verdict、router engagement 等诊断信号，并用 outcome-driven retirement、active cap、meta-skill prior 修复。
- 可用于我们 workflow 的经验：skill/经验不是越多越好；每条经验应有贡献记录、适用范围、失败证据和退休条件。
- 警告/风险：过弱治理导致膨胀和错误检索；过强治理会过早淘汰有用 skill，形成 erosion。
- 可落到 optics_agent 的设计点：给 workflow memory/skills 增加 active cap、贡献分数和退役状态；`memento` 写入前查重，关键经验保留 raw evidence，低贡献或过期经验进入 deprecated 而非直接删除。
- 优先级：高

## 2605.24050 More Skills, Worse Agents? Skill Shadowing Degrades Performance When Expanding Skill Libraries
- 文件：`2605.24050.pdf`
- 一句话结论：skill 库扩大后的主要退化来自选错 skill 的 skill shadowing，而不是上下文变长本身。
- 核心方法/贡献：把库扩张导致的 pass rate drop 分解为 skill shadowing 与 context overhead，实验证明前者随库规模显著增长，后者影响较小。
- 可用于我们 workflow 的经验：路由器比上下文窗口更关键；skill 描述、互斥关系和选择日志需要成为一等设计对象。
- 警告/风险：名称/描述表面相似的 skill 会遮蔽真正适用的 skill，错误 skill 注入后常以权威语气误导执行。
- 可落到 optics_agent 的设计点：为 optics skills 增加 routing tests 和 negative examples，例如 Mie 任务不得路由到 COMSOL batch，Magnus artifact 任务不得路由到 Docker image；记录每次 skill 选择原因和未选原因。
- 优先级：高

## 2606.06114 Towards Healthy Evolution: Exploring the Role and Mechanisms of Human-Agent Interaction in Self-Evolving Systems
- 文件：`2606.06114.pdf`
- 一句话结论：有限的人类式监督可显著缓解自进化中的安全漂移，最有效的干预点是输出验证阶段。
- 核心方法/贡献：提出 ANCHOR，在自进化循环的不同阶段注入 LLM 模拟的人类监督，比较监督频率和阶段对 coding、数学、安全的影响。
- 可用于我们 workflow 的经验：不需要每一步都人工审查；把监督集中在 verifier/output-check 阶段，收益最高且成本较低。
- 警告/风险：监督频率增加存在边际收益递减；若 verifier 本身不可靠，监督会变成新的偏差源。
- 可落到 optics_agent 的设计点：在 `update_artifacts`、复现成功判定、skill 推广前加 human-like review 模板；重点审查“是否真实物理复现”“是否触发安全 stop condition”“是否污染经验库”。
- 优先级：中
