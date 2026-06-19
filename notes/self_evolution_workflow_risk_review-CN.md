# 自演化 Workflow 风险审计笔记

> 2026-06-19
> 这份中文版是给自己看的，不是论文综述。重点是：这些自演化 agent 论文对我们现在的 `optics_agent` workflow 计划有什么警告、哪些假设不可靠、下一步应该怎么改。

## 一句话结论

我们现在的 workflow 设计已经有雏形，但还不能算严格意义上的“自演化系统”。

更准确地说，现在是：

```text
workflow 编排 + 复盘后改文档
```

真正需要变成：

```text
workflow 编排 + 物理验证器 + 证据日志 + 技能管理员 + 回放测试 + 接受门控
```

最危险的地方不是 workflow 某次失败，而是它看起来在进步，实际上在悄悄积累错误经验、过度泛化的规则、越来越长的 skill、越来越复杂的 workflow，最后变得更脆弱。

这正是几篇崩溃论文反复警告的东西：Library Drift、Skill Shadowing、Forgetting、Misevolution。

## 读了哪些论文

### 崩溃和负结果论文

- `2605.19576` Library Drift
- `2605.24050` Skill Shadowing
- `2509.26354` Misevolve
- `2605.09315` Forgetting
- `2601.22436` Not Faithful Self-Evolvers
- `2604.16968` Safety Risks
- `2606.06114` Healthy Evolution / ANCHOR

### 正向框架论文

- `2606.07412` Socratic-SWE
- `2605.22148` Ratchet
- `2305.16291` Voyager
- `2303.11366` Reflexion
- `2303.17651` Self-Refine

### 评测和 benchmark 论文

- `2508.07407` Self-Evolving Agents Survey
- `2606.17546` SEAGym
- `2606.08106` PACE

## 我们当前计划最大的问题

### 问题 1：`update_artifacts` 太危险

现在 `paper_reproduction.workflow.yaml` 里的 `update_artifacts` 节点会让 agent 在一次复现结束后直接做这些事：

- 更新 `.codex/skills/*/SKILL.md`
- 更新 `.magnus/.blueprints/*`
- 更新 `paper_reproduction.workflow.yaml` 本身
- 把 lessons learned 追加进长期 skill

这个设计很自然，但从论文看，它是最大风险源。

原因很简单：一次失败不等于通用规律，一次成功也不等于可复用技能。

比如：

```text
Degiron v2 的 COMSOL 模式分析失败
```

这条经验是有价值的，但它不能直接变成：

```text
所有 SU-8 waveguide mode analysis 都不可行
```

也不能直接变成：

```text
以后遇到 matrix factorization 都这样调 shift
```

如果把这种单次经验直接写进长期 skill，后面就会污染新的任务。

### 问题 2：我们的设计缺少“技能管理员”

Ratchet 和 Library Drift 的核心结论是：skill library 的问题不是 LLM 不会写 skill，而是没有 librarian。

也就是没有人或机制回答这些问题：

- 这条经验用过几次？
- 哪些 case 里有用？
- 哪些 case 里有害？
- 它现在还适用吗？
- 它是不是应该降级为 deprecated？
- 它是不是只适用于某个 case？
- 它有没有 shadow 掉更正确的 skill？

我们现在的 SKILL.md 更像“经验堆积区”。这在项目早期有用，但如果真要自迭代，会变成 Library Drift 的温床。

### 问题 3：skill 越多不一定越好

Skill Shadowing 论文的结论很直接：skill library 变大后，agent 可能更差。

原因不是上下文太长这么简单，而是 agent 会选错 skill，或者因为相似 skill 太多而干脆不用 skill。

这对我们非常危险，因为 optics_agent 的技能边界本来就容易重叠：

- `optics-comsol-runtime`：镜像、license、runtime
- `optics-comsol-batch`：headless COMSOL batch
- `comsol-java-api`：COMSOL Java API 语法
- `optics-magnus-platform`：Magnus/Gustation 作业
- `optics-paper-reproduction`：论文复现流程
- Mie 理论：其实是 Python-only 解析/半解析模型

如果 Mie Python 任务加载了 COMSOL/Magnus 经验，反而可能被误导。

所以 skill router 必须允许：

```text
本节点不加载任何 skill
```

也必须按任务类型 gate，而不是只按语义相似度检索。

### 问题 4：主管 agent 不能当最终裁判

我们现在很多节点靠 supervisor 判断：

- theory_check
- numerical_check
- check_iteration

这可以作为第一层检查，但不能作为最终证据。

Self-Refine 和 Reflexion 都说明：模型经常会觉得“looks good”，尤其在数学推导、物理判断、复杂代码调试里。

