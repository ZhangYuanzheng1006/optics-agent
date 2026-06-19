# 自演化 Workflow 风险审计笔记

> 2026-06-19
> 这份中文版是给自己看的，不是论文综述。重点是：这些自演化 agent / agent workflow 论文对我们现在的 `optics_agent` workflow 计划有什么警告、哪些假设不可靠、下一步应该怎么改。

## 一句话结论

我们现在的 workflow 设计已经有雏形，但还不能算严格意义上的“自演化系统”。

更准确地说，现在是：

```text
workflow 编排 + 复盘后改文档
```

真正需要变成：

```text
workflow 编排 + 物理验证器 + 证据日志 + provenance + 技能管理员 + 回放测试 + 沙箱/导出门控
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

### 后续扩展的 workflow / skill / memory / safety 论文

后来 `papers/self-evolution/` 扩展到 127 篇 PDF，并给每个目录写了 `README_summaries.md`。新增重点不是单纯“成功/失败/综述”，而是更贴近我们工程设计的模块：

- `workflow_optimization/`：AFlow、JudgeFlow、workflow generation benchmark、workflow provenance、Externalization
- `agent_skills/`：Agent Skills、SkillOps、SkillTester、Skill Drift、SkillWiki、skill prompt injection、skill supply-chain
- `multi_agent_orchestration/`：AgentOrchestra、MAFBench、AutoGen、MetaGPT、Echoing、plan reuse
- `memory_lifelong/`：memory evaluation、MemEvoBench、feedback-to-memory、procedural memory
- `evaluation_benchmarks/`：AEMA、benchmark audit、uncertainty decomposition
- `safety_governance/`：ToolEmu、AgentDojo、AgentGuard、SafeSearch、VESTA
- `scientific_agents/`：AI Scientist、AI-Researcher、autonomous scientific discovery、Why LLMs Aren't Scientists Yet

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

## 新 127 篇后补充出来的风险

这批新增论文让我更确定一件事：风险不只在“agent 会不会反思错”，而在于整个外部化系统变复杂后，**skill、memory、workflow、工具、日志、benchmark、多人协作**都会成为新的失真来源。

### 新风险 1：workflow 拓扑错了，但最终报告看起来完整

AFlow、Benchmarking Agentic Workflow Generation、JudgeFlow 这类论文提醒：workflow 不是只看最后答案，流程结构本身也会错。

比如：

- 参数还没确认，就进入代码生成。
- 物理 formalization 没完成，就开始 COMSOL。
- verifier 只检查文件存在，workflow 就学会绕过真正物理检查。
- Judge 把失败归因到错误节点，导致自迭代一直修错地方。

对我们来说，`case_workflow.yaml` 不能只记录节点顺序，还必须检查 required nodes、dependency edges、data dependencies、assumption dependencies。

### 新风险 2：外部化组件之间会互相耦合

Externalization 和 workflow provenance 论文说明：agent 行为不是模型单独决定的，而是这些东西一起决定的：

- `AGENTS.md`
- `SKILL.md`
- workflow YAML
- case_workflow YAML
- memory 检索结果
- CLI/model 参数
- 工具版本
- Docker/COMSOL/Magnus 环境

如果 run 只记录最终结果，我们根本不知道是哪一项改变带来了“进步”。

所以每次 run 都需要 `run_manifest.yaml`，记录 workflow hash、skill 版本、memory ID、模型、工具版本、container/runtime digest、artifact hash。

### 新风险 3：skill 是供应链包，不只是 Markdown

Agent Skills、SkillOps、Skill supply-chain 论文很关键。一个 skill 不只是 `SKILL.md`，还可能包括：

- 代码块
- 辅助脚本
- 配置文件
- 示例命令
- 资源文件
- 初始化逻辑

所以不能只看 Markdown 说得是否安全。必须检查 declared capability 和 actual capability 是否一致。

例如一个 skill 文字上说“整理论文”，脚本里却递归扫描 private 目录，这就是高风险。

### 新风险 4：skill 的文本声明和脚本行为可能不一致

Behavioral Integrity、SkillMutator、Semia 这类论文强调：skill 的自然语言说明和可执行行为可能不一致。

我们应该给每个 skill 建这样的检查：

```yaml
declared_capabilities: []
actual_capabilities: []
shell_access: true/false
network_access: true/false
private_path_access: true/false
writes_canonical_artifacts: true/false
```

只要 actual capability 超过声明，就不能 promotion。

### 新风险 5：把 prose skill 改成 typed skill 也会出错

Skill-as-Pseudocode、SkillRevise、SkillGrad 说明，把散文式经验改成结构化 contract / pseudocode / executable skill program 有好处，但也会丢边界。

比如：

```text
Degiron v2 需要 GUI-exported Java template
```

可能被错误改写成：

```text
所有 COMSOL mode analysis 都必须先要 GUI template，否则不能尝试
```

所以 typed skill 必须保留 source evidence，并强制写：

- applies_when
- does_not_apply_when
- source_capsules
- risk_tags

### 新风险 6：多 agent 不等于独立审查

Echoing、MAFBench、多 agent orchestration 论文提醒：多 agent 可能互相迎合。

风险包括：

- reviewer 只是复述 worker 的话
- expert 被 supervisor 的 framing 带偏
- 多 agent 达成共识，但共识基于同一个错误前提
- 长对话后角色边界漂移

所以 reviewer 必须读 artifact/verifier/log，不能只读 worker summary。每次 reviewer 输出都应引用证据路径或 artifact ID。

### 新风险 7：模板复用会带入旧论文假设

Plan reuse 论文对我们很重要，因为我们正在设计 template library。

模板不能只靠语义相似度复用。每个模板都要有：

```yaml
slots: []
fixed_assumptions: []
required_inputs: []
required_verifiers: []
does_not_apply_when: []
forbidden_reuse_conditions: []
```

否则 Degiron/COMSOL 的经验可能被错误套到 Mie/Python-only 任务上。

### 新风险 8：memory 类型混用会污染推理

MemoryAgentBench、MemEvoBench、feedback-to-memory 论文说明：记忆不是只要检索相关就有用。

我们至少要区分：

- fact
- procedure
- reflection
- failed_attempt
- raw_observation
- reviewer_feedback
- policy

不同 workflow 节点应该声明允许加载哪些 memory type。否则失败反思、旧反馈、COMSOL debug 痕迹会污染当前节点。

### 新风险 9：graph memory 可能固化错误因果

Graph memory 论文提醒：如果自动建立 `caused_by` / `mitigated_by` 边，很容易把相关性写成因果。

例如：

```text
COMSOL matrix factorization failure -> caused_by eigenvalue shift
```

这未必是真的。也可能是 physics setup、边界条件、网格、模板缺失。

所以因果边必须有 evidence、confidence、反证机制。报告里也要区分 observed correlation 和 verified cause。

### 新风险 10：benchmark disclosure 不足会制造“可复现性幻觉”

benchmark audit 和 AEMA 论文说明，很多 agent benchmark 论文没有充分披露 harness、模型参数、失败分类、成本、人类介入等信息。

我们如果只说“pass rate 提高了”，其实不能说明 workflow 真的变好了。

最低要求：每个实验都记录 task version、workflow version、model/inference params、tool versions、container digest、cost、retry、human intervention、verifier outputs、replay regression。

### 新风险 11：外部内容和工具输出都是 prompt injection 面

AgentDojo、SafeSearch、AgentGuard 说明，攻击不只来自用户 prompt，还来自：

- PDF 文本
- 网页
- README
- 日志
- 搜索结果
- 工具输出
- 代码注释

所以论文原文、网页资料、工具日志都要标成 untrusted data，不能覆盖 AGENTS/workflow/system 规则。

### 新风险 12：工具链组合比单个工具更危险

单个工具调用可能看起来安全，但组合起来就危险。

比如：

```text
read private artifact -> summarize -> write public report -> git push
```

这要求我们做 artifact taint tracking：如果产物来自 private PDF、private run、license-adjacent path，就不能直接 public export。

### 新风险 13：LLM 模拟沙箱不能等同真实执行

ToolEmu 类论文说明，模拟工具和模拟环境可以做红队筛查，但不能证明真实可执行。

以后报告里要区分：

```text
emulated pass < dry-run pass < real sandbox pass < real execution pass
```

尤其是 COMSOL/Magnus/license/resource 相关任务，模拟通过意义很有限。

### 新风险 14：科学 agent 最容易“正确地解决错误问题”

AI Scientist、AI-Researcher、Lang-PINN、Why LLMs Aren't Scientists Yet 共同提醒：代码运行不等于科学问题对。

对我们来说，必须在代码/COMSOL 之前加一个结构化 `physics_formalization`：

```yaml
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

