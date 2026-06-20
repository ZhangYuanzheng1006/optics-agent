# Memory Retrieval 论文摘要与风险分析

本目录共 8 篇 PDF，全部用 `pdftotext -layout` 提取后通读。统一格式如下，文末附 5 个重点问题的综合分析。

每篇论文的 arxiv_id 取自文件名前缀。

---

## 2503.14800 ERMAR: Enhanced Ranked Memory-Augmented Retrieval

- 文件：`2503.14800_ERMAR_Ranked_Memory_Augmented_Retrieval.pdf`
- 一句话结论：在 MemLong 之上加入 relevance scoring + pointwise re-ranking，对长上下文 K-V 记忆做动态排序，显著缓解长上下文信息稀释问题。
- 核心方法/贡献：四阶段流程（Long Memory Retrieval → Search → Reranking → Memory Fusion Generation）；relevance score 用 `softmax(qK^T/√d_ret)`；RSAR 机制 `TopK{sim(E(tq),e) · max_j s_j}`，把内容相似度与历史 relevance 分数相乘；冻结下层 transformer + 可训练上层 + 检索增强注意力；BGE-M3 embeddings；memory capacity 32768 个 KV pair；pruning 阈值丢弃低分条目；引入 historical usage patterns 修正 relevance。
- 可用于我们向量记忆系统的经验：
  - relevance scoring 用乘法（内容相似度 × 历史重要性）而非纯点积，可作为 reranker 打分参考。
  - historical usage patterns 整合到 relevance，访问过的记忆权重动态调整。
  - pruning 策略（按历史 score 阈值裁剪）是"几十万条不治理"的替代方案——按 relevance 衰减裁剪比完全不治理更稳。
- 警告/风险：
  - ERMAR 的 reranking 在模型内部 KV 层做，与 transformer 层耦合，不是外部向量库 reranker，实现路径与我们不同。
  - 16k token 处有性能退化（训练只到 32k），属于效率-收益 trade-off 而非系统性失败。
  - 需要 fine-tune 模型（OpenLLaMA-3B + LoRA），hidden dim d=100 偏小。
  - 长上下文语言建模 benchmark（WikiText-103/PG-19/Proof-Pile），不是 agent 记忆场景。
- 可落到 optics_agent 的设计点：
  - reranker 打分公式可借鉴 `sim · max(history_score)` 形式，把记忆的 importance 字段纳入排序。
  - pruning 策略替代"完全不治理"——按 `importance × recency_decay` 软裁剪低价值记忆。
  - historical usage patterns 可记录每条记忆被检索后是否被采用，回填到 importance。
- 优先级：中（理念契合但实现路径与我们外部向量库方案不同，取其打分与 pruning 思想）

---

## 2511.07587 GSW: Generative Semantic Workspace for Episodic RAG

- 文件：`2511.07587_GSW_Generative_Semantic_Workspace_Episodic_RAG.pdf`
- 一句话结论：用 Operator+Reconciler 构建 actor-role-state-verb 的结构化 episodic workspace，在 EpBench 上比 GraphRAG/HippoRAG2/LightRAG 高达 20% recall，且 query-time context token 减少 51%。
- 核心方法/贡献：受海马体-新皮质神经科学启发；Operator 把观察映射到中间语义结构（roles/states/verbs/time-space），Reconciler 用 Markovian 转移模型 `P(Mn|C0:n)` 递归更新 workspace；query 时匹配实体→生成摘要→rerank→LLM 合成答案；GPT-4o 实现；时空连续性约束规范语义映射。
- 可用于我们向量记忆系统的经验：
  - 结构化 world model 比纯 chunk 检索更准且更省 token（51% token 节省）。
  - actor-centric 表示适合追踪实体演变（角色/状态转移）。
  - 时空连续性约束可规范关联推理。
- 警告/风险：
  - 依赖 GPT-4o 做 Operator/Reconciler，成本高。
  - 针对 narrative/episodic 文本（犯罪报告、政治简报、叙事）设计，科学计算记忆场景不直接契合。
  - schema 需针对领域定制，工程量大。
  - EpBench 是合成叙事 benchmark，泛化到真实技术记忆未验证。