所以正确的优先级应该是：

```text
LLM supervisor < deterministic verifier < held-out benchmark
```

supervisor 可以解释、路由、挑风险，但不能独立宣布“物理复现成功”。

### 问题 5：没有 replay suite，会出现遗忘

Forgetting 论文讲的是：agent 为了适应新任务，会破坏旧能力。

我们这里也一样。

例如：

- 为 Mie 解析模型优化 workflow，可能破坏 COMSOL/Magnus 流程。
- 为 COMSOL 调试增加很多规则，可能让简单 Python 任务变复杂。
- 为某篇论文写的失败经验，可能误导下一篇论文。

所以任何长期更新都要先跑 replay。

初始 replay suite 不需要很大，但必须有：

- 一个简单 Mie case
- 一个金属球 LSPR case
- 一个 COMSOL smoke 或已知 blocked case
- 一个 paper-reading-only case
- 一个报告生成 case，专门检查是否区分 pipeline/job/physical 三种状态

### 问题 6：抽象 lessons 可能不被忠实使用

Not Faithful Self-Evolvers 论文说明：agent 对 raw trace 有时有因果依赖，但对 condensed experience，也就是压缩后的经验总结，经常不忠实。

它可能：

- 忽略总结
- 误解总结
- 只学习了总结的风格
- 在错误上下文里套用总结

所以我们不能只写一句：

```text
不要把 surrogate 当作 physical reproduction。
```

更好的经验格式应该包含：

- 这条经验来自哪个 run / case
- 当时的上下文是什么
- 什么时候适用
- 什么时候不适用
- 触发检查项是什么
- 有哪些反例
- 原始日志在哪里

### 问题 7：成功经验会强化“行动偏置”

Safety Risks 和 Misevolve 论文提醒：即使经验都来自 benign task，也会让 agent 更倾向于行动。

也就是说，agent 会越来越想：

- 继续试
- 继续提交
- 继续改
- 继续包装结果
- 继续把经验写入长期规则

这在我们的项目里很危险。

高风险行为包括：

- 自动提交 Magnus job
- 自动增大资源
- 修改 active COMSOL image
- 泄露 private/license/token 路径内容
- 把 surrogate 或 diagnostic 说成复现成功
- 在缺少 GUI-exported COMSOL 模板时继续盲调
- 把一次失败写进全局规则

所以 workflow 每个高风险节点都要有 stop condition 和 human review condition。

## 文献给我们的核心启发

### 成功框架靠的不是“反思”本身

这些成功框架不是因为 agent 会反思就成功。

它们真正依赖的是：

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

### 我们现在最该借鉴 Ratchet

Ratchet 的思路最适合现在的 optics_agent。

不需要一上来做复杂 RL，不需要大规模 benchmark。先加一个最小 librarian：

- candidate / active / deprecated 状态
- 每条经验有来源 run_id
- 每条经验有适用边界
- 每条经验有调用记录
- 每条经验有成功/失败统计
- active skill 数量有上限
- 出现退化可以 rollback

这比继续堆 SKILL.md 更重要。

## 应该怎么改

### 1. 重新定义 `update_artifacts`

不要让它直接改长期文件。

新的流程应该是：

```text
生成候选 patch
→ 说明证据来源
→ critic/supervisor 审查
→ schema 检查
→ replay suite
→ accept / quarantine / reject
```

默认策略：

```text
低风险 run note：可以自动写
普通经验：进入 candidate
长期 SKILL / workflow / AGENTS / blueprint：必须 gate
高风险规则：必须人工确认
```

### 2. workflow schema 增加风险字段

现在的 `workflow_schema.yaml` 太简单，只描述拓扑。需要加自演化治理字段。

建议新增：

```yaml
risk_level: low | medium | high

loads_skills:
  allowed: []
  forbidden: []
  allow_none: true

loads_memories:
  scope: case | project | global
  max_items: integer

verifiers:
  - name: string
    command: string
    required: true

success_metrics:
  pipeline: string
  numerical: string
  physical: string

stop_conditions: []
human_review_conditions: []
regression_checks: []
artifact_write_policy: proposal_only | auto_write | human_gate
```

### 3. 每次节点执行生成 attempt capsule

现在的日志适合人读，但不适合统计和自迭代。

需要每次节点执行都生成结构化记录：

```yaml
attempt_capsule:
  run_id:
  case_id:
  node_id:
  task_type:
  selected_skills:
  selected_memories:
  commands_run:
  artifacts_read:
  artifacts_written:
  verifier_results:
  outcome: pass | fail | blocked | surrogate | diagnostic
  failure_type:
  human_intervention:
```

