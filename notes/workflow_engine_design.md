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


# ============ 自迭代节点（独立多轮对话）============
update_artifacts:
  type: self_iterate
  description: 自迭代：修改 YAML / SKILL / 蓝图

  # 此节点启动 3 个独立对话 + 6 步程序化验证
  # 详见 第 8 节
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
| Library Drift (2605.19576) | 自动积累经验导致质量下降 | 提示词有 `auto-generated` 标记 |
| Skill Shadowing (2605.24050) | 信息太多反而不行 | 每次 prompt 只含当前节点必要信息 |
| 输出质量问题 (2603.24631) | 60-69% 失败是质量非定位 | 主管检查要关注内容质量 |
| 思维退化 (2512.20845) | 自我反思会退化 | 关键检查可开新 session 交叉验证 |
| 外部验证器不可缺（共识） | 纯 LLM 评估不够 | numerical_check 加脚本验证钩子 |

---

## 8. 自迭代设计（update_artifacts 节点）

自迭代不是让一个 agent 直接改文件，而是**3 个独立对话 + 6 步流程 + 程序化验证**，逐层保证质量。

### 8.1 整体流程

```
主管 agent 的最终报告
    │
    ├── 对话 1: 方案 agent（设计者）
    │   Step 1: 基于报告 + 知识库，提出修改方案
    │   Step 2: 基于论文注意事项，审查方案合理性
    │
    ├── 对话 2: 执行 agent（修改者）
    │   Step 3: 加载语法 SKILL，执行修改
    │   Step 4: 修改后自我检查
    │
    ├── Step 5: 程序化验证（固定语法检查程序）
    │   确认修改后的文件能被 workflow 正确读取
    │
    └── Step 6: 验证通过 → 应用修改 / 失败 → 退回
```

### 8.2 三个对话的角色分工