- 可落到 optics_agent 的设计点：
  - 对"论文复现案例追踪"可试用 `actor=paper, role=reproduction_target, state=reproduction_status` 的结构化表示，但收益有限。
  - token 效率证明结构化检索比暴力 top-k 经济——支持我们 top-5 窄注入方向。
  - 我们的记忆主要是技术事实/决策/pitfalls，不是叙事，GSW 的 actor-role 模型不直接适用。
- 优先级：低（领域不匹配，narrative/episodic 场景为主，技术记忆收益有限）

---

## 2601.01885 AgeMem: Agentic Memory (Unified LTM/STM Management)

- 文件：`2601.01885_AgeMem_Unified_Long_Term_Short_Term_Management.pdf`
- 一句话结论：把 LTM/STM 管理统一进 agent policy，通过 6 个 memory tools（ADD/UPDATE/DELETE/RETRIEVE/SUMMARY/FILTER）+ 三阶段渐进 RL + step-wise GRPO 训练，端到端学习何时存/取/弃。
- 核心方法/贡献：unified RL formulation，memory ops 作为 action；三阶段轨迹（Stage1 LTM 构建 → Stage2 干扰+STM 管理 → Stage3 协调任务）；step-wise GRPO 解决稀疏不连续奖励，把终局 reward 回传到早期存储决策；progressive curriculum；penalty 抑制冗余存储、过度工具调用和 context 爆炸。
- 可用于我们向量记忆系统的经验：
  - memory management 作为可学习策略而非硬规则——让 agent 自主决定存/取/弃。
  - tool-based interface 把记忆操作显式化（ADD/UPDATE/DELETE/RETRIEVE/SUMMARY/FILTER）。
  - step-wise credit assignment：把任务终局成功回传到早期存储决策，奖励早期正确存储。
  - penalty 项控制 context 爆炸和冗余存储，值得引入。
- 警告/风险：
  - 需要 RL 训练（step-wise GRPO），工程重，GPU 成本高。
  - 三阶段 curriculum 需要任务可分解为"信息获取→干扰→协调"三段，不是所有任务都适用。
  - 依赖训练时的 expected answer 监督，弱监督场景难用。
  - 推理时多工具调用增加延迟和 token。
- 可落到 optics_agent 的设计点：
  - "几十万条不治理"可借鉴 learned forgetting 思想，但 RL 训练对我们不现实——可退化为规则版：按 `importance × recency × retrieval_hit_rate` 衰减。
  - tool-based memory ops 思路可简化为规则版（已有 memory_store/update/delete/pin）。
  - penalty 抑制冗余存储值得引入：存储时检查 dedup，过度相似拒绝写入。
- 优先级：中（理念有用但 RL 路径不现实，取其 tool-based ops 与 penalty 思想）

---

## 2602.13530 REMem: Reasoning with Episodic Memory (ICLR 2026)

- 文件：`2602.13530_REMem_Reasoning_Episodic_Memory_Language_Agent.pdf`
- 一句话结论：两阶段框架——indexing 构建 hybrid memory graph（time-aware gists + time-scoped facts）+ agentic inference 用 ReAct + 5 个 curated tools 迭代检索图，在 4 个 episodic benchmark 上超越 Mem0/HippoRAG2（recollection +3.4%, reasoning +13.4%），且对不可答问题更鲁棒拒绝。
- 核心方法/贡献：gist（带时间戳的简洁事件描述）+ fact（time-scoped triples 带 Wikidata qualifiers: point_in_time/start_time/end_time）；hybrid graph 同时有 gist 节点和 phrase 节点，synonymy edges 连接相似 gists；tools: `semantic_retrieve`/`lexical_retrieve`（带时间过滤参数 start_time/end_time/start_op/end_op）+ `find_gist_contexts`/`find_entity_contexts`（图探索）+ `output_answer`；ReAct 迭代；保留潜在矛盾的记忆以备历史复查。
- 可用于我们向量记忆系统的经验：
  - hybrid memory（gist 摘要 + fact 三元组）比单一表示强——concept-level + context-level 双层。
  - 时间感知是 episodic 关键，时间过滤参数让检索工具更灵活。
  - agentic iterative retrieval 比 one-shot top-k 强，可分解复杂问题为子查询。
  - curated tools 带结构化参数（时间过滤、limit、ordering、aggregation）比纯相似度灵活。
  - 对不可答问题应主动拒绝而非强行回答。
