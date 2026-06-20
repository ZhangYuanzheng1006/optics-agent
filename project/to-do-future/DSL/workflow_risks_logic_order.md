# Workflow 风险与修改建议（底层逻辑顺序）

> 2026-06-20
> 这份笔记按"问题之间的因果关系"和"重要性"组织，不是简单编号清单。
> 核心思路：先解决方向性问题，再解决治理基础，再解决可审计性，最后才谈经验治理和远期。
> 每层不解决，后面层的工作都建立在错误前提上。

---

## 为什么按这个顺序

```text
方向错了 → 治理再好也是在错误方向上做精致工程
治理没基础 → 审计再细也无法阻止错误经验流入长期工件
没有审计 → 任何"改进"都不可归因，自迭代变成黑箱
没有判断路由 → 系统在不确定时仍执行，缺参时仍 retry
没有安全隔离 → 私有数据可能通过工具链外泄
没有经验治理 → skill/memory/template/benchmark 自己会 drift
```

所以顺序是：

```text
方向 → 治理基础 → 可审计性 → 判断路由 → 安全 → 经验治理 → 远期
```

---

## 第一层：方向性问题

> 这一层不解决，后面所有工程工作都可能在错误前提下进行。

### 1. 核心卖点错位：agent 框架不是成果

**问题**

2026 年大量传统学科 researcher 都在包装 agent 框架。如果我们最终成果只是"做了一个多 agent workflow，能读论文、分配任务、写代码、总结经验"，这在垂域内已经 cheap。

学长直接问了：

```text
你的 workflow/agent 框架相比一个聪明人使用 Claude Code 有什么真实增益？
```

**为什么是方向性问题**

这决定了我们评估什么、写什么论文、怎么设计系统。如果核心是 agent 框架，就会追求"更自动、更复杂、更多节点"。如果核心是垂域可验证效果，就会追求"更难假进步、更可复现、verifier 更强"。

**建议**

- 核心卖点定位为：**光学复现 benchmark + deterministic verifier + 可审计执行系统**
- agent 只是实现手段
- 所有成果必须回答：相比 baseline 有什么真实增益

**优先级**：最高。影响所有后续设计取舍。

---

### 2. 智能介入边界未定义：拆分原则错了

**问题**

我们之前的设计倾向是"为了编排性，多拆 agent 节点、多拆蓝图"。但学长的逻辑是：

```text
只有需要智能介入的断点才拆分；
能 rule-based 写死的就写死，不必让 agent 知会。
```

**为什么是方向性问题**

如果拆分原则错了，系统会变成"为了 agent 而 agent"——确定性流程也被 LLM 包裹，带来延迟、成本、不可复现、错误放大。这正好是学长问的第二个问题：

```text
固定场景 agent 解法相比写死脚本有什么本质不同和效率提升？
```

**建议**

明确两类节点：

| 节点类型 | 执行器 | 适用场景 |
|---------|--------|---------|
| deterministic | script / rule | 输入输出明确、验收条件固定 |
| intelligence | agent | 信息欠指定、需要跨文献/物理判断 |

以下优先用脚本，不启动 agent：

- 文件结构初始化
- schema 校验
- PDF 文本提取
- verifier 执行（能量守恒、Rayleigh 极限等）
- artifact hash / run manifest 写入
- export whitelist 检查
- replay suite 运行

以下保留 agent：

- 论文意图理解
- 物理 formalization
- 参数缺失判断
- 异常归因
- 停止/继续/请求人工决策
- 报告措辞审查

**优先级**：最高。影响 architecture 设计。

---

### 3. DSL/自迭代优势是假设，不是结论

**问题**

我们现在默认"DSL 比固定脚本好""自迭代有净收益"，但零验证。

更诚实的分层：

```text
DSL 比纯 prompt 有优势     → 基本成立（可审计、可回放）
DSL 比固定脚本有优势       → 未证明（只在流程结构可变时才可能）
自迭代 DSL 比固定脚本有优势 → 完全未证明，且风险最大
```

