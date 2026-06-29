# 新上下文 Handoff 文档

> 2026-06-21
> 给新 agent 的完整交接说明。请新 agent 读完这份文档后再开始工作。

---

## 项目是什么

`optics_agent` 是北京大学光学组的一个项目，目标是**用 AI agent 系统辅助微纳光学论文的复现工作**。

长远方向：
```text
论文复现 → 可复用的科研蓝图 → case/DSL + 参数扫描 → 新的科学探索
```

论文复现是蓝图的回归测试，不是最终目标。光学是当前用例，工作流要能泛化到不熟悉的科研领域。

仓库根目录：`C:\Users\27370\Desktop\project\optics_agent`
GitHub：`https://github.com/PKU-QNO/optics-agent-zyz`
当前分支：`main`
用户环境：Windows + PowerShell，SSH 到 Gustation 集群

---

## 本次会话干了什么（2026-06-20 ~ 2026-06-21）

这是一次超长会话，主要完成了**大量调研 + 设计决策 + 方向调整**，但**没有写代码**。

### 1. 文献调研（161 篇 PDF）

- `papers/self-evolution/`：127 篇，自演化 agent / agent workflow 方向，10 个子目录
- `papers/memory/`：34 篇，向量记忆系统 / agent 进化方向，5 个子目录
- 每个子目录有 `README_summaries.md`（子 agent 生成的逐篇摘要）
- 两个总索引：`papers/self-evolution/README_expanded_literature.md` 和 `papers/memory/README_memory_literature.md`

### 2. 风险评审

- `notes/self_evolution_workflow_risk_review.md`（英文）：从 7 类扩展到 24 类风险
- `notes/self_evolution_workflow_risk_review-CN.md`（中文）：新增 16 条风险
- `notes/workflow_risks_and_recommendations.md`：按优先级排序的 19 项风险建议
- v1 风险笔记已归档到 `project/to-do-future/DSL/`

### 3. 方向调整（关键）

学长意见采纳：
- **核心卖点不是 agent 框架，而是垂域可验证复现效果**
- 只有需要智能介入的断点才拆 agent，能写死的写死
- DSL 优势是假设不是结论，需要 baseline 验证

### 4. v2 计划重写

- v1 计划（完整 DSL 自迭代）归档到 `project/to-do-future/DSL/`
- 新建 v2 计划：`notes/workflow_v2_plan-CN.md`
- 新建 v2 风险：`notes/workflow_v2_risks-CN.md`

v2 核心：固定 9 步工作流拓扑，只迭代 skill / 提示词备注，自迭代禁止迭代自己。

### 5. project-flow 设计

- `notes/project_flow_plan-CN.md`
- 项目级状态树版本控制（类 git）
- 节点 = 完整系统快照
- 3 种状态改变：论文复现 / 自迭代 / 人工介入
- 临时镜像 + 回传白名单守门 + 自迭代权限分层
- Magnus job 集成 + 多后端存储（本地/Gustation/GitHub）+ 可视化

### 6. 记忆系统设计

- `notes/memory_system_literature_review-CN.md`
- 三层经验系统：提示词备注 → SKILL（含蓝图）→ 向量记忆库
- 硬件：qdrant + Qwen3-Embedding-0.6B + Qwen3-Reranker-8B INT8 常驻 RTX 5880 Ada
- 原计划"不治理靠检索"被 Zombie Agents / MRMMIA / EvoMemBench 证伪
- 改为：写入侧过滤 + 效用标记 + 定期离线治理

### 7. ECC 深度分析

- `notes/ECC_analysis-CN.md`：详细分析报告
- `notes/ECC_takeaways_human_language-CN.md`：15 条借鉴细节的人话解释
- ECC（218k 星）验证了经验自动提取路线可行
- 借鉴 15 条工程细节，保留 4 项差异化壁垒（verifier/replay/gate/sandbox）
- 核心改良：Worker 与 Evolver 严格分离

### 8. 学长汇报

- `notes/advisor_report-CN.md`：全中文正式汇报

---

## 当前设计状态

### 核心定位

```text
垂域可验证复现系统
  agent 只在不确定断点介入
  确定性流程用脚本
  固定 workflow 拓扑，人工管
  自迭代只迭代 skill / 提示词备注
  自迭代系统本身不允许迭代自己
```

### CLI 选型

**opencode**（免费开源、兼容性最好、功能较全、较稳定）
参考：`C:\Users\27370\Desktop\project\opencode-linux-install-and-noninteractive.md`
调用方式：`opencode run -q "prompt" --dir /mirror --model provider/model-id`

