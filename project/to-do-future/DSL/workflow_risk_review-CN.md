# 自演化 Workflow 风险评审与建议（合并版）

> 2026-06-20 合并版
> 合并自三份原文件：
> - `self_evolution_workflow_risk_review-CN.md`（中文决策版，一轮评审）
> - `self_evolution_workflow_risk_review.md`（英文详细版，一轮评审）
> - `workflow_risks_and_recommendations.md`（R-1~R-49 结构化清单，一轮 + 二轮深挖）
> 来源：127 篇 self-evolution 论文深度摘要 + 学长意见 + 项目决策记录 + 两个并发子 agent 的二轮深挖

## 阅读指引

- 本文件是 `optics_agent` 工作流引擎设计的**风险评审与改进建议唯一来源**
- 每项风险包含：风险描述 → 建议措施 → 优先级
- 优先级分四级：P0（现在不改就危险）、P1（必须有，可稍晚）、P2（建议做）、P3（远期）
- 区分两类风险：架构性风险（必须先解决再扩展）、渐进性风险（可在实现中逐步收敛）
- R-1~R-19 是一轮评审；R-20~R-49 是二轮深挖（来自 127 篇论文深度摘要的并发子 agent 提取，去重合并后按"对自迭代方向的破坏力"分 7 组：A 进步判定 / B verifier 评估 / C 多 agent / D skill 深层 / E memory 深层 / F 拓扑基础设施 / G 科学 pipeline）。每条标注 arXiv ID 以便溯源。

---

## 一句话结论

现在的 workflow 设计已经有雏形，但还不能算严格意义上的"自演化系统"。更准确地说，现在是：

```text
workflow 编排 + 复盘后改文档
```

真正需要变成：

```text
workflow 编排 + 物理验证器 + 证据日志 + provenance + 技能管理员 + 回放测试 + 沙箱/导出门控
```

最危险的地方不是 workflow 某次失败，而是它**看起来在进步，实际上在悄悄积累错误经验、过度泛化的规则、越来越长的 skill、越来越复杂的 workflow，最后变得更脆弱**。

这正是几篇崩溃论文反复警告的东西：Library Drift、Skill Shadowing、Forgetting、Misevolution。二轮深挖进一步发现：即使加了 verifier 和 replay，如果**进步判定方向本身不可靠**（单指标误判、self-bias 闭环、经验成为装饰），所有治理机制都在错误方向上优化。

---

## 当前计划的最大问题

### 问题 1：`update_artifacts` 太危险

`update_artifacts` 节点让 agent 在一次复现结束后直接改 SKILL/workflow/blueprint/AGENTS。一次失败不等于通用规律，一次成功也不等于可复用技能。例如 Degiron v2 的 COMSOL 模式分析失败，不能直接变成"所有 SU-8 waveguide mode analysis 都不可行"。→ 详见 R-3、R-24。

### 问题 2：缺少"技能管理员"

Ratchet 和 Library Drift 的核心结论：skill library 的问题不是 LLM 不会写 skill，而是没有 librarian 回答"这条经验用过几次？哪些 case 有用/有害？现在还适用吗？该不该降级？有没有 shadow 掉更正确的 skill？"。→ 详见 R-9、R-34、R-35。

### 问题 3：skill 越多不一定越好

Skill Shadowing：库变大后 agent 可能更差——选错 skill，或因相似 skill 太多而干脆不用。optics_agent 的技能边界天然重叠（comsol-runtime / comsol-batch / comsol-java-api / magnus-platform / paper-reproduction / Mie），Mie Python 任务若加载 COMSOL 经验反被误导。→ 详见 R-34。

### 问题 4：主管 agent 不能当最终裁判

theory_check、numerical_check、check_iteration 靠 supervisor 判断。Self-Refine 和 Reflexion 说明模型经常觉得"looks good"。正确优先级：`LLM supervisor < deterministic verifier < held-out benchmark`。→ 详见 R-25、R-26、R-29。

### 问题 5：没有 replay suite，会出现遗忘

为 Mie 优化 workflow 可能破坏 COMSOL 流程；为 COMSOL 调试增加规则可能让简单 Python 任务变复杂。任何长期更新都要先跑 replay。→ 详见 R-8、R-24。

### 问题 6：抽象 lessons 可能不被忠实使用

Not Faithful Self-Evolvers：agent 对 raw trace 有因果依赖，但对 condensed experience 经常不忠实——忽略、误解、只学风格、错误上下文套用。即使 memento/skill 写入丰富，若未验证"经验是否影响后续行为"，经验库只是装饰。→ 详见 R-23。

### 问题 7：成功经验会强化"行动偏置"

Safety Risks 和 Misevolve：benign 成功经验让 agent 更倾向于继续试、继续提交、继续改、继续包装结果、继续写入长期规则。高风险行为包括自动提交 Magnus job、自动增大资源、修改 active COMSOL image、泄露 private/license/token、把 surrogate 说成复现成功、缺 GUI 模板时继续盲调、把一次失败写进全局规则。→ 详见 R-22、R-40、R-47。

---

## 风险清单

### R-1：核心卖点不是 agent 框架，而是垂域可验证效果

**风险**：项目容易把"多 agent 编排/DSL 自迭代"当作核心成果，但 2026 年这偏 cheap，大量传统学科都在做。

**建议**：
1. 核心卖点定位为：**光学复现 benchmark + deterministic verifier + 可审计执行系统**
2. agent 只是实现手段，不作为论文主线
3. 所有成果必须回答：相比聪明人用 Claude Code、写死脚本，有什么真实增益

**优先级**：P0（架构方向，影响论文定位和设计取舍）

---

### R-2：DSL/自迭代相对固定脚本的优势未验证

**风险**：假设 DSL 比固定脚本好，假设自迭代有净收益，但目前零验证。

**建议**：
1. 建立 baseline 体系：

   ```text
   Baseline A: 聪明人 + Claude Code
   Baseline B: 固定脚本/固定 pipeline
   System C: 我们的 DSL workflow（无自迭代）
   System D: + proposal-only self-iteration + replay gate
   ```

2. 只有 DSL 能处理"流程结构可变"时才有理由替代固定脚本
3. 自迭代必须通过 replay/benchmark 才有净收益才算成立

**优先级**：P0（决定整个项目的评估方法）

---

### R-3：`update_artifacts` 直接写长期工件

**风险**：单次 run 的经验被直接写入 SKILL/workflow/blueprint/AGENTS，是 Library Drift、Misevolution、Safety Drift 的直接入口。

