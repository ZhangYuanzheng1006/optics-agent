# 工作流引擎设计笔记

> 2026-06-18
> 本文档记录 optics_agent 工作流引擎的架构设计方案。

---

## 0. 术语约定

| 术语 | 含义 | 举例 |
|------|------|------|
| **提示词** | YAML 文件中预设的文本片段 | `worker.提示词`, `supervisor.提示词` |
| **prompt** | CLI 发送给 agent 的完整消息，由多个提示词 + 上下文组装而成 | 工作 prompt、主管 prompt |
| **工作 prompt** | workflow 发给工作 agent 的完整消息 | = 工作提示词 + 主管补充 + 系统工具说明 |
| **主管 prompt** | workflow 发给主管 agent 的完整消息 | = 主管提示词 + 工作产出 + 工作提示词选择 + MCP 工具说明 |

---

## 1. 为什么用 CLI 而非裸 API

Agent CLI（如 opencode）本质是一个**命令行控制的 vibe-coding IDE**：

- 通过 CLI 控制，workflow 程序可以启动/继续/结束对话
- agent 可以使用原生工具：读文件、写文件、运行 PowerShell、git 操作等
- optics_agent 的任务天然需要这些能力（读论文、写 Java、提 Magnus 作业、解析结果）
- 如果接入裸 API，agent 只是一个 LLM，无法直接操作文件系统和运行命令
- **CLI = LLM + 工具链 + 文件系统访问**，这才是完整的 coding agent

所以 workflow 程序通过 CLI 控制 agent，而不是直接调 API。

---

## 2. 核心架构

```
┌──────────────────────────────────────────────────────────────────┐
│                         workflow.py                               │
│                                                                    │
│  循环:                                                             │
│  1. 读 YAML 当前节点                                               │
│  2. 组装 工作 prompt → CLI → 工作 agent                              │
│  3. 捕获工作 agent 输出                                            │
│  4. 组装 主管 prompt → CLI → 主管 agent                              │
│  5. 接收 MCP 指令（来自主管 agent）→ 更新 state                     │
│  6. 回到 1                                                         │
│                                                                    │
│  对话命名: <workflow>_<时间>_worker / supervisor                    │
│  例: paper_reproduction_20260618_103000_worker                     │
│       paper_reproduction_20260618_103000_supervisor                 │
└──────────┬──────────────────────────────┬─────────────────────────┘
           │ CLI: 工作 prompt              │ CLI: 主管 prompt
           ▼                               ▼
┌──────────────────────┐   ┌──────────────────────────────┐
│   工作 agent          │   │   主管 agent                  │
│   (连续对话)          │   │   (连续对话)                  │
│                       │   │                              │
│   收到:                │   │   收到:                       │
│   工作 prompt =         │   │   主管 prompt =               │
│   · 工作提示词(YAML)   │   │   · 主管提示词(YAML)          │
│   · 主管补充指令       │   │   · 工作 agent 的输出         │
│   · 系统工具说明       │   │   · 工作提示词选择(YAML)       │
│                       │   │   · MCP 工具说明               │
│   职责:                │   │                              │
│   · 执行具体任务       │   │   职责:                       │
│   · 读/写文件          │   │   · 评估工作 agent 的结果     │
│   · 运行命令           │   │   · 选择下一轮的工作提示词     │
│   · 输出结果文本       │   │   · 调 MCP 工具控制流程       │
│                       │   │   · 维护经验笔记               │
│                       │   │   · 补充指令给工作 agent       │
│                       │   │   · 输出评估文本               │
└──────────────────────┘   └───────────┬──────────────────┘
                                       │ MCP: advance/rollback/report_failure/...
                                       ▼
                                workflow.py
```

### 数据流方向

```
workflow.py ──CLI──→ 工作 agent     # 发送 工作 prompt
工作 agent ──回复──→ workflow.py     # 返回执行结果文本

workflow.py ──CLI──→ 主管 agent     # 发送 主管 prompt
主管 agent ──MCP──→ workflow.py     # 调 advance/rollback 等流程控制
主管 agent ──回复──→ workflow.py     # 返回评估文本 + 补充指令（可选）
```

### MCP 调用不结束对话

主管 agent 调 MCP 工具（如 `advance`）只是一个**普通的工具调用**，不意味对话结束。MCP 等价于写入一个配置文件，如果语法出问题则工具调用直接失败报错。对话仍然以 LLM 的回复文本正常结束。

```python
# 主管 agent 的回复包含两部分:
# 1. MCP 调用: advance(branch="pass")  — 通知 workflow 更新 state
# 2. 回复文本: "推导正确，已通过"       — 正常的 LLM 回复，workflow 用来构造下一轮 prompt

# workflow.py 的处理:
mcp_call = mcp.wait_for_call()  # 阻塞等 MCP
reply_text = read_stdout()       # 读 LLM 回复文本
state.update(mcp_call)           # state 受 MCP 控制
prompt_next = build_prompt(reply_text)  # 下一轮 prompt 受回复文本控制
```

---

## 3. 一次节点执行的完整循环

