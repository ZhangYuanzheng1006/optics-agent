# ECC 可借鉴的 15 条工程细节——人话版

> 2026-06-21
> 每条用大白话解释 + 在我们 project-flow / workflow 中的具体应用方式

---

## 1. hook 100% fire 机制

**人话**：别指望 agent 自己记得写总结。用一个跟 agent 无关的、每次必定触发的机制来记录。

ECC 的做法是：agent 每用一次工具（写文件、跑命令），系统层就自动记一条日志。不管 agent 愿不愿意，都会记。

**在我们这里怎么用**：

```text
workflow runner（Python 脚本）每跑完一个节点，
不管 agent 输出了什么，自动生成一条 attempt_capsule。

不是在 agent 的 prompt 里写"请记得总结经验"——
agent 可能忘、可能偷懒、可能编造。

而是 workflow runner 自己从 agent 的 stdout、
verifier 输出、文件变化里提取结构化记录。

agent 不参与"决定记什么"，agent 只负责干活。
记录是 workflow runner 的事。
```

---

## 2. SIGUSR1 cooldown

**人话**：刚跑完一轮治理，别马上再跑一轮。设个冷却时间。

ECC 的做法是：observer 收到信号后 60 秒内不再响应同类型信号。防止短时间内重复分析同一批数据，浪费 LLM 调用。

**在我们这里怎么用**：

```text
自迭代 workflow 跑完后，设一个 cooldown（比如 1 小时）。
1 小时内即使未整理的 case 又攒够了 10 篇，也不触发。

为什么？
  刚改完 SKILL，新的 capsule 还没来得及用新 SKILL 跑。
  马上又自迭代，会基于旧的 capsule 改 SKILL，改了又改，drift。

project-flow 里记录 last_self_iteration_time，
触发条件加一条：now - last_self_iteration_time > cooldown。
```

---

## 3. tail 采样

**人话**：自迭代 agent 读历史记录时，只读最近 N 条，别从头读到尾。

ECC 的做法是：observer 分析时只取 observations.jsonl 的最后 500 行。不读全部历史——全部历史可能有几万行，LLM 根本读不完，而且大部分是过时的。

**在我们这里怎么用**：

```text
自迭代 workflow 的 concurrent_review 步骤：
  每个子 agent 审查一篇论文的 workflow run。
  子 agent 读的是这一篇的 capsule + 报告 + 产出物。

但 cluster_and_plan 步骤需要看跨论文的模式：
  不读全部历史 capsule（可能有几百篇）。
  只读最近 N 篇的审查报告（比如最近 10 篇 + 之前已整理的摘要）。

具体：
  cluster_and_plan 的输入 =
    本轮 10 篇的审查报告（完整）
    + 之前已整理 run 的治理报告摘要（每篇 1-2 句）
    + 不读原始 capsule

如果需要更早的历史，自迭代 agent 可以主动查向量记忆库检索。
但默认注入的上下文只给最近的。
```

---

## 4. confidence 按频次初始赋值

**人话**：一条经验被遇到过几次，就给它打多高的初始分。次数少给低分，次数多给高分。

ECC 的做法：
```text
1-2 次 → 0.3（不太确定，建议但不强制）
3-5 次 → 0.5（有点把握了，相关时可以用）
6-10 次 → 0.7（很确定了，自动用）
11+ 次 → 0.85（核心经验，必须用）
```

**在我们这里怎么用**：

```text
向量记忆库每条记忆的 utility_score 初始值：

论文复现中发现一个技巧，第一次遇到 → utility_score = 0.3
第二次在不同论文又遇到 → 0.5
第三次 → 0.7
反复出现 → 0.85

检索时排序：
  score = 0.5 × embedding_similarity + 0.5 × utility_score

这样一条"出现过很多次的经验"即使和当前 query 语义相似度一般，
也会因为 utility_score 高而排到前面。

反过来，一条"只见过一次的碎片"即使语义很像，
也会因为 utility_score 低而被压下去。

升级到 SKILL 的条件：
  utility_score ≥ 0.7（相当于被验证过 6-10 次）
  或人工确认
```

---

## 5. /learn-eval 四裁决

**人话**：自迭代 agent 提了一条新经验，不是简单的"要"或"不要"，而是四种情况：