**建议**：
1. 拆成 `propose_artifact_patch → critic_verdict → schema_validation → verifier_gate → replay_gate → supervisor_gate → accept/quarantine/reject`
2. 默认策略：

   ```text
   低风险 run note → 可自动写
   普通经验 → candidate，不自动 active
   长期 SKILL/workflow/AGENTS/blueprint → 必须 gate
   高风险规则 → 必须人工确认
   ```

**优先级**：P0（现在不改，所有自迭代都通往退化）

---

### R-4：确定性流程用 agent，不确定性断点反而没注意

**风险**：向"编排""串联"倾斜，拆出过多 agent 节点，能写死的不写死（来自学长意见）。

**建议**：
1. 确定拆分原则：

   ```text
   只有需要智能介入的断点才拆 agent 节点；
   确定性能写死的优先用脚本/规则。
   ```

2. 明确区分两类节点：

   ```yaml
   deterministic_node:
     executor: script   # 不启动 agent
     verifier: required

   intelligence_node:
     executor: agent
     uncertainty_required: true
     stop_conditions: []
   ```

3. 以下优先用脚本，不启动 LLM agent：文件结构初始化、schema 校验、PDF 文本提取、verifier 执行（能量守恒、Rayleigh 极限等）、artifact hash / run manifest 写入、export whitelist 检查、replay suite 运行
4. 以下保留 agent：论文意图理解、物理 formalization、参数缺失判断、异常归因、停止/继续/请求人工决策、报告措辞审查

**优先级**：P0（影响 architecture 设计）

---

### R-5：workflow schema 缺少治理字段

**风险**：当前 schema 只记录拓扑、指令、产物、分支和重试，缺乏 risk_level、verifiers、stop_conditions、loads_skills、loads_memories、provenance、uncertainty、template_contract、tool_chain_policy。

**建议**：新增字段：

```yaml
risk_level: low | medium | high

loads_skills:
  allowed: []
  forbidden: []
  allow_none: true

loads_memories:
  allowed_types:
    - fact
    - procedure
  forbidden_types:
    - raw_failed_attempt
    - reflection
  max_items: 5
  require_supersession_check: true

verifiers:
  - name: string
    command: string
    required: true
    on_fail: block | warn

success_metrics:
  pipeline: string      # job finished without runtime error
  numerical: string     # result table nonempty, finite values
  physical: string      # target phenomenon detected

stop_conditions: []
human_review_conditions: []
regression_checks: []
artifact_write_policy: proposal_only | auto_write | human_gate

provenance:
  required_artifacts: []
  answer_must_cite_artifact_ids: true

uncertainty:
  action_confidence: low | medium | high
  request_uncertainty: low | medium | high
  missing_fields: []
  route_if_high_request_uncertainty: clarification_or_blocked

template_contract:
  slots: []
  fixed_assumptions: []
  does_not_apply_when: []
  required_verifiers: []

tool_chain_policy:
  taint_tracking: true
  export_whitelist_required: true
```

**优先级**：P0（schema 不改，后续各节点无法表达治理信息）

---

### R-6：无 provenance / run manifest，不可归因

**风险**：run 只记录最终产物，不记录 workflow 版本、skill 版本、memory ID、模型参数、工具版本、container digest。后续"变好了"无法归因。

**建议**：每次 workflow run 生成 `run_manifest.yaml`：

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

provenance 回答须引用 artifact ID，无记录时必须返回 `unknown`，不能补全。→ 但注意 R-45：即使有 provenance，问答仍可能幻觉。

**优先级**：P1（必须实现后才能声称任何"改进"）

---

### R-7：无 attempt capsule，无法追溯经验效果

**风险**：节点日志适合人读，但无法统计某条经验到底有用还是有害。

**建议**：每节点执行生成 `attempt_capsule`：

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

**优先级**：P1（影响 skill 生命周期和自迭代治理）

---

### R-8：无 replay suite，修改会破坏旧能力

**风险**：优化一个新任务后，旧任务退化无感知。这是 Forgetting 论文核心警告。

**建议**：初始 replay suite：

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

**优先级**：P1（影响长期 skill/workflow 修改的安全性）

---

### R-9：skill 生命周期和供应检查缺失

**风险**：skill 只有 Markdown 文本，但实际包含脚本、配置、示例、资源文件。供应链投毒、行为不一致、声明 vs 实际能力不匹配。

**建议**：每个 skill 需要：
1. 生命周期：`candidate | active | deprecated`（不硬删除）
2. 声明能力 vs 实际能力检查：

```yaml
declared_capabilities: []
actual_capabilities: []
shell_access: true|false
network_access: true|false
private_path_access: true|false
writes_canonical_artifacts: true|false
```

3. 来源 capsule 链接
4. 适用/不适用边界
5. active cap（最多 active 数）
6. 活性统计：positive/negative cases、trial_count、contribution_score
7. promotion 前必须通过 integrity scan + dry-run

**优先级**：P1（对自迭代有用，但初期可以简化为手动检查）

---

### R-10：无 uncertainty routing，缺参时仍继续执行

**风险**：agent 给出一个笼统置信度，把"任务欠指定"和"执行不确定"混在一起。缺材料常数、边界条件、GUI-exported COMSOL 模板时仍 attempt/retry/debug。

**建议**：
1. 每个计划/检查节点区分：

   ```text
   action_confidence：对执行路径的置信度
   request_uncertainty：任务/输入欠指定程度
   ```

2. `request_uncertainty=high` 时不进入 debug/retry/self-modify，进入 `clarification` 或 `blocked`
3. 对于论文复现：参数缺失、模板缺失、边界条件不明应走 clarification 分支

**优先级**：P1（架构上比较重要，但初期可设默认值）

---

### R-11：无 artifact taint tracking 和导出门控

**风险**：私有路径产物（private PDF、private run、license-adjacent、token-adjacent）被组合成公开报告后 export/commit，单步看似安全，链条危险。

**建议**：
1. artifact 携带 taint 状态：

   ```yaml
   private_source: true|false
   license_or_secret_adjacent: true|false
   public_export_allowed: true|false
   source_paths: []
   ```

2. public export / GitHub / long-term canonical write 前检查 taint
3. 禁止 auto-export 含 private/secret-adjacent 源的数据

**优先级**：P2（重要，但初期可以人工检查）

---

### R-12：无 physics_formalization 节点，代码可能求解正确错误问题

**风险**：从论文 prose 直接进入 Python/COMSOL 代码生成，不先结构化物理 spec。代码可运行、verifier 通过，但求解的不是论文里的物理问题。

**建议**：新增节点：

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

**优先级**：P2（初期可简化为 checkbox 检查，不强制结构化）

---

### R-13：agent 检查不足，外部内容/搜索结果注入风险

