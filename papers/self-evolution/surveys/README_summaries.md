# PDF 文献摘要

## 2606.17546 SEAGym: An Evaluation Environment for Self-Evolving LLM Agents
- 文件：`2606.17546.pdf`
- 一句话结论：评价 self-evolving agent 不能只看最终分数，必须记录 harness 更新过程、快照、验证集、回放、迁移和成本。
- 核心方法/贡献：SEAGym 把 Harbor 兼容 benchmark 转成动态 self-evolution 任务源，支持 train batches、frozen update-validation、ID/OOD transfer、replay diagnostics、snapshot 和 cost records。
- 可用于我们 workflow 的经验：它把可变的 harness state 明确定义为 prompts、memory、skills、tools、middleware、workflow、project files 和 runtime config，正好对应 optics_agent 的可自迭代对象。
- 警告/风险：实验基于 Terminal-Bench/HLE 等 agent benchmark，不直接覆盖科学仿真；但评价结构比具体任务更可迁移。
- 可落到 optics_agent 的设计点：为 workflow 自迭代建立 snapshot 机制，每次修改 prompt/skill/workflow 后冻结版本，用旧任务 replay、新任务 transfer、成本和失败率共同判断是否接受。
- 优先级：高

## 2606.08106 PACE: Anytime-Valid Acceptance Tests for Self-Evolving Agents
- 文件：`2606.08106.pdf`
- 一句话结论：self-evolving agent 的关键薄弱点是“是否提交修改”的 acceptor；简单的“分数升高就接受”会在复用小验证集时自我 p-hacking。
- 核心方法/贡献：提出 PACE，把候选修改与当前版本在相同样本上做 paired anytime-valid sequential test，通过 e-process 达到证据阈值才 commit，并控制单次候选的 false-commit 概率。
- 可用于我们 workflow 的经验：自迭代不应只设计 proposer，还要设计 commit gate；每次 prompt、skill、workflow 修改都应有 paired comparison、阈值和拒绝路径。
- 警告/风险：论文主要验证 prompt-level evolution，未实证复杂技能、代码和多 agent 拓扑；且保证是 per-decision，不是整个长期运行的全局错误率。
- 可落到 optics_agent 的设计点：在 `update_artifacts` 节点加入 acceptance test：同一批复现/诊断样例上比较旧版与新版，只有显著改善且无回归时才写入 AGENTS、SKILL 或 workflow。
- 优先级：高

## 2605.24117 SkillEvolBench: Benchmarking the Evolution from Episodic Experience to Procedural Skills
- 文件：`2605.24117.pdf`
- 一句话结论：当前 agent 常能局部适应任务，但很难把一次性经验稳定抽象成可复用技能；原始轨迹有时比压缩技能更有效。
- 核心方法/贡献：SkillEvolBench 用 180 个任务、6 个真实 agent 环境和 role-conditioned task families，测试从 acquisition 轨迹与 verifier feedback 到 frozen skill library 的转化能力。
- 可用于我们 workflow 的经验：它清楚区分 acquisition、replay、context shift、adversarial shortcut 和 composition，适合评估 optics_agent 的技能是否真能泛化到新论文、新图和组合任务。
- 警告/风险：skill 写得更多或资源库更大不一定更好，可能引入 episode-specific drift、procedural clutter 和信息丢失。
- 可落到 optics_agent 的设计点：保留失败轨迹与完整 run logs，不只保存压缩后的 lesson；技能更新后用旧复现 replay、相似论文迁移、反作弊检查和组合任务测试。
- 优先级：高

## 2508.07407 A Comprehensive Survey of Self-Evolving AI Agents: A New Paradigm Bridging Foundation Models and Lifelong Agentic Systems
- 文件：`2508.07407.pdf`
- 一句话结论：self-evolving agent 是从静态模型、在线适配、多 agent 编排走向多 agent 自演化的范式，核心是基于环境反馈持续优化 agent 组件。
- 核心方法/贡献：提出统一反馈 loop，包括 System Inputs、Agent System、Environment、Optimisers；综述 foundation model、prompt、memory、tool、workflow、communication 等不同演化目标，并提出安全、性能保持、自治演化三原则。
- 可用于我们 workflow 的经验：这篇提供 self-evolving agent taxonomy，可作为 optics_agent 自迭代架构索引，明确每次演化到底改的是模型、提示、记忆、工具、workflow 还是通信机制。
- 警告/风险：综述范围很广，具体 commit 机制和科学复现评价不足；若没有 SEAGym/PACE 类 gate，容易只形成“持续修改”的幻觉。
- 可落到 optics_agent 的设计点：在 workflow 设计中加入 evolution target 字段和安全层级：先保证不破坏既有复现与敏感资源，再追求性能提升，最后才允许自主修改结构。
- 优先级：中