```
workflow.py 读 YAML → 当前节点 theory_derivation
    │
    ├── 组装 工作 prompt:
    │    [workflow 元信息]
    │    [工作提示词 (YAML)]: "基于 params.yaml 完成理论推导..."
    │    [主管补充指令]: (无，第一次)
    │    [系统工具说明]
    │
    ├── CLI ──→ 工作 agent (继续对话 xxx_worker):
    │    工作 agent 执行 → 读 params.yaml → 写 theory_derivation.md
    │
    ├── 工作 agent 回复文本 → workflow 捕获
    │
    ├── 组装 主管 prompt:
    │    [workflow 元信息]
    │    [主管提示词 (YAML)]: "检查理论推导质量，做 pass/fail 决策"
    │    [工作 agent 的输出]: (上一步的回复文本)
    │    [工作提示词选择 (YAML)]: 
    │       选择 A: "请补充边界条件分析"
    │       选择 B: "已通过，进入数值程序"
    │    [MCP 工具说明]: advance(branch=pass/fail), rollback, ...
    │    [经验笔记]
    │
    ├── CLI ──→ 主管 agent (继续对话 xxx_supervisor):
    │    主管 agent 读工作输出 → 评估 →
    │    调 MCP advance(branch="pass") →
    │    回复文本（含补充指令，可选）
    │
    ├── workflow 接收 MCP: advance(branch="pass")
    │   → 更新 state → 下一节点 numerical_program
    │
    └── 下一轮：工作 prompt 中可附带主管补充指令
```

### 分支节点（如 theory_check）

```
workflow 读 YAML → theory_check
    │
    ├── 组装 主管 prompt（工作 agent 可能不需要执行）:
    │    [主管提示词]: "检查 theory_derivation.md 质量"
    │    [工作输出]: (读 theory_derivation.md 内容)
    │    [工作提示词选择]: 
    │       选择 A: "推导不足，请补充" → 回 theory_derivation
    │       选择 B: "已通过" → 进 numerical_program
    │    [MCP 工具说明]
    │
    ├── CLI ──→ 主管 agent
    │    主管 → 评估 → MCP advance(branch="pass")
    │
    └── workflow 更新 state → numerical_program
```

---

## 4. YAML 节点定义格式

```yaml
# ============ 普通执行节点 ============
theory_derivation:
  type: prompt
  description: 推导理论模型

  worker:
    提示词: |
      基于 params.yaml，完成理论推导：
      1. 写出控制方程
      2. 确定边界条件
      3. 分析预期物理行为
      输出: theory_derivation.md

  # 无 supervisor → workflow 跳过主管，直接 next
  next: theory_check


# ============ 分支节点 ============
theory_check:
  type: branch
  description: 检查理论推导质量

  supervisor:
    提示词: |
      检查 theory_derivation.md 的质量：
      - 方程量纲一致？(critical)
      - 边界条件合理？(critical)
      - 预期行为符合物理？(normal)
      决策 → 调 advance(branch=pass/fail)

    worker_choices:           # 给主管选择的工作提示词
      default: |
        基于检查意见，完善理论推导。
        重点补充: 边界条件的数学形式和适用性分析。
      pass: |
        推导通过，进入下一步。

  branches:
    pass: numerical_program
    fail: theory_derivation
  max_retries: 3


# ============ 导出节点（候选包，不直接改长期工件）============
export_bundle:
  type: prompt
  description: 打包报告、case_workflow、日志、verifier 结果和候选修改

  # 单次 workflow 只能导出候选包，不能直接修改长期 SKILL / workflow / 蓝图
  # 批量自迭代详见 第 10 节
```

---

## 5. workflow.py 构造 prompt 的逻辑

### 工作 prompt 的组装

```python
def build_worker_prompt(node, supervisor_extra=""):
    parts = [
        f"[workflow: paper_reproduction v{version}]",
        f"[node: {node.id}]",
        "",
        "--- 当前任务 ---",
        node.worker.提示词,
        "",
    ]
    
    if supervisor_extra:
        parts += [
            "--- 主管补充指令 ---",
            supervisor_extra,
            "",
        ]
    
    parts.append("--- 工具说明 ---\n你可以使用所有 opencode 内置工具。")
    
    return "\n".join(parts)
```

### 主管 prompt 的组装

```python
def build_supervisor_prompt(node, worker_output, experience_notes):
    parts = [
        f"[workflow: paper_reproduction v{version}]",
        f"[node: {node.id}]",
        "",
        "--- 你的任务 ---",
        node.supervisor.提示词,
        "",
        "--- 工作 agent 的输出 ---",
        worker_output,
        "",
    ]
    
    if node.supervisor.worker_choices:
        parts += [
            "--- 可用的工作提示词选择 ---",
        ]
        for name, text in node.supervisor.worker_choices.items():
            parts.append(f"[{name}]: {text}")
        parts.append("")
    
    parts += [
        "--- 经验笔记 ---",
        experience_notes,
        "",
        "--- 可用 MCP 工具 ---",
        "- advance(branch=pass/fail)  — 前进到下一节点",
        "- rollback()                — 回退到上一节点",
        "- read_file(path)           — 读取工作 agent 产出",
        "- update_experience(note)   — 追加经验笔记",
        "",
        "决策后请调用 MCP 工具控制流程。",
        "如有补充指令给工作 agent，在回复文本末尾用 【补充指令】 标记。",
    ]
    
    return "\n".join(parts)
```