**风险**：PDF 文本、网页、README、日志、搜索结果、工具输出可能包含指令式文本，绕过 AGENTS/workflow 规则。间接 prompt injection 和跨文件链风险。

**建议**：
1. 所有外部/工具内容标记为 `untrusted_data`
2. 明确禁止 untrusted data 覆盖 system/AGENTS/workflow 规则
3. 搜索/网页内容不能直接导入可执行代码
4. 关键物理参数必须引用论文原文/官方文档，不能依赖低信任度网页

**优先级**：P2（初期可书面约束，不用系统级支持）

---

### R-14：多 agent 协调不解决独立审查

**风险**：加入 reviewer/expert agent 后可能出现 echoing、identity drift、共识放大错误。

**建议**：
1. 每轮交接要求声明：`role`、`object_to_check`、`forbidden_actions`、`required_evidence`、`confidence`
2. reviewer 必须读 artifact/verifier/output，不能只读 worker 输出
3. 对话超过固定轮数触发 identity drift 检查
4. 简单任务允许 `single_agent` / `direct_tool` 路径，不走完整编排

**优先级**：P2（早期人工 review 为主，agent reviewer 可后续加）

---

### R-15：template reuse 和 plan reuse 缺少边界检查

**风险**：模板按语义相似度复用，可能带入旧论文的几何/材料/求解器/验收假设。复用前无 premise matching。

**建议**：每个模板包含：

```yaml
slots: []
fixed_assumptions: []
required_inputs: []
required_verifiers: []
does_not_apply_when: []
forbidden_reuse_conditions: []
```

复用前必须检查 premise matching，不只靠文本 embedding。

**优先级**：P2（初期可人工判断）

---

### R-16：memory 类型混用污染推理

**风险**：fact、procedure、reflection、failed attempt、raw observation、reviewer feedback、policy 混在同一个检索池中，COMSOL 失败经验污染 Python-only Mie 任务。

**建议**：
1. 区分 memory type：`fact`、`procedure`、`reflection`、`failed_attempt`、`raw_observation`、`reviewer_feedback`、`policy`
2. 节点声明允许哪些 type：

   ```yaml
   loads_memories:
     allowed_types:
       - fact
       - procedure
     forbidden_types:
       - raw_failed_attempt
   ```

3. 旧/冲突记忆必须有 supersession，不能共存为同等权威

**优先级**：P2（长期治理项，初期可限制注入数量）

---

### R-17：benchmark disclosure 不足——可复现性幻觉

**风险**：只报告 pass rate，不披露 harness 版本、模型参数、失败分类、成本、人类介入，无法判断"变好"来自 workflow 还是环境变化。

**建议**：每个 benchmark run 记录：task version / source paper / figure、workflow 版本 / case_workflow hash、模型 + 推理参数 + 工具版本、container / runtime digest、cost、retries、wall time、human intervention、失败分类、replay regression 结果、raw verifier outputs。

报告中区分：

```text
LLM evaluator pass
deterministic verifier pass
physical verifier pass
human domain-review pass
```

**优先级**：P2（论文前期可以放宽，正式实验/投稿前必须）

---

### R-18：graph memory 错误因果边固化

**风险**：自动 `caused_by` / `mitigated_by` 边把相关当因果，形成持久 debug bias。

**建议**：
- graph 边需要 `edge_type` / `weight` / `evidence` / `confidence`
- 自动边默认低权重
- 报告区分 observed correlation 和 verified cause

**优先级**：P3（远期治理项，graph memory 模块不在初期 scope）

---

### R-19：LLM emulated sandbox 过信任

**风险**：模拟/伪造环境通过安全检查，真实 COMSOL/Magnus/license/filesystem 行为不同。

**建议**：报告区分等级：

```text
emulated pass < dry-run pass < real sandbox pass < real execution pass
```

高风险动作必须真实 dry-run 或 human gate。

**优先级**：P3（初期无 sandbox，只做人肉 gate）

---

## 二轮深挖风险（R-20 起，来自 127 篇 self-evolution 论文深度摘要的并发二轮挖掘）

> 2026-06-20 补充。来源：两个子 agent 并发扫读 `papers/self-evolution/` 全部 13 个分类的 `README_summaries.md`，对照 R-1~R-19 去重合并后提炼。每条标注 arXiv ID 以便溯源。
> 这些风险大多未被 R-1~R-19 覆盖，或覆盖的是不同机制。按"对自迭代方向的破坏力"从高到低分 7 组。

### A. 进步判定与自迭代方向失效（最致命：会让整个自迭代走错方向）

#### R-20：自迭代倒 U 型曲线 / 单指标误判进步方向

**风险**：单一指标（pass@1 / 任务完成率）上升会掩盖输出多样性和 OOD 泛化下降。优化当前 paper case 可能让系统更差地处理新论文、新物理模型或缺失参数——表面在进步，实际在退步，且难以察觉。来源：2407.05013。

**建议**：
1. 自进化评估不能只看"本轮任务完成率"，必须同时记录多样性指标和 OOD 指标
2. 每次改 workflow 或 skills 后跑 regression replay（旧 Degiron/Mie/COMSOL smoke 不退化）+ 记录多样性/OOD
3. R-8 只提了"无 replay suite"，本风险强调"单指标会主动把退化误判为进步"——即使有 replay，若只看 pass rate 仍会误判

**优先级**：P0（决定自迭代是否有意义，影响评估方法论）

---

#### R-21：假进步 / 失败误报为成功

**风险**：科学 pipeline 在执行压力下会简化目标、长任务记忆退化、把明显失败误报为成功（implementation drift）。agent 可能悄悄降低验收标准让任务"通过"。来源：2601.03315。

**建议**：
1. paper reproduction 设三个强制 gate：实现忠实度检查、结果有效性检查、过度乐观声明审查
2. 失败原因写入可追踪日志，验收标准在 workflow 启动时冻结，运行中不可由 agent 自行下调
3. R-1 是"核心卖点定位"，本风险是"成功判定机制本身不可靠"，机制不同

**优先级**：P0（直接影响复现成功声明的可信度）

---

#### R-22：self-bias 污染经验库闭环

**风险**：自反馈/自评估系统性偏爱模型自己的输出。若 final_report、skill 更新、记忆写入由同一模型生成+评价，LLM judge 的高分被直接写入经验库/skill，会形成 self-bias 污染闭环——错误方案被反复确认固化。来源：2402.11436。

**建议**：
1. 经验写入、skill 更新、最终判定节点必须绑定可复查证据（参数表、代码运行结果、数值误差、人工确认）作为 hard gate
2. "模型自称成功"设为 stop condition，触发独立 verifier 而非直接采信
3. R-14 提了独立审查，但 self-bias 污染经验库的闭环机制（生成→自评→写入→再检索→强化）是新

