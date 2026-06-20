# memory_architectures 文献摘要与风险分析

> 本文件由 `pdftotext -layout` 提取 PDF 文本后阅读生成，仅读取未修改原 PDF。
> 背景：三层记忆系统（提示词备注 ≤3 条/节点 → SKILL evidence gate → 向量库几十万条不治理靠检索）；
> qdrant/chroma + Qwen3-Embedding-0.6B 向量 + Qwen3-Reranker-8B INT8 常驻 RTX 5880 Ada；
> 检索：向量召回 top-100 → 8B rerank → top-5 注入；实时只标记 outcome/importance，定期 API 合并/清理/降权；
> workflow 固定拓扑，只迭代 skill 和提示词备注。

---

## 2212.02098 A Machine with Short-Term, Episodic, and Semantic Memory Systems
- 文件：`2212.02098_Machine_with_Short_Term_Episodic_Semantic_Memory.pdf`
- 一句话结论：用知识图谱建模 short-term/episodic/semantic 三层记忆，Deep Q-learning agent 学习记忆调度策略（遗忘/转 episodic/转 semantic），有人类式分层记忆的 agent 优于无分层 agent。
- 核心方法/贡献：三层记忆（STM 容量 1，EM/SM 各最多 32）均用 KG 四元组 (h,r,t,timestamp/strength) 表示；STM 满时 RL 决策三选一（遗忘/转 EM/转 SM）；检索规则——episodic 取最近、semantic 取 strength 最高；KGE 拼接做 Q-network 状态输入。semantic 用 strength（累计存储次数）而非时间戳，EM 用时间戳。
- 可用于我们向量记忆系统的经验：分层映射清晰——STM→提示词备注（≤3 条，满了就淘汰最旧）、EM→session 级情景记录、SM→向量库长期事实；semantic memory 的 strength 字段对应我们的 importance/outcome 标记；"semantic 取最强、episodic 取最近"的检索策略可融入 rerank 排序权重。
- 警告/风险：硬容量上限（EM/SM ≤32）与"几十万条不治理"路线相反——该论文验证的是小容量精治理，我们是大容量粗治理；RL 学习调度策略需要大量交互和奖励信号，科研场景成本高；KG 表示与纯向量表示不同，不能直接套用。
- 可落到 optics_agent 的设计点：三层映射可作为概念模型（提示词备注=STM，SKILL=固化规则，向量库=semantic）；importance 字段类比 strength，检索时作为 rerank 的辅助排序信号。
- 优先级：中

---

## 2306.07174 LongMem: Augmenting LLMs with Long-Term Memory
- 文件：`2306.07174_LongMem_Augmenting_LLMs_with_Long_Term_Memory.pdf`
- 一句话结论：解耦记忆架构——冻结 backbone LLM 做记忆编码器、训练轻量 SideNet 做检索/融合，解决记忆陈旧（memory staleness）问题，支持 65k token 长期记忆。
- 核心方法/贡献：冻结 backbone 提取历史段 attention KV 对缓存到 memory bank；SideNet 用当前 query 检索 top-K KV 并融合；跨网络残差连接传递 backbone 知识；解耦使编码与检索独立演化，避免参数更新后旧缓存表示分布偏移。
- 可用于我们向量记忆系统的经验：编码与检索解耦的理念——我们的 Qwen3-Embedding（编码）与 Qwen3-Reranker（排序）本就解耦，可各自独立迭代；"记忆陈旧"问题（编码模型更新后旧向量分布偏移）是真实风险，提醒 embedding 模型版本必须锁定。
- 警告/风险：这是参数级记忆（改模型结构/权重），与我们的外部向量库路线根本不同；记忆陈旧问题在 embedding 模型升级时会全面重现（全库向量失效）。
- 可落到 optics_agent 的设计点：embedding 模型版本锁定后不随意更换，更换需全库重新生成向量；rerank 模型可独立迭代不影响已存向量。
- 优先级：低（路线不同，但解耦与版本锁定理念有参考价值）

---