```text
Save           → 这条经验是新的、有用的、scope 合理 → 直接存
Improve then Save → 这条经验有料但写得不好 → 改一改再存
Absorb into X  → 这条经验其实应该并到已有的某条 SKILL 里 → 合并
Drop           → 这条经验太碎、太泛、重复了 → 扔掉
```

**在我们这里怎么用**：

```text
自迭代 workflow 的 quality_gate 节点用这四种裁决：

自迭代 agent 产出一条 SKILL candidate 后，
quality_gate agent 判断：

  Save → 新 SKILL，存为 candidate，等 replay + human gate
  Improve then Save → 告诉自迭代 agent 哪里要改，改完再评一次
  Absorb into [已有SKILL] → 不新建，把内容合并到已有 SKILL 里
  Drop → 说明为什么扔掉，记录到治理报告

比简单的 accept/reject 好在哪？
  "Absorb" 解决了"新经验和老经验其实是同一件事"的问题。
  "Improve then Save" 解决了"方向对但写得差"的问题。
  这两种情况在简单 accept/reject 下要么强行新建重复 SKILL，
  要么直接扔掉有价值的经验。
```

---

## 6. 5 层自循环过滤

**人话**：防止系统自己观察自己、自己评价自己、自己给自己打高分。

ECC 的做法是 5 层检查：这个 session 是不是 agent 自己跑的？是的话不记录。

**在我们这里怎么用**：

```text
自迭代 workflow 产出的 capsule、治理报告、SKILL candidate，
在下次自迭代 review 时不应该被当作"工作 workflow 的产出"来审查。

project-flow 的节点元数据里有 change_type 字段：
  paper_reproduction → 可以被自迭代 review
  self_iteration → 不可以被自迭代 review（这是自迭代自己的产出）
  human_intervention → 可以被自迭代 review（人工改了什么值得看）

自迭代 concurrent_review 步骤只筛 change_type=paper_reproduction 的 run。
self_iteration 类型的节点只读不审。

否则：
  自迭代 agent 审查自己上次的治理报告 →
  发现"上次做得挺好"（因为是自己做的）→
  Echoing，自己给自己正反馈 →
  drift。
```

---

## 7. secret redaction 正则 + 看门狗

**人话**：往记忆库里写东西之前，先把看起来像密钥的文本涂掉。用正则匹配，但加一个超时保护防止正则卡死。

ECC 的正则：
```text
匹配：api_key / token / secret / password / authorization / credentials / auth
后面跟着 8-256 字符的值
替换为 [REDACTED]
8 秒超时看门狗防止正则灾难性回溯
```

**在我们这里怎么用**：

```text
向量记忆库写入侧（memory_delta 回传到 project-flow 时）：

project-flow 回传处理脚本在合并 memory_delta 之前，
对每条新记忆的 content 跑一遍 secret redaction：

  匹配到 api_key=sk-xxxx → 替换为 api_key=[REDACTED]
  匹配到 token=abc123 → 替换为 token=[REDACTED]
  匹配到 password="xyz" → 替换为 password=[REDACTED]

正则用 ECC 的那个就行，加 8 秒超时。

这样即使 agent 把论文 PDF 里的 API key、
Magnus token、COMSOL license 内容写进了记忆库，
也不会泄露到向量库里被检索出来。

同时加注入检测：
  如果记忆内容里有命令式语句（"ignore previous instructions"之类），
  标记为 untrusted + 只能以 data 块注入，不能进 instruction。
```

---

## 8. 数据放 ~/.claude 外

**人话**：别把你的数据放在 agent 工具链的"敏感目录"里，否则 agent 的安全机制可能阻止你读写。

ECC 的做法是：把 observer 数据放在 `~/.local/share/ecc-homunculus/` 而不是 `~/.claude/`，因为 Claude Code 对 `~/.claude/` 有安全 guard，后台进程写入会被拦。

**在我们这里怎么用**：

```text
临时镜像的工作目录结构：

/mirror/
  ├── workspace/              agent 在这里干活（reproduction_test/、产出物/）
  ├── opencode.json           opencode 配置
  ├── skills/                 SKILL 文件（只读挂载）
  ├── blueprints/             蓝图文件（只读挂载）
  ├── memory_snapshot/        向量记忆库快照
  ├── capsules/               attempt_capsule 输出
  └── config/                 运行参数

不要把数据放在 opencode 的默认配置目录里。
opencode 的 ~/.config/opencode/ 只放配置，
数据放 /mirror/ 下自己的目录。

这样 opencode 的安全机制不会干扰我们的数据读写。
project-flow 回传时只读 /mirror/capsules/ 和 /mirror/workspace/ 的变化。
```