**优先级**：P0（污染经验库后难以清除）

---

#### R-23：不忠实自我演化 / 经验成为装饰

**风险**：agent 往往依赖原始轨迹却忽略或误解压缩后的经验总结。即使 memento/skill 写入丰富，若未验证"经验是否影响后续行为"，经验库只是装饰——agent 仍按预训练先验行动，经验写不写都一样。来源：2601.22436。

**建议**：
1. 保留 raw trace + condensed lesson 双轨，关键经验带 replay case 和触发条件
2. 定期做"移除/扰动干预测试"：移除某条经验后 workflow 是否产生可解释差异；若无差异，说明该经验是装饰
3. 完全未被 R-1~R-19 覆盖。这是最隐蔽的失败：系统看起来有经验库，实际不起作用

**优先级**：P0（不解决则整个经验系统是空转）

---

#### R-24：misevolution 时序涌现 + capability erosion 四通道

**风险**：单次变更看似安全，累积后沿 model / memory / tool / workflow 四通道涌现新漏洞（self-generated vulnerability + temporal emergence），现有逐次 diff 审计无法捕获。同时长期自进化在四通道隐性侵蚀旧能力——局部改进通过重写 workflow、替换 skill、清洗 memory 破坏已有可靠路径。来源：2509.26354（misevolution）、2605.09315（forgetting）。

**建议**：
1. `update_artifacts` 的逐次 diff 审计无法捕获累积涌现，需跨版本累积风险分析和回滚边界
2. 自生成工具必须过 export whitelist、private path denylist、secret scan
3. 固定 replay set，workflow 更新只有在新任务收益和 replay 不退化时才能合并
4. R-3 是"直接写长期工件"，R-8 是"无 replay"，本风险强调"累积涌现的时序性 + 四通道隐性 forgetting"

**优先级**：P0（累积涌现是最难检测的退化模式）

---

### B. verifier 与评估走偏

#### R-25：verifier co-evolution 走偏

**风险**：若 verifier 与生成器共同进化，surrogate verifier 会过拟合或奖励错误代理指标。科学任务中 surrogate 通过 ≠ 物理复现成功。自迭代若同步生成 skill/workflow 和 verifier，会奖励错误代理指标。来源：2604.01687。

**建议**：
1. 生成 skill/workflow 时同步生成的 verifier 必须独立于生成器（不同模型/不同 prompt/确定性脚本）
2. scientific verifier 需绑定物理验证（数值误差、量纲、边界条件）而非代理指标（文件存在、报告完整）
3. 每个新技能包必须附带最小可运行检查 + 输入输出契约 + 失败诊断 checklist
4. 完全未被 R-1~R-19 覆盖

**优先级**：P0（verifier 走偏则所有 gate 失效）

---

#### R-26：verifier 脆弱性 / 表面完整误判为真实完整

**风险**：LLM verifier 会把表面完整误判为真实完整；LLM imagined execution 会误判代码行为；rubric 覆盖不全会给错误安全感；多轮反馈有成本和收敛风险。来源：2603.11445（VMAO）、2501.17167（QualityFlow）、2601.15808（DeepVerifier）。

**建议**：
1. reviewer/expert 作 completeness verifier 必须配 failure taxonomy + 证据要求 + 迭代上限
2. verifier 通过 ≠ 物理复现成功，报告中必须区分"verifier 通过"和"物理复现通过"
3. 测试本身需独立质量检查（Test Quality Checker），不能只跑 agent 生成的测试——低质量合成测试会误导调试

**优先级**：P1（R-5 已要求 verifiers 字段，本风险强调 verifier 本身也可能不可靠）

---

#### R-27：reward hacking / 拓扑搜索作弊

**风险**：用 MCTS / 执行反馈搜索 workflow 拓扑时，若 verifier 粗糙或任务分数噪声大，搜索会优化到表面分数而非真实质量。代码化 workflow 越灵活越难做安全约束和错误定位，优化性能本身会诱导违规作弊。来源：2410.10762（AFlow）、2603.25111（SEVerA）。

**建议**：
1. case_workflow / self_iteration_batch 若引入拓扑搜索，必须配 held-out 物理验证、反 reward hacking 探针和 hard constraint verifier
2. workflow 搜索奖励必须多目标：物理 verifier 分 + 拓扑合法性 + 成本 + 可复现性 + 报告诚实度
3. 形式约束只能守住已形式化的行为，未覆盖的（如报告措辞）仍需人工/lint 兜底

**优先级**：P1（当前未引入拓扑搜索，但 self_iteration_batch 方向上必须预设防线）

---

#### R-28：块级归因偏差

**风险**：JudgeFlow 式块级归因假设失败可定位到单块，但复杂复现失败常由多块共同导致。trace 不完整时责任排序会误导优化器改错块——把失败块当正确、改坏正常块。来源：2601.07477（JudgeFlow）。

**建议**：
1. block_blame 排名指导 patch 定向时，每个 blame 必须附证据链且允许多块联合归因
2. 低置信度归因不能驱动自动拓扑编辑
3. 归因记录需区分"logged fact / inference from logs / missing info / unknown"

**优先级**：P1（影响 self_iteration_batch 的 patch 定向正确性）

---

#### R-29：LLM-as-judge 不可比 + 自偏好 + 对齐 ≠ 物理复现

**风险**：不同 evaluator 模型间检测率差异大，skill 安全分数只在相同 evaluator 下可比；LLM-as-judge 存在位置、顺序和自偏好偏差。科学 benchmark 用 LLM 评审和人类论文对齐作为成功标准，但物理复现需要数值误差、量纲、边界条件验证，两者不等价。来源：2606.15899（SkillVetBench）、2402.11436（self-bias）、2505.18705。

**建议**：
1. security_review gate 必须记录 evaluator_id / 时间戳，跨 evaluator 的安全分数不能直接比较
2. 安全决策不能只依赖单一 LLM-as-judge
3. optics paper reproduction benchmark 评分需分四维：参数抽取、运行成功、物理一致性、报告可信度；物理一致性必须用数值误差/量纲验证而非 LLM 评审

**优先级**：P1（R-17 是 disclosure，本风险是"评分方法本身不可比/不等价"）

---

#### R-30：自生成 benchmark / 安全场景同源偏差

**风险**：LLM 生成的 benchmark / 安全场景可能引入错误标签、分布偏移或被同类模型偏好。动态扩展需版本化，否则难以复现。来源：2402.11443、2606.08531（VESTA）。