## 2601.18642 FadeMem: Biologically-Inspired Forgetting for Efficient Agent Memory
- 文件：`2601.18642_FadeMem_Biologically_Inspired_Forgetting.pdf`
- 一句话结论：双层记忆（长期 LML 慢衰减 / 短期 SML 快衰减）+ Ebbinghaus 自适应指数衰减 + LLM 冲突消解 + 记忆融合，存储减少 45% 同时多跳推理优于 Mem0/MemGPT。
- 核心方法/贡献：重要性 `I = α·rel + β·freq/(1+freq) + γ·recency` 驱动层级分配（θ_promote > θ_demote 带迟滞防抖）；衰减 `v(t)=v(0)·exp(-λ·(t-τ)^β)`，λ 随重要性自适应降低，LML β=0.8 慢衰减、SML β=1.2 快衰减；4 类冲突消解（compatible 共存降冗余 / contradictory 新 suppress 旧 / subsumes-subsumed 合并）；时间-语义聚类融合，融合后衰减率降低；访问时强化 v(t+)=v(t)+Δv·(1-v)·exp(-n/N) 实现 spacing effect。
- 可用于我们向量记忆系统的经验：★★★ 衰减函数 `v(t)=v(0)·exp(-λ·(t-τ)^β)` 可直接用于定期治理降权（非删除）低重要性记忆；重要性驱动的差异化衰减率——重要记忆 λ 小、衰减慢，非重要 λ 大、衰减快；4 类冲突消解逻辑（compatible/contradictory/subsumes/subsumed）适合嵌入定期合并 API；融合记忆衰减率降低 = 合并后的记忆更持久；访问强化（spacing effect）= 检索命中后提升 importance。
- 警告/风险：实时衰减需每次检索时计算 v(t)（计算开销）；LLM 冲突消解和融合的 token 成本（论文用 GPT-4o-mini）；θ_promote/θ_demote/θ_sim/θ_fusion 多个阈值需网格搜索调参；硬容量上限（LML 1000 / SML 500）与我们"不治理"策略冲突——但衰减降权可替代硬删除。
- 可落到 optics_agent 的设计点：定期治理用指数衰减函数降权（score 乘以 v(t)）而非物理删除；冲突消解四分类逻辑嵌入合并 API；检索命中后 importance 自增（spacing effect）；θ_promote > θ_demote 的迟滞设计防止记忆在层级间反复跳动。
- 优先级：高

---

## 2603.11768 Governing Evolving Memory: Risks, Mechanisms, and the SSGM Framework
- 文件：`2603.11768_Governing_Evolving_Memory_Risks_Mechanisms.pdf`
- 一句话结论：系统综述 evolving memory 的四维失败分类（稳定性/有效性/效率/安全），提出 SSGM 治理框架（写验证门 + 读过滤门 + 双轨存储 + 周期对账），形式化证明周期对账使语义漂移有界 O(N·ε_step) 而非 O(T·ε_step)。
- 核心方法/贡献：四维失败 taxonomy——稳定性（semantic drift 迭代摘要失真 / procedural drift 强化次优工作流 / goal drift 角色偏移）、有效性（memory hallucination / temporal obsolescence 过时事实）、效率（retrieval latency 线性增长 / index bloat 冗余日志膨胀）、安全（memory poisoning 恶意注入 / privacy leakage 跨用户泄露）；SSGM 四原则——预合并验证（NLI 矛盾检查拒绝冲突写入）、时间+溯源接地（Weibull 衰减 + 密码学溯源）、访问范围检索（ABAC 注入查询层）、可逆对账（不可变 episodic ledger + 可变 active graph，周期 replay 纠正漂移）；漂移 δ=1-sim(E(M_T), E(K_true))，对账后上界 O(N·ε_step)。
- 可用于我们向量记忆系统的经验：★★★ 极高相关。失败 taxonomy 直接诊断我们的风险——index bloat（几十万条不治理的核心风险）、temporal obsolescence（过时事实如旧 COMSOL 参数）、semantic drift（如果做迭代摘要）；不可变 ledger 思路——保留原始证据 trace，定期对账纠正被扭曲内容，这恰好对应"定期 API 合并/清理/降权"；有界漂移证明说明周期治理能控制累积误差，数学上支撑"定期治理"而非"实时治理"的合理性。
- 警告/风险：★ 直接警告——"检索延迟随 |M| 线性/二次增长"是 index bloat 的必然后果，几十万条时检索延迟可能显著上升（需 HNSW 等近似索引缓解）；"记忆投毒"在外部输入/多用户场景是真实风险；完全连接的多 agent 记忆网络最大化泄露风险。
- 可落到 optics_agent 的设计点：保留原始 trace 作为不可变 ledger，定期对账纠正向量库内容；Weibull 时间衰减 `w(Δτ)=exp(-(Δτ/η)^κ)` 剪枝过时记忆；写验证门简化为 importance/outcome 标记一致性检查；project_path/tags 做访问范围隔离（类比 ABAC）。
- 优先级：高

