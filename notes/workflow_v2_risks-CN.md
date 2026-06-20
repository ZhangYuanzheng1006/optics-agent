# Workflow v2 风险笔记

> 2026-06-20
> v1 风险评审已归档到 `project/to-do-future/DSL/`（24 类风险，7 层治理）。
> v2 风险笔记只保留 v2 简化版实际需要处理的风险，按优先级排序。

---

## 阅读指引

- v2 相比 v1 大幅简化，但不是无风险
- 风险分三档：现在不改就危险 / 跑通后必须加 / 远期
- 每项含：问题、依据、建议、优先级

---

## P0：现在不改就危险

### R1. 核心卖点错位

**问题**：如果最终成果只是"做了一个 agent workflow"，在 2026 年 cheap。学长直接问：相比聪明人用 Claude Code 有什么真实增益？

**建议**：核心卖点 = 光学复现 benchmark + deterministic verifier + 可审计执行。agent 只是手段。

**优先级**：P0

---

### R2. DSL 优势是假设不是结论

**问题**：我们假设 DSL 比固定脚本好，假设自迭代有净收益，但零验证。

**建议**：建立 baseline A/B/C/D 对比。固定脚本能跑通单球 Mie + 能量守恒 + 画图 + 报告的话，DSL 的增量价值必须明确。

**优先级**：P0

---

### R3. 确定性流程用 agent

**问题**：向"编排性"倾斜，能写死的不写死。学长问：固定场景 agent 解法相比写死脚本有什么本质不同？

**建议**：只有 4 个断点用 agent（intake/formalization/implementation/report），其余 4 个节点用脚本。每个 agent 节点必须回答"为什么脚本不能做"。

**优先级**：P0

---

### R4. 向量记忆"不治理靠检索"被证伪

**问题**：Zombie Agents 证明检索是攻击触发面不是防御面。MRMMIA 证明不治理 = 隐私信号最强。EvoMemBench 证明记忆注入在简单任务上有害。SSGM 证明不治理漂移无界。

**建议**：写入侧加 trust_level + 注入检测；检索侧 data/instruction 隔离；定期离线治理（衰减 + 合并 + 冲突消解）；按 memory_type 分衰减率；按任务难度动态注入。

**优先级**：P0

---

### R5. Zombie 持久注入

**问题**：我们架构几乎逐项复刻 Zombie Agents 威胁模型——agent 读 PDF/网页/工具输出写入记忆，workflow 检索注入上下文。受测模型含 GLM 系列，直接适用。

**建议**：
- 写入侧：source/provenance/trust_level 三字段；untrusted 内容做注入检测 + paraphrase
- 检索侧：untrusted 记忆只作 data 块注入，不得进 instruction 通道
- 禁止"检索结果自动回写记忆"闭环
- 周期性注入模式扫描

**优先级**：P0

---

## P1：跑通后必须加

### R6. 无 provenance / run manifest

**问题**：run 只记录最终产物，"变好了"无法归因。

**建议**：每次 run 生成 run_manifest.yaml（workflow hash、skill 版本、memory ID、模型参数、工具版本、container digest、artifact hash）。

**优先级**：P1

---

### R7. 无 attempt capsule

**问题**：无法统计某条经验有用还是有害。

**建议**：每节点产 attempt_capsule（selected_skills、selected_memories、commands_run、verifier_results、outcome、uncertainty）。再加 critic_verdict（attribution、failure_pattern、evidence）。

**优先级**：P1

---

### R8. 无 replay suite

**问题**：优化新任务后旧任务退化无感知（Forgetting 论文核心警告）。

**建议**：初始 replay suite（replay_mie_simple、replay_mie_lspr、replay_comsol_smoke、replay_report_boundary、replay_workflow_schema）。接受条件：净收益 + 无 PASS→FAIL + 成本不升 + 安全未削弱。

**优先级**：P1

---

### R9. 无 uncertainty routing

**问题**：缺参时仍 retry/debug，而不是走 clarification。

**建议**：每节点区分 action_confidence 和 request_uncertainty。request_uncertainty=high 时走 clarification/blocked，不走 debug/retry。

**优先级**：P1

---

### R10. 无 physics_formalization

**问题**：从论文 prose 直接生成代码，可能正确求解错误物理问题。

**建议**：新增 physics_formalization 节点（geometry/materials/equations/boundary_conditions/sources/solver/observables/assumptions/missing_fields）。所有代码生成必须消费此节点输出。

**优先级**：P1

---

### R11. 记忆效用值未参与排序

**问题**：纯语义相似度无法区分"相似但有用"和"相似但有害"。

**建议**：每条记忆加 utility_score，检索用 score = 0.5×similarity + 0.5×utility。运行时根据任务结果更新。MemRL 证明 λ=0.5 最优。

**优先级**：P1

---

### R12. 无 store routing