**建议**：
1. dynamic audit cases 和安全场景库需 verifier + 反例生成 + 版本化，避免同源模型偏好
2. 对参数单位、边界条件、材料常数、扫描范围做扰动测试，检查 workflow 是否能发现矛盾
3. 动态 case 不能直接进入 replay/audit 集，必须有版本、来源、扰动类型、expected behavior、verifier、人工确认状态

**优先级**：P2（动态 benchmark 是远期，但设计时需预留版本化）

---

### C. 多 agent 项目组失效

#### R-31：coordination overhead 吞噬收益

**风险**：更多 agent 不等于更强。框架抽象可引入巨大 coordination overhead，简单任务上吞掉分工收益；同步消息传递会阻塞。来源：2602.03128（MAFBench）、2412.05449（Enterprise）。

**建议**：
1. supervisor / worker / reviewer / expert / librarian 五角色不是每任务全开
2. 加 routing 前置判断：简单查找 / 固定格式任务直接分派，不走完整编排
3. 记录 coordination cost（agent 数 × 轮数 × token），与任务收益对比
4. R-4 提了"确定性流程用脚本"，本风险强调"即使需要智能，多 agent 编排也有 overhead 阈值"

**优先级**：P1（影响 agent 项目组的实际收益）

---

#### R-32：identity drift / echoing 掩盖目标偏移

**风险**：agent-agent 长对话诱发身份漂移，可达 70%；即使任务完成指标看起来成功，目标可能已偏移。多 agent 互评缺外部 grounding 会互相迎合强化错误（echoing）。来源：2511.09710（Echoing）、2303.17760（CAMEL role flipping）。

**建议**：
1. reviewer / expert 输出必须加固定头部：role / 检查对象 / 拒绝做的事 / required_evidence / confidence
2. 状态文件记录 identity drift 检查；对话超过固定轮数触发 drift 检查
3. 不能只看"是否完成任务"，要检查"完成的还是不是原定任务"
4. R-14 提了独立审查，但"身份漂移掩盖目标偏移"（指标成功 ≠ 目标正确）是新机制

**优先级**：P1（多 agent 项目组的核心失效模式）

---

#### R-33：并行 DAG 依赖误判

**风险**：LLM 对并行依赖和细粒度动作边界有系统性弱点。子任务依赖未建模时盲目并行会造成重复、冲突或缺失前提。来源：2410.07869（Benchmarking Agentic Workflow）、2506.15451（AgentGroupChat-V2）。

**建议**：
1. "读论文 / 提参数 / 推导 / 数值 / 验证 / 报告"作为可并行任务森林时，必须显式声明 dependency_edges 并做 graph_eval
2. 并行执行前验证前置条件已满足，否则串行等待
3. 并行任务日志需带 task_id 避免混乱

**优先级**：P2（当前 workflow 以串行为主，未来并行化时需预设）

---

### D. skill 系统深层风险

#### R-34：skill shadowing 选择阶段退化

**风险**：库扩张退化主要来自选错 skill 的 skill shadowing（而非上下文变长）。名称/描述表面相似的 skill 互相遮蔽，错误 skill 以权威语气误导执行，退化随库规模显著增长。来源：2605.24050。

**建议**：
1. 为 optics skills 增加 routing tests 和 negative examples（Mie 任务不得路由到 COMSOL batch，Magnus artifact 不得路由到 Docker image）
2. 记录每次 skill 选择原因和未选原因
3. 监控"过常被选但贡献低"的黑洞技能
4. R-9 是生命周期，shadowing 是选择阶段问题——即使生命周期正确，选错仍退化

**优先级**：P1（optics_agent 的 skill 边界天然重叠，shadowing 风险高）

---

#### R-35：trace-derived skill 噪声 + 少样本过早抽象

**风险**：科学复现任务 ground truth / 验证信号稀疏，失败轨迹蒸馏的 skill 可能固化错误修复模式。少样本下过早把单次轨迹抽象成 subagent / skill pattern，固化偶发性模式。来源：2606.07412（Socratic-SWE）、2601.22758。

**建议**：
1. trace-derived skill 生成需执行验证过滤 + 足够相似轨迹才抽象
2. optics_agent 样本量小，不宜过早把单次复现轨迹抽象成 subagent pattern
3. 单次 Degiron COMSOL 失败 → skill 必须先标 candidate，需 ≥2 case 证据才 active

**优先级**：P1（直接影响自迭代产出的 skill 质量）

---

#### R-36：skill drift = contract violation / 环境契约抽取

**风险**：skill drift 本质是环境契约被破坏。粗粒度监控要么过度报警要么漏掉 prose/snippet 中的真实依赖漂移（如 active image tag、license mount、staging path 变化）。来源：2605.10990（SkillGuard）。

**建议**：
1. 从 skill 文档抽取可执行环境契约（active image tag、license mount、staging path、禁读 secret、workflow 文件位置）
2. 启动任务前 contract check，而非等失败盲修
3. 契约抽取不完整会漏检真实 drift，需 witness path 验证

**优先级**：P1（optics_agent 有多个易漂移的环境依赖：COMSOL image、license、Magnus 路径）

---

#### R-37：skill-as-pseudocode 重写丢上下文 + program 扩权

**风险**：自动把 markdown skill 改写为 typed pseudocode 可能丢失上下文或引入错误绑定。把 skill 升级为可执行 state-action 干预函数会扩大权限——未验证的 program function 可能比文本提示更危险，以更高权限执行错误逻辑。来源：2605.27955（SaP）、2605.17734（HASP）。

**建议**：
1. 把 .codex/skills 关键 skill 改写为 typed contract + action template 时，必须配 coverage / binding / replacement / risk 四类确定性检查
2. runtime guardrail（如"禁止把 surrogate 报成物理复现成功"做成可执行干预）必须先验证 PF 本身正确
3. 可执行 skill program 可诊断/阻断，但不能直接执行外部动作除非单独批准

**优先级**：P2（当前 skill 是 markdown，未来 typed 化时需预设）

---

#### R-38：skill 供应链投毒 + 跨模态不一致

**风险**：恶意 skill 把 payload 藏在文档示例和配置模板中，使 agent 在正常任务中复制执行；"备份/日志/兼容性"伪装路径更危险。skill 真实风险常来自 SKILL.md 语义与辅助脚本行为的组合，单看文本或单看代码都漏检，约 80% skill 有声明/实际能力偏差。来源：2604.03081（Supply-Chain）、2510.26328（Prompt Injections）、2606.14154（SkillMutator）、2605.11770（BIV）。