---

## 2604.03295 LLMA-Mem: Memory Enabled Lifelong Learning in LLM Multi-Agent Systems
- 文件：`2604.03295_LLMA_Mem_Lifelong_Memory_Episodic_Procedural.pdf`
- 一句话结论：多 agent 终身学习记忆框架，三层（episodic 轨迹 / procedural 可复用流程 / transactive 团队能力），发现团队规模与终身学习非单调——记忆设计好时小团队可超越大团队，token 成本降低 9.4%–71.7%。
- 核心方法/贡献：episodic 存原始任务轨迹，每 N 任务固化为 procedural（可复用流程知识）；transactive memory 建模团队角色画像（专长/熟练度/协作历史/成功率）；记忆拓扑（local / shared / hybrid）；MARBLE/A-Mem baseline 的累积增益 plateau 说明现有方法未充分支持跨任务复用。
- 可用于我们向量记忆系统的经验：episodic→procedural 固化周期（每 N 任务）对应我们"session 记录→SKILL 提炼"的定期固化；transactive memory（谁知道什么/擅长什么）对应我们的 skill 路由表；非单调 scaling 提示——记忆质量比 agent 数量更重要，支持我们单 agent + 好记忆的路线。
- 警告/风险：多 agent 场景与当前单 agent 不同；hybrid 拓扑的检索噪声随 agent 数增长；procedural 固化过早可能锁定次优流程（procedural drift，见 SSGM）。
- 可落到 optics_agent 的设计点：episodic→procedural 固化周期可参考（每 N 个论文复现任务提炼一次 skill）；skill 路由表类比 transactive memory 记录各 skill 适用场景；procedural 固化需验证门（避免锁定次优流程）。
- 优先级：中

---

## 2604.20943 SCM: Sleep-Consolidated Memory with Algorithmic Forgetting for LLMs
- 文件：`2604.20943_SCM_Sleep_Consolidated_Memory_Algorithmic_Forgetting.pdf`
- 一句话结论：仿生记忆架构——工作记忆（7 项 FIFO）+ 4 维重要性标记 + 离线睡眠巩固（NREM replay 强化 / REM 新关联生成）+ 价值阈值遗忘，10 轮对话完美召回同时噪声降低 90.9%，检索 <1ms。
- 核心方法/贡献：5 模块（MeaningEncoder 语义图提取 / ValueTagger 4 维打分 / WorkingMemory 7 项 / LongTermMemory graph+SQLite / SleepCycle）；4 维重要性 `I = 0.30·novelty + 0.20·|emotional| + 0.35·task + 0.15·repetition`（task relevance 权重最高）；NREM = replay + Hebbian 强化共现 + 比例 downscale；REM = 高重要性概念生成新组合；遗忘 = 复合重要性低于自适应阈值则剪枝；触发条件 = memory entropy / conflict density / time elapsed。
- 可用于我们向量记忆系统的经验：★★ 睡眠巩固 = 我们的定期离线治理，NREM 强化对应"合并相似 + 强化高频访问"，REM 新关联对应"发现隐含关系"（可选高级功能）；4 维重要性比单维 outcome/importance 更丰富——可扩展为 novelty（与现有记忆的语义距离）/ task-relevance（与当前任务余弦）/ access-frequency / outcome；遗忘触发条件（entropy/conflict/time）可做定期治理的触发信号而非定时器。
- 警告/风险：工作记忆硬限 7 项过于严格（我们提示词备注 ≤3 条更激进）；本地 Llama 3.2 提取概念质量有限；graph+SQLite 实现与纯向量库不同；REM 阶段生成新关联可能引入幻觉。
- 可落到 optics_agent 的设计点：定期治理仿两阶段——先 NREM（合并强化高频记忆），再可选 REM（发现跨 skill 隐含关联）；4 维重要性标记扩展；用 conflict density / memory entropy 作为治理触发信号。
- 优先级：中

---