### 主管补充指令的提取

```python
def extract_supervisor_extra(reply_text):
    """从主管回复中提取补充指令"""
    if "【补充指令】" in reply_text:
        return reply_text.split("【补充指令】")[1].strip()
    return ""
```

---

## 6. 经验笔记

主管 agent 维护两种笔记，用途和生命周期不同。

### 6.1 运行笔记（workflow 中读取）

用于本次 workflow 中后续节点的参考。控制长度，每次只读最新内容。

```markdown
# run_notes.md — 工作流运行期间的经验
更新规则: 主管 agent 通过 MCP update_experience 追加
读取规则: workflow 每次构造主管 prompt 时附上
长度控制: 提示词要求"保持简洁，超出 30 行则归档旧内容"

内容示例:
- Au 介电常数符号容易写反 (Drude: ωp=1.37e16)
- 网格最大单元 ≤ λ/8
- 特征值 shift=1.5 矩阵分解失败 → 改 2.0 解决
- theory_derivation 提示词缺少对边界条件的指导
```

### 6.2 节点日志（workflow 不读）

每个节点结束后，主管 agent 在 `logs/<session_id>/` 下新建文件详细记录：
- 这个节点发生了什么
- 遇到了什么问题和如何解决
- 成功/失败的结果

Workflow 不读这些日志，只保存。只有最终走完复现，进入总结阶段（准备给人类的报告 & 给自迭代 agent 的报告）时才会去读。

---

## 7. 论文发现对设计的影响

| 论文发现 | 对设计的影响 | 措施 |
|---------|-------------|------|
| Self-bias (2402.11436) | 同一模型自我评价有 bias | 主管和工作是**两个独立对话** |
| Library Drift (2605.19576) | 自动积累经验导致质量下降 | 单次 workflow 不直接写长期工件；经验进入 candidate / active / deprecated 生命周期 |
| Skill Shadowing (2605.24050) | 信息太多反而不行 | 用 agent 项目组和 skill router 控制上下文；大 skill 由专家 agent 消化，不直接塞给主 worker |
| 输出质量问题 (2603.24631) | 60-69% 失败是质量非定位 | 主管检查要关注内容质量 |
| 思维退化 (2512.20845) | 自我反思会退化 | 关键检查可开新 session 交叉验证 |
| 外部验证器不可缺（共识） | 纯 LLM 评估不够 | 物理 verifier、replay suite、独立 reviewer agent 共同判定 |

---

## 8. 单篇论文复现执行层：模板库 + 强制 case_workflow

之前的 `paper_reading -> theory_derivation -> numerical_program` 线性流程太粗。真实论文往往有多张图、多个方法、共享前置模型、互相独立的子任务，甚至需要 COMSOL / MATLAB / XFDTD / Python 混合。因此，单篇论文复现不应由一个 loose todo-list 管理，也不应把所有细节硬编码进外层 workflow。

当前决定：使用**三层结构**。

```text
外层 workflow.yaml
  管固定阶段、审计门、导出契约、自迭代触发

模板库 template_library/*.yaml
  管常见论文复现套路，替代人类师兄/PI 的流程经验

实例化 case_workflow.yaml
  supervisor 读论文后，拼接模板并微调，生成该论文的强制执行图
```

### 8.1 外层 workflow 管什么

外层 workflow 只管所有论文都必须有的阶段：

```text
读论文
→ 做复现计划
→ 生成 case_workflow.yaml
→ 主复现过程（执行 case_workflow，含主管发起的检查）
→ 独立检查
→ 可选：核对人工标准复现答案
→ 最终提交整理
→ 导出候选包
→ 可选/批量：自迭代
```

外层 workflow 的作用不是规定 Fig.3 怎么复现，而是规定：

- 什么产物必须存在
- 什么时候必须独立检查
- 哪些文件可以导出
- 什么时候必须停手
- 什么时候需要人工确认
- 什么时候进入批量自迭代 inbox

### 8.2 模板库管什么

YAML 仍然要替代人类经验，但替代的是“复现套路”，不是具体论文内容。

局部模板示例：

```text
template_library/local_templates/
  nano_optics_theory.yaml
  mie_theory.yaml
  comsol_reproduction.yaml
  xfdtd_reproduction.yaml
  matlab_reproduction.yaml
  parameter_sweep.yaml
  figure_comparison.yaml
  report_generation.yaml
```

整体示例模板：

```text
template_library/global_templates/
  single_figure_analytical_paper.yaml
  multi_figure_shared_model_paper.yaml
  hybrid_comsol_xfdtd_paper.yaml
  experimental_reference_with_simulation_paper.yaml
```

局部模板不是某篇论文的步骤，而是“遇到这类复现任务通常怎么做”。例如：

