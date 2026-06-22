# Workflow v2 计划

> 2026-06-21 更新
> v1 计划已归档到 `project/to-do-future/DSL/`，那份是完整 DSL 自迭代系统的远期设计。
> v2 是当前要实现的简化版，基于学长意见 + 127 篇文献风险评审 + 34 篇记忆系统调研 + ECC 深度分析。
> ECC（github.com/affaan-m/ECC，218k 星）验证了经验自动提取路线可行，但它的"LLM judgment 够用 + 无 gate"路线不适合科研垂域。我们借鉴了 ECC 的 15 条工程细节，同时保留了 ECC 没有的 4 项差异化壁垒：deterministic verifier / replay regression / human gate / sandbox + 状态树。

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

### CLI 选型：opencode

使用 opencode CLI 作为所有 agent 节点的执行器。

```text
理由：
  免费开源（Go 编写，无 API 调用费外的许可成本）
  兼容性最好（支持 Anthropic/OpenAI/Gemini/Groq/OpenRouter 等主流 provider）
  功能较全（非交互 run 模式、管道输入、JSON 输出、session 续接、文件附加）
  较为稳定（Go 二进制，无 Python 依赖地狱）
  支持 MCP 工具集成
  支持 JSONC 项目配置（opencode.json）
```

参考文档：`C:\Users\27370\Desktop\project\opencode-linux-install-and-noninteractive.md`

#### opencode 非交互调用方式

```bash
# 基本调用（workflow runner 用这种方式启动 agent 节点）
opencode run -q "节点指令内容" --dir /path/to/mirror --model provider/model-id

# 管道输入（把上下文喂给 agent）
cat context.md | opencode run -q "基于以下上下文执行任务" --dir /path/to/mirror

# JSON 输出（workflow runner 解析 agent 输出）
opencode run -q "任务指令" --format json --dir /path/to/mirror

# 附加文件
opencode run -q "分析这篇论文" -f paper.pdf -f notes.md --dir /path/to/mirror
```

#### workflow runner 调用 opencode 的模式

```text
每个 agent 节点：
  1. workflow runner 构造节点指令（从 workflow.yaml 的 instruction + 提示词备注 + SKILL + 记忆检索结果拼接）
  2. workflow runner 调用 opencode run --dir /临时镜像路径 --model 配置的模型
  3. opencode 在临时镜像的工作目录内执行
  4. agent 输出写到 stdout，workflow runner 捕获
  5. workflow runner 记录 attempt_capsule

每个 script 节点：
  1. workflow runner 直接调用 Python 脚本
  2. 不启动 opencode，不启动 LLM
```

#### opencode 在 Magnus 集群上的部署

```text
Gustation 上的 opencode 安装：
  curl -fsSL https://opencode.ai/install | bash
  → 安装到 ~/.opencode/bin/opencode

API provider 配置：
  环境变量方式（Magnus job 注入提交者密钥）：
    export OPENAI_API_KEY=...      （由 Magnus 环境变量提供）
    或 opencode.json 配置自定义 endpoint

项目配置：
  临时镜像内放 opencode.json（从 project-flow 节点复制）
  指定 model / provider / MCP servers
```

#### 关键注意事项

```text
- opencode run 每次创建独立会话，无连续性 → 每个节点是独立 agent 调用
- --dangerously-skip-permissions 用于自动化（临时镜像已隔离，可安全使用）
- --dir 指定临时镜像工作目录，确保 agent 只在镜像内操作
- --format json 适合 workflow runner 程序化解析输出
- session 续接用 --session 或 --continue（自迭代质询场景需要 fork 历史 agent 时使用）
```

### 工作 workflow 拓扑（9 步）

基于用户框架 + 物理通用检查节点：