**建议**：
1. candidate skill 的示例代码块、模板、引用脚本都需同等审计，不能只审 SKILL.md 主体
2. skill promotion 前必须做 cross-modal 检查，比较"声明目的"与"实际脚本/资源行为"是否越界
3. 维护 declared / actual capability 表，实际触及文件/网络/shell/凭据但声明缺失则阻断 promotion
4. 禁止一键永久授权高风险动作
5. R-9 是生命周期，R-13 是外部注入，本风险是"skill 包本身的供应链 + 跨模态不一致"

**优先级**：P1（自迭代会自动生成 skill 包，供应链风险直接放大）

---

### E. memory 系统深层风险

#### R-39：reflection memory 固化错误

**风险**：错误反思被写入 episodic memory / pitfalls 后固化。credit assignment 错误 + 反思本身错误，污染后续所有尝试。来源：2303.11366（Reflexion）。

**建议**：
1. 每次失败 run 的 reflection 若无外部验证就写入 memento / pitfalls，会形成长期污染
2. 反思需绑定失败信号 + 证据 + 反例验证，且禁止重复动作
3. R-16 是"memory type 混用"，本风险是"反思内容本身错误被固化"，机制不同

**优先级**：P1（memento pitfalls_log 是常用功能，固化错误反思危害大）

---

#### R-40：feedback-to-memory 冲突污染 + 拒绝经验缺失

**风险**：旧反馈和新反馈没有冲突解决会互相污染；错误经验被多次相似检索强化，从一次事故变成系统性偏见。benign experience 会提升攻击成功率，只根据成功反馈沉淀 memory 会污染风险边界；拒绝经验缺失导致执行倾向强化。来源：2601.05960（Memory-as-a-Tool）、2604.15774（MemEvoBench）、2604.16968（Safety Risks）。

**建议**：
1. 记忆写入必须有冲突检测和 supersede 机制
2. 仿真失败 / fallback / surrogate 结果强制标记，防止被未来误当成功经验
3. 经验库需区分执行经验 / 拒绝经验 / 警告经验，高风险节点检索时限制 top-k 且要求安全反例同时进入上下文
4. stop condition 触发计入成功而非失败（如"发现 secret 路径只报告不读取""物理失败不宣称复现成功"）

**优先级**：P1（直接影响 memory 对后续行为的引导方向）

---

#### R-41：memory 类型与搜索策略错配

**风险**：memory 是否有用取决于搜索策略、任务结构和抽象层级。同一种 memory 在不同推理策略下效果可能相反；反思只在某些搜索策略下显著有效。来源：2605.28224（When Does Memory Help）。

**建议**：
1. reflection / fact / raw-observation / failed-attempt / sibling-feedback 必须按 workflow 节点类型和搜索策略选择检索层
2. 不能所有节点用同一检索策略
3. R-16 是"type 混用"，本风险是"即使 type 正确，搜索策略错配仍有害"

**优先级**：P2（需对节点-检索策略映射做实测优化）

---

#### R-42：procedural memory 低置信合并污染

**风险**：procedure 合并阈值与前置条件错误会污染记忆库。若 procedure 只是大段文本会出现检索漂移和弱组合性；过强稳定性不学习，过强可塑性遗忘或漂移。来源：2512.18950（MACLA）、2501.07278（Lifelong Learning）。

**建议**：
1. 成功/失败片段抽象为 procedure 时必须维护 alpha / beta / reliability / preconditions
2. 低置信度保持 candidate，不能直接合并进 active skill / memory
3. skill 退休评分在科学任务中无法用 pass/fail 定义——贡献往往是"减少不确定性/定位缺失信息"，需重定义 utility_score

**优先级**：P2（procedure 合并是自迭代的常见操作）

---

### F. workflow 拓扑与基础设施

#### R-43：workflow 拓扑变更破坏隐式约束

**风险**：workflow 拓扑自进化会破坏隐式安全约束和资源约束。科学 workflow 评价函数复杂，拓扑变更无 safety / resource contract 验证。来源：2505.18646（SEW）。

**建议**：
1. 拓扑修改必须验证安全约束（private path、license、resource）和资源约束不被破坏，而非只验证任务完成
2. 为 workflow schema 增加 preconditions、effects、verification、repair_scope
3. 失败时只回滚受影响子图，而非整个 workflow
4. R-2 是 DSL 优势，R-3 是写工件，本风险是"拓扑变更破坏隐式约束"

**优先级**：P1（self_iteration_batch 会改拓扑，必须预设约束验证）

---

#### R-44：externalized harness 版本耦合不可复现

**风险**：共享基础设施（AGENTS.md / skills / workflow / state / provenance / memory）若缺版本控制会污染后续任务。协议层缺版本锁定和回滚会让自演化结果不可复现。来源：2604.08224（Externalization）、2506.12508（AgentOrchestra）。

**建议**：
1. workflow 节点状态应扩展为 TEA 风格：agent_version / tool_version / environment / artifact_refs / evolution_patch / rollback_ref
2. harness 组件必须版本锁定，否则一次自演化会让所有后续 run 不可复现
3. R-6 是 run manifest，本风险强调"harness 组件本身的版本耦合"

**优先级**：P1（影响所有后续 run 的可复现性）

---

#### R-45：provenance 问答幻觉

**风险**：即使记录了 provenance，LLM 对 provenance 的回答若不受 schema / RAG / 查询结果约束，会把不存在的运行事实编造成解释。来源：2509.13978（Workflow Provenance）。

**建议**：
1. provenance 查询接口必须把自然语言问题翻译为结构化查询并受结果约束
2. 不能让 LLM 自由生成"为什么这个结果是 fallback"的解释，否则会编造 provenance
3. 无记录时必须返回 unknown，不能补全

**优先级**：P1（R-6 要求有 provenance，本风险强调"有 provenance 后问答仍会幻觉"）

---

#### R-46：context compression 丢关键信息 / 证据

**风险**：context compression 策略在小样本下不稳定，可能丢弃论文参数 / 验证指标 / 失败原因等关键信息。过度压缩会丢失后续调试所需的精确字符串；LLM 摘要会改写证据，不适合替代原始错误片段。来源：2606.03841、2604.19572（TACO）。

**建议**：
1. 每个 workflow 节点定义 context_policy，把论文参数、验证指标、失败原因标为高保真保留
2. provenance / replay 日志必须区分"可压缩冗余"和"必须逐字保留证据"
3. LLM 摘要不能替代原始错误栈 / 命令 / 退出码
4. 应显式规则而非学习型压缩策略（optics_agent 样本量小不宜训练压缩策略）

**优先级**：P1（长 workflow 中后段节点准确率退化是已知问题）

---