**为什么是方向性问题**

如果我们把项目赌在"自迭代有效"上，但最后 benchmark 显示自迭代不如固定脚本，那所有 self-evolution 基础设施都白做。反过来，如果先证明 DSL 在"流程结构可变"场景下比固定脚本好，再谨慎加自迭代，风险可控。

**建议**

建立 baseline 体系：

```text
Baseline A: 聪明人 + Claude Code
Baseline B: 固定脚本 / 固定 pipeline
System C:   DSL workflow，无自迭代
System D:   + proposal-only self-iteration + replay gate
```

比较指标：物理 verifier 通过率、缺参发现率、复现耗时、过度声明率、replay regression 数、人工介入次数、成本。

**优先级**：最高。决定整个项目的评估方法。

---

## 第二层：自迭代治理基础

> 这一层决定系统能否安全运行。不解决，任何经验都会直接污染长期工件。

### 4. `update_artifacts` 直接写长期工件

**问题**

当前 `paper_reproduction.workflow.yaml` 的 `update_artifacts` 节点允许 agent 在一次复现结束后直接修改：

- `.codex/skills/*/SKILL.md`
- `.magnus/.blueprints/*`
- `paper_reproduction.workflow.yaml` 本身
- AGENTS.md

这是 Library Drift、Misevolution、Safety Drift 的直接入口。一次失败不等于通用规律，一次成功也不等于可复用技能。

**为什么是治理基础**

如果这个不改，后面所有 skill lifecycle、replay、verifier 都没有意义——因为错误经验已经直接进入长期工件了。

**建议**

拆成证据门控流程：

```text
collect_capsules
→ cluster_failures
→ synthesize_candidate_patch
→ critic_verdict
→ schema_validation
→ deterministic_verifiers
→ replay_gate
→ supervisor/human_gate
→ accept / quarantine / reject
```

默认策略：

```text
低风险 run note → 可自动写
普通经验 → candidate，不自动 active
长期 SKILL/workflow/AGENTS/blueprint → 必须 gate
高风险规则 → 必须人工确认
```

**优先级**：最高。现在不改，所有自迭代都通往退化。

---

### 5. workflow schema 缺少治理字段

**问题**

当前 `workflow_schema.yaml` 只记录拓扑、指令、产物、分支、重试。无法表达风险级别、verifier、stop condition、skill 加载、memory 加载、provenance、uncertainty、template 契约、tool chain 策略。

**为什么是治理基础**

schema 是系统描述能力的上限。schema 不能表达的东西，workflow 就无法约束。如果 schema 没有这些字段，后面所有节点都无法携带治理信息。

**建议**

新增字段（按必要性排序）：

```yaml
# 第一批：必须立刻加
risk_level: low | medium | high
verifiers:
  - name: string
    command: string
    required: true
stop_conditions: []
artifact_write_policy: proposal_only | auto_write | human_gate
loads_skills:
  allowed: []
  forbidden: []
  allow_none: true

# 第二批：实现 run manifest 时加
provenance:
  required_artifacts: []
  answer_must_cite_artifact_ids: true

# 第三批：实现 uncertainty routing 时加
uncertainty:
  action_confidence: low | medium | high
  request_uncertainty: low | medium | high
  missing_fields: []

# 第四批：实现 template library 时加
template_contract:
  slots: []
  fixed_assumptions: []
  does_not_apply_when: []

# 第五批：实现 export gate 时加
tool_chain_policy:
  taint_tracking: true
  export_whitelist_required: true
```

**优先级**：最高。先改 schema，后改 workflow。

---

## 第三层：可审计性

> 这一层决定能否验证任何"改进"。不解决，所有 pass rate 变化都不可归因。

### 6. 没有 provenance / run manifest

**问题**

run 只记录最终产物，不记录 workflow 版本、skill 版本、memory ID、模型参数、工具版本、container digest。后续"变好了"无法归因——可能是模型换了，可能是 skill 改了，可能是 memory 检索返回了不同条目，可能是 COMSOL 镜像变了。