```yaml
id: comsol_reproduction
applies_when:
  - figure requires FEM / COMSOL style numerical simulation
default_steps:
  - extract_geometry_material_boundary
  - select_or_request_comsol_template
  - build_or_modify_java_model
  - run_compile_smoke
  - run_parameter_sweep
  - export_result_table
  - compare_with_paper
recommended_agents:
  - comsol_agent
  - magnus_agent
verifiers:
  - java_static_check
  - comsol_compile_smoke
  - result_table_nonempty
stop_conditions:
  - required_geometry_parameters_missing
  - gui_exported_template_required
  - same_solver_error_repeats_without_new_evidence
```

整体模板用于表达多图论文常见结构，例如：

```yaml
id: hybrid_comsol_xfdtd_paper
workflow_pattern:
  - theory_main:
      template: nano_optics_theory
  - fig3_comsol:
      template: comsol_reproduction
      depends_on: theory_main
  - fig2_xfdtd:
      template: xfdtd_reproduction
      depends_on: theory_main
  - integration:
      template: cross_figure_consistency_check
      depends_on:
        - fig3_comsol
        - fig2_xfdtd
```

### 8.3 case_workflow.yaml 是事实来源，不是 todo-list

supervisor 读完论文后，不应只维护自己的 todo。它必须生成一个标准 YAML 文件：

```text
reproduction_test/private/<case>/case_workflow.yaml
```

`case_workflow.yaml` 是单篇论文复现过程的事实来源。普通 todo 只能作为 UI 或状态显示，不是事实来源。

每个步骤必须记录：

```yaml
step_id: fig3_comsol
title: Implement Fig. 3 COMSOL model
template: comsol_reproduction
owner_agent: comsol_agent
prompt_profile: implementation_work
depends_on:
  - theory_main
inputs:
  - reproduction_targets.yaml
  - params.yaml
  - theory_main/theory_derivation.md
expected_outputs:
  - fig3_model.java
  - fig3_magnus_job.yaml
acceptance_criteria:
  - Java file follows COMSOL batch constraints
  - model exposes public static Model run()
  - no inner classes or anonymous classes
  - output result table is configured
verifiers:
  - java_static_check
  - comsol_compile_smoke
stop_conditions:
  - required_geometry_parameters_missing
  - gui_exported_template_required
risk_level: high
status: pending
```

### 8.4 supervisor 可以微调模板，但必须结构化记录

supervisor 的微调不能只存在于聊天上下文。每一次微调都必须写入 `case_workflow.yaml` 或 `workflow_edit_log.yaml`。

允许的编辑：

```text
add_step
modify_step
add_note
add_dependency
assign_agent
set_prompt_profile
set_acceptance_criteria
set_stop_condition
mark_completed
mark_blocked
request_review
```

示例：

```yaml
workflow_edit_log:
  - edit_id: E003
    step_id: fig3_comsol
    action: add_stop_condition
    value: gui_exported_template_required
    reason: isolated mode-analysis reached eigensolver but produced matrix factorization failure in prior Degiron run
    by: supervisor_agent
```

这保证后续自迭代系统能看到 supervisor 在执行中做过哪些优化，而不会漏在私人 todo 里。

### 8.5 agent 项目组，而不是单 worker

两条主线 agent 不够。更合理的是“agent 课题组”：

```text
Supervisor / PI agent
  管流程、调度专家、冲突裁决、停止/继续决策

Main worker agent
  执行普通任务或整合任务

Independent reviewer agent
  在关键检查点做 artifact-grounded 审查

Domain expert agents
  COMSOL expert
  Mie expert
  Magnus expert
  MATLAB/XFDTD expert
  Report expert

Librarian / self-iteration agent
  每 N 篇论文后离线整理经验、提出候选长期修改
```

大 SKILL 不直接塞给主 worker，而是由专家 agent 消化。主管负责“人事管理”：决定叫谁、给什么目标、用什么 prompt profile、验收标准是什么。

专家 agent 的输出必须受约束：

```yaml
expert_response:
  diagnosis:
  evidence:
  recommendation:
  confidence:
  required_inputs:
  stop_or_continue:
```

### 8.6 prompt profiles 预置“工作模式”，不是预置具体论文任务

YAML 中应预置 prompt profiles：

```yaml
prompt_profiles:
  intake:
    purpose: read paper and identify reproducible targets
  planning:
    purpose: create case_workflow by composing templates
  theory_work:
    purpose: derive equations, assumptions, physical limits
  implementation_work:
    purpose: write code/model/config
  debugging:
    purpose: diagnose failed task with bounded retries
  checking:
    purpose: independent artifact-grounded review
  integration:
    purpose: merge outputs across figures/tasks
  reporting:
    purpose: write final report without overclaiming
  handoff:
    purpose: produce blocker report for human/domain expert
  self_iteration_review:
    purpose: offline batch review, not per-case execution
```

具体任务目标由 supervisor 在 `case_workflow.yaml` 中填写。

### 8.7 最小可行复现流程

第一版不需要实现所有模板，只需要：

```text
outer workflow
  paper_intake
  reproduction_planning
  instantiate_case_workflow
  execute_case_workflow
  independent_review
  final_packaging
  export_bundle

local templates
  paper_target_selection
  nano_optics_theory
  numerical_python_reproduction
  comsol_reproduction
  result_comparison_and_report
```