- 警告/风险：
  - 依赖 LLM 做 gist/fact 抽取，质量影响下游检索。
  - ReAct 多轮迭代增加延迟和 token 成本。
  - 图构建成本（每条记忆都要抽取 gist+facts）。
  - 针对 conversational/temporal 场景优化，技术记忆场景需适配。
- 可落到 optics_agent 的设计点：
  - hybrid graph 可补充纯向量：gist = 决策一句话总结，fact = 结构化三元组（subject/predicate/object + 时间限定）。
  - 检索工具加时间过滤参数（`from_date/to_date`），支持"只查最近 N 天的决策"。
  - agentic iterative retrieval 对复杂多跳查询有用（如"复现案例 A 的失败原因如何关联到案例 B 的成功条件"），但日常简单检索 top-100→rerank→top-5 足够。
  - 保留矛盾记忆以备历史复查——与我们 supersedes 链设计一致。
  - 加入 `output_answer` 式拒绝工具，对检索证据不足的查询直接回"无相关记忆"。
- 优先级：高（hybrid graph + agentic retrieval + 时间过滤直接对标我们的改进方向）

---

## 2603.09297 TA-Mem: Tool-Augmented Autonomous Memory Retrieval

- 文件：`2603.09297_TA_Mem_Tool_Augmented_Autonomous_Memory_Retrieval.pdf`
- 一句话结论：三部分框架——one-shot 语义分块提取 episodic notes + multi-indexed database（person/tag/keyword key + events/facts similarity）+ agentic retrieval loop 自主选工具，在 LoCoMo 上显著超越 Mem0/A-Mem/MemoryOS，token 效率高（3755 tokens/Q）。
- 核心方法/贡献：memory note `Ni={m,n,Si,Ki,Pi,Fi,Ei,ti,Ti}`（summary/keywords/people/facts/events/timestamps/tags）；multi-index 支持 key matching `Qs` 和 cosine similarity `Qk`；person profile 查询 `Ep/Fp`（聚合某人的所有 events/facts）；retrieval agent agentic loop（最多 7 轮，平均 2.71 轮，97.73% 在 4 轮内收敛）；per-QA cache 去重；提供 available keys 参考集引导 LLM 选词。
- 可用于我们向量记忆系统的经验：
  - multi-index（key + similarity + profile）比单一向量索引灵活得多。
  - 不同问题类型用不同工具分布——temporal 问题主要查 events，open-domain 主要查 facts，说明检索策略应随问题类型自适应。
  - agentic loop 4 轮收敛，迭代检索成本可控。
  - per-QA cache 避免同一 session 内重复检索同一记忆。
  - available keys 参考集辅助 LLM 在 key-based 查询时选对词，缓解词汇变异问题。
- 警告/风险：
  - extractor 依赖 prompt 一致性，需 fine-tune instructions。
  - agentic loop 引入延迟，time-sensitive 应用受限。
  - GPT-4o-mini 实现，更小模型可能无法驾驭工具选择。
  - LoCoMo 单一 benchmark，泛化性待验证。
- 可落到 optics_agent 的设计点：
  - multi-index 思路——在向量召回之外加 key-based lookup（按 `memory_type`/`project_path`/`tags` 精确过滤），混合检索。
  - per-QA cache 减少重复检索（同一对话内同一查询不重复打 reranker）。
  - 工具分布分析直接支持我们"reranker prompt 加节点类型"的设计——不同节点类型（Mie Python analytical / COMSOL Java / Magnus platform）应用不同检索策略。
  - available keys 参考集：把可用 tags/memory_type 列表喂给 LLM，辅助构造精准查询。
- 优先级：高（multi-index + 工具分布 + per-QA cache 直接支持我们的多 store + 节点类型设计）

---

## 2603.15658 Cost-Sensitive Store Routing for Memory-Augmented Agents (ICLR 2026 Workshop)