否则程序可能可运行，甚至 verifier 通过，但它求解的不是论文里的物理问题。

### 新风险 15：动态 benchmark 也会 drift

如果以后自动生成 audit cases、扰动参数、反例测试，这些 benchmark 本身也会出错。

动态 case 不能直接进入 replay/audit 集。它们必须有版本、来源、扰动类型、expected behavior、verifier、人工确认状态。

### 新风险 16：长程任务的局部进展会被误读成整体成功

SWE-EVO/SWE-bench 类论文提醒：长程 agent 可能修好一部分、破坏另一部分。

我们必须记录：

- fix_count
- forget_count
- cost_delta
- PASS->PASS
- PASS->FAIL
- FAIL->PASS
- FAIL->FAIL

不能只看“最后有没有产物”。

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

provenance:
  required_artifacts: []
  answer_must_cite_artifact_ids: true

uncertainty:
  action_confidence: low | medium | high
  request_uncertainty: low | medium | high
  missing_fields: []

template_contract:
  slots: []
  fixed_assumptions: []
  does_not_apply_when: []

tool_chain_policy:
  taint_tracking: true
  export_whitelist_required: true
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

### 7. 加 run manifest / provenance / artifact hash

每次 workflow run 都要记录：

- workflow 和 case_workflow hash
- AGENTS/project policy hash
- skill 版本和实际加载的 skill ID
- 注入的 memory ID
- 模型、推理参数、CLI/tool 版本
- container/runtime digest
- artifact path、hash、producer node
- human intervention
- cost、retry、wall time、failure taxonomy