这比固定线性 workflow 更适合真实论文，也比自由 todo 更可审计。

---

## 9. 沙箱执行与导出包

长期资产不能被单次 workflow 直接改写。每次 workflow 应在 Docker 或类似隔离环境中运行。

```text
long_term_store/
  skills/
  blueprints/
  workflows/
  programs/
  benchmarks/
  reports/

workflow_run_container/
  input_snapshot/        # 从长期存储复制进来的只读副本
  workdir/               # agent 实际工作区
  outputs/               # 普通结果
  export_candidates/     # 允许传回长期存储的候选包

long_term_inbox/
  run_0001_export/
  run_0002_export/
  ...
  run_0010_export/
```

原则：

```text
Workflow run is sandboxed.
Self-iteration is batched.
Long-term memory is append-only and gate-controlled.
```

### 9.1 输入只读，输出白名单

长期存储不能以可写方式挂载进容器。推荐：

```text
-v long_term_store:/input:ro
-v run_outputs:/output:rw
```

或者启动前复制 snapshot 到容器。

允许导出：

```text
final_report.md
params.yaml
comparison.yaml
attempt_capsule.yaml
critic_verdict.yaml
candidate_skill_patch.md
candidate_blueprint_patch.yaml
candidate_workflow_patch.yaml
candidate_program/
plots/
logs/
```

禁止导出：

```text
secret.json
license.dat
SSH keys
private raw PDF unless explicitly allowed
Docker credentials
Magnus token
```

### 9.2 export manifest

每次导出必须有：

```yaml
run_id:
case_id:
source_snapshot:
export_type:
  - report
  - candidate_skill
  - candidate_blueprint
  - candidate_program
  - candidate_workflow_patch
files:
  - path:
    type:
    source:
    reason:
    replaces:
    checksum:
evidence:
  - attempt_capsule_id:
  - verifier_result:
risk_level:
requires_human_review:
```

主管 agent 只能提交候选导出包，不能合并到长期资产。

---

## 10. 批量自迭代治理（替代单次 update_artifacts）

`update_artifacts` 不再是每篇论文末尾直接改文件的节点。workflow 执行和自迭代必须完全分离。

```text
单次论文复现
  → 只提交报告、case_workflow、attempt_capsules、verifier_results、export bundle
  → 不改长期 SKILL / blueprint / workflow

累计 N 篇论文（例如 10 篇）
  → 启动 self_iteration_batch
  → 读取 long_term_inbox
  → 聚类失败模式
  → 生成候选长期修改
  → replay / verifier / human gate
  → accept / quarantine / reject
```

### 10.1 触发参数

```yaml
self_iteration:
  mode: disabled_during_case
  trigger:
    type: batch
    min_cases: 10
  inputs:
    - final_reports
    - case_workflows
    - workflow_edit_logs
    - attempt_capsules
    - verifier_results
    - failure_taxonomy
```

### 10.2 证据门控流程

```text
candidate patch
→ critic verdict
→ schema validation
→ deterministic verifiers
→ replay gate
→ supervisor/human gate
→ accept / quarantine / reject
```

证据等级：

```text
single_observation -> run-local note only
repeated_evidence -> candidate skill
benchmark_backed -> active skill/workflow patch
human_confirmed -> allowed for high-risk project policy
```

### 10.3 skill/经验生命周期

长期经验必须从自由文本 lessons 变成可治理条目：

```yaml
skill_item:
  id:
  status: candidate | active | deprecated
  scope: case | project | global
  domain: mie | comsol | magnus | paper_reading | reporting | safety | workflow
  applies_when:
  does_not_apply_when:
  source_capsules:
  evidence_count:
  positive_cases:
  negative_cases:
  trial_count:
  contribution_score:
  last_verified:
  risk_tags:
```

### 10.4 replay suite

任何 canonical 修改前必须跑 replay。

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
当前任务有收益
且 replay 没有关键退化
且成本没有明显上升
且安全规则没有被削弱
```

### 10.5 对旧 `update_artifacts` 的处理

旧 `update_artifacts` 节点保留为导出阶段的一部分，但只允许生成候选，不允许写 canonical 文件。

```yaml
export_bundle:
  type: prompt
  artifact_write_policy: proposal_only
  instruction: |
    Package final report, case_workflow, attempt capsules, verifier results,
    logs, plots, and candidate patches into export_candidates/.
    Do not modify canonical AGENTS, SKILL, workflow, blueprint, or reusable tool files.

self_iteration_batch:
  type: offline_batch
  trigger: after_10_cases
  artifact_write_policy: human_gate
```

---

## 11. 运行参数系统：让重试次数可配置

不同论文难度不同，YAML 中硬编码 `max_retries` 不够灵活。改为启动时传入参数。

### 11.1 启动方式

```bash
# 简单论文：少点重试，快速失败
python workflow.py paper_reproduction --case "simple_waveguide" --retry-budget 5

# 复杂论文：多点重试，容忍反复失败
python workflow.py paper_reproduction --case "Degiron_Fig3" --retry-budget 20