**为什么是可审计性问题**

没有 provenance，自迭代的"改进"就是黑箱。你无法回答：

```text
这次 pass rate 上升，是因为 workflow 变好，还是因为模型更新了？
```

**建议**

每次 run 生成 `run_manifest.yaml`：

```yaml
run_id:
workflow_version:
case_workflow_hash:
agents_policy_hash:
skill_versions: []
loaded_memories: []
model:
inference_params:
tool_versions: []
container_or_runtime_digest:
artifacts:
  - path:
    hash:
    producer_node:
    taint:
      private_source: true|false
      license_or_secret_adjacent: true|false
human_interventions: []
cost:
retry_count:
failure_taxonomy: []
```

provenance 回答须引用 artifact ID，无记录时必须返回 `unknown`，不能补全。

**优先级**：高。必须实现后才能声称任何"改进"。

---

### 7. 没有 attempt capsule

**问题**

节点日志适合人读，但无法统计某条经验到底有用还是有害。无法回答"这条 skill 在哪些 case 里 helped，在哪些里 hurt"。

**为什么是可审计性问题**

skill 生命周期、critic verdict、自迭代的证据门控，都依赖 attempt capsule。没有它，就无法做 evidence-driven 的 skill promotion/deprecation。

**建议**

每节点执行生成 `attempt_capsule`：

```yaml
run_id:
case_id:
node_id:
task_type:
selected_skills: []
selected_memories: []
commands_run: []
artifacts_read: []
artifacts_written: []
verifier_results: []
uncertainty:
  action_confidence:
  request_uncertainty:
  missing_fields: []
outcome: pass | fail | blocked | surrogate | diagnostic
failure_type:
human_intervention:
```

再加 `critic_verdict`：

```yaml
capsule_id:
attribution: helped | hurt | neutral | inapplicable
failure_pattern:
evidence:
confidence: low | medium | high
```

**优先级**：高。影响 skill 生命周期和自迭代治理。

---

### 8. 没有 replay suite

**问题**

优化一个新任务后，旧任务可能退化而无感知。这是 Forgetting 论文核心警告。

**为什么是可审计性问题**

没有 replay，任何长期修改都无法验证"没有破坏旧能力"。自迭代会变成"改了就改了"，无法回滚判断。

**建议**

初始 replay suite：

```text
replay_mie_simple
replay_mie_lspr
replay_comsol_smoke_or_blocked
replay_report_boundary
replay_workflow_schema
```

接受条件：

```text
当前任务有净收益
且 replay 无关键退化（PASS→FAIL count ≤ threshold）
且成本不显著上升
且安全/隐私规则未削弱
```

**优先级**：高。影响长期 skill/workflow 修改的安全性。

---

## 第四层：判断与路由

> 这一层决定系统能否在不确定时正确行为。不解决，系统会在缺参时继续猜、在错误问题上继续算。

### 9. 没有 uncertainty routing

**问题**

agent 给出一个笼统 confidence，把"任务欠指定"和"执行不确定"混在一起。缺材料常数、边界条件、GUI-exported COMSOL 模板时仍 attempt/retry/debug。

**为什么是判断路由问题**

论文复现最常见的问题不是"代码写错了"，而是"参数缺失/物理假设不明"。如果系统把缺参当作 debug 问题处理，就会陷入无效 retry。

**建议**

每个计划/检查节点区分：

```text
action_confidence：对执行路径的置信度
request_uncertainty：任务/输入欠指定程度
```

`request_uncertainty=high` 时不进入 debug/retry/self-modify，进入 `clarification` 或 `blocked`。

**优先级**：高。架构上比较重要，但初期可设默认值。

---

### 10. 没有 physics_formalization 节点

**问题**

从论文 prose 直接进入 Python/COMSOL 代码生成，不先结构化物理 spec。代码可运行、verifier 通过，但求解的不是论文里的物理问题。

