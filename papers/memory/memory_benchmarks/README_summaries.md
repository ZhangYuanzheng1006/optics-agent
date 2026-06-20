# memory_benchmarks 文献摘要与风险分析

> 本文件由 `pdftotext -layout` 提取 PDF 文本后阅读生成，仅读取未修改原 PDF。
> 背景：三层记忆系统（提示词备注 ≤3 条/节点 → SKILL evidence gate → 向量库几十万条不治理靠检索）；
> qdrant/chroma + Qwen3-Embedding-0.6B 向量 + Qwen3-Reranker-8B INT8 常驻 RTX 5880 Ada；
> 检索：向量召回 top-100 → 8B rerank → top-5 注入；实时只标记 outcome/importance，定期 API 合并/清理/降权；
> workflow 固定拓扑，只迭代 skill 和提示词备注。
>
> 本目录论文为 benchmark，重点提取：常见记忆系统失败模式、对我们"几十万条不治理靠检索"策略的风险评估。

---

## 2402.17753 LoCoMo: Evaluating Very Long-Term Conversational Memory of LLM Agents
- 文件：`2402.17753_LoCoMo_Evaluating_Very_Long_Term_Conversational_Memory.pdf`
- 一句话结论：超长期对话记忆 benchmark（50 段对话，300 轮 / 9K token / 35 session），发现 LLM 在时间推理和对抗问题上远落后人类（分别落后 73% 和 56%），长上下文模型对抗问题反而降 83%、事件摘要落后 base model 14%。
- 核心方法/贡献：persona + 时间事件图生成对话 + 人工编辑（编辑 15% 轮次、替换 19% 图片）；5 类 QA（single-hop / multi-hop / temporal / open-domain / adversarial）+ 事件图摘要 + 多模态对话；RAG 检索单元对比（dialog / observation 断言 / session summary）；发现 observation-based RAG 在 top-5 时最优，检索量增加信噪比下降；事件摘要 5 类错误（遗漏 / 幻觉 / 误解对话线索 / 错误说话者归因 / 无关对话误判为重要）。
- 可用于我们向量记忆系统的经验：★★ 对抗问题（设计诱导错误答案）是长上下文模型致命弱点——我们的 rerank 需抵抗这类干扰；observation/断言化存储比原始对话或 session 摘要更有效（top-5 observation F1=41.4 > top-5 dialog F1=31.7）；信噪比随检索量下降——top-5 优于 top-50，验证我们 top-5 注入的合理性；session summary 召回率高(90.7%)但 F1 低(31.5)——摘要丢信息导致"召回了但答不对"。
- 警告/风险：长上下文 ≠ 好记忆——16K 模型对抗问题仅 2.1%（vs 4K base 22.1%），长上下文更易被误导和错误归因；摘要化存储会丢失时间/因果信息（summary RAG 召回 90.7% 但 F1 仅 31.5）；时间推理是最弱环节（长上下文模型也仅 25% vs 人类 92.6%）；RAG 引入不准确检索上下文反而降低 open-domain 表现。
- 可落到 optics_agent 的设计点：记忆存储用"断言/事实"形式而非原始对话/摘要（对应 RecMem 的 semantic memory 原子事实）；检索量适度（top-5 注入计划正确）；时间戳元数据必须保留以支持时间推理；rerank 需对抗 adversarial 干扰。
- 优先级：中（作为评估参考和检索策略验证）

---

## 2511.21730 A Benchmark for Procedural Memory Retrieval in Language Agents
- 文件：`2511.21730_Procedural_Memory_Retrieval_Benchmark.pdf`
- 一句话结论：首个隔离过程记忆检索质量（独立于执行）的 benchmark，发现 embedding 方法在熟悉语境强但 novel 语境急剧退化（generalization cliff），LLM 生成的过程抽象更稳定，语料规模收益远大于表示丰富度。
- 核心方法/贡献：ALFWorld 双语料库（78 条 expert + 336 条 LLM-generated）；6 种检索方法（action-only / enriched / summary embedding + BM25）；coverage-balanced query bank 分难度分层；定义 generalization gap `Gap = (MAP_seen - MAP_unseen) / MAP_seen`；5 项验证分析（lexical overlap / corpus ablation / semantic clustering / format comparison / human annotation）。
- 可用于我们向量记忆系统的经验：★★★ 直接警示——纯 embedding 检索在词汇分布偏移时遭遇 generalization cliff（novel 语境排名逆转）；LLM 抽象化（去除对象特异信息保留过程结构）比原始 embedding 更稳定跨语境迁移；语料规模扩大 >> embedding 模型升级——支持我们"几十万条"扩规模策略；两阶段检索（先 LLM 抽象提取再相似度计算）优于单阶段 embedding；embedding 本质 ≈ bag-of-words，丢弃时序/因果结构。
- 警告/风险：★ 我们的 Qwen3-Embedding 在跨子方向（如从 COMSOL 转到 Mie 理论，词汇分布差异大）时可能遭遇 generalization cliff；embedding 方法把过程当无序词袋，丢失步骤时序——工作流/SKILL 检索可能匹配到结构错误的流程；novel 语境下 embedding 方法排名逆转，原本"最好"的方法变最差；enriched embedding（加 metadata）改善有限，天花板在 encoder 架构。
- 可落到 optics_agent 的设计点：过程记忆（SKILL / 工作流）存储时做 LLM 抽象化——去除项目特异细节（如具体文件路径）保留通用过程结构；rerank 可部分弥补 embedding 的结构丢失（8B reranker 理解力强于 embedding）；扩大记忆库规模优先于追求更好 embedding 模型；SKILL 内容应包含结构化步骤序列而非纯文本描述。
- 优先级：高