# 指定参数文件
python workflow.py paper_reproduction --params params_run.yaml
```

### 11.2 运行参数文件

```yaml
# params_run.yaml — 每次运行的配置
case: Degiron_Fig3
description: "Degiron 2009 Fig3 复现，已知矩阵分解问题可能需多次调试"

retry_budget:
  total: 20                # 整个 workflow 的总重试次数，超限算失败
  per_node:                # 按节点单独设（可选）
    theory_check: 5
    numerical_check: 8
    independent_review: 5

user_intervention:
  require_confirm:          # 需要用户确认的节点
    - answer_verification
    - export_bundle
    - self_iteration_batch
  auto_continue_after: 300  # 用户无操作 5 分钟后自动继续

cli:
  default: "opencode"           # 默认 CLI
  worker: "opencode"            # 工作 agent 用的 CLI（可选，不设则用 default）
  supervisor: "opencode"        # 主管 agent 用的 CLI（可选）
  reviewer: "opencode --model gpt-4o"   # 独立 reviewer（可选，不同模型）
  expert_comsol: "opencode"     # 专家 agent（可选）
  expert_mie: "opencode"        # 专家 agent（可选）
  timeout: 600                  # 单节点超时(秒)
```

### 11.3 "返工算失败"机制

```
累计重试次数贯穿整个 workflow：

理论检查 第 1 次 fail → retry_count=1
理论检查 第 2 次 pass → retry_count=2
数值检查 第 1 次 fail → retry_count=3
数值检查 第 2 次 fail → retry_count=4
数值检查 第 3 次 pass → retry_count=5
独立检查 第 1 次 fail → retry_count=6

如果 retry_budget.total=5 → 独立检查失败时已超限，整个 workflow 失败

失败时的输出:
- 保存完整 debug 日志
- 生成 handoff 报告（说明已尝试的路径、失败原因、建议下一步）
- 标记最终状态为 "workflow_failed: retry_budget_exhausted"
```

### 11.4 论文难度分级参考

| 级别 | 案例 | 建议 retry_budget | 说明 |
|------|------|------------------|------|
| 简单 | 单层薄膜透射率 | 3-5 | 解析解已知，数值稳定 |
| 中等 | 波导模式分析 | 8-12 | 需要特征值求解，shift 调优 |
| 复杂 | Degiron 等离激元 | 15-20 | 多物理场耦合，矩阵分解难点 |
| 前沿 | 微纳光学新结构 | 20-30 | 模型参数不确定，需大量迭代 |

### 11.5 YAML 中的变化

YAML 节点中不再硬编码 `max_retries`，改为引用运行参数：

```yaml
theory_check:
  type: branch
  supervisor: ...
  branches:
    pass: numerical_program
    fail: theory_derivation
  # 无 max_retries — 由运行参数控制
```

由 workflow 引擎在运行时从参数文件读取。

---

## 12. 已确认的设计决策

### D1: 角色分离（对应 R4）

工作 agent 和主管 agent 是两个独立对话，每个 prompt 只服务一个角色：
- 工作 prompt 不含评估要求 → 工作 agent 只管执行
- 主管 prompt 不含执行任务 → 主管 agent 只管评估和决策

已在 §2 架构中实现。

### D2: 本地版本控制（对应 R3）

用类似 git 的指令在磁盘备份文件夹中记录每次节点执行前后的状态。不是真的 git，是本地脚本。

```
基本指令（workflow.py 内置或轻量脚本）:
  wf commit "<message>"    # 自动 add + commit 当前工作目录到备份区
  wf push                  # 推送到备份仓库 (<session_id> 目录)
  wf pull                  # 从备份仓库拉取（用于恢复）

规则:
  工作 agent: 每个节点完成后自愿执行 wf commit（记录做了什么）
  主管 agent: 如果不记得 commit → 强制返工主管节点
  
  自动 add: 本地备份无需隐私考虑，不区分 staged/unstaged

作用:
  - 崩溃恢复：workflow 检测到 CLI 异常退出时，pull 回退到上一 commit
  - 事后排查：备份仓库完整记录了每一步的文件变更
  - 审计：可以追溯谁（主管/工作/哪一轮）改了哪些文件

  push/pull 都是本地的 <backups/<session_id>/ 目录
  无需网络，无需 github，无隐私问题

实现: 
  可用 git 的 bare repo 做后端，或用 robocopy + 快照记录
  实在不行自己写一个也不复杂（commit = 压缩当前目录快照）