**为什么是判断路由问题**

这是科学 agent 最容易犯的错：正确地解决错误问题。AI Scientist、AI-Researcher、Lang-PINN、Why LLMs Aren't Scientists Yet 都警告这一点。

**建议**

新增节点：

```yaml
physics_formalization:
  outputs:
    geometry:
    materials:
    equations:
    boundary_conditions:
    sources:
    solver:
    observables:
    assumptions:
    missing_fields:
```

所有代码/COMSOL 生成必须由此节点消费，不能从原始 prose 直接生成。

**优先级**：中高。初期可简化为 checklist 检查，不强制结构化。

---

### 11. skill 生命周期缺失

**问题**

skill 只有 Markdown 文本，没有 candidate/active/deprecated 状态、没有来源、没有适用边界、没有活性统计。经验只进不出，Library Drift 必然发生。

**为什么是判断路由问题**

skill router 需要知道哪些 skill 可信、哪些适用、哪些已过时。没有生命周期，router 无法做正确选择。

**建议**

每个 skill 需要：

1. 生命周期：`candidate | active | deprecated`（不硬删除）
2. 来源 capsule 链接
3. 适用/不适用边界：`applies_when` / `does_not_apply_when`
4. 活性统计：positive/negative cases、trial_count、contribution_score
5. active cap（最多 active 数）
6. promotion 规则：至少 2 个 case 帮助过，或人工确认
7. deprecation 规则：2 次被判定 hurt 或 inapplicable

**优先级**：高。对自迭代有用，但初期可以简化为手动检查。

---

## 第五层：安全与隔离

> 这一层决定系统能否防止私有数据外泄和外部内容劫持。

### 12. taint tracking 和导出门控缺失

**问题**

私有路径产物（private PDF、private run、license-adjacent、token-adjacent）被组合成公开报告后 export/commit。单步看似安全，链条危险：

```text
read private artifact → summarize → write public report → git push
```

**为什么是安全问题**

现有规则可能只限制单次文件读取或单次提交，但忽略跨 file/web/github/Magnus/shell 的组合副作用。

**建议**

1. artifact 携带 taint 状态：`private_source`、`license_or_secret_adjacent`、`public_export_allowed`、`source_paths`
2. public export / GitHub / long-term canonical write 前检查 taint
3. 禁止 auto-export 含 private/secret-adjacent 源的数据

**优先级**：中。重要，但初期可以人工检查。

---

### 13. 外部内容/搜索结果注入风险

**问题**

PDF 文本、网页、README、日志、搜索结果、工具输出可能包含指令式文本，绕过 AGENTS/workflow 规则。间接 prompt injection。

**为什么是安全问题**

被污染内容会在后续所有任务中持续注入，可能诱导自动修改 AGENTS、提交 Magnus 作业、读取 private 目录、错误报告物理复现状态。

**建议**

1. 所有外部/工具内容标记为 `untrusted_data`
2. 明确禁止 untrusted data 覆盖 system/AGENTS/workflow 规则
3. 搜索/网页内容不能直接导入可执行代码
4. 关键物理参数必须引用论文原文/官方文档

**优先级**：中。初期可书面约束，后续系统级。

---

### 14. 多 agent 独立审查退化

**问题**

加入 reviewer/expert agent 后可能出现 echoing、identity drift、共识放大错误。reviewer 只是复述 worker 的话，expert 被 supervisor framing 带偏。

**为什么是安全问题**

互评机制失去反驳能力，错误物理解释、缺参、过度声明会被多 agent 共识放大。

**建议**

1. 每轮交接要求声明：`role`、`object_to_check`、`forbidden_actions`、`required_evidence`、`confidence`
2. reviewer 必须读 artifact/verifier/output，不能只读 worker 输出
3. 对话超过固定轮数触发 identity drift 检查
4. 简单任务允许 `single_agent` / `direct_tool` 路径，不走完整编排