```
┌─────────────────────────────────────────────────────────────────┐
│  对话 1: 方案 agent (designer)                                   │
│  独立的连续对话，命名: xxx_designer                              │
│                                                                  │
│  Step 1 prompt:                                                   │
│  内容:                                                            │
│  · 主管的最终报告（本轮复现摘要、失败模式、经验）                  │
│  · 知识库（相关 SKILL.md、notes/reference/ 下的论文笔记）          │
│  · MCP arxiv 搜索工具（需要时查论文佐证）                         │
│  · 当前 YAML / SKILL / 蓝图文件内容                               │
│  任务: 输出修改方案（diff 格式或结构化描述）                       │
│                                                                  │
│  Step 2 prompt:                                                   │
│  内容:                                                            │
│  · 方案 agent 自己刚才 Step 1 的输出                              │
│  · 检查清单（来源于之前 arxiv 调研发现的注意事项）:                 │
│    - Library Drift: 是否会导致 skill 无限膨胀？                  │
│    - Skill Shadowing: 新技能是否可能干扰已有技能？               │
│    - Self-bias: 修改是否过于自信？                               │
│    - 外部验证器: 新增的检查点是否有程序化验证？                  │
│    - ...（从 reference 提取的完整清单）                            │
│  任务: 用这些注意事项审查自己的方案，输出最终修改方案               │
│                                                                  │
│  输出: 修改方案文件（修改方案.yaml 或 diff）                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  对话 2: 执行 agent (executor)                                   │
│  独立的连续对话，命名: xxx_executor                              │
│                                                                  │
│  Step 3 prompt:                                                   │
│  内容:                                                            │
│  · 方案 agent 的最终修改方案                                     │
│  · 语法 SKILL（描述 YAML 格式、SKILL.md 格式、蓝图语法的 SKILL） │
│  · 注意事项（如: YAML version 必须递增、history 必须追加等）      │
│  任务: 按修改方案执行文件修改                                     │
│                                                                  │
│  Step 4 prompt:                                                   │
│  内容:                                                            │
│  · 执行 agent 自己刚才修改的文件内容                              │
│  · 修改方案（用于对照检查）                                       │
│  任务: 自我检查修改是否完整、格式是否正确、无遗漏                 │
│                                                                  │
│  输出: 已修改的文件                                              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Step 5: 程序化验证 (workflow.py 内置)                          │
│  不启动 agent，直接跑脚本                                        │
│                                                                  │
│  验证项目:                                                        │
│  · YAML 语法解析: python -c "import yaml; yaml.safe_load(...)"   │
│  · SKILL.md frontmatter 完整性: name, description, version 必填  │
│  · workflow schema 合规: nodes 结构正确？next/branches 引用存在？ │
│  · 引用完整性: 所有 next/branch 指向的节点 ID 都存在              │
│                                                                  │
│  Step 6:                                                         │
│  验证通过 → workflow 确认修改，更新 state                         │
│  验证失败 → 退回执行 agent 修复                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 8.3 YAML 节点定义

```yaml
update_artifacts:
  type: self_iterate
  description: 自迭代：修改 YAML / SKILL / 蓝图

  designer:                             # → 方案 agent (对话 1)
    step1_prompt: |
      基于主管的最终报告和经验笔记，分析本轮复现的问题，
      提出对以下工件的修改方案:
      1. paper_reproduction.workflow.yaml — 拓扑、提示词、分支条件
      2. 相关 SKILL.md — 失败模式、API 经验
      3. .magnus 蓝图 — 参数默认值

      可用工具:
      - MCP arxiv search — 搜索相关论文佐证
      - 文件读写 — 读取 SKILL.md、notes/reference/ 等

      输出: 修改方案.yaml（包含: 文件路径、修改类型、修改内容、理由）

    step2_prompt: |
      用以下 checklist 审查你刚才的方案:

      □ Library Drift: 新追加的经验是否可标记为 auto-generated？
      □ Skill Shadowing: 新增内容是否简洁？是否可能淹没已有知识？
      □ Self-bias: 是否有外部参考（论文/文档）支持修改？
      □ 回溯兼容: 修改后旧 session 的状态文件是否仍可读？
      □ 语义正确: YAML 中 next/branches 引用的节点 ID 是否存在？
      □ 迭代节制: 是否真的需要修改？还是本轮经验不够普遍？

      输出: 最终修改方案.yaml（通过上述检查后的版本）

  executor:                             # → 执行 agent (对话 2)
    syntax_skill: workflow_yaml_grammar  # 引用语法 SKILL

    step3_prompt: |
      加载 workflow_yaml_grammar SKILL，了解 YAML/workflow 语法规范。
      按 修改方案.yaml 执行文件修改。

      注意事项:
      - workflow.yaml version 必须递增
      - history 必须追加变更记录
      - SKILL.md 的 auto-generated 经验必须标记
      - 修改后立即验证文件可解析

    step4_prompt: |
      自我检查:
      1. 所有修改是否与修改方案一致？
      2. 文件格式是否正确？
      3. 是否遗漏了 version/history 更新？
      4. 修改是否影响其他节点？

  validation:                           # → 程序化验证
    check_scripts:
      - "python -c \"import yaml; yaml.safe_load(open('workflows/paper_reproduction.workflow.yaml'))\""
      - "python -c \"import yaml; d=yaml.safe_load(open('...')); assert d.get('version')\""
    next_on_pass: check_iteration
    next_on_fail: executor_step3       # 退回执行 agent