---

## 9. shortId 防覆盖

**人话**：给东西起 ID 时用随机短串，别用 1、2、3 递增编号。否则两个分支各自编了 S7，合并时冲突。

ECC 的做法是：instinct 用 `kebab-case-name`（如 `use-react-hooks-pattern`）而不是 `instinct_001`。

**在我们这里怎么用**：

```text
project-flow 节点 ID：

别用 S0, S1, S2, ...（递增）
用随机短 ID：S_a3f2, S_b7c1, S_d4e8

为什么？
  分支 A 跑了 3 篇论文 → S1, S2, S3
  分支 B 也跑了 3 篇论文 → S1, S2, S3
  合并分支时 S1 冲突——是分支 A 的还是分支 B 的？

用随机短 ID：
  分支 A → S_a3f2, S_b7c1, S_d4e8
  分支 B → S_f1a0, S_c3d2, S_e5b4
  永不冲突。

SKILL candidate ID 也一样：
  别用 skill_001
  用 comsol-matrix-factorization-workaround
  （kebab-case 描述性 ID，既防冲突又可读）
```

---

## 10. SUMMARY marker 幂等

**人话**：处理过的东西打个标记，下次别重复处理。

ECC 的做法是：observer 分析完 observations.jsonl 后，在文件里留一个 SUMMARY 标记。下次检测到这个标记就跳过。

**在我们这里怎么用**：

```text
attempt_capsule 里加一个 processed 字段：

  processed: false  → 未被自迭代审查过
  processed: true   → 已被自迭代审查过

自迭代 concurrent_review 只选 processed=false 的 capsule。

审查完后：
  capsule.processed = true
  capsule.reviewed_by = self_iteration_S_a3f2
  capsule.review_summary = "..."

project-flow 节点的"已整理/未整理"标注就是这个机制。
已整理 = processed=true
未整理 = processed=false

幂等保证：
  即使自迭代 workflow 中途崩了重跑，
  不会重复审查已经审查过的 capsule。
```

---

## 11. blueprint adversarial review gate

**人话**：做完计划后，派一个"杠精"agent 专门来挑刺。不是请人夸，是请人骂。骂完了所有 critical 问题都修了，计划才算过。

ECC 的做法是：blueprint 生成计划后，用最强模型（Opus）当 sub-agent，拿着 checklist + anti-pattern catalog 专门审查这个计划有什么问题。

**在我们这里怎么用**：

```text
theory_check 节点改造为对抗式审查：

  theory_check 不只是"检查对不对"，
  而是启动一个专门挑刺的 agent，
  带着光学复现的 anti-pattern catalog：

  Anti-patterns:
    - 几何参数和正文描述不一致（图里画的是圆柱，公式用的是球）
    - 材料介电常数只给了实部没给虚部（金属必须有虚部）
    - 边界条件用 PML 但没说厚度/层数
    - 观测量定义不明（"透射率"是功率比还是振幅比？）
    - 归一化条件缺失（截面单位是面积还是无量纲？）
    - 假设了长波极限但尺寸参数 x > 1
    - 用了有效介质近似但体积分数 > 40%

  agent 必须逐条检查，输出：
    - 每条 anti-pattern：PASS / FAIL / N/A
    - 所有 FAIL 的必须修
    - 修完重新检查
    - 全部 PASS 才进入下一步

这比"请检查一下对不对"强得多——
后者 agent 可能敷衍说"看起来没问题"，
前者必须逐条回答，有问题藏不住。
```

---

## 12. blueprint cold-start brief

**人话**：每一步的指令要写得足够完整，换一个全新的人来也能直接干活，不需要"你先看看上一步做了什么"。

ECC 的做法是：blueprint 的每个 step 都有一个 self-contained context brief——包含这一步需要的所有背景信息，fresh agent 可以直接开始。

**在我们这里怎么用**：

