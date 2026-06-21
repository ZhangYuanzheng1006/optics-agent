# Project-Flow 计划

> 2026-06-20 v2 更新
> project-flow 是比 workflow 更高一层的系统：它管的是整个项目状态的演化，不是单次论文复现的执行。
> 本质是给项目做一个类 git 的状态树版本控制系统，但每个 commit 是全部系统状态的完整快照。
> v2 更新：明确节点内容结构、临时镜像机制、回传白名单守门、自迭代权限分层、已整理/未整理标注。

---

## 核心概念

```text
workflow    管的是"一次论文复现怎么跑"
自迭代      管的是"经验怎么治理和更新"
project-flow 管的是"整个系统的状态怎么演化"
```

---

## 状态节点的完整内容

每个 project-flow 节点包含以下全部状态，作为一个不可分割的整体：

```text
一个状态节点 = 完整系统快照
  │
  ├── CLI 配置
  │     模型、MCP 配置、参数
  │
  ├── 工作 workflow 全套
  │     ├── workflow.yaml + schema + prompts
  │     ├── 蓝图（.magnus/.blueprints/）
  │     ├── SKILL（.codex/skills/ 中工作 workflow 用的）
  │     └── 向量记忆库（工作 workflow 写入的碎片）
  │
  ├── 自迭代 workflow 全套
  │     ├── workflow.yaml + schema + prompts
  │     ├── 蓝图（自迭代专用）
  │     ├── SKILL（自迭代专用，不允许被自迭代修改）
  │     └── 向量记忆库（自迭代专用）
  │
  ├── 历史上下文
  │     ├── 已整理的 workflow run 列表
  │     │     每次 run 的 capsule + verdict + outcome + 产出引用
  │     ├── 未整理的 workflow run 列表
  │     │     同上，等待自迭代处理
  │     └── 人工介入记录
  │
  ├── 历史 workflow（已跑完的完整记录）
  │     run_001 / run_002 / ...
  │
  ├── AGENTS.md
  ├── params/
  └── context/
```

### 工作 workflow 和自迭代 workflow 的共享与分离

```text
              分离                  共享
yaml/蓝图     ✅ 两套不同的拓扑      -
prompts       ✅ 两套不同的指令      -
SKILL         ✅ 各自专用            -
  工作 SKILL   光学复现方法论         -
  自迭代 SKILL 经验蒸馏/治理方法论    -
向量记忆库     ✅ 各自专用            -
  工作记忆库   论文复现碎片           -
  自迭代记忆库 治理经验碎片           -
```

自迭代 agent 改的是工作 workflow 的 SKILL，但用的是自迭代 workflow 的 SKILL。两套 SKILL 完全不同域。

### 已整理 / 未整理标注

```text
工作 workflow 跑完 → run 标记为"未整理" → 放入历史上下文
未整理数量 ≥ N（比如 10）→ 触发自迭代 workflow
自迭代 workflow 跑完 → 这 N 个标记为"已整理" → 产出新节点
```

自迭代 workflow 可以访问：
- 当前未整理的 N 次 run 资料
- 之前已整理的历史 run 资料
- 人工介入记录

所有资料对自迭代 agent 都是**只读**的。修改写到新 copy 的文件夹。

任何一次状态改变都生成一个新节点，旧节点不可变。

---

## 状态改变的 3 种类型

```text
├── paper_reproduction    跑了一篇论文复现
├── self_iteration        自迭代了一轮 skill/备注
└── human_intervention    人工改了什么（SKILL/规则/参数/记忆）
```

只有这 3 种。没有第 4 种。

每种改变都会：
1. 从当前状态节点生成临时镜像
2. workflow 在临时镜像内运行
3. workflow 结束后传回变化
4. project-flow 脚本按白名单处理回传
5. 创建新状态节点
6. 旧节点保持不变

---

## 临时镜像机制

每次 workflow 启动时，project-flow 从当前节点生成一个临时镜像：

```text
project-flow 节点（持久、不可变）
  ↓ 复制
临时镜像（可变、隔离）
  │
  ├── CLI 配置（从节点复制）
  ├── workflow.yaml + schema + prompts（从节点复制）
  ├── SKILL（从节点复制，只读挂载或可读可写取决于 workflow 类型）
  ├── 向量记忆库快照（从节点复制，可读可写）
  ├── 工作目录（空，agent 在这里操作）
  │     ├── reproduction_test/private/<case>/
  │     ├── 产出物
  │     └── attempt_capsules/
  └── 临时配置（run_id、case_id、retry_budget 等）

workflow 在镜像内跑
  ↓ 产出 attempt_capsule + 产出物 + 变化清单
  ↓ 传回
project-flow 脚本处理回传
  ↓ 白名单检查
新 project-flow 节点（持久、不可变）
```