```

### 8.4 论文发现与自迭代的映射

| 论文发现 | 对应设计 |
|---------|---------|
| Library Drift (2605.19576) | Step 2 checklist 中标记 auto-generated，防止无限膨胀 |
| Skill Shadowing (2605.24050) | Step 2 要求评估"新增内容是否简洁" |
| Self-bias (2402.11436) | 方案和执行是两个独立对话，无法互相影响 |
| 外部验证器不可缺 | Step 5 程序化验证，不依赖 LLM |
| 基准可靠性问题 (2603.00520) | 语法验证而非语义验证，确保文件可读 |
| 框架比模型重要 (2606.12344) | 语法 SKILL 确保修改符合框架规范 |

---

## 9. 运行参数系统：让重试次数可配置

不同论文难度不同，YAML 中硬编码 `max_retries` 不够灵活。改为启动时传入参数。

### 9.1 启动方式

```bash
# 简单论文：少点重试，快速失败
python workflow.py paper_reproduction --case "simple_waveguide" --retry-budget 5

# 复杂论文：多点重试，容忍反复失败
python workflow.py paper_reproduction --case "Degiron_Fig3" --retry-budget 20

# 指定参数文件
python workflow.py paper_reproduction --params params_run.yaml
```

### 9.2 运行参数文件

```yaml
# params_run.yaml — 每次运行的配置
case: Degiron_Fig3
description: "Degiron 2009 Fig3 复现，已知矩阵分解问题可能需多次调试"

retry_budget:
  total: 20                # 整个 workflow 的总重试次数，超限算失败
  per_node:                # 按节点单独设（可选）
    theory_check: 5
    numerical_check: 8
    check_iteration: 3

user_intervention:
  require_confirm:          # 需要用户确认的节点
    - answer_verification
    - update_artifacts
  auto_continue_after: 300  # 用户无操作 5 分钟后自动继续

cli:
  default: "opencode"           # 默认 CLI
  worker: "opencode"            # 工作 agent 用的 CLI（可选，不设则用 default）
  supervisor: "opencode"        # 主管 agent 用的 CLI（可选）
  designer: "opencode --model gpt-4o"   # 方案 agent（可选，不同模型）
  executor: "opencode"          # 执行 agent（可选）
  timeout: 600                  # 单节点超时(秒)
```

### 9.3 "返工算失败"机制

```
累计重试次数贯穿整个 workflow：

理论检查 第 1 次 fail → retry_count=1
理论检查 第 2 次 pass → retry_count=2
数值检查 第 1 次 fail → retry_count=3
数值检查 第 2 次 fail → retry_count=4
数值检查 第 3 次 pass → retry_count=5
自迭代 第 1 次 fail  → retry_count=6

如果 retry_budget.total=5 → 自迭代失败时已超限，整个 workflow 失败

失败时的输出:
- 保存完整 debug 日志
- 生成 handoff 报告（说明已尝试的路径、失败原因、建议下一步）
- 标记最终状态为 "workflow_failed: retry_budget_exhausted"
```

### 9.4 论文难度分级参考

| 级别 | 案例 | 建议 retry_budget | 说明 |
|------|------|------------------|------|
| 简单 | 单层薄膜透射率 | 3-5 | 解析解已知，数值稳定 |
| 中等 | 波导模式分析 | 8-12 | 需要特征值求解，shift 调优 |
| 复杂 | Degiron 等离激元 | 15-20 | 多物理场耦合，矩阵分解难点 |
| 前沿 | 微纳光学新结构 | 20-30 | 模型参数不确定，需大量迭代 |

### 9.5 YAML 中的变化

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

## 10. 已确认的设计决策

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

### D3: retry_budget 运行时配置（已在 §9 实现）

重试次数为运行参数而非 YAML 硬编码。简单论文 budget=5，复杂论文 budget=20。

---

## 11. 风险项状态总览

| 风险 | 内容 | 状态 | 说明 |
|------|------|------|------|
| **R1** | 主管误判导致浪费时间或错误结果 | ⏳ 未解决 | 你在想 |
| **R2** | 自迭代导致 SKILL 质量退化 | ⏳ 未解决 | 你在想 |
| **R3** | CLI 崩溃后恢复 | ✅ D2 | 本地 git 版控 + 重试一次 |
| **R4** | 同一 prompt 中角色混淆 | ✅ D1 | 独立对话，一个 prompt 一个角色 |
| **R5** | 用户被排除在 loop 之外 | ⏳ 未解决 | 需组会后决定：全自动 vs 少量人工介入 |
| **R6** | 经验笔记过长 | ✅ | 运行笔记(控制长度) + 节点日志(不看) |
| **R7** | 对话名称冲突 | ✅ 无风险 | workflow 程序管理命名，含时间戳 |
| **R8** | 路径参数化 `<case>` | ⏳ 未解决 | 你对 YAML 结构不熟，后续再讲 |
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
  R1, R2 — 你想清楚方案后补充
  
  R8 — 路径参数化，了解 YAML 结构后自然能理解
  
  #1, #2 — 调研 opencode --session 和 MCP 配置
```