```text
1. pdf_preprocessing        [agent→script]  PDF 提取文字/公式/图表，曲线图特殊处理
    ↓
2. paper_reading            [agent]  论文阅读 + 搜索资料&记忆 + 确认原论文无明显疏漏
    ↓
3. reproduction_design      [agent]  设计复现目标（哪些可复现、分几部分、各部分关系）
    ↓
4. theory_and_implementation [agent]  理论推导 + 数值脚本编写
    ↓
5. theory_check             [agent]  检查理论/数值是否符合论文，判断是我们错了还是论文错了
    ↓
6. run_and_monitor          [agent→script]  运行程序 + 监视收敛性/稳定性/异常
    ↓
6.5 physical_verification   [agent→script]  物理通用检查（能量守恒/光学定理/极限趋势/截断收敛）
    ↓
7. result_analysis          [agent]  分析结果是否符合预期，反思原因，双向归因
    ↓
8. reproducibility_selfcheck [agent]  确认数值结果不是瞎猫碰上死耗子（重跑/参数扰动/网格收敛）
    ↓
9. summary_and_report       [agent]  总结经验 + 添加记忆 + 自迭代报告 + 人类复现报告
    ↓
   export_bundle            [script]  taint check + whitelist + manifest
```

### 各节点详细说明

#### 1. pdf_preprocessing [agent→script]

```text
agent:
  - 识别论文结构（摘要/方法/结果/附录/参考文献）
  - 识别图表类型（曲线图/示意图/数据表/流程图）
  - 曲线图特殊处理：提取坐标轴/数据点/图例，标记为待对比目标

script:
  - pdftotext -layout 提取文字
  - pdfimages 提取图片
  - 公式提取（OCR 或 LaTeX 识别）
  - 输出结构化"论文内容包"（文字 + 图表引用 + 公式 + 元数据）
```

#### 2. paper_reading [agent]

```text
- 阅读论文内容包
- 搜索外部资料（arXiv/Google Scholar/官方文档）补充背景
- 检索向量记忆库（有没有复现过类似论文）
- 确认原论文无明显疏漏（参数完整？方法可复现？引用可追溯？）
- 输出：论文理解报告 + 疏漏清单 + uncertainty 标记
```

#### 3. reproduction_design [agent]

```text
- 分析哪些图/表/结论可以复现
- 拆分复现目标（可能各部分有联系，也可能独立）
- 例如：Fig2 透射谱 + Fig3 模式分析，共享几何材料但独立验证
- 输出：reproduction_targets.yaml（每部分的依赖关系、所需参数、验收标准）
- 这一步等价于生成 case_workflow.yaml 的核心内容
```

#### 4. theory_and_implementation [agent]

```text
- 理论推导（解析公式、近似条件、假设）
- 数值脚本编写（Python/COMSOL Java/Magnus 作业配置）
- 代码必须消费 physics_formalization 输出的结构化物理 spec
- 输出：代码文件 + 推导笔记 + 运行配置
```

#### 5. theory_check [agent]

```text
- 检查理论推导是否符合论文
- 检查数值脚本实现是否正确
- 如果不符：判断是我们错了还是论文错了
- 指出错误、风险、不足
- 输出：理论检查报告 + 归因结论
```

#### 6. run_and_monitor [agent→script]

```text
agent:
  - 构造 Magnus job 提交参数
  - 监视 job 状态（pending/running/success/failed/timeout）

script:
  - 提交 Magnus job
  - 轮询 job 状态
  - 收集 job 输出（stdout/log/result files）
  - 监视收敛性、数值稳定性、异常行为
```

#### 6.5 physical_verification [agent→script]

```text
agent:
  - 读论文方法类型（解析/数值/仿真/实验对比）
  - 选适用的检查项
  - 调用对应脚本
  - 交叉验证检查项之间的关系
  - 判断结果合理性

script（检查项库）:
  - energy_conservation.py     散射+吸收+消光 = 1
  - optical_theorem.py          前向散射虚部 = 总截面
  - limit_behavior.py           大球 Qext→2，小球 Rayleigh 极限
  - truncation_convergence.py   N 项 vs N+1 项 < 阈值
  - causal_symmetry.py          因果性/对称性/单位制一致性
  - numerical_sanity.py         无 NaN/无负截面/无超光速

按论文类型选不同检查项：
  解析散射（Mie/Rayleigh）：能量守恒 + 光学定理 + 极限趋势 + 截断收敛
  FEM 仿真（COMSOL）：能量守恒 + 网格收敛 + 对称性 + 边界条件一致性
  有效介质近似：静态极限 + 长波极限 + 体积分数约束
```