### 工作 workflow 的临时镜像

```text
工作 workflow 镜像：
  ├── 工作 workflow.yaml + prompts     可执行
  ├── 工作 SKILL                       只读（工作 workflow 不改 SKILL）
  ├── 工作向量记忆库快照               可读可写（检索 + 写入碎片）
  ├── 自迭代 workflow 全套             不包含（工作 workflow 看不到自迭代系统）
  ├── 工作目录                         可读可写
  └── AGENTS.md                        只读
```

### 自迭代 workflow 的临时镜像

```text
自迭代 workflow 镜像：
  ├── 自迭代 workflow.yaml + prompts   可执行
  ├── 自迭代 SKILL                     只读（不允许被自迭代修改）
  ├── 自迭代向量记忆库快照             可读可写
  ├── 工作 workflow 全套               只读数据（作为分析对象）
  │     ├── 工作 workflow.yaml         只读
  │     ├── 工作 SKILL                 只读（自迭代 agent 读它们是为了改它们）
  │     ├── 工作蓝图                   只读
  │     └── 工作向量记忆库             只读
  ├── 历史上下文                       只读
  │     ├── 已整理 run 的 capsule + verdict
  │     ├── 未整理 run 的 capsule + verdict
  │     └── 人工介入记录
  ├── 新 copy 文件夹                   可读可写（修改建议写这里）
  └── AGENTS.md                        只读
```

关键区别：自迭代 agent 眼里，工作 workflow 的 SKILL 不是"我要执行的规则"，而是"我要分析的对象"。

### 向量记忆库的隔离

```text
工作 workflow → 复制工作记忆库快照 → 在快照内检索和写入 → 传回 memory_delta
自迭代 workflow → 复制自迭代记忆库快照 → 在快照内检索 → 传回 memory_delta

两个记忆库完全分离，互不干扰。
工作 workflow 不影响自迭代记忆库。
自迭代 workflow 不影响工作记忆库（自迭代读工作记忆库是只读的）。
```

### 并行支持（初期可不支持）

```text
S3 → 镜像A → 跑论文4 → S4
  → 镜像B → 跑论文5 → S5
```

同一节点可生成多个临时镜像，各自创建子节点。记忆库合并时需要冲突消解。初期串行更简单。

---

## 回传白名单守门机制

project-flow 回传处理脚本是纯 Python 程序，不是 agent，不启动 LLM。它不信任 workflow 的任何输出结构，只按预定义的白名单处理回传。

### 工作 workflow 回传白名单

```text
允许修改：
  ├── reproduction_test/private/<case>/    产出物（代码、报告、图、verifier 输出）
  ├── attempt_capsules/                    capsule 文件
  └── memory_delta.json                    工作向量记忆库变化清单

拒绝（记录风险警告）：
  ├── .codex/skills/              → 警告：工作 workflow 试图改 SKILL
  ├── workflows/                  → 警告：工作 workflow 试图改 workflow.yaml
  ├── .magnus/.blueprints/        → 警告：工作 workflow 试图改蓝图
  ├── AGENTS.md                   → 警告：工作 workflow 试图改项目规则
  ├── CLI 配置                    → 警告：工作 workflow 试图改 API 配置
  └── 自迭代 workflow 全套         → 警告：工作 workflow 试图改自迭代系统
```

### 自迭代 workflow 回传白名单

```text
允许修改（仍走 human gate）：
  ├── .codex/skills/              SKILL candidate（对工作 SKILL 的修改建议）
  ├── prompt_notes/               提示词备注修改建议
  ├── forbidden_regions/          forbidden region 建议
  └── governance_report.md        治理报告

拒绝（记录风险警告）：
  ├── workflows/                  → 警告：自迭代试图改 workflow 拓扑
  ├── .magnus/.blueprints/        → 警告：自迭代试图改蓝图
  ├── AGENTS.md                   → 警告：自迭代试图改项目规则
  ├── CLI 配置                    → 警告：自迭代试图改 API 配置
  ├── 自迭代 workflow 全套         → 警告：自迭代试图迭代自己
  └── reproduction_test/          → 警告：自迭代试图改产出物
```

### 风险警告处理

即使 agent 脑残了，project-flow 脚本也不会接受清单外的修改：

```text
agent 把 workflow.yaml 删了     → 脚本拒绝，workflow.yaml 不变
agent 把 API key 换了           → 脚本拒绝，CLI 配置不变
agent 把自迭代 SKILL 改了       → 脚本拒绝，自迭代系统不变
agent 把 AGENTS.md 重写了       → 脚本拒绝，项目规则不变
                                → 全部记录为风险警告
```