### R8 快速解释（怕你下次忘了）

```
workflow.yaml 中用 <case> 做占位符:
  
  produces:
    - reproduction/private/<case>/model.java

启动时替换:
  python workflow.py ... --case Degiron_Fig3

实际路径:
  reproduction/private/Degiron_Fig3/model.java
```

---

## 13. 最终成功标准

### 13.1 什么是成功（理想情况）

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

### 13.2 如果成功且解决了未报道的崩溃

如果同时满足：
- 发现并解决了几个未经报道的自迭代崩溃模式
- workflow 最终指标优越
- 兼容性强（跨工具、跨模型）

**发表级别**：可冲 **Nature Computational Science**（科学发现+方法贡献+工程验证）

### 13.3 最可能的结果（现实判断）

多数科研项目最终是：
- **负成果**：自迭代效果不好，或不如现有框架
- **无显著优势**：metrics 和已有报道差不多

这不是放弃，而是清醒的风险评估。应对策略：**三个瓶盖盖住一个就不算白做**。

### 13.4 三个瓶盖策略

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

### 13.5 额外的小成果（实证问题）

这些不大不小，但每个都可以作为论文的一个 section 或 workshop 短文：

| # | 问题 | 实验设计 |
|---|------|---------|
| Q1 | 弱模型迭代后能否接近强模型？ | 同 workflow 用 Qwen2.5-7B / DeepSeek-R1-32B / GPT-5.5 分别跑，比较首次 vs 迭代 N 次后成功率 |
| Q2 | workflow 对新工具的泛化效果？ | 同 workflow 换后端 COMSOL → MATLAB → XFDTD, 比较成功率和错误模式 |
| Q3 | 自迭代是否真的有效？ | 同一论文，初始 workflow vs 迭代 5 次 vs 20 次，比较成功率和执行时间 |
| Q4 | 主管强+工作弱 vs 全强的效果？ | 强-强/强-弱/弱-强/弱-弱 四种组合，比较成功率+成本 |
| Q5 | 重试几次边际收益最大？ | 固定复杂节点，记录每次重试的通过率，找最优停止点 |

### 13.6 已下载的相关论文

论文下载在 `papers/self-evolution/`，按分类：

| 分类 | 数量 | 代表性论文 |
|------|------|-----------|
| failures/ | 10 | Library Drift (2605.19576), Skill Shadowing (2605.24050), Misevolve (2509.26354), 遗忘 (2605.09315), 不忠实自我演化 (2601.22436), 安全风险 (2604.16968), 健康演化 (2606.06114), Self-Bias (2402.11436), 进步或退步 (2407.05013), Skill Drift (2605.10990) |
| frameworks/ | 18 | Socratic-SWE, GEA, SkillRL, EXG, CoEvoSkills, Ratchet, Skill1, Scaling Laws, SkillDAG, GraSP, Voyager, Reflexion, Self-Refine, 符号学习自演化, SEW, AutoRefine, EvoDS, MemCoder |
| surveys/ | 4 | Self-Evolving 综述 (2508.07407), SkillEvolBench (2605.24117), SEAGym (2606.17546), PACE (2606.08106) |