```

### D3: retry_budget 运行时配置（已在 §11 实现）

重试次数为运行参数而非 YAML 硬编码。简单论文 budget=5，复杂论文 budget=20。

---

## 13. 风险项状态总览

| 风险 | 内容 | 状态 | 说明 |
|------|------|------|------|
| **R1** | 主管误判导致浪费时间或错误结果 | 🟡 部分解决 | agent 项目组 + 独立 reviewer + artifact-grounded 检查，仍需 verifier |
| **R2** | 自迭代导致 SKILL 质量退化 | 🟡 部分解决 | workflow 执行和自迭代分离，批量 evidence-gated governance，仍需实现 librarian/replay |
| **R3** | CLI 崩溃后恢复 | ✅ D2 | 本地 git 版控 + 重试一次 |
| **R4** | 同一 prompt 中角色混淆 | ✅ D1 | 独立对话，一个 prompt 一个角色 |
| **R5** | 用户被排除在 loop 之外 | ⏳ 未解决 | 需组会后决定：全自动 vs 少量人工介入 |
| **R6** | 经验笔记过长 | ✅ | 运行笔记(控制长度) + 节点日志(不看) |
| **R7** | 对话名称冲突 | ✅ 无风险 | workflow 程序管理命名，含时间戳 |
| **R8** | 路径参数化 `<case>` | 🟡 部分解决 | case_workflow 固定放到 `reproduction_test/private/<case>/`，仍需实现替换逻辑 |
| **R9** | 多 CLI 支持 | ⏳ 未解决 | 未决定用哪个 CLI，且不同角色可能用不同 CLI（YAML 加选项） |

### 当前未解决项（按优先级）

```
立即级:
  R5 — 开组会问光学组同学愿不愿意参与部分 workflow
        如果全自动则不需要设计"用户介入点"（待调研 #3 取消）

实现前必须定:
  R9 — 确定用什么 CLI，以及不同角色是否用不同 CLI
       （影响 YAML 节点定义 + workflow.py 的 CLI 调用逻辑）

实现中解决:
  R1, R2 — 已有架构方向，待实现 verifier / librarian / replay
  
  R8 — case_workflow / export bundle 路径参数化，待实现替换逻辑
  
  #1, #2 — 调研 opencode --session 和 MCP 配置
```

### R8 快速解释（怕你下次忘了）

```
workflow.yaml / case_workflow.yaml 中用 <case> 做占位符:
  
  produces:
    - reproduction_test/private/<case>/case_workflow.yaml

启动时替换:
  python workflow.py ... --case Degiron_Fig3

实际路径:
  reproduction_test/private/Degiron_Fig3/case_workflow.yaml
```

---

## 14. 最终成功标准

### 14.1 什么是成功（理想情况）

两条核心标准：

**1. 迭代曲线健康**
```
pass rate
  ↑
80% ──────────────── 稳定平台（不崩溃，不退化）
  │               ↗
60%           ↗
  │        ↗        形状: 对数增长型
40%     ↗           不是倒 U 型（先升后降）
  │  ↗
20% ↗
  │
  └───|───|───|───|──→ 迭代轮数
      5  10  15  20
```

**2. 最终表现明显优于已有报道**

| 对比基准 | 目前数据 |
|---------|---------|
| LLM 自写 skill 增益 vs 无 skill 基线 | +0.0pp (SkillAxe 2606.10546) |
| 人类编写 skill 增益 | +16.2pp |
| Socratic-SWE 3 轮迭代 | 50.40% SWE-bench |
| 人工复现一篇光学论文 | ~2-4 周 |

### 14.2 如果成功且解决了未报道的崩溃

如果同时满足：
- 发现并解决了几个未经报道的自迭代崩溃模式
- workflow 最终指标优越
- 兼容性强（跨工具、跨模型）

**发表级别**：可冲 **Nature Computational Science**（科学发现+方法贡献+工程验证）

### 14.3 最可能的结果（现实判断）

多数科研项目最终是：
- **负成果**：自迭代效果不好，或不如现有框架
- **无显著优势**：metrics 和已有报道差不多

这不是放弃，而是清醒的风险评估。应对策略：**三个瓶盖盖住一个就不算白做**。

### 14.4 三个瓶盖策略

```
瓶盖 1: 工具论文
  前提: workflow 能跑通一个 case（不要求 agent 多聪明）
  投稿: CPC / SoftwareX
  用途: 简历 + 结题 ✓
  时间: 半年内

瓶盖 2: 实证/数据集
  前提: 每次跑记录成功/失败/错误类型，攒 50 次以上
  投稿: 实证论文或数据集论文
  用途: 简历 + 结题 ✓
  时间: 随时开始攒

瓶盖 3: 负结果→发现
  前提: 遇到规律性崩溃，且你把它描述清楚了
  投稿: Scientific Reports 等接受负结果的期刊
  用途: 简历 + 结题 ✓