- 文件：`2603.15658_Cost_Sensitive_Store_Routing_Memory_Augmented_Agents.pdf`
- 一句话结论：把 memory retrieval 形式化为 store-routing 问题，oracle router 比 uniform retrieval 准确率高（86.7% vs 81.3%）且 context token 少 62%（299 vs 787），并形式化为 cost-sensitive subset-selection `π*(q)=argmax E[Acc(q,G)-λΣcs]`。
- 核心方法/贡献：4 stores（STM/Summary/LTM/Episodic）；routing metrics（Coverage/Exact Match/Waste）；hybrid heuristic（语义模式匹配 + 保守 fallback Sum+LTM，coverage 94%）；长上下文放大 over-retrieval 惩罚（long context oracle 72% vs uniform 60%）；feature ablation：semantic 信号 +33% coverage，embedding similarity +4%；conflicting information 跨 store 误导模型。
- 可用于我们向量记忆系统的经验：
  - selective retrieval 同时提升准确率和降低成本——"更多 context 不必然更好"是重要反直觉结论。
  - 长上下文 over-retrieval 惩罚放大——每个额外 store 引入 ~1000 token 噪声会显著降低准确率。
  - coverage 优先于 precision（miss store = 不可答，worse than over-retrieval）。
  - fixed policy（STM+Sum+LTM）接近 oracle，说明简单的"总是查几个核心 store"可能就够。
  - heuristic router 在 synthetic 上 coverage 94% 但 QA 只有 70%——routing 正确不等于 QA 正确，extraction 环节也关键。
  - cost-sensitive 公式 `π*(q)=argmax E[Acc(q,G)-λΣcs]` 提供决策论框架。
- 警告/风险：
  - synthetic labels 非人工标注，真实部署 store 必要性可能不同。
  - 只测 GPT-3.5/4o-mini 两个模型族。
  - heuristic router 与 oracle gap 大，需 learned routing 才能闭合。
  - store 分类（STM/Sum/LTM/Epi）依赖认知科学假设，可能不全。
- 可落到 optics_agent 的设计点：
  - 直接对标我们多 store（project / global / team + direction:phybench tag）——应加 store routing 层，而非每次查所有 store。
  - cost-sensitive 公式可直接套用：`π*(q)=argmax E[Acc(q,G)-λΣcost]`，λ 控制 token 成本权衡。
  - 先做 hybrid heuristic 路由：按 query 语义信号（"COMSOL"→project comsol skill，"phybench 共享"→global direction tag）路由到对应 store，coverage 优先。
  - fixed policy "总是查 project + global" 可能接近 oracle，作为兜底。
  - 我们的 top-5 窄注入已是 anti-over-retrieval 设计，符合论文结论。
  - 注意跨 store conflicting info——我们 supersedes 链和 importance 排序可解决版本冲突。
- 优先级：高（直接解决我们多 store 场景，公式与结论可直接套用）

---

## 2604.07863 ACGM: Adaptive Cross-Modal Graph Memory (SIGIR 2026)

- 文件：`2604.07863_ACGM_Task_Adaptive_Retrieval_Graph_Memory.pdf`
- 一句话结论：用 policy-gradient 学习 task-adaptive relevance predictor 构建稀疏图（3.2 edges/node）+ modality-specific decay（visual 4.3× 快于 text：λv=0.47 vs λx=0.11）+ O(logT) 层级检索，在 WebShop/VisualWebArena/Mind2Web 上 nDCG@10 82.7（+9.3 over GPT-4o，p<0.001）。
- 核心方法/贡献：neural predictor `gφ` 估计 `P(relevant(i,j))=σ(gphi(ẽi,ẽj,fij))`；policy gradient 用 task success 作为 reward，EMA baseline `bt` 降方差 38%；两阶段训练（supervised edge pretrain 18h → policy gradient finetune 22h，共 40 GPU-hours）；modality-specific decay `λm`（visual=0.47, text=0.11, knowledge=0.23）；two-tier 结构（recent flat + older 4-ary tree via online k-means）；learned sparsity 3.2 edges/node vs dense 8.7。
- 可用于我们向量记忆系统的经验：
  - task-adaptive retrieval（用下游任务成功训练检索）比静态相似度强——relevance 应从任务反馈学。
  - modality-specific decay——不同记忆类型衰减速率不同，不能用统一时间衰减。
  - learned sparsity 降低检索成本（3.2 vs 8.7 edges/node）。
  - two-tier（recent flat + old hierarchical）平衡效率和精度，O(logT) 检索。
  - policy gradient + EMA baseline 稳定训练，binary task success 即可。