然后再有 critic verdict：

```yaml
critic_verdict:
  capsule_id:
  attribution: helped | hurt | neutral | inapplicable
  failure_pattern:
  evidence:
  confidence: low | medium | high
```

这样后面才能回答：某条经验到底有没有用。

### 4. 先做 Mie verifier，而不是急着做很多论文

如果 Mie 任务既是科研任务，又是 workflow 自演化 benchmark，那么第一阶段最重要的不是复现三篇论文，而是把 verifier 做稳。

第一阶段目标建议改成：

```text
单球 Mie 程序
+ 能量守恒检查
+ Rayleigh 极限检查
+ 大尺寸 Qext 趋近 2 检查
+ 截断收敛检查
+ benchmark manifest
```

金属 LSPR、核壳、阵列可以放到第二阶段。

因为没有 verifier，后面所有 self-evolution 都没有可信 reward signal。

### 5. 区分短期反思和长期 skill

不要把每次反思都写进长期 SKILL。

建议四层存储：

```text
short-term reflection：当前节点/当前 case 内有效，最多 1-3 条
case pitfall：某篇论文/某个 case 专属经验
project skill candidate：多 case 证据支持的候选技能
active skill / project policy：经过 replay 或人工确认的长期规则
```

### 6. 建立最小 replay suite

每次 canonical 修改前都跑。

初始可以很小：

```text
replay_mie_simple
replay_mie_lspr
replay_comsol_smoke_or_blocked
replay_report_boundary
replay_workflow_schema
```

接受条件：

```text
当前任务有收益
且 replay 没有关键退化
且成本没有明显上升
且安全规则没有被削弱
```

### 7. 把成功定义分层

以后不要直接说 workflow 成功。建议分成 6 级：

```text
Level 0: workflow 跑完一个 case
Level 1: deterministic verifier 通过
Level 2: replay 不退化
Level 3: paired validation 有净收益
Level 4: held-out ID/OOD 测试确认提升
Level 5: 有统计证据优于已有框架
```

Level 0-1 只能叫工程可行性。

Level 2-3 才能说初步自演化有效。

Level 4-5 才能说方法真的强。

## 对当前 `paper_reproduction.workflow.yaml` 的具体评价

### 好的地方

- 已经明确有 paper reading、theory、numerical、verification、report、update_artifacts 的完整链路。
- 已经区分 pipeline / COMSOL job / physical reproduction 三种状态。
- numerical_check 已经列出 mesh_error、solver_error、matrix_error、unphysical、license_error。
- numerical_debug 已经写了超过重试后请求 GUI-exported Java 模板。
- worker/supervisor 分离是正确方向。

### 不足

- `max_retries` 写在 YAML 里，和之前“retry_budget 是运行时参数”的设计不完全一致。
- `theory_check`、`numerical_check` 仍主要靠 LLM 判断。
- `update_artifacts` 默认直接改长期工件。
- `check_iteration` 只检查格式和合理性，没有 replay 或 acceptance test。
- 没有风险级别。
- 没有 stop condition。
- 没有 human review condition。
- 没有 skill loading gate。
- 没有 attempt capsule。
- 没有 replay suite。

### 最该先改的节点

第一优先级是 `update_artifacts`。

它应该拆成：

```text
collect_capsules
critic_verdict
cluster_failures
synthesize_candidate_patch
validate_patch
run_replay
accept_or_quarantine
```

而不是：

```text
复现结束 → 总结经验 → 修改 SKILL/workflow/blueprint
```

## 下一步建议

### 最小可行改造

1. 先不大改代码，先更新 `workflow_schema.yaml`，把风险字段定义出来。
2. 把 `paper_reproduction.workflow.yaml` 的 `update_artifacts` 改成 proposal-only。
3. 设计 `attempt_capsule.yaml` 和 `critic_verdict.yaml` 格式。
4. 给 Mie 任务写第一个 verifier：能量守恒。
5. 建立一个 tiny replay suite。
6. 后续每次长期更新都必须引用 attempt capsule。

### 当前科研策略

最稳的路线不是一开始追求完全自演化成功，而是：

```text
先做低成本 Mie verifier / benchmark
再做 workflow runner
再记录 agent 失败模式
再引入 evidence-gated self-evolution
最后评估是否真的提升
```

即使最后 self-evolution 没有明显优势，也能留下：

- 工具论文材料
- benchmark / dataset 材料
- LLM 在光学仿真中的失败模式实证数据
- 自演化崩溃现象观察

## 最终判断

现在最重要的不是让 workflow 更自动，而是让 workflow 更难“假进步”。

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
