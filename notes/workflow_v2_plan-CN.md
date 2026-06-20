# Workflow v2 计划

> 2026-06-20
> v1 计划已归档到 `project/to-do-future/DSL/`，那份是完整 DSL 自迭代系统的远期设计。
> v2 是当前要实现的简化版，基于学长意见 + 127 篇文献风险评审 + 34 篇记忆系统调研。

---

## 核心定位

```text
垂域可验证复现系统
  agent 只在不确定断点介入
  确定性流程用脚本
  固定 workflow 拓扑，人工管
  自迭代只迭代 skill / 提示词备注
  自迭代系统本身不允许迭代自己
```

不是 agent 框架。不是 DSL 自演化平台。是一个让光学论文复现更难假进步、更可审计的执行系统。

---

## 与 v1 的关键区别

| 维度 | v1 | v2 |
|------|----|----|
| 核心卖点 | agent workflow 框架 | 光学复现 benchmark + verifier + 可审计执行 |
| workflow 拓扑 | 可自迭代 | 人工写死，不可自动改 |
| 节点拆分 | 倾向多 agent | 只有智能断点才用 agent，其余脚本 |
| 自迭代范围 | workflow + skill + 蓝图 + AGENTS | 只迭代 skill 内容 + 提示词备注 |
| 自迭代系统能否迭代自己 | 未明确 | 禁止，全部 human gate |
| 记忆系统 | 不治理靠检索 | 写入侧过滤 + 效用标记 + 定期离线治理 |
| 评估 | 模糊 | baseline A/B/C/D 对比 |
| 复杂度 | 7 层治理 + 5 批 schema | 先跑通再针对性加治理 |

---

## 固定 workflow 拓扑

```text
paper_intake           [agent]  论文到底要复现什么
    ↓
physics_formalization  [agent]  几何/材料/方程/边界/缺什么
    ↓
parameter_table        [agent→script]  agent 提取，script 校验 schema
    ↓
implementation         [agent→script]  agent 写代码，script 跑 verifier
    ↓
physical_verify        [script]  能量守恒/Rayleigh/Qext/截断收敛
    ↓
result_comparison      [script]  和论文曲线比 RMSE/peak shift
    ↓
report_generation      [agent]  写报告，必须区分 pipeline/job/physical
    ↓
export_bundle          [script]  taint check + whitelist + manifest
```

4 个 agent 断点：intake、formalization、implementation、report。
4 个脚本节点：parameter_table 校验、physical_verify、result_comparison、export。

为什么是这 4 个 agent 断点：
- intake：论文意图无法规则化
- formalization：物理建模需要判断，缺参需要识别
- implementation：代码生成需要适应不同物理问题
- report：措辞边界需要判断

为什么其他 4 个是脚本：
- parameter_table 校验：schema 固定
- physical_verify：数学不变量
- result_comparison：数值对比
- export：taint/whitelist/manifest 纯规则

---

## 三层经验系统

```text
提示词备注    每节点 ≤3 条    AI 加，人可见，轻量 lifecycle
    ↓
SKILL         几十到几百条    evidence gate（2+ case 或人工确认）
    ↓
向量记忆库    几十万条        不人工治理，程序化治理
```

### 提示词备注

- 每节点最多 3 条，append 但超过 3 条时保留最相关的
- 新备注 supersede 旧备注，不叠加
- 备注是建议性的，不是强制指令
- 必须有来源 case_id
- 更新走自迭代 workflow 的 human gate

### SKILL

- 生命周期：candidate → active → deprecated
- promotion：至少 2 个 case 帮助过，或人工确认
- deprecation：2 次被判定 hurt 或 inapplicable
- 必须有 applies_when / does_not_apply_when / source_capsules
- 更新走自迭代 workflow的 evidence gate + replay gate + human gate

### 向量记忆库

- 规模：几十万条
- 检索：向量召回 top-100 → store routing → 8B rerank → top-5 注入
- 不人工治理
- 程序化治理：
  - 实时：标记 outcome/importance，不删除
  - 定期：API 合并相似、衰减降权、冲突消解、硬删除 deprecated 且 contribution < 0
- 安全：写入侧 trust_level + 注入检测，检索侧 data/instruction 隔离

---

## 硬件部署

```text
向量库:       qdrant 或 chroma（本地，CPU 够用）
embedding:    Qwen3-Embedding-0.6B
reranker:     Qwen3-Reranker-8B INT8 常驻 RTX 5880 Ada（~8GB VRAM）
检索流程:     向量召回 top-100 → store routing → 8B rerank → top-5
COMSOL:       CPU + RAM，不抢显卡
```

---

## 自迭代 workflow（元 workflow）

```text
collect_capsules          [script]  收集 N 轮 capsule + verdict
    ↓
cluster_failure_modes     [agent]  聚类失败模式
    ↓
diagnose_root_cause       [agent]  归因（必须查原始 capsule）
    ↓
propose_candidates        [agent]  提 SKILL candidate / 备注建议 / forbidden region
    ↓
novelty_check             [script]  与现有 SKILL 去重 ADD/MERGE/REPLACE
    ↓
quality_gate              [agent]  检查适用边界、触发条件、source_capsule
    ↓
replay_regression         [script]  跑 replay suite，检查 PASS→FAIL
    ↓
safety_check              [script]  安全规则未削弱，taint 未传播
    ↓
human_gate                [human]  所有产出必须人工确认
    ↓
apply_or_quarantine       [script]  accept / quarantine / reject + 治理报告
```

关键约束：
- 自迭代 workflow 拓扑人工写死，不可自动改
- 自迭代 workflow 节点指令人工写死，不可自动改
- 自迭代系统不允许迭代自己
- 所有产出必须过 human gate
- 自迭代 workflow 自己也要产 capsule（元治理留痕）

激活条件：论文复现 workflow 跑通至少 5-10 个真实 case 后。

---

## 评估体系

```text
Baseline A: 聪明人 + Claude Code
Baseline B: 固定脚本 / 固定 pipeline
System C:   DSL workflow，无自迭代
System D:   + 自迭代 skill/备注 + replay gate
```

比较指标：
- 物理 verifier 通过率
- 缺参发现率
- 复现耗时
- 过度声明率
- replay regression 数
- 人工介入次数
- 成本

---

## 实施顺序

```text
第一步：跑通最小 case（不建治理基础设施）
  ├── 写 Mie 能量守恒 verifier
  ├── 写最小 workflow runner（8 节点固定拓扑）
  ├── 跑通一个真实 Mie case
  └── 记录什么真的断了

第二步：针对性加治理（只加真断的）
  ├── run_manifest.yaml
  ├── attempt_capsule.yaml
  └── 最小 replay suite

第三步：记忆系统
  ├── qdrant + Qwen3-Embedding + Qwen3-Reranker-8B
  ├── 写入侧 trust_level + 注入检测
  ├── store routing
  └── 定期治理 API

第四步：自迭代 workflow
  ├── 等 5-10 个 case 积累
  ├── 实现 10 节点元 workflow
  └── human gate

第五步：评估
  ├── baseline A/B/C/D 对比
  └── benchmark disclosure
```

---

## 一句话

```text
先跑通，再加治理。
固定拓扑，迭代经验。
人工管流程，自动管经验。
自迭代不迭代自己。
```