```text
每个 agent 节点的 prompt 构造：

不是：
  "请继续上一步的工作，实现数值脚本"
  （agent 不知道上一步做了什么）

而是：
  "论文：Degiron 2009 NJP Fig 3
   复现目标：SU-8 波导模式分析，neff vs wavelength
   物理形式化结果：geometry=..., materials=..., equations=...
   参数表：...
   上一步理论检查结论：...
   本步任务：编写 COMSOL Java 模型代码
   验收标准：代码可编译、exposes public static Model run()、
             output result table is configured
   相关 SKILL：optics-comsol-batch
   相关记忆：（向量检索 top-5）
   提示词备注：（≤3 条）"

这样即使每个节点是独立的 opencode run（无 session 连续性），
agent 也能直接干活。

workflow runner 负责把前序节点的输出结构化地注入当前节点的 prompt。
不依赖 agent 自己"记得"前序做了什么。
```

---

## 13. session-guardian 三门控

**人话**：自迭代不是随时都能跑的。要满足三个条件：人在工作时间、上次跑完过了一阵子、用户没在用电脑。

ECC 的三个条件：
1. 时间窗（8:00-23:00）
2. 项目 cooldown（同一项目至少间隔 N 秒）
3. idle 检测（用户 30 分钟没操作就不跑，可能不在电脑前）

**在我们这里怎么用**：

```text
自迭代 workflow 触发条件（全部满足才触发）：

1. 未整理的 case ≥ 10
2. 距上次自迭代 > cooldown（比如 1 小时）
3. 当前没有工作 workflow 在跑（不抢集群资源）
4. （可选）人工确认——初期不自动触发，手动 project-flow trigger

第 4 条初期很重要：
  自迭代改 SKILL 是高风险操作，
  初期应该人工说"开始自迭代"才跑。
  后期验证过 replay/gate 可靠了再自动触发。

时间窗和 idle 检测对我们不太适用——
我们跑在 Magnus 集群上，不是个人电脑。
但"不抢集群资源"是等价约束。
```

---

## 14. profile 三档控制

**人话**：给 agent 的自由度分三档。低风险的事多给自由，高风险的事收紧。

ECC 的三档：
- minimal：只保留基本安全 hook
- standard：默认，平衡质量和安全
- strict：额外提醒 + 更严的 guardrails

**在我们这里怎么用**：

```text
按节点的 risk_level 控制 agent 的工具权限：

low risk 节点（pdf_preprocessing、paper_reading）：
  agent 可以自由读文件、搜索、查记忆
  可以写工作目录
  不需要人工确认

medium risk 节点（implementation、run_and_monitor）：
  agent 可以读写工作目录
  可以提交 Magnus job
  产出物过 verifier
  不可以直接改 SKILL/蓝图/AGENTS

high risk 节点（summary_and_report、自迭代所有步骤）：
  agent 可以读工作目录
  可以写 capsule 和报告
  不可以提交 Magnus job（避免意外消耗资源）
  产出物过 human gate
  不可以改任何持久状态

实现方式：
  opencode run 的 --dangerously-skip-permissions 只在 low risk 开
  medium/high risk 用正常权限模式
  project-flow 回传白名单按 risk_level 分档
```

---

## 15. plan-orchestrate agent chain

**人话**：不同类型的任务自动派给不同的专家。不用一个 agent 干所有事。

ECC 的做法是：根据任务关键词（design/implement/test/refactor/security）自动选不同的 agent 链。

**在我们这里怎么用**：

```text
远期可以按论文类型自动选不同的 agent 链：

  解析散射论文（Mie/Rayleigh）：
    paper_reading → theory_check → implementation(Python) 
    → physical_verify(能量守恒+光学定理+极限) → report

  FEM 仿真论文（COMSOL）：
    paper_reading → theory_check → implementation(COMSOL Java) 
    → run_magnus_job → physical_verify(能量守恒+网格收敛) → report

  混合论文（解析+仿真）：
    paper_reading → theory_check → 
    parallel[implementation(Python) + implementation(COMSOL)] →
    parallel[physical_verify(解析) + run_magnus + physical_verify(仿真)] →
    cross_figure_consistency_check → report

但初期不需要——
9 步固定拓扑已经覆盖大部分情况。
等跑过 10+ 篇论文发现确实需要分链了再加。

现在只需要在 reproduction_design 节点的输出里
标明每部分的类型（analytical/fem/experimental），
后面节点根据类型选不同的 verifier 脚本就够。
```