#### 7. result_analysis [agent]

```text
- 分析结果是否符合预期
- 如果不符：反思原因
  - 代码 bug？
  - 物理假设错了？
  - 论文参数不对？
  - 数值精度不够？
- 消费 6.5 物理通用检查的结论做归因
  - 物理检查通过但结果和论文不符 → 可能是论文用了不同假设
  - 物理检查失败 → 代码或物理形式化一定有错，不用怀疑论文
- 输出：结果分析报告 + 归因结论
```

#### 8. reproducibility_selfcheck [agent]

```text
- 确认数值结果不是瞎猫碰上死耗子
- 按论文类型选不同级别的自检：
  解析公式复现 → 检查极限行为 + 收敛性
  数值仿真复现 → 参数扰动 + 网格收敛
  实验对比复现 → 误差棒范围内的 robustness
- 输出：可复现性自检报告
```

#### 9. summary_and_report [agent]

```text
- 总结复现过程
- 自行总结经验
- 添加记忆（写入向量记忆库，带 trust_level + utility_score）
- 提交自迭代报告（给自迭代 agent 看）
- 提交人类复现报告（给 PI 看，必须区分 pipeline/job/physical）
- 输出：自迭代报告 + 人类报告 + memory_delta
```

### 节点类型统计

```text
agent 节点：  8 个（1-8 步，export 是纯脚本）
script 节点： 2 个（6.5 的检查脚本库 + export_bundle）
agent→script：3 个（1, 6, 6.5 先 agent 判断再 script 执行）

为什么大部分是 agent：
  这是科研工作流，不是工程流水线
  每一步都需要判断、归因、调整
  但 6.5 的物理检查脚本和 export 是确定性的
```

---

## 三层经验系统

```text
提示词备注    每节点 ≤3 条    AI 加，人可见，轻量 lifecycle
    ↓
SKILL         几十到几百条    evidence gate（2+ case 或人工确认）
  └── 蓝图    每个 SKILL 下 0~N 个    执行模板，从属于 SKILL
    ↓
向量记忆库    几十万条        不人工治理，程序化治理
```

### SKILL 与蓝图的从属关系

```text
SKILL = 方法论（为什么这么做、什么时候做、注意什么）
蓝图  = 执行模板（具体怎么跑、参数填什么、提交什么 job）

一个 SKILL 可以有多个蓝图
一个蓝图只从属于一个 SKILL
一个 SKILL 可以没有蓝图（纯方法论，如 paper_reading_skill）
```

示例：

```text
optics-comsol-batch SKILL
  ├── 蓝图：Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
  │     COMSOL job 怎么提交、资源怎么配、license 怎么挂
  ├── 蓝图：Mie_sphere_sweep.magnus.blueprint.yaml
  │     Mie 参数扫描 job 模板
  └── 蓝图：Degiron_mode_analysis.magnus.blueprint.yaml
        Degiron 模式分析 job 模板

optics-mie-theory SKILL
  ├── 蓝图：Mie_analytical_python.magnus.blueprint.yaml
  │     纯 Python 解析计算运行模板
  └── 蓝图：Mie_array_effective_medium.magnus.blueprint.yaml
        球阵有效介质计算运行模板

optics-paper-reading SKILL
  └── （无蓝图，纯方法论）
```

### 自迭代时的修改关系

```text
自迭代改 SKILL 内容      → 可能需要同步改/加/删其下的蓝图
自迭代改蓝图参数         → 不需要改父 SKILL 的方法论
自迭代新增蓝图           → 必须挂到某个已有 SKILL 下
自迭代新增 SKILL         → 可以不带蓝图（纯方法论）
```

### 回传白名单对应调整

