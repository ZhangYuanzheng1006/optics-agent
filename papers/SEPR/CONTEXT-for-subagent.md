# SEPR workflow-v3 文献阅读子 agent 上下文

## 1. SEPR 是什么

SEPR（self-evo-paper-repro）是 `optics_agent` 的姐妹工作区，用来实验“论文复现 + agent/skill 自迭代”。它把论文复现当作可验证的工程回归测试，而不是只追求一次性生成图。

当前 v3 设计假设：

- 有 4 个核心 agent：`main-agent`、`sub-agent`、`evolution-agent`、`sub-E-agent`。
- 复现 workflow 与自迭代 workflow 分开：复现负责读论文、提参数、实现、验证、报告；自迭代负责从复现经验里提取 skill/规则/风险。
- 允许子 agent / sub-subagent 分层委派，但需要明确上下文、输出协议、终止条件和证据边界。
- `.human/` 用中文给人类审阅；`.claude/` 用英文 prompt-engineered 版本给 Claude Code 执行。本次任务不写这两个目录。
- v3 的核心风险不是“能否跑起来”，而是：是否会误判复现成功、是否会空跑、是否会把错误经验沉淀成长期规则。

## 2. v3 设计十块概要

1. 提示词工程：`CLAUDE.md`、`SKILL.md`、spawn 模版拼接形成多层指令体系，靠 progressive disclosure 控制上下文。
2. 子 agent 系统：4 agent + subsubagent 形成层级委派，靠 spawn 拼接传递任务、上下文和输出协议。
3. 自迭代系统：evolution workflow 从复现失败/成功中提取经验，经过分类、裁决、人审后更新经验层。
4. 6 分类法：用 Save / Improve / Absorb / Fork / Archive / Drop 决定经验去向，并用 Tier-1/2/3 管理治理强度。
5. workflow 结构：复现约 11 步，自迭代约 6 步，要求固定阶段、明确产物、可追踪状态。
6. AI 判断复现正确性：重点防 self-bias、LLM-as-judge 偏差、verifier 被 reward hacking、假进步和错误成功声明。
7. 失败防护/防空跑：通过重跑轮数上限、终止判断、LoopTrap、缺口验证和显式 blocker 防止无限重试。
8. 记忆系统：memento + provenance 五要素记录事实、证据、来源、时间、适用范围，防止 memory pollution。
9. 蓝图扫描泛用：把可复用计算流程参数化成蓝图，支持参数扫描、workflow fork、replay 和 sweep。
10. 物理 verifier：三层检验为物理硬约束、极限退化、论文图量化比较，避免只用 LLM 文字判断。

## 3. 子 agent 阅读时要带的问题

每篇文献都按以下问题阅读：

- 它支持 v3 的哪一块设计？
- 它暴露了 v3 的哪类风险？
- 它给出的工程经验能否落到 SEPR：prompt、agent、workflow、memory、provenance、verifier、blueprint、报告？
- 它依赖什么前提？这些前提在 SEPR 是否成立？
- 它的成功证据是否充分？是否可能只是 toy benchmark 或 LLM judge 过拟合？
- 它是否提醒我们需要 human gate、schema gate、retry budget、termination gate、external verifier 或 artifact provenance？

## 4. 输出格式

每篇或每组相关论文输出一条，格式如下：

```text
- 来源：arXiv ID / 标题 / 文件路径
- 类型：经验 / 风险 / 反例 / 综述
- 适用块：v3 十块中的编号和名称
- 结论：一句话说明对 v3 的启发
- 经验/风险：具体说明，不写空泛“有帮助”
- 严重度：高 / 中 / 低
- 建议动作：Save / Improve / Absorb / Fork / Archive / Drop 中的一个或多个
```

## 5. 严重度判定

- 高：会导致错误复现成功声明、长期记忆污染、无限空跑、不可复现、越权改规则、成本爆炸或物理错误被掩盖。
- 中：会降低稳定性、可维护性、可审计性、上下文质量或多 agent 协调效率，但有明确缓解手段。
- 低：主要是提示词质量、命名、文档、工程易用性等改进。

## 6. 本轮 A-K 分类

- A：提示词工程 agent。
- B：子 agent 系统/编排。
- C：自迭代系统。
- D：6 分类法/裁决/知识管理。
- E：workflow 结构/11 步复现。
- F：AI 判断复现正确性。
- G：失败防护/防空跑。
- H：记忆/provenance。
- I：蓝图扫描/参数化。
- J：物理 verifier。
- K：综述。