**问题**：多 store 场景下每次查所有 store，over-retrieval 引入噪声。

**建议**：向量召回前加 routing 层。query 含 "COMSOL" → project store；"phybench" → global + direction tag；模糊 → fallback project + global。先规则版，coverage 优先。

**优先级**：P1

---

### R13. skill 生命周期缺失

**问题**：skill 只进不出，Library Drift 必然发生。

**建议**：candidate → active → deprecated。promotion 需 2+ case 帮助或人工确认。deprecation 需 2 次 hurt。必须有 applies_when / does_not_apply_when / source_capsules。

**优先级**：P1

---

## P2：建议做

### R14. 失败记忆未被主动管理

**问题**：MemRL/FactorMiner/UI-Mem 都证明失败记忆是重要资产，但我们没有主动存储和管理。

**建议**：向量库主动存 failure_pattern 和 forbidden region。入库时检查与已有 failure pattern 的语义相似度。

**优先级**：P2

---

### R15. 记忆内容存储格式

**问题**：LoCoMo 证明 observation-based 存储优于 dialog/summary。摘要丢信息。

**建议**：记忆用结构化事实存储，如"在{{论文}}的{{图}}复现中，{{方法}}因为{{原因}}失败"。不存原始对话。

**优先级**：P2

---

### R16. embedding generalization cliff

**问题**：Procedural memory benchmark 证明 embedding 在 novel 语境排名逆转。跨子方向（COMSOL → Mie）词汇分布差异大。

**建议**：8B reranker 弥补 embedding 结构丢失；扩大记忆库规模优先于追求更好 embedding 模型；SKILL 内容做 LLM 抽象化。

**优先级**：P2

---

### R17. MRMMIA 隐私泄露

**问题**：黑盒 AUC 0.99，system prompt 防御无效。我们记忆含 PDF 段落、工具输出，可被推断。

**建议**：写入侧 paraphrase + 敏感字段过滤；检索侧 recall 式查询检测 + 泛化回答；调试日志按敏感数据处理。

**优先级**：P2（初期不公开部署，风险可控）

---

### R18. 多 agent 独立审查退化

**问题**：reviewer 只是复述 worker 的话，echoing 放大错误。

**建议**：reviewer 必须读 artifact/verifier/output；每轮交接声明 role/object_to_check/required_evidence/confidence；简单任务允许 single_agent 路径。

**优先级**：P2（早期人工 review 为主）

---

### R19. benchmark disclosure 不足

**问题**：只报 pass rate 不披露 harness/模型/成本/人工介入，无法归因。

**建议**：每个 benchmark run 记录 task version、workflow hash、模型参数、工具版本、container digest、cost、retry、human intervention、verifier outputs、replay regression。区分 LLM evaluator pass / deterministic verifier pass / physical verifier pass / human review pass。

**优先级**：P2（正式实验前必须）

---

## P3：远期

### R20. graph memory 错误因果边

**问题**：自动 caused_by/mitigated_by 边把相关当因果。

**建议**：graph 边需要 evidence/confidence，自动边默认低权重。远期再做。

**优先级**：P3

---

### R21. emulated sandbox 过信任

**问题**：模拟环境通过但真实 COMSOL/Magnus 行为不同。

**建议**：报告区分 emulated < dry-run < real sandbox < real execution。远期。

**优先级**：P3

---

## v2 相比 v1 消除的风险

以下 v1 风险在 v2 中通过设计决策直接消除，不需要额外处理：

| v1 风险 | v2 消除方式 |
|---------|-----------|
| workflow 拓扑自迭代导致 reward hacking | 拓扑人工写死 |
| 自迭代迭代自己导致元递归 | 禁止，全部 human gate |
| update_artifacts 直接写长期工件 | 拆成 propose → gate → apply，human gate |
| 外部化组件版本耦合 | run manifest 记录全版本 |
| skill 供应链投毒 | skill integrity check + candidate 不可执行 |
| skill 文本与脚本行为不一致 | declared vs actual capability 检查 |
| typed skill refactoring 丢边界 | applies_when / does_not_apply_when 强制 |
| 模板复用带入旧假设 | template_contract 字段 |
| memory type 混用污染 | loads_memories allowed_types 约束 |
| benchmark 动态 drift | 动态 case 标 candidate_benchmark |

这些不是"解决了"，而是"通过限制自迭代范围从设计上避开了"。

---

## 优先级总览

| 优先 | 数量 | 含义 |
|------|------|------|
| P0 | 5 | 现在不改就危险 |
| P1 | 8 | 跑通后必须加 |
| P2 | 6 | 建议做 |
| P3 | 2 | 远期 |

---

## 一句话

```text
v2 的风险治理策略不是"建更多 gate"，
而是"限制自迭代范围 + 先跑通再加治理"。
最大的风险不是某个具体技术问题，
而是我们在没有验证 DSL 价值之前就过度投资治理基础设施。
```