- 警告/风险：
  - 需要下游任务成功信号和 GPU 训练（40 GPU-hours on 8×A100），对我们不现实。
  - 针对多模态 web 导航（screenshots + HTML），我们纯文本记忆不直接适用。
  - frozen pretrained embeddings（CLIP/RoBERTa）依赖外部模型。
  - binary reward 需两阶段预训练才能稳定收敛。
- 可落到 optics_agent 的设计点：
  - modality-specific decay 启示——我们的记忆类型（decision/lesson/fact/pitfall/command）应有不同衰减率：decision 慢（λ=0.05）、lesson 中（λ=0.15）、log/command 快（λ=0.4），用 importance × exp(-λ·age) 软排序。
  - two-tier 结构可借鉴：近期 30 天记忆 flat 全检索，更早的按 project_path 聚类成 hierarchical 索引。
  - learned 路径不现实，可改用规则版 task-adaptive：按节点类型（Mie/COMSOL/Magnus）调整召回权重。
  - 不需要 graph 构建对我们——decay + two-tier 即可。
- 优先级：中（modality-specific decay 和 two-tier 结构可借鉴，但 learned 路径不现实）

---

## 2606.06036 MRAgent: Memory is Reconstructed, Not Retrieved (ICML 2026)

- 文件：`2606.06036_MRAgent_Memory_Reconstructed_Not_Retrieved_Graph.pdf`
- 一句话结论：提出 active memory reconstruction 范式——Cue–Tag–Content 异构图 + LLM 驱动迭代重建，理论证明 active policy 严格强于 passive policy（Theorem 4.1: H_passive ⊊ H_active），在 LoCoMo/LongMemEval 上提升达 23% 且 token/runtime 显著降低。
- 核心方法/贡献：Cue–Tag–Content graph（cues=细粒度关键词, tags=关联中介, contents=记忆项）；multi-granular layers（episodic/semantic/topic abstraction）；reconstruction state `S(t)=(Z(t),H(t))`；traversal actions（forward Cue→Tag→Content + reverse Content→(Cue,Tag)）；LLM routing 选 action + 剪枝避免组合爆炸；Theorem 4.1 严格证明 active ⊋ passive；tags 作为语义桥梁降低 content 访问成本。
- 可用于我们向量记忆系统的经验：
  - active reconstruction（边检索边推理）理论严格强于 one-shot passive retrieval——这是对我们 top-100→rerank→top-5 范式的根本性挑战。
  - Cue–Tag–Content 中介结构避免 n-hop 邻居爆炸，tags 作为"先选路径再访内容"的廉价路由。
  - reverse traversal 让已检索内容激活新线索，支持"基于已知再找关联"。
  - multi-granular layers（episodic 事件 / semantic 稳定知识 / topic 抽象）支持不同粒度推理。
  - 理论保证提供方法论底气，不只是经验提升。
- 警告/风险：
  - LLM 每步推理成本高，迭代重建延迟显著。
  - 图构建依赖 LLM 抽取 cue/tag/content 质量。
  - 针对 conversational memory（LoCoMo/LongMemEval），技术记忆场景需适配。
  - 迭代过程可能不收敛或循环，需设最大步数。
- 可落到 optics_agent 的设计点：
  - active reconstruction 是 top-100→rerank→top-5 的进阶方向——对复杂多跳查询可加一轮"基于 top-5 结果再检索"（reverse traversal：检索到决策后反向找相关 pitfalls/lessons）。
  - Cue–Tag–Content 可简化为：cues = 记忆关键词，tags = 我们已有的 tags 字段，contents = 记忆正文——tags 已是现成的关联索引。
  - reverse traversal 启发：检索到一条 decision 后，自动查与其有 `caused_by`/`mitigated_by`/`references` 边的记忆（memory_graph 已支持）。
  - 日常简单检索仍用 top-100→rerank→top-5，只对"多跳/关联/因果链"查询触发 active reconstruction 二轮。
  - multi-granular：decision=episodic, fact=semantic, direction-level summary=topic，三层已隐含在我们的 scope 设计里。