否则后续无法判断“进步”到底来自 workflow，还是来自模型/工具/环境变化。

### 8. 加 skill integrity / supply-chain gate

每个 skill promotion 前必须检查：

- `SKILL.md` 文本
- 代码块
- helper scripts
- config/examples/resources
- 是否访问 shell/network/private path/canonical artifacts

一个 skill 不能只因为文档写得安全就 active。

### 9. 加 uncertainty routing

每个计划/检查节点都要区分：

```text
action_confidence：我会不会做
request_uncertainty：任务本身是不是欠指定
```

如果 request_uncertainty 高，例如缺材料常数、边界条件、GUI-exported COMSOL 模板，就应该进入 clarification/block，不应该继续 retry/debug/self-modify。

### 10. 加 artifact taint tracking 和 export whitelist

来自 private PDF、private run folder、license-adjacent path、secret-adjacent path 的产物，都要带 taint。

public export、GitHub、长期 canonical 写入之前必须检查 taint。

### 11. 加 physics_formalization 节点

在代码/COMSOL 前先生成结构化物理 spec：geometry、materials、equations、boundary conditions、sources、solver、observables、assumptions、missing_fields。

否则“程序跑通”可能只是正确求解了错误问题。

### 12. 把成功定义分层

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
- 没有 run manifest / provenance。
- 没有 skill integrity / supply-chain gate。
- 没有 uncertainty routing。
- 没有 artifact taint tracking。
- 没有 physics_formalization 节点。

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

1. 先不大改代码，先更新 `workflow_schema.yaml`，把风险字段、provenance、uncertainty、template_contract、tool_chain_policy 定义出来。
2. 把 `paper_reproduction.workflow.yaml` 的 `update_artifacts` 改成 proposal-only。
3. 设计 `attempt_capsule.yaml` 和 `critic_verdict.yaml` 格式。
4. 给 Mie 任务写第一个 verifier：能量守恒。
5. 建立一个 tiny replay suite。
6. 加 `run_manifest.yaml`、artifact hash、provenance-cited answer。
7. 加 skill integrity 检查和 artifact taint tracking。
8. 后续每次长期更新都必须引用 attempt capsule。

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