## 2605.13941 EvolveMem: Self-Evolving Memory Architecture via AutoResearch
- 文件：`2605.13941_EvolveMem_Self_Evolving_Memory_AutoResearch.pdf`
- 一句话结论：将检索基础设施本身作为可优化 action space——LLM 读失败日志→诊断根因→提议配置调整→带 revert-on-regression 保护应用，LoCoMo 上超最强 baseline 25.7%（超 minimal baseline 78.0%），配置可跨 benchmark 正迁移。
- 核心方法/贡献：三层（typed memory store 6 类记忆 + 多视图检索 BM25/semantic/structured + 自演化引擎）；检索配置 = action space（k_sem/k_kw/k_str 召回数、B_ctx 上下文预算、fusion mode SUM/WEIGHTED/RRF、per-view 权重、答案风格、per-category override）；EVALUATE–DIAGNOSE–PROPOSE–GUARD 闭环；回滚防退化（fr-1-fr > τ_rev 则回退最优）、停滞则随机探索；consolidation 三步（dedup Jaccard / importance 线性衰减有下限 / entity reinforcement 查询共现强化）。
- 可用于我们向量记忆系统的经验：★★★ 核心启发——检索配置不应冻结，应随记忆规模和查询分布自演化；revert-on-regression 机制适合定期治理时"先验证再应用"；per-category override（不同问题类型用不同检索参数）——论文复现/COMSOL/Mie 理论可各自配参；failure-log 诊断驱动的改进比盲目调参有效；importance 衰减有下限 `ι_min` 防止有用记忆彻底消失——对应我们"降权不删除"。
- 警告/风险：自演化需要离线评估集（有 ground-truth），科研场景不一定有标准答案；LLM 诊断的 token 成本；可能过拟合特定 benchmark（论文证明可迁移但非保证）。
- 可落到 optics_agent 的设计点：检索参数（top-100 召回/rerank top-5/融合权重）作为可迭代 action space；定期治理用 revert-on-regression——先小范围验证再全量应用；按子方向（论文复现/COMSOL/Mie）设置 per-category 检索配置；importance 衰减设下限防止有用记忆归零。
- 优先级：高

---

## 2605.16045 RecMem: Recurrence-based Memory Consolidation for Efficient and Effective Long-Running LLM Agents
- 文件：`2605.16045_RecMem_Recurrence_based_Memory_Consolidation.pdf`
- 一句话结论：三层（subconscious 轻量缓冲 / episodic 事件叙事 / semantic 原子事实）+ 递归触发巩固——只有当新交互在 subconscious 中找到足够多语义相似旧交互时才调 LLM 提取，token 成本降低 87% 同时精度更高。
- 核心方法/贡献：subconscious 层用轻量 embedding 缓冲原始交互单元（不调 LLM，成本极低）；递归检测——新单元检索 top-k 相似，`|{cos ≥ θ_sim}| ≥ θ_count` 才触发 LLM 巩固；merge-first 策略（同主题 episode 就地合并而非新增，防碎片化）；semantic refinement 回溯原始交互恢复 episode 摘要遗漏的细粒度事实；查询时三库各取小预算（k_sem = 2·k_epi）。
- 可用于我们向量记忆系统的经验：★★★ 递归触发 = 不每条记忆都急着 LLM 处理，等语义聚类形成再批量巩固——完全对应我们"实时只标记 outcome/importance，定期 API 合并"；merge-first 避免同主题碎片化（论文复现同一图的多条记录应合并而非各存）；semantic refinement 补救摘要损失（对应 SSGM 的对账机制）；subconscious 层 = 我们的向量库原始存储，episodic/semantic = 定期治理后的提炼层。
- 警告/风险：subconscious 层需存储全部原始交互（存储成本随时间线性增长——与我们"几十万条"一致但需关注）；θ_count/θ_sim 需调参，过低则频繁触发（成本高），过高则低频重要信息延迟巩固甚至遗漏；延迟巩固期间相关查询只能命中 subconscious 原始层（精度可能不如已巩固的 semantic 层）。
- 可落到 optics_agent 的设计点：实时只做轻量标记（embedding + outcome/importance），语义聚类形成后批量 LLM 巩固；merge-first 合并同主题记忆（同论文同图的多条记录合并为一条 episodic）；定期治理时回溯原始 trace 做 semantic refinement 补救摘要损失。
- 优先级：高