```

三个瓶盖不冲突。**瓶盖 2（攒数据）现在就可以开始**，不需要等 workflow 完整实现。

### 14.5 额外的小成果（实证问题）

这些不大不小，但每个都可以作为论文的一个 section 或 workshop 短文：

| # | 问题 | 实验设计 |
|---|------|---------|
| Q1 | 弱模型迭代后能否接近强模型？ | 同 workflow 用 Qwen2.5-7B / DeepSeek-R1-32B / GPT-5.5 分别跑，比较首次 vs 迭代 N 次后成功率 |
| Q2 | workflow 对新工具的泛化效果？ | 同 workflow 换后端 COMSOL → MATLAB → XFDTD, 比较成功率和错误模式 |
| Q3 | 自迭代是否真的有效？ | 同一论文，初始 workflow vs 迭代 5 次 vs 20 次，比较成功率和执行时间 |
| Q4 | 主管强+工作弱 vs 全强的效果？ | 强-强/强-弱/弱-强/弱-弱 四种组合，比较成功率+成本 |
| Q5 | 重试几次边际收益最大？ | 固定复杂节点，记录每次重试的通过率，找最优停止点 |

### 14.6 已下载的相关论文

论文下载在 `papers/self-evolution/`，按分类：

| 分类 | 数量 | 代表性论文 |
|------|------|-----------|
| failures/ | 10 | Library Drift (2605.19576), Skill Shadowing (2605.24050), Misevolve (2509.26354), 遗忘 (2605.09315), 不忠实自我演化 (2601.22436), 安全风险 (2604.16968), 健康演化 (2606.06114), Self-Bias (2402.11436), 进步或退步 (2407.05013), Skill Drift (2605.10990) |
| frameworks/ | 18 | Socratic-SWE, GEA, SkillRL, EXG, CoEvoSkills, Ratchet, Skill1, Scaling Laws, SkillDAG, GraSP, Voyager, Reflexion, Self-Refine, 符号学习自演化, SEW, AutoRefine, EvoDS, MemCoder |
| surveys/ | 4 | Self-Evolving 综述 (2508.07407), SkillEvolBench (2605.24117), SEAGym (2606.17546), PACE (2606.08106) |

---

## 15. 可能的科研成果全览

### 15.1 7 种成果类型

| # | 类型 | 内容 | 投稿方向 | 难度 | 简历价值 | 结题价值 |
|---|------|------|---------|------|---------|---------|
| 1 | **工具论文** | workflow 框架本身，能跑通一个 case 即可 | CPC / SoftwareX / JOSS | 低 | ★★★ | ★★★ |
| 2 | **科学发现论文** | agent 发现了人类没注意到的新物理（从复现走向创新） | Nature Computational Science / PRL / npj | 极高 | ★★★★★ | ★★★★★ |
| 3 | **方法论论文** | 声明式 DSL + 多角色隔离 + 科学领域 skill 自演化 | NeurIPS AI4Science / ICML AI4Science / Nature Machine Intelligence | 高 | ★★★★ | ★★★★ |
| 4 | **负结果论文** | 系统性描述自迭代的失败模式、能力边界、崩溃机制 | Scientific Reports / CPC (经验报告) / arXiv + workshop | 中 | ★★ | ★★★ |
| 5 | **数据集论文** | 复现积累的参数表 + 预期结果 + 失败案例 → benchmark | NeurIPS Datasets & Benchmarks / Scientific Data | 中 | ★★★ | ★★★ |
| 6 | **实证研究论文** | LLM 写 COMSOL Java 的正确率？多少次交互能复现？失败模式分布？ | ACM Computing Surveys / Empirical Software Engineering | 中高 | ★★★ | ★★★ |
| 7 | **综述论文** | "LLM Agent in Computational Optics" 占坑 | arXiv + 后续投期刊 | 低（但开头难） | ★ | ★★ |

### 15.2 三种情况的投稿策略

| 情况 | 建议打包 | 说明 |
|------|---------|------|
| **workflow 成功**（指标优越+解决崩溃） | 2(发现) + 3(方法论) 绑一起投 Nat. Comput. Sci. | 科学发现+方法贡献+工程验证 |
| **workflow 一般**（能跑但无显著优势） | 1(工具) + 6(实证) 分开投 CPC 和 workshop | 工具保底+实证数据补充 |
| **workflow 失败** | 4(负结果) + 5(数据集) 投 Scientific Reports 或 NeurIPS D&B | 失败的发现也是发现 |

### 15.3 额外的小成果清单

以下每个问题都可以作为论文的一个 section（ablation study）或独立 workshop 短文：

| # | 问题 | 实验设计 | 最小可行产出 |
|---|------|---------|------------|
| Q6 | **主管强+工作弱的成本收益** | 强-强 vs 强-弱 vs 弱-强 vs 弱-弱，记录成功率和 token 消耗 | 一张四象限图 + 短文 |
| Q7 | **节点顺序敏感性** | 同一个 workflow 随机打乱节点顺序，看成功率变化 | 说明拓扑设计是否真的重要 |
| Q8 | **失败模式分布** | 统计 50+ 次失败的节点分布、错误类型、根因 | 饼图 + bar chart |
| Q9 | **MCP vs 无 MCP 对比** | 有 advanced/rollback 工具 vs 没工具让 agent 自己管理状态 | ablation study |
| Q10 | **上下文压缩的影响** | 长 workflow（20+ 节点）中, 工作 agent 在开头 vs 结尾的准确率变化 | 退化曲线 |
| Q11 | **人类辅助点设计** | 在不同节点插入人类确认，比较完成时间和最终质量 | 人机协同设计建议 |
| Q12 | **CLI 选择的影响** | 同一 prompt 用 opencode vs Claude Code vs Codex CLI 的效果 | 框架选择指南 |

### 15.4 务实建议

```
不要一篇论文想装下所有档位，分开发更清晰。

短期(半年内): 瓶盖 1(工具论文) → 保简历+结题
中期(一年内): 瓶盖 2(实证数据) + Q6-Q12 挑 2-3 个做
长期: 如果 workflow 真的成功 → 冲发现+方法论
如果 workflow 失败 → 负结果也是发现
```