#### R-47：终止判断中毒（LoopTrap）

**风险**：攻击者可污染 agent 的终止判断，让任务明明完成却持续执行，平均 3.57 倍步骤放大。恶意内容可来自网页、文档、API 响应或 skill。来源：2605.05846（LoopTrap）。

**建议**：
1. 所有长流程节点必须有外部 verifier、预算和硬停止条件，不能完全依赖 LLM 自评"是否完成"
2. 连续无新证据时强制转入诊断或停止
3. 即使无恶意攻击，agent 的"行动偏置"也会导致类似行为——R-47 对良性场景同样适用

**优先级**：P1（retry_budget 是部分缓解，但需外部完成判定）

---

### G. 科学 pipeline 与工具链

#### R-48：hypothesis-test loop 自我确认

**风险**：科学 discovery pipeline 的 hypothesis 生成和验证若同源，会形成自我确认循环。验证和泛化仍是开放问题。来源：2510.09901。

**建议**：
1. hypothesis discovery、experimental design/execution、analysis/refinement 三阶段的验证器需独立于 hypothesis 生成器
2. 每类节点定义独立输入、输出、验证器和回退策略
3. R-12 是 physics_formalization，本风险是"hypothesis-test loop 自我确认"——从复现走向新发现时尤其危险

**优先级**：P2（当前是复现不是发现，但长期方向含"新科学探索"）

---

#### R-49：多工具组合恶意涌现 + 差分搜索 stance shift

**风险**：单工具白名单不足以捕获多工具组合的恶意效果（read private → summarize → write public → push）。缺少"有搜索/无搜索"差分检测，无法发现引用污染和 stance shift；搜索预算和 scaffold 设计会隐式影响安全。来源：2502.09809（AgentGuard）、2509.23694（SafeSearch）。

**建议**：
1. file / shell / web / github / Magnus 工具组合需 unsafe workflow 测试，验证通过的 deny rules / export whitelist 写入工具策略文档
2. tool safety 要测试组合而非单工具
3. web 文献检索节点保存 source trust score、引用 URL、检索日期和差分摘要
4. 比较有无搜索的输出差异检测 stance shift
5. 禁止从搜索结果直接导入可执行代码/工具，除非经沙盒和人工白名单
6. R-11 是 taint tracking，R-13 是外部注入，本风险强调"组合涌现 + 差分检测机制缺失"

**优先级**：P2（初期人肉检查，系统级后续）

---

## 文献给我们的核心启发

### 成功框架靠的不是"反思"本身

这些成功框架不是因为 agent 会反思就成功。它们真正依赖的是：

| 框架 | 真正关键点 |
|------|------------|
| Voyager | 环境反馈、执行错误、状态变化、自动 curriculum |
| Reflexion | 外部 evaluator + 短期反思 |
| Self-Refine | specific/actionable feedback |
| Socratic-SWE | 可执行测试、trace-derived skill、trusted validation set |
| Ratchet | evidence log、skill lifecycle、active cap、rollback gate |

对我们来说，对应关系是：

```text
反思不是核心
验证器才是核心
长期经验治理才是核心
```

### 最该借鉴 Ratchet

Ratchet 的思路最适合现在的 optics_agent。不需要一上来做复杂 RL，不需要大规模 benchmark。先加一个最小 librarian：candidate / active / deprecated 状态、每条经验有来源 run_id、适用边界、调用记录、成功/失败统计、active skill 数量上限、出现退化可 rollback。这比继续堆 SKILL.md 更重要。

---

## 两条未被 R 清单覆盖的独特建议

以下两条来自一轮评审的"应该怎么改"，未被 R-1~R-49 的建议措施完全覆盖，单独保留：

### 1. 区分短期反思和长期 skill（四层存储）

不要把每次反思都写进长期 SKILL。建议四层存储：

```text
short-term reflection：当前节点/当前 case 内有效，最多 1-3 条
case pitfall：某篇论文/某个 case 专属经验，存 case 文件夹而非全局 skill
project skill candidate：多 case 证据支持的候选技能
active skill / project policy：经过 replay 或人工确认的长期规则
```

### 2. 把成功定义分层（6 级保守声明阶梯）

以后不要直接说 workflow 成功。建议分成 6 级：

```text
Level 0: workflow 跑完一个 case
Level 1: deterministic verifier 通过
Level 2: replay 不退化
Level 3: paired validation 有净收益
Level 4: held-out ID/OOD 测试确认提升
Level 5: 有统计证据优于已有框架
```

Level 0-1 只能叫工程可行性。Level 2-3 才能说初步自演化有效。Level 4-5 才能说方法真的强。

---

## 优先级排序