风险警告存入新节点的元数据，并反馈给下次自迭代作为输入：

```yaml
node_id: S11
parent: S10
change_type: self_iteration
validation:
  schema_check: pass
  replay_regression: pass
  safety_check: pass
  human_gate: pending
risk_warnings:
  - severity: high
    type: unauthorized_modification_attempt
    detail: "自迭代 agent 试图修改 workflows/paper_reproduction.workflow.yaml"
    action: rejected
    file: workflows/paper_reproduction.workflow.yaml
  - severity: critical
    type: unauthorized_modification_attempt
    detail: "自迭代 agent 试图修改自迭代 workflow 自身的 SKILL"
    action: rejected
    file: .codex/skills/self_iteration/skill_writing_guide/SKILL.md
accepted_changes:
  - path: .codex/skills/optics-comsol-batch/SKILL.md
    type: skill_modified
    diff_hash: abc123
  - path: prompt_notes/implementation_note_003.md
    type: note_added
```

风险警告的二次价值：如果某个 agent 反复试图修改不允许的文件，可能是 SKILL 写得不够清楚或 prompt 设计有误导。下次自迭代时把风险警告作为"上次尝试了什么不该做的"输入，帮助自迭代 agent 调整行为。

---

## 自迭代的权限分层

```text
自迭代 agent 加载的（可执行规则）：
  ├── 自迭代 workflow.yaml
  ├── 自迭代专用 SKILL（experience_distillation / skill_writing_guide / replay_testing / safety_audit / governance_report）
  ├── 自迭代专用提示词
  └── 自迭代专用向量记忆库
  → 这一套不允许被自迭代修改

自迭代 agent 看到的（只读数据）：
  ├── 工作 workflow 的 yaml / 蓝图 / SKILL / 提示词    ← 作为普通文件
  ├── 未整理的 N 次 run 的 capsule + verdict + 产出
  ├── 之前已整理的 run 的 capsule + verdict + 产出
  └── 人工介入记录
  → 这些是分析对象，不是执行对象

自迭代 agent 产出的（新 copy 文件夹）：
  ├── SKILL candidate（对工作 workflow SKILL 的修改建议）
  ├── 提示词备注修改建议
  ├── forbidden region 建议
  └── 治理报告
  → 写到新 copy 的文件夹，不动原始
```

自迭代 agent 眼里，工作 workflow 的 SKILL 不是"我要执行的规则"，而是"我要分析的对象"。这个分离防止了自迭代 agent 混淆"我在用的规则"和"我在改的规则"。

### 自迭代专用 SKILL 内容

```text
自迭代 SKILL/
  ├── experience_distillation    如何从 capsule 聚类失败模式
  ├── skill_writing_guide        如何写合格的 SKILL（有 applies_when / does_not_apply_when）
  ├── replay_testing             如何跑 replay suite 判断退化
  ├── safety_audit               如何检查安全规则未被削弱
  └── governance_report          如何写治理报告
```

这些是"怎么做好自迭代"的方法论，和工作 workflow 的"怎么复现光学论文"完全不同域。

### 自迭代的历史访问范围

```text
只看当前分支的历史：  S0→S1→...→S10，只看这条链
不看其他分支：        跨分支对比是 project-flow 的 compare 操作做的事
```

### 自迭代产出怎么变成新节点

```text
自迭代跑完 → 产出新 copy 文件夹（含 SKILL candidate 等）
  → replay_regression（script）
  → safety_check（script）
  → human_gate（人工确认）
  → accept → project-flow 创建新节点，合并修改到工作 workflow 的 SKILL
  → reject → 创建节点但标记"rejected"（自迭代失败也有留痕）
```

human gate 之前创建"pending"节点，gate 通过后转正式节点，gate 拒绝则标记"rejected"。这样自迭代本身的失败/拒绝也可审计。

---

## 树结构

```text
S0 (初始空状态)
│
├── S1 [paper] 论文1：Mie 单球
│   │
│   ├── S2 [paper] 论文2：Mie 球阵
│   │   │
│   │   ├── S3 [paper] 论文3：Degiron Fig3
│   │   │   │
│   │   │   ├── S4 [self_iter] 第1轮自迭代
│   │   │   │   └── S5 [human] 人工确认 skill 修改
│   │   │   │
│   │   │   └── S6 [human] 人工补 COMSOL 模板
│   │   │
│   │   └── S7 [self_iter] 第1轮自迭代（从 S2 直接迭代）
│   │
│   └── S8 [paper] 论文3：Degiron Fig3（不同顺序）
│       └── S9 [paper] 论文2：Mie 球阵（在 S8 之后重跑）
│
└── S10 [paper] 论文3：Degiron Fig3（另一条分支）
    └── S11 [paper] 论文2：Mie 球阵
        └── S12 [paper] 论文1：Mie 单球
```