### 工作 Workflow（9 步，固定拓扑）

```text
1. pdf_preprocessing        [agent→script]  PDF 提取文字/公式/图表
2. paper_reading            [agent]  论文阅读 + 搜索 + 确认无疏漏
3. reproduction_design      [agent]  设计复现目标，拆分
4. theory_and_implementation [agent]  理论推导 + 代码
5. theory_check             [agent]  对抗式审查，双向归因
6. run_and_monitor          [agent→script]  运行 + 监视
7. physical_verification    [agent→script]  物理通用检查
8. result_analysis          [agent]  分析 + 归因
9. reproducibility_selfcheck [agent]  排除瞎猫碰上死耗子
10. summary_and_report      [agent]  经验 + 记忆 + 双报告
```

### 自迭代 Workflow（5 步，积累 10 篇后触发）

```text
1. concurrent_review     [并发×10]  审查 + 质询
2. cluster_and_plan      [agent]  聚类 + 规划 skill 修改
3. concurrent_skill_work [并发×M]  每个 skill 一个子 agent
4. validate_and_replay   [agent→script]  验证 + replay regression
5. generate_report       [agent]  治理报告 + human gate
```

### 三层经验系统

```text
提示词备注    每节点 ≤3 条    AI 加，人可见
  ↓
SKILL         几十到几百条    evidence gate
  └── 蓝图    每个 SKILL 下 0~N 个    Magnus job 执行模板
  ↓
向量记忆库    几十万条        程序化治理
```

### project-flow 状态树

```text
节点 = 完整系统快照
  ├── CLI 配置
  ├── 工作 workflow 全套（yaml/蓝图/SKILL/记忆库）
  ├── 自迭代 workflow 全套（独立的一套）
  ├── 历史上下文（已整理/未整理 run）
  └── 人工介入记录

状态改变只有 3 种：论文复现 / 自迭代 / 人工介入
临时镜像隔离 → workflow 在镜像内跑 → 回传白名单守门 → 新节点
```

### 硬件

```text
向量库:    qdrant 或 chroma
embedding: Qwen3-Embedding-0.6B
reranker:  Qwen3-Reranker-8B INT8 常驻 RTX 5880 Ada（~8GB VRAM）
COMSOL:    CPU + RAM，不抢显卡
集群:      Magnus / Gustation（校园网，不能访问公网）
```

---

## 文件结构

### notes/（设计文档，本次会话主要产出）

```text
notes/
├── workflow_v2_plan-CN.md              ★ v2 计划主线（最重要）
├── workflow_v2_risks-CN.md             v2 风险笔记（21 项）
├── project_flow_plan-CN.md             project-flow 设计
├── memory_system_literature_review-CN.md  记忆系统调研
├── ECC_analysis-CN.md                  ECC 深度分析
├── ECC_takeaways_human_language-CN.md  ECC 15 条借鉴人话版
├── advisor_report-CN.md                学长汇报（全中文正式版）
├── workflow_risks_and_recommendations.md  风险按优先级排序
├── agent_skill_self_iteration.md       早期 agent skill 调研
├── agent_papers_survey.json            早期论文调研数据
└── self_improving_agent_search_results-EN.json
```

### project/to-do-future/DSL/（v1 归档，远期）

```text
project/to-do-future/DSL/
├── workflow_engine_design-CN.md        v1 完整 DSL 设计（40KB）
├── workflow_risk_review-CN.md          v1 风险评审（52KB）
└── workflow_risks_logic_order.md       v1 逻辑排序风险（19KB）
```

### papers/（文献库）

```text
papers/
├── self-evolution/                     127 篇，10 个子目录
│   ├── README_expanded_literature.md   总索引
│   ├── agent_skills/                   21 篇
│   ├── workflow_optimization/          11 篇
│   ├── multi_agent_orchestration/      14 篇
│   ├── memory_lifelong/                12 篇
│   ├── evaluation_benchmarks/          7 篇
│   ├── safety_governance/              7 篇
│   ├── scientific_agents/              6 篇
│   ├── tool_use/                       6 篇
│   ├── coding_agents/                  5 篇
│   ├── planning_reasoning/             6 篇
│   ├── frameworks/                     18 篇
│   ├── failures/                       10 篇
│   └── surveys/                        4 篇
│   （每个子目录有 README_summaries.md）
│
└── memory/                             34 篇，5 个子目录
    ├── README_memory_literature.md     总索引
    ├── memory_architectures/           8 篇
    ├── self_evolving_memory/           12 篇
    ├── memory_retrieval/               8 篇
    ├── memory_security/                2 篇
    └── memory_benchmarks/              4 篇
    （每个子目录有 README_summaries.md）
```