- 优先级：高（理论支撑 active>passive + Cue–Tag–Content 结构可落地到现有 tags + memory_graph）

---

# 综合分析：5 个重点问题

## 问题 1：检索策略（graph memory、active reconstruction、tool-augmented retrieval、store routing）哪些比纯向量+rerank 更强？

| 策略 | 论文 | 是否强于纯向量+rerank | 适用条件 |
|---|---|---|---|
| Active reconstruction | MRAgent | 是（理论严格证明 +23%） | 复杂多跳/关联查询，需 LLM 每步推理 |
| Tool-augmented agentic retrieval | REMem, TA-Mem | 是（+3.4%~13.4%，迭代 curated tools） | 需要 structured tools 和多轮迭代 |
| Hybrid graph memory | REMem, MRAgent | 是（gist+fact 双层，多跳增益） | 需要 LLM 抽取 gist/fact 构图 |
| Task-adaptive learned retrieval | ACGM | 是（+9.3 nDCG） | 需要下游任务成功信号 + GPU 训练 |
| Store routing | Cost-Sensitive | 是（+5.4% acc，-62% token） | 多 store 架构，先验 store 语义清晰 |
| Structured workspace | GSW | 是（+20% recall，-51% token） | narrative/episodic 场景 |
| Learned memory management | AgeMem | 是（端到端优化） | 需要 RL 训练 + 任务可分解 |
| Ranked KV reranking | ERMAR | 是（缓解信息稀释） | 长上下文 KV 层，需 fine-tune |

**结论**：所有 8 篇都比纯向量+rerank 强，但增益场景不同。**对我们而言**：
- 简单事实检索（"COMSOL license 路径"）：纯向量 + rerank 足够。
- 复杂关联查询（"案例 A 失败如何关联到案例 B"）：active reconstruction / hybrid graph 有显著增益。
- 多 store 选择：store routing 直接增益。
- **不应急于全面替换**向量+rerank，而应**按查询复杂度分层**——简单查询走快路径，复杂查询触发迭代检索。

## 问题 2：是否需要 graph 结构补充纯向量检索？

**需要，但分场景分强度**。

**支持 graph 的证据**：
- REMem：hybrid graph（gist+fact）+ agentic tools 比 Mem0/HippoRAG2 强 3.4%~13.4%。
- MRAgent：Cue–Tag–Content graph + active reconstruction 理论严格强于 passive，+23%。
- ACGM：learned sparse graph 比 dense retrieval 强 9.3 nDCG。
- GSW：结构化 workspace 比 GraphRAG/HippoRAG2 强 20% recall。

**graph 的三个核心作用**：
1. 多跳关联（A→B→C 因果链，纯向量难以召回）
2. 结构化过滤（时间范围、entity 精确匹配，比相似度精准）
3. 剪枝避免 n-hop 爆炸（MRAgent 的 tags 中介）

**对我们的建议**：
- **不要全面替换向量库**——日常 80% 查询是简单事实检索，向量+rerank 足够且快。
- **加轻量 graph 层**作为补充：
  - 利用现有 `memory_link` / `memory_graph` 已建的 `caused_by`/`mitigated_by`/`references`/`implements` 边。
  - 利用现有 `tags` 字段作为 Cue–Tag–Content 中的 Tag 中介。
  - 检索到一条记忆后，可选触发 1-hop 邻居扩展（reverse traversal）。
- **graph 构建成本控制**：只在 `memory_store` 时抽取轻量三元组（subject=tags, predicate=memory_type, object=title），不额外跑 LLM。
- **风险**：graph 维护成本高，依赖抽取质量；建议先小规模试点（只对 decision/lesson 类型建图，fact 不建）。

## 问题 3：cost-sensitive routing 对我们多 store 场景的启示