同一个父节点可以有多个子节点，形成分支。分支来源：

- 不同论文处理顺序
- 自迭代 vs 不自迭代
- 人工介入产生分叉
- 回滚后重新跑（从历史节点创建新分支）

---

## 节点元数据

每个状态节点有一个元数据文件：

```yaml
node_id: S4
parent: S3
created: 2026-06-21T14:30:00Z
change_type: self_iteration   # paper_reproduction | self_iteration | human_intervention

# 变更来源
source:
  workflow_run_id: run_0015
  case_id: Degiron_2009_Fig3
  trigger: batch_after_10_cases

# 变更内容
changes:
  skills_added: []
  skills_modified:
    - path: .codex/skills/optics-comsol-batch/SKILL.md
      diff_hash: abc123
  skills_deprecated: []
  notes_added:
    - node: implementation
      note: "检查边界条件是否和论文一致"
  memories_added: 47
  memories_modified: 12
  memories_deprecated: 3
  workflow_yaml_modified: false
  agents_md_modified: false

# 验证状态
validation:
  schema_check: pass
  replay_regression: pass
  safety_check: pass
  human_gate: pass

# 存储信息
storage:
  full_snapshot: false          # 首次为 true，后续增量
  incremental_from: S3
  delta_size: 2.3MB
  snapshot_path: states/S4/
```

---

## 存储策略

44T 磁盘足够，但不需要每次全量复制。

```text
states/
  S0/                         完整快照（初始状态）
    skills/
    blueprints/
    memory_db/
    workflows/
    agents.md
    ...
  
  S1/                         增量（相对 S0）
    delta.json                变更清单
    files/                    只存变化的文件
    memory_delta/             只存新增/修改的记忆条目
  
  S2/                         增量（相对 S1）
    ...
```

存储估算：

```text
SKILL/YAML/AGENTS：  ~1-5MB/状态，文本文件
向量库增量：         每轮 run 新增 ~50-200 条记忆，每条 ~1-4KB
                   增量 ~0.2-1MB/状态
capsule/manifest：  ~50-200KB/状态

单状态增量：        ~1-7MB
1000 个状态：       ~1-7GB
10000 个状态：      ~10-70GB

44T 磁盘绰绰有余。
```

特殊处理：
- 每 50 个节点做一次完整快照（避免增量链太长）
- 向量库用 qdrant snapshot 或逐条增量
- 大文件（PDF/COMSOL .mph）不存入状态树，只存路径引用

---

## 核心操作

### checkout：切换到某个状态

```text
project-flow checkout S4
  → 从 S4 恢复全部系统状态
  → skills/ blueprints/ memory_db/ workflows/ AGENTS.md 全部回到 S4 时刻
  → 后续操作从 S4 开始创建新分支
```

用途：回滚到某个已知良好状态，重新开始。

### diff：对比两个状态

```text
project-flow diff S3 S4
  → 列出所有变化的文件
  → 列出新增/修改/废弃的记忆条目
  → 列出新增/修改/废弃的 SKILL
  → 列出 workflow.yaml 是否变化
  → 列出 AGENTS.md 是否变化
```

用途：精确知道某次自迭代到底改了什么。

### log：查看状态树

```text
project-flow log
  → 显示从当前节点到根的路径
  → 每个节点的 change_type、时间、变更摘要

project-flow log --tree
  → 显示整棵树的结构
  → 每个分支的起点和当前状态
```

### branch：管理分支

```text
project-flow branch list
  → 列出所有分支

project-flow branch create experiment-order-3-2-1
  → 从当前节点创建命名分支

project-flow branch delete experiment-order-3-2-1
  → 删除分支（只删引用，不删状态节点）
```

### compare：跨分支对比

```text
project-flow compare S4 S12
  → 对比两条不同分支的最终状态
  → SKILL 内容差异
  → 记忆库内容差异
  → verifier 结果差异
  → 回答"处理顺序重要吗？"
```

用途：做论文顺序对比实验。

### rollback：回滚

```text
project-flow rollback S3
  → 从当前节点回到 S3
  → 不删除 S4 及其子节点
  → 从 S3 创建新分支继续工作
```

回滚不是删除历史，是创建新分支。旧分支保留用于对比。

### replay-from：从历史状态重跑