---

## 2603.25973 MemoryCD: Benchmarking Long-Context User Memory for Lifelong Cross-Domain Personalization
- 文件：`2603.25973_MemoryCD_Benchmarking_Long_Context_User_Memory.pdf`
- 一句话结论：首个基于真实用户行为（Amazon Review 跨年跨域）的长期记忆 benchmark，12 域 4 任务，14 个 LLM + 6 种记忆方法，发现现有记忆方法远未达用户满意，跨域记忆有潜力但利用策略尚不成熟。
- 核心方法/贡献：真实用户数据（vs LoCoMo/MemBench 等合成 persona）；4 任务（评分预测 MAE/RMSE / 物品排序 NDCG@K / 评论摘要 ROUGE+BLEU / 评论生成）；单域 vs 跨域记忆设置（跨域 = 用其他域记忆在目标域评估，测冷启动）；端到端用户满意度评估（vs 纯检索指标）；6 种记忆系统实现对比。
- 可用于我们向量记忆系统的经验：★★ 真实用户行为 vs 合成数据的差异——合成 benchmark 可能高估系统表现（LoCoMo 等用 LLM 模拟用户，缺乏真实反馈）；跨域记忆迁移有正面价值（一个域的偏好可辅助另一域冷启动）但需抑制域特异噪声；端到端评估（记忆是否影响下游决策结果）比纯检索 recall@k 更重要——我们应看记忆是否真正改善论文复现/COMSOL 任务结果。
- 警告/风险：合成 benchmark 高估能力——我们的记忆系统在真实科研场景可能比任何 benchmark 表现更差；跨域噪声是真实风险（COMSOL 记忆注入 Mie 理论任务可能干扰而非帮助）；14 个 SOTA LLM + 6 种记忆方法仍"远未满意"——说明记忆问题远未解决，不要对检索效果过度乐观。
- 可落到 optics_agent 的设计点：用 project_path / tags 做域隔离（对应单域 vs 跨域设置），跨方向检索时注意噪声；评估记忆效果看下游任务结果（论文复现成功率 / COMSOL 作业结果）而非纯检索 recall；跨方向冷启动时可尝试迁移通用性记忆（如 workflow 引擎经验）但需验证。
- 优先级：中

---

## 2605.18421 EvoMemBench: Benchmarking Agent Memory from a Self-Evolving Perspective
- 文件：`2605.18421_EvoMemBench_Benchmarking_Agent_Memory_Self_Evolving.pdf`
- 一句话结论：自演化记忆 benchmark，双轴（in-episode / cross-episode × knowledge / execution），15 种记忆方法对比，发现长上下文 baseline 仍极具竞争力、记忆在上下文不足或任务难时帮助最大、无单一记忆形式通吃所有场景。
- 核心方法/贡献：4 设置（in-ep knowledge / in-ep execution / cross-ep knowledge / cross-ep execution）× 6 数据集；15 种方法（retrieval-augmented / short-term / general long-term / procedural long-term / meta-evolution）；7 大发现——(1) 长上下文 baseline 仍最强（Gemini-3-Flash 综合排名 #1）；(2) 记忆方法擅长保留不擅长修正（FactConsolidation multi-hop 是瓶颈）；(3) 上下文受限时记忆帮助最大（+14.5%@16K → +8.5%@128K），128K 时部分方法反而低于 baseline；(4) 执行任务靠 procedural guidance 但压缩有风险；(5) 记忆在难任务帮助大但伤害简单任务；(6) 瓶颈在形成可复用知识而非存储更多；(7) 不同执行域偏好不同记忆形式。
- 可用于我们向量记忆系统的经验：★★★ 极高相关。Finding 1：上下文够时保留原始证据比外部记忆抽象更可靠——提示词备注应保留关键原文而非仅摘要；Finding 2：冲突时的更新/抑制/替换是记忆系统瓶颈（非检索）——我们定期治理的冲突消解是关键投入点；Finding 3：记忆帮助随上下文预算增大递减，128K 时部分方法低于 baseline——记忆注入噪声/消耗上下文空间，top-5 注入需严格质量控制；Finding 4：执行状态压缩有风险，丢失精确参数/实体引用/中间结果——SKILL/工作流不要过度压缩；Finding 5：简单任务上记忆有害——应按任务难度动态决定是否注入；Finding 7：不同域偏好不同记忆形式——按子方向配不同检索策略。
- 警告/风险：★ 直接警告我们"几十万条不治理靠检索"策略——(a) 记忆注入可能引入噪声、不匹配旧信息、prompt 偏置，甚至低于无记忆 baseline；(b) 简单任务上记忆有害（cross-ep knowledge easy split 上记忆方法全部低于无记忆 baseline 52.1）；(c) 压缩执行状态丢失关键细节是系统性风险；(d) 15 种方法无一个通吃——我们的单一策略（向量召回+rerank）可能在某些设置下失效；(e) 长上下文 baseline 仍最强说明记忆系统整体尚未成熟，不能盲目信任。
- 可落到 optics_agent 的设计点：top-5 注入需严格 rerank 质量控制（8B reranker 是关键投资）；按任务难度/类型动态决定是否注入记忆（简单任务跳过注入）；SKILL/工作流内容保留精确参数和步骤细节不过度压缩；不同子方向（论文复现/COMSOL/Mie）配不同检索参数（呼应 EvolveMem 的 per-category override）；定期治理重点投入冲突消解（Finding 2 的瓶颈）。
- 优先级：高