```text
自迭代允许修改：
  ├── .codex/skills/<skill>/SKILL.md           方法论
  ├── .codex/skills/<skill>/blueprints/*.yaml   该 SKILL 下的蓝图
  ├── prompt_notes/                            提示词备注
  ├── forbidden_regions/                       禁区
  └── governance_report.md                     治理报告
```

### 四层经验的平衡

```text
经验碎片（只发生过一次）    → 向量记忆库
反复出现的模式（2+ case）   → SKILL candidate
具体执行模板（参数/job 配置）→ 蓝图（从属于 SKILL）
节点级小经验                → 提示词备注
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
- 更新走自迭代 workflow 的 evidence gate + replay gate + human gate

### 蓝图

- 从属于某个 SKILL，不能独立存在
- 描述具体执行模板：Magnus job 参数、资源配额、license 挂载、输入输出路径
- 修改走自迭代 workflow 的 replay gate + human gate
- 新增蓝图必须挂到已有 SKILL 下
- 蓝图修改不需要改父 SKILL 方法论，但 SKILL 方法论修改可能需要同步蓝图

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

### 自迭代拓扑（5 步）

基于用户框架：

```text
1. concurrent_review         [并发 agent×10]  审查每个工作 workflow + 质询
    ↓
2. cluster_and_plan          [agent]  聚类相似方法/技巧，规划 skill 修改
    ↓
3. concurrent_skill_work     [并发 agent×M]  每个 skill/蓝图发子 agent 工作
    ↓
4. validate_and_replay       [agent→script]  验证新 skill 无错误 + 对旧任务泛用性
    ↓
5. generate_report           [agent]  生成自迭代报告
    ↓
   human_gate                [human]  人工确认
    ↓
   apply_or_quarantine       [script]  accept / quarantine / reject
```

### 各步骤详细说明

#### 1. concurrent_review [并发 agent×10]

```text
触发条件：未整理的工作 workflow run 累计 ≥ N（如 10 篇）

每个子 agent 负责一篇论文的 workflow run：

子 agent 信息源（分层）：
  第一级（必读）：
    - 工作 workflow 的最终报告（人类可见的那种输出上下文）
    - attempt_capsule + critic_verdict
    - 项目输出文件夹（代码/图/verifier 输出）
    - 工作向量记忆库（只读，看检索了哪些记忆、哪些有用）

  第二级（按需，发现疑点时）：
    - fork 某次压缩前或某个工作节点的 workflow agent 提起质询
    - 这需要 project-flow 支持恢复中间状态
    - 初期不实现，只读第一级

质询核心（确定为什么）：
  - 本可以复现的内容没有复现 → 漏掉了什么
  - 本可查记忆的内容反复造轮子 → 记忆系统没起作用
  - 本可总结的经验没有出现在 workflow 的报告 → agent 总结能力不足
  - workflow 的报告错误归因 → 甩锅给论文/参数但实际是自己错了
  - workflow 工作错误 → 执行层面的错误

子 agent 输出：
  - 每篇论文的审查报告
  - 质询记录（如果 fork 了历史 agent）
  - 发现的问题清单 + 严重度分级
```

#### 2. cluster_and_plan [agent]

```text
输入：10 篇论文的审查报告 + 历史已整理的 run 资料 + 记忆库

任务：
  - 通过最终报告和记忆，初步确认哪些论文复现中有相似处理方法
  - 识别跨论文的物理技巧
  - 识别重复出现的失败模式
  - 规划：准备分几个 skill / 是否修改原 skill
  - 判断哪些经验值得上升为 SKILL，哪些留在向量记忆库

输出：
  - skill 修改计划（新增几个 / 修改几个 / 废弃几个）
  - 每个 skill 的需求规格
  - 禁区（forbidden region）建议
  - 提示词备注修改建议
```

#### 3. concurrent_skill_work [并发 agent×M]

```text
每个 skill（或有关联的多个 skill）发一个子 agent：

子 agent 加载：
  - 自迭代专用 SKILL（skill_writing_guide 等）
  - 该 skill 的需求规格
  - 相关的历史 capsule 和审查报告（只读）
  - 现有工作 SKILL 内容（只读，作为分析对象）