### workflows/（早期 v1 workflow，需更新到 v2）

```text
workflows/
├── ENGINE.md
├── paper_reproduction.workflow.yaml    ★ 还是 v1 的，需重写为 v2 9 步
├── schemas/
│   ├── workflow_schema.yaml            需加治理字段
│   └── params_schema.yaml
└── prompts/
```

### .codex/skills/（现有 skill）

```text
.codex/skills/
├── optics-agent-core/
├── optics-paper-reproduction/
├── optics-comsol-runtime/
├── optics-comsol-batch/
├── comsol-java-api/
├── optics-magnus-platform/
├── optics-magnus-artifacts/
└── optics-docker-images/
```

### 其他重要文件

```text
AGENTS.md                               项目规则（必读）
C:\Users\27370\Desktop\project\opencode-linux-install-and-noninteractive.md  opencode 使用文档
C:\Users\27370\Desktop\project\secret.json  密钥（不要读内容）
```

---

## 关键决策（必须遵守）

1. **核心卖点 = 垂域可验证效果，不是 agent 框架**
2. **固定 workflow 拓扑，人工管，不自动迭代拓扑**
3. **自迭代只迭代 skill / 提示词备注，不迭代 workflow / 蓝图 / AGENTS**
4. **自迭代禁止迭代自己，全部 human gate**
5. **只有智能断点用 agent，能写死的写死**
6. **Worker 和 Evolver 严格分离**（不同容器，只读边界）
7. **记忆库不治理靠检索被证伪**，必须写入侧过滤 + 定期治理
8. **先跑通再加治理**，不要过度设计
9. **DSL 优势是假设不是结论**，需要 baseline A/B/C/D 验证
10. **不创建新文件除非明确要求**；不 commit 除非明确要求

---

## 待办（按优先级）

### 立即要做（实现阶段）

```text
1. 查 5-10 篇提示词工程论文（1 天，限时）→ papers/prompt/
2. 写 energy_conservation.py + 最小 workflow.py（本地跑通 Mie case）
3. 打 Docker 镜像（workflow.py + opencode + MCP）
4. Magnus job 集成（注意：magnus login 用 162 地址，不是 gustation.phybench.cn）
5. project-flow 最小版（snapshot / checkout / log）
6. 实践 + 总结经验
```

### 实现细节待确认

```text
- opencode 在容器内调 LLM API 的 endpoint 是否在校园网内可达
  （https://openai.phybench.cn/v1 能不能从 Gustation 容器访问）
- MCP server 的 entry command 启动机制
- 记忆数据库是挂载还是复制快照（初期挂载，后期加隔离）
- SKILL 是挂载到 opencode skill 目录还是 workflow.py 自己读取注入（建议后者）
- project-flow 跑在本地 Docker 还是 Gustation（建议本地，做好迁移准备）
```

### 远期

```text
- 自迭代 workflow 实现（等 5-10 case 积累）
- 多后端同步（Gustation rsync + GitHub push）
- 状态树可视化（mermaid / HTML）
- baseline A/B/C/D 对比评估
- fork 质询功能（远期，需 project-flow 支持中间状态恢复）
```

---

## 关键风险提醒

1. **零实现**：所有设计都是纸面，没有代码。最大的风险是过度设计而不跑。
2. **DSL 价值未验证**：先跑通 Mie case 再说 DSL 有没有用。
3. **记忆安全**：Zombie Agents 攻击直接命中我们的架构，写入侧过滤是第一优先级。
4. **Gustation 网络限制**：只能访问校园网，不能访问公网。容器内不能 pip install / npm install（镜像预装）。
5. **不要碰 secret.json / license.dat / SSH key**。

---

## 给新 agent 的建议

1. **先读 `notes/workflow_v2_plan-CN.md`**，这是当前主线设计。
2. **再读 `AGENTS.md`**，这是项目规则。
3. **如果要做实现，从 `energy_conservation.py` 开始**，这是最小可验证单元。
4. **不要再改方案了**——设计已经足够，需要的是代码和跑通的结果。
5. **学长那两个问题要始终记住**：相比 Claude Code 的增益？相比固定脚本的区别？
6. **所有自迭代产出必须过 human gate**，这是不可妥协的。
7. **记忆库写入侧必须有 trust_level + 注入检测**，否则 Zombie 风险直接落地。

---

## 一句话

```text
设计已经完成，方向已经明确。
现在需要的不是更多设计，是第一个跑通的结果。
从 energy_conservation.py + 最小 workflow.py 开始。
```