```text
project-flow replay-from S3 --case Degiron_2009_Fig3
  → 从 S3 状态出发，重新跑 Degiron 复现
  → 结果进入新节点 S3'
  → 可以对比 S3' 和原来的 S4，看结果是否一致
```

用途：验证结果可复现性。

### export：导出某个状态的完整快照

```text
project-flow export S4 --output /tmp/S4_snapshot
  → 导出 S4 的完整系统状态
  → 可用于分享、备份、迁移
```

---

## 与 workflow / 自迭代的关系

```text
project-flow 是外壳
  ├── paper_reproduction workflow 在 project-flow 内运行
  │     └── 每次运行产出一个新状态节点
  │
  ├── 自迭代 workflow 在 project-flow 内运行
  │     └── 每次运行产出一个新状态节点
  │
  └── 人工介入直接修改当前状态
        └── 修改后产出一个新状态节点
```

```text
用户操作流程：

1. project-flow checkout S3        切换到某个状态
2. workflow run Degiron_Fig3       跑论文复现
   → 产出 S4 [paper_reproduction]
3. project-flow log                查看状态历史
4. （发现 S4 的 skill 有问题）
   project-flow rollback S3        回到 S3
5. 人工修改 SKILL
   → 产出 S3' [human_intervention]
6. workflow run Degiron_Fig3       重跑
   → 产出 S4' [paper_reproduction]
7. project-flow compare S4 S4'     对比两次结果
```

---

## project-flow 管理器

project-flow 本身是一个轻量 Python 程序，不是 agent，不启动 LLM。

```text
project_flow.py
  ├── checkout(node_id)
  ├── diff(node_a, node_b)
  ├── log()
  ├── branch(action, name)
  ├── compare(node_a, node_b)
  ├── rollback(node_id)
  ├── replay_from(node_id, case)
  ├── export(node_id, output_path)
  └── snapshot(changes)             被 workflow / 自迭代 / 人工调用
```

workflow runner 在每次 run 结束后调用 `snapshot()` 创建新节点。
自迭代 workflow 在每次迭代结束后调用 `snapshot()` 创建新节点。
人工介入后用户手动调用 `snapshot()` 创建新节点。

---

## 安全约束

```text
1. 旧状态节点不可变
   → 任何修改都创建新节点，不改旧节点
   → 即使是"修正错误"也创建新节点

2. 删除分支只删引用，不删状态节点
   → 状态节点只能归档，不能物理删除
   → 除非用户显式 project-flow gc --older-than 1year

3. 大文件不进状态树
   → PDF / .mph / 大数据文件只存路径引用
   → 引用路径失效时标记 orphan

4. 敏感数据不进状态树快照
   → secret.json / license.dat / SSH key 只存路径引用
   → 快照中对应位置留 placeholder + "see original path"

5. 向量库快照用增量，不每次全量
   → 只存新增/修改/删除的记忆条目
   → 每 50 个节点做一次完整快照
```

---

## 实现顺序

```text
第一步：最小 project-flow
  ├── project_flow.py 基础操作（snapshot / checkout / log / diff）
  ├── 增量存储
  └── 被 workflow runner 调用

第二步：对比和回滚
  ├── branch / rollback / compare
  └── 用于"自迭代改坏了→回滚→重跑"

第三步：实验管理
  ├── replay_from / export
  └── 用于论文顺序对比实验

第四步：清理和归档
  ├── gc / archive
  └── 长期状态节点管理
```

project-flow 不依赖 workflow 完成，可以并行开发。最小版本只需要 snapshot + checkout + log。

---

## 为什么 project-flow 重要

```text
1. 回滚精确    自迭代改坏了 → 回到任何一个历史状态
2. 对比可能    不同论文顺序 → 不同分支 → 对比结果
3. 因果归因    diff(S3,S4) → 精确知道改了什么导致什么
4. 实验可复现  拿到状态节点 → 从那个点复现后续实验
5. 人工介入留痕  改了什么 → 为什么改 → 产生什么影响
6. 自迭代安全   自迭代产出 → 回滚不影响旧状态
```

---

## 一句话

```text
project-flow 是项目状态的 git。
每个节点 = 完整系统快照（CLI + 工作 workflow 全套 + 自迭代 workflow 全套 + 历史上下文）。
状态改变只有 3 种：论文复现 / 自迭代 / 人工介入。
每次改变走临时镜像 → 回传白名单守门 → 新节点。
自迭代权限高于工作 workflow，但不允许迭代自己。
回传时 project-flow 脚本只接受白名单内的修改，其余拒绝并记录风险警告。
三者共同形成一棵可回滚、可对比、可审计的状态树。
```