**直接套用 Cost-Sensitive Store Routing 的框架**。

我们当前的 store 划分：
- `scope=project` + `project_path` → 项目级
- `scope=global` + 无 tag → 用户级
- `scope=global` + `direction:phybench` tag → 方向级
- `scope=team` → 团队级

**启示**：

1. **加 store routing 层**，而非每次查所有 store。公式 `π*(q)=argmax E[Acc(q,G)-λΣcs]` 可直接套用，λ 控制 token 成本权衡。

2. **先做 hybrid heuristic 路由**（Cost-Sensitive 论文的 baseline）：
   - query 含 "COMSOL/Magnus/Docker" → 路由到 project store（optics_agent）
   - query 含 "phybench/共享/跨项目" → 路由到 global + direction:phybench
   - query 含 "用户偏好/默认" → 路由到 global user-preference
   - 模糊 query → fallback 到 project + global（coverage 优先，类似 Sum+LTM）

3. **coverage 优先于 precision**：miss store = 不可答，比 over-retrieval 更糟。fallback 用宽 store 集合。

4. **fixed policy 接近 oracle**：简单的"总是查 project + global"可能就够，不必强求 learned router。

5. **长上下文 over-retrieval 惩罚放大**：我们 top-5 窄注入已是 anti-over-retrieval 设计，符合论文结论。每个额外 store 引入 ~1000 token 噪声会显著降低准确率——所以 store routing 收益在我们场景下可能更大。

6. **跨 store conflicting info**：我们已有 `supersedes` 链和 `importance` 排序解决版本冲突，比论文场景更有优势。

7. **heuristic router 在 QA 上不如 oracle**：说明纯规则路由有上限，长期应考虑 learned routing（用检索命中率/采用率作为监督信号）。

## 问题 4：episodic memory 检索和 reasoning 的结合方式

**四种结合范式**（按耦合度从松到紧）：

1. **REMem**：ReAct + curated tools 迭代——检索和推理交替进行，工具带结构化参数（时间过滤、limit、ordering），agent 自主决定下一步工具调用。中等耦合。

2. **MRAgent**：active reconstruction + traversal actions + LLM routing——LLM 每步选 traversal action（forward/reverse），基于累积证据 `H(t)` 决定方向，剪枝避免爆炸。紧耦合，理论保证 active ⊋ passive。

3. **GSW**：Operator 抽取 + Reconciler 递归更新 + query 匹配实体——离线构建结构化 workspace，query 时匹配实体生成摘要再 rerank。松耦合（构建与查询分离）。

4. **AgeMem**：memory ops 作为 RL action，端到端学习——检索/存储/过滤都是 policy 的一部分，与任务奖励联合优化。最紧耦合，但需 RL 训练。

**共同点**：把检索和推理耦合，**迭代进行**，而非 one-shot。证据累积驱动下一步检索方向。

**对我们的启示**：
- 日常检索保持 one-shot（top-100→rerank→top-5），快且够用。
- 对"为什么/如何关联/因果链"类查询，触发 **REMem 式 ReAct 迭代**：
  - 第 1 轮：向量召回 top-5 + rerank
  - 第 2 轮（可选）：基于 top-5 结果抽取新关键词，再向量召回 + rerank
  - 第 3 轮（可选）：reverse traversal 查 memory_graph 的 1-hop 邻居
  - 最多 3 轮，设上限避免延迟爆炸（TA-Mem 97.73% 在 4 轮内收敛）。
- MRAgent 的理论保证给了我们底气：active 严格强于 passive，但成本也高——按需触发是关键。

## 问题 5：对我们"top-100 → rerank → top-5"流程的改进建议

按优先级排序（结合 8 篇论文证据）：

### 高优先级改进

1. **加 store routing 层**（Cost-Sensitive）
   - 在向量召回前加一层 router，按 query 语义信号选 store，再各 store 内 top-100。
   - 先 hybrid heuristic，coverage 优先，fallback 到 project+global。
   - 收益：准确率 +5%，token -62%（论文数据）。
   - 落地难度：低（规则版即可）。