子 agent 产出：
  - 新 skill 内容 / 修改后的 skill 内容
  - applies_when / does_not_apply_when / source_capsules
  - 修改理由和预期效果
  - 写到新 copy 文件夹，不动原始
```

#### 4. validate_and_replay [agent→script]

```text
agent:
  - 检查新 skill 格式合规
  - 检查适用边界完整性
  - 检查 source_capsule 链接有效
  - 检查安全规则未被削弱

script:
  - novelty_check：与现有 SKILL 去重（ADD/MERGE/REPLACE）
  - replay_regression：跑 replay suite
    - replay_mie_simple
    - replay_mie_lspr
    - replay_comsol_smoke
    - replay_report_boundary
    - replay_workflow_schema
  - 检查 PASS→FAIL count
  - 检查成本不显著上升
  - 检查安全/隐私规则未削弱

接受条件：
  当前任务有净收益
  且 replay 无关键退化
  且成本不显著上升
  且安全规则未削弱
```

#### 5. generate_report [agent]

```text
- 汇总本轮自迭代的全部活动
- 列出所有 skill 修改 / 新增 / 废弃
- 列出所有 replay 结果
- 列出所有风险警告（project-flow 回传白名单拒绝的修改尝试）
- 列出人工待确认项
- 生成自迭代治理报告
```

### 关键约束

```text
- 自迭代 workflow 拓扑人工写死，不可自动改
- 自迭代 workflow 节点指令人工写死，不可自动改
- 自迭代系统不允许迭代自己
- 所有产出必须过 human gate
- 自迭代 workflow 自己也要产 capsule（元治理留痕）
- 回传白名单：只接受 SKILL candidate / 备注建议 / forbidden region / 治理报告
- 清单外修改 → 拒绝 + 记录风险警告 + 反馈给下次自迭代
```

### 激活条件

```text
论文复现 workflow 跑通至少 5-10 个真实 case 后。
没有足够 capsule 就没有东西可聚类。
没有真实失败就没有 evidence 可提 candidate。
```

### fork 质询的远期规划

```text
初期（v2）：
  只读 capsule + 报告 + 产出物，不 fork agent
  覆盖 80% 情况

远期：
  第一级发现疑点但无法确认时，fork 历史 agent 质询
  需要 project-flow 支持：
    - 存 workflow 执行过程中的中间 checkpoint
    - 至少存 agent 对话的压缩前后版本
    - 用 opencode --session 续接历史会话
  覆盖剩余 20%
```

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
  ├── 在 Gustation 上安装 opencode
  ├── 写物理通用检查脚本（energy_conservation.py 先写一个）
  ├── 写最小 workflow runner（9 步固定拓扑，用 opencode run 调 agent）
  ├── 跑通一个真实 Mie case
  └── 记录什么真的断了

第二步：project-flow 最小版
  ├── project_flow.py（snapshot / checkout / log）
  ├── 增量存储（本地）
  ├── 临时镜像生成
  └── 回传白名单守门

第三步：Magnus job 集成
  ├── workflow → Magnus job 提交
  ├── job 状态轮询 → 回传处理
  └── 密钥由 Magnus 注入

第四步：针对性加治理（只加真断的）
  ├── run_manifest.yaml
  ├── attempt_capsule.yaml
  └── 最小 replay suite

第五步：记忆系统
  ├── qdrant + Qwen3-Embedding + Qwen3-Reranker-8B
  ├── 写入侧 trust_level + 注入检测
  ├── store routing
  └── 定期治理 API

第六步：自迭代 workflow
  ├── 等 5-10 个 case 积累
  ├── 实现 5 步元 workflow（并发审查 / 聚类 / 并发 skill 工作 / 验证 / 报告）
  ├── human gate
  └── 回传白名单

第七步：多后端同步 + 可视化
  ├── Gustation rsync 同步
  ├── GitHub private repo 同步
  └── mermaid / HTML 状态树可视化

第八步：评估
  ├── baseline A/B/C/D 对比
  └── benchmark disclosure
```