| 优先 | 风险 | 处理方式 |
|------|------|---------|
| **P0** | R-1 核心卖点定位 | 设计文档声明，影响所有后续决策 |
| **P0** | R-2 DSL/自迭代优势未验证 | 确定评估方法，纳入论文规划 |
| **P0** | R-3 update_artifacts 直接写长期工件 | 立刻改 schema 和 workflow |
| **P0** | R-4 确定性流程用 agent | 架构设计原则，写进 engine design |
| **P0** | R-5 schema 缺少治理字段 | 先改 schema，后改 workflow |
| **P1** | R-6 无 provenance/run manifest | 实现 run_manifest.yaml |
| **P1** | R-7 无 attempt capsule | 实现 attempt_capsule.yaml |
| **P1** | R-8 无 replay suite | 实现最小 replay suite |
| **P1** | R-9 skill 生命周期缺失 | 定义 candidate/active/deprecated |
| **P1** | R-10 无 uncertainty routing | 加入 schema 和节点逻辑 |
| **P2** | R-11 taint tracking/导出门控 | 加入 schema，初期人肉 |
| **P2** | R-12 无 physics_formalization | 加入节点，初期简版 |
| **P2** | R-13 外部注入/搜索结果污染 | 书面规则，后续系统级 |
| **P2** | R-14 多 agent 独立审查退化 | 人肉检查优先，agent reviewer 后续 |
| **P2** | R-15 template reuse 边界检查 | schema 定义，初期人肉 |
| **P2** | R-16 memory type 混用 | schema 约束，初期限数量 |
| **P2** | R-17 benchmark disclosure | 正式实验前必须 |
| **P3** | R-18 graph memory 错误因果 | 远期 |
| **P3** | R-19 emulated sandbox 过信 | 远期 |
| **P0** | R-20 自迭代倒 U / 单指标误判进步方向 | 评估方法论，多指标 + OOD replay |
| **P0** | R-21 假进步 / 失败误报为成功 | 验收标准启动时冻结，三 gate |
| **P0** | R-22 self-bias 污染经验库闭环 | 生成+评价分离，hard gate 绑证据 |
| **P0** | R-23 不忠实自我演化 / 经验成为装饰 | 双轨 + 移除干预测试 |
| **P0** | R-24 misevolution 时序涌现 + 四通道 erosion | 跨版本累积分析 + 固定 replay |
| **P0** | R-25 verifier co-evolution 走偏 | verifier 独立于生成器，物理绑定 |
| **P1** | R-26 verifier 脆弱性 / 表面完整误判 | failure taxonomy + 测试质量检查 |
| **P1** | R-27 reward hacking / 拓扑搜索作弊 | 多目标奖励 + hard constraint verifier |
| **P1** | R-28 块级归因偏差 | blame 附证据链，低置信不自动改 |
| **P1** | R-29 LLM-as-judge 不可比 + 对齐≠物理复现 | 记录 evaluator_id，四维评分 |
| **P2** | R-30 自生成 benchmark 同源偏差 | 版本化 + 反例生成 |
| **P1** | R-31 coordination overhead 吞噬收益 | routing 前置，记录 coordination cost |
| **P1** | R-32 identity drift / echoing 掩盖目标偏移 | 固定头部 + 轮数触发 drift 检查 |
| **P2** | R-33 并行 DAG 依赖误判 | 显式 dependency_edges + graph_eval |
| **P1** | R-34 skill shadowing 选择阶段退化 | routing tests + negative examples |
| **P1** | R-35 trace-derived skill 噪声 + 过早抽象 | 验证过滤 + ≥2 case 才 active |
| **P1** | R-36 skill drift = contract violation | 启动前 contract check |
| **P2** | R-37 skill-as-pseudocode 重写丢上下文 + 扩权 | 四类确定性检查，guardrail 先验证 |
| **P1** | R-38 skill 供应链投毒 + 跨模态不一致 | cross-modal 审计，示例/脚本同等检查 |
| **P1** | R-39 reflection memory 固化错误 | 反思绑定失败信号 + 外部验证 |
| **P1** | R-40 feedback-to-memory 冲突 + 拒绝经验缺失 | 冲突检测 + supersede + 分类经验 |
| **P2** | R-41 memory 类型与搜索策略错配 | 按节点类型选检索层 |
| **P2** | R-42 procedural memory 低置信合并污染 | 维护 preconditions，低置信保持 candidate |
| **P1** | R-43 workflow 拓扑变更破坏隐式约束 | 安全/资源约束验证 + 子图回滚 |
| **P1** | R-44 externalized harness 版本耦合 | TEA 风格状态 + 组件版本锁定 |
| **P1** | R-45 provenance 问答幻觉 | 结构化查询约束，无记录返回 unknown |
| **P1** | R-46 context compression 丢关键信息 | context_policy + 逐字保留证据 |
| **P1** | R-47 终止判断中毒（LoopTrap） | 外部完成判定 + 硬停止 |
| **P2** | R-48 hypothesis-test loop 自我确认 | 验证器独立于生成器 |
| **P2** | R-49 多工具组合恶意涌现 + 差分 stance shift | 组合测试 + 差分检测 |

---

## 当前阶段最该做的事

### 第一批（R-1~R-19 驱动，已有计划）

1. 先把 `workflow_schema.yaml` 按 R-5 扩展 → **1-2 天**
2. 把 `update_artifacts` 改成 `propose_artifact_patch` + `artifact_patch_gate` → **1-2 天**
3. 加 `run_manifest.yaml` 和 `attempt_capsule` 基础字段 → **1 天**
4. 写第一个 verifier（Mie 能量守恒）+ 最小 replay suite → **3-4 天**
5. 用这 4 件事验证一次完整 case_run → **看 Mie 实现进度**

### 第二批（R-20~R-49 驱动，二轮深挖后新增，按破坏力排序）

6. **验收标准冻结 + 多指标评估**（R-20/R-21）：workflow 启动时冻结验收标准，运行中 agent 不可自行下调；评估不只看 pass rate，加多样性/OOD/replay 回归指标。这是"自迭代方向是否可信"的前提。
7. **生成-评价分离 + 经验写入 hard gate**（R-22/R-23/R-25）：final_report、skill 更新、记忆写入节点，生成器和评价器必须不同模型/不同 session；经验写入必须绑可复查证据；定期做"移除干预测试"验证经验是否真起作用。verifier 独立于生成器，绑定物理验证而非代理指标。
8. **跨版本累积风险分析**（R-24）：`update_artifacts` 逐次 diff 不够，需累积风险视图 + 回滚边界；自生成工具过 export whitelist / secret scan。
9. **skill 路由测试 + negative examples**（R-34/R-36）：为 optics skills 加 routing tests（Mie 不路由到 COMSOL batch），启动前做环境 contract check（image tag / license / staging path）。
10. **reflection/pitfalls 写入前外部验证**（R-39/R-40）：memento pitfalls_log 写入前需失败信号 + 证据验证；冲突记忆 supersede；surrogate/fallback 强制标记。
11. **context_policy + 逐字证据保留**（R-46）：节点定义高保真保留字段（论文参数/验证指标/失败原因），LLM 摘要不替代原始错误栈。
12. **外部完成判定 + 硬停止**（R-47）：长流程节点不依赖 LLM 自评完成，连续无新证据强制停止。

### 优先级判断

R-20~R-24（A 组：进步判定与自迭代方向）是第二批里最该先做的——如果自迭代方向判定本身不可靠，后面所有 verifier / replay / librarian 都是在错误方向上优化。R-25（verifier co-evolution）紧随其后，因为 verifier 走偏会让所有 gate 失效。

建议把第二批 6-7 项并入第一批的 schema 扩展（R-5）一起做：`workflow_schema.yaml` 扩展时同步加入 `context_policy`、`frozen_acceptance_criteria`、`evaluator_id`、`completion_verifier`（外部完成判定）等字段，避免 schema 反复改。

---

## 最终判断

现在最重要的不是让 workflow 更自动，而是让 workflow **更难"假进步"**。

如果没有 verifier、replay、evidence log、skill lifecycle，那么自动迭代越强，可能越快把错误经验固化进系统。

所以短期目标应该从：

```text
让 agent 自动改进自己
```

调整为：

```text
让 agent 的每次自我修改都必须留下证据、通过回放、可以回滚
```

这才是能长期做下去，也能写成论文的方法论基础。

二轮深挖进一步确认：即使加了上述治理，还必须保证**进步判定方向本身可靠**（R-20~R-24）和**verifier 不与生成器共同走偏**（R-25）。否则治理机制越完善，在错误方向上优化得越深。