2. **reranker prompt 加节点类型**（已有想法，TA-Mem 工具分布分析强烈支持）
   - TA-Mem 显示 temporal 问题 70% 调 events 工具，open-domain 60% 调 facts 工具——不同节点类型需要不同检索策略。
   - 我们的节点类型（Mie Python analytical / COMSOL Java / Magnus platform / Docker / paper reproduction）应注入 reranker prompt。
   - 收益：压低不相关记忆，提升 top-5 精度。
   - 落地难度：低（改 prompt 即可）。

3. **hybrid index：向量 + key-based 混合**（TA-Mem multi-index）
   - 在向量召回之外加 key-based lookup（按 `memory_type`/`project_path`/`tags` 精确过滤）。
   - 对"查所有 decision"或"查 phybench 方向记忆"类查询，key-based 比向量更精准。
   - 收益：精准查询命中率提升。
   - 落地难度：中（需加索引）。

4. **memory_type-specific decay**（ACGM modality-specific decay）
   - 不同 memory_type 用不同衰减率：decision 慢（λ=0.05）、lesson 中（λ=0.15）、fact 慢（λ=0.08）、pitfall 中（λ=0.2）、command 快（λ=0.4）、log 很快（λ=0.6）。
   - 排序时用 `importance × exp(-λ·age_in_days)`。
   - 收益：旧决策不被新 log 淹没，几十万条记忆自然分层。
   - 落地难度：低（改排序公式）。

5. **reverse traversal 二轮检索**（MRAgent active reconstruction）
   - 对复杂查询，top-5 结果作为新线索触发第 2 轮：查 memory_graph 的 1-hop 邻居（`caused_by`/`mitigated_by`/`references`）。
   - 最多 2 轮，设上限。
   - 收益：多跳关联查询 +23%（MRAgent 数据）。
   - 落地难度：中（需 query 复杂度判断 + memory_graph 已有）。

### 中优先级改进

6. **pruning 策略替代"完全不治理"**（ERMAR）
   - 按 `importance × recency × retrieval_hit_rate` 软裁剪，低于阈值的降级（不删除，但不入召回池）。
   - 比完全不治理更稳，比硬删除更安全。
   - 落地难度：低。

7. **per-QA cache 去重**（TA-Mem）
   - 同一 session 内同一查询不重复打 reranker，缓存 top-5。
   - 收益：延迟和 GPU 成本降低。
   - 落地难度：低。

8. **relevance score 用乘法**（ERMAR）
   - reranker 打分用 `sim · max(importance, history_hit_score)` 而非纯相似度。
   - 把记忆的 importance 字段纳入排序。
   - 落地难度：低（改打分公式）。

9. **时间过滤参数**（REMem）
   - 检索工具加 `from_date/to_date`，支持"只查最近 N 天的决策"。
   - 对"当前状态"类查询有用，避免旧版本误导。
   - 落地难度：低。

10. **拒绝能力**（REMem）
    - 检索证据不足（top-5 reranker score 都低于阈值）时，直接回"无相关记忆"而非强行注入。
    - 避免幻觉。
    - 落地难度：低。

### 低优先级改进（长期/实验性）

11. **learned routing**（Cost-Sensitive 长期方向）
    - 用检索命中率/采用率作为监督信号，训练 store router。
    - 需积累日志数据。
    - 落地难度：高。

12. **hybrid graph 构建**（REMem 长期方向）
    - 对 decision/lesson 类型记忆抽取轻量三元组（subject=tags, predicate=memory_type, object=title）建图。
    - 支持 graph 探索工具。
    - 落地难度：高（需 LLM 抽取 pipeline）。

13. **RL 训练 memory management**（AgeMem 长期方向）
    - 端到端学习存/取/弃策略。
    - 对我们规模不现实，仅作长期参考。
    - 落地难度：极高。

---

# 处理统计

- 处理篇数：8
- 读取失败：无
- 输出文件：`C:\Users\27370\Desktop\project\optics_agent\papers\memory\memory_retrieval\README_summaries.md`
- 提取工具：`pdftotext -layout`（D:\Download\texlive\2026\bin\windows\pdftotext.exe）
- 临时文本目录：`C:\Users\27370\AppData\Local\Temp\opencode\mem_txt\`