---

## 借鉴 ECC 的工程细节

> 来源：ECC（github.com/affaan-m/ECC，218k 星）深度分析
> 详细人话解释见 `notes/ECC_takeaways_human_language-CN.md`

### 从 ECC 借鉴并已纳入 v2 设计的 15 条

| # | ECC 机制 | 在 v2 中的应用 |
|---|---------|---------------|
| 1 | hook 100% fire | workflow runner 每节点自动产 capsule，不依赖 agent 自觉 |
| 2 | SIGUSR1 cooldown | 自迭代触发条件加 cooldown（距上次 > 1 小时） |
| 3 | tail 采样 | 自迭代只读最近 N 篇审查报告，不读全部历史 capsule |
| 4 | confidence 按频次初始赋值 | utility_score 初始值：1-2 次→0.3 / 3-5 次→0.5 / 6-10 次→0.7 / 11+→0.85 |
| 5 | /learn-eval 四裁决 | quality_gate 用 Save/Improve then Save/Absorb into X/Drop |
| 6 | 5 层自循环过滤 | 自迭代只审 change_type=paper_reproduction 的节点，不审自己的产出 |
| 7 | secret redaction 正则 + 看门狗 | 回传处理脚本对 memory_delta 跑 secret redaction + 8 秒超时 |
| 8 | 数据放 ~/.claude 外 | 临时镜像数据放 /mirror/ 下，不放 opencode 默认配置目录 |
| 9 | shortId 防覆盖 | project-flow 节点用随机短 ID（S_a3f2），SKILL 用 kebab-case 描述性 ID |
| 10 | SUMMARY marker 幂等 | capsule 加 processed 字段，自迭代只选 processed=false |
| 11 | blueprint adversarial review gate | theory_check 带 anti-pattern catalog 逐条挑刺，全修完才过 |
| 12 | blueprint cold-start brief | 每节点 prompt 含完整上下文，不依赖 agent 记得前序状态 |
| 13 | session-guardian 三门控 | 自迭代触发：未整理≥10 + cooldown + 无工作 workflow 在跑 + 初期人工确认 |
| 14 | profile 三档控制 | 按 risk_level 控制 agent 工具权限（low/medium/high） |
| 15 | plan-orchestrate agent chain | 远期按论文类型选不同 agent 链，初期固定拓扑 |

### ECC 没有而我们有的差异化壁垒

| 我们有 | ECC 没有 | 为什么重要 |
|--------|---------|-----------|
| deterministic verifier（物理通用检查）| 完全没有 | 科研复现需要物理不变量验证，不能靠 LLM judgment |
| replay regression suite | 完全没有 | 改了 SKILL 不知道旧任务退化没有，长期使用必然 Library Drift |
| human gate（所有自迭代产出）| /evolve 直接生成 | 自迭代产出不经验证直接进长期工件，是 Misevolution 的直接入口 |
| sandbox / 临时镜像 / 状态树 | 完全没有 | ECC 直接改用户目录，不能回滚不能对比，黑箱不可复现 |

### 相对 ECC 的核心改良

```text
ECC 的范式：在线自演化与执行耦合，LLM judgment 够用，无 gate
  → 适合日常 coding（verifier 就是 go build / go test）
  → 不适合 AI4S（需要物理正确性 + 同行评审可复现性）

我们的范式：生产 worker 与 meta-evolver 严格分离
  → 工作 workflow 跑在隔离 Magnus 容器里，产出是 ephemeral + immutable
  → 自迭代跑在另一个容器里，读工作产出（只读），产出走 gate
  → 科学输出（COMSOL capsules）保持 deterministic + auditable
  → 满足同行评审期刊的 reproducibility mandate
```

---

## 一句话

```text
先跑通，再加治理。
固定拓扑，迭代经验。
人工管流程，自动管经验。
自迭代不迭代自己。
借鉴 ECC 的工程细节，保留 verifier/replay/gate/sandbox 四项壁垒。
```