**优先级**：中。早期人工 review 为主，agent reviewer 可后续加。

---

## 第六层：经验治理

> 这一层决定 skill/memory/template/benchmark 自己会不会 drift。初期可以简化，正式实验前必须到位。

### 15. template reuse 边界缺失

**问题**

模板按语义相似度复用，可能带入旧论文的几何/材料/求解器/验收假设。复用前无 premise matching。

**建议**

每个模板包含：

```yaml
slots: []
fixed_assumptions: []
required_inputs: []
required_verifiers: []
does_not_apply_when: []
forbidden_reuse_conditions: []
```

复用前必须检查 premise matching，不只靠文本 embedding。

**优先级**：中。初期可人工判断。

---

### 16. memory type 混用污染推理

**问题**

fact、procedure、reflection、failed attempt、raw observation、reviewer feedback、policy 混在同一个检索池中。COMSOL 失败经验污染 Python-only Mie 任务。

**建议**

1. 区分 memory type：`fact`、`procedure`、`reflection`、`failed_attempt`、`raw_observation`、`reviewer_feedback`、`policy`
2. 节点声明允许哪些 type
3. 旧/冲突记忆必须有 supersession，不能共存为同等权威

**优先级**：中。长期治理项，初期可限制注入数量。

---

### 17. benchmark disclosure 不足

**问题**

只报告 pass rate，不披露 harness 版本、模型参数、失败分类、成本、人类介入，无法判断"变好"来自 workflow 还是环境变化。

**建议**

每个 benchmark run 记录：task version、workflow 版本、模型+推理参数、工具版本、container digest、cost、retry、human intervention、失败分类、replay regression、raw verifier outputs。

报告中区分：

```text
LLM evaluator pass
deterministic verifier pass
physical verifier pass
human domain-review pass
```

**优先级**：中。论文前期可以放宽，正式实验/投稿前必须。

---

## 第七层：远期治理

> 这一层在初期 scope 之外，但要在设计文档中预留位置。

### 18. graph memory 错误因果边固化

**问题**：自动 `caused_by` / `mitigated_by` 边把相关当因果，形成持久 debug bias。

**建议**：graph 边需要 `edge_type` / `weight` / `evidence` / `confidence`；自动边默认低权重；报告区分 observed correlation 和 verified cause。

**优先级**：远期。

---

### 19. LLM emulated sandbox 过信任

**问题**：模拟/伪造环境通过安全检查，真实 COMSOL/Magnus/license/filesystem 行为不同。

**建议**：报告区分 `emulated pass < dry-run pass < real sandbox pass < real execution pass`。高风险动作必须真实 dry-run 或 human gate。

**优先级**：远期。

---

## 按重要性排序的实施顺序

```text
第一步：方向锁定（不做工程，只做决策）
  ├── 确认核心卖点 = 垂域可验证效果，不是 agent 框架
  ├── 确认拆分原则 = 只有智能介入断点才拆 agent
  └── 确认评估方法 = baseline A/B/C/D 对比

第二步：治理基础
  ├── 扩展 workflow_schema.yaml（第一批字段）
  └── update_artifacts → propose_artifact_patch + gate

第三步：可审计性
  ├── run_manifest.yaml
  ├── attempt_capsule.yaml
  └── 最小 replay suite

第四步：判断路由
  ├── uncertainty routing（schema 字段 + 节点逻辑）
  ├── physics_formalization 节点（初期简版）
  └── skill 生命周期（candidate/active/deprecated）

第五步：安全
  ├── taint tracking + export whitelist
  ├── untrusted data 标记
  └── multi-agent 独立审查约束

第六步：经验治理
  ├── template_contract
  ├── memory type 分离
  └── benchmark disclosure

第七步：远期
  ├── graph memory 因果边治理
  └── emulated sandbox 分级
```

---

## 一句话总结

```text
现在的优先级不是让 workflow 更自动，
而是让 workflow 更难假进步，
并且只在真正需要智能判断的地方用 agent。
```
