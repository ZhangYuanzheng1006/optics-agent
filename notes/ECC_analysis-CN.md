# ECC 深度分析报告

> 2026-06-21
> 基于 3 个子 agent 对 github.com/affaan-m/ECC 的深度阅读
> ECC：218k 星，跨 harness 的 agent 经验系统，10+ 个月日常使用打磨

---

## 一句话总结

```text
ECC 是"LLM judgment 够用 + 开放进化 + 通用复用"路线的工程化典范。
它验证了 instinct→skill 自动聚类路线可行，
但它没有 replay / human gate / sandbox / 状态树——
这四件事正是我们的差异化壁垒。
```

---

## ECC 的核心机制

### 自迭代闭环（8 层）

```text
1. 观察层：PreToolUse/PostToolUse hook 每次 tool call 触发
   → secret scrubbing → 5 层自动化过滤 → observations.jsonl

2. 提取层：Haiku 后台 observer 每 5 分钟或每 20 次 SIGUSR1 触发
   → tail -500 采样 → pattern 检测 → 写 instinct YAML

3. 评估层：confidence 动态调整（+0.05 确认 / -0.1 纠正 / -0.02 周衰减）
   → /learn-eval 手动质量门控（Save/Improve/Absorb/Drop 四裁决）

4. 聚类层：/evolve trigger 归一化聚类
   → cluster≥2 → skill / domain=workflow&conf≥0.7 → command / cluster≥3&avg≥0.75 → agent

5. 提升层：/promote 跨项目扫描
   → 出现在≥2 项目 && avg confidence≥0.8 → 写入 global

6. 共享层：/instinct-export / /instinct-import

7. 清理层：pending 30 天 TTL + observations 30 天清理 + observer idle 自退出

8. 应用层：evolved skill/command/agent 自动加载 → 影响下次 session → 回到 1
```

### instinct 格式

```yaml
---
id: use-react-hooks-pattern        # kebab-case, ≤128 字符
trigger: "when creating React components"
confidence: 0.65                    # 0.3-0.85 初始, 0.9 封顶
domain: "code-style"                # code-style/testing/git/debugging/workflow/file-patterns/security/general
source: "session-observation"       # session-observation/inherited/repo-analysis/promoted/auto-promoted
scope: project                      # project(默认)/global
project_id: "a1b2c3d4e5f6"          # git remote URL SHA256 前 12 字符
project_name: "my-react-app"
---

# Title
## Action
Always use functional components with hooks instead of class components.
## Evidence
- Observed 8 times in session abc123
- Last observed: 2025-01-22
```

### confidence 评分

| 观察次数 | 初始 confidence | 含义 |
|---------|----------------|------|
| 1-2 | 0.3 | tentative（建议但不强制）|
| 3-5 | 0.5 | moderate（相关时应用）|
| 6-10 | 0.7 | strong（自动批准应用）|
| 11+ | 0.85 | very strong |

动态调整：再次观察 +0.05 / 用户纠正 -0.1 / 每周无观察 -0.02。

### hook 触发机制

关键设计：不用 session end hook（v1 用 Stop hook 不可靠），改用 **PreToolUse + PostToolUse 每次 tool call 都触发**（100% fire）。

5 层自动化 session 过滤防止观察自己的 observer 造成自循环：
1. 只允许特定 entrypoint
2. minimal profile 直接退出
3. ECC_SKIP_OBSERVE=1 协作跳过
4. subagent 直接退出
5. 特定路径匹配退出

---

## 和我们 v2 的异同

### 相似的设计

| ECC 机制 | 我们 v2 对应 | 相似度 |
|---------|-------------|--------|
| instinct（原子 YAML + confidence）| 向量记忆库碎片 + utility_score | 概念相似，实现不同 |
| /evolve instinct→skill 聚类 | 自迭代 workflow cluster_and_plan | 相似 |
| confidence scoring | utility_score 运行时更新 | 相似 |
| pending 30 天 TTL | 定期治理 deprecated + 衰减 | 相似 |
| /learn-eval 质量门控 | human gate | 相似但 ECC 更细 |
| /promote project→global | SKILL candidate→active 升级 | 相似 |
| secret redaction 正则 | trust_level + 注入检测 | 我们更严 |
| 5 层自循环过滤 | 回传白名单守门 | 不同机制解决同类问题 |
| hook 100% fire | workflow runner 每节点产 capsule | 不同机制 |
| blueprint 5 阶段 + adversarial review gate | physics_formalization + theory_check | 概念相似 |

### ECC 没有的（我们的差异化）

| 我们有 | ECC 没有 | 影响 |
|--------|---------|------|
| replay regression suite | 无 | ECC 改了 skill 不知道旧任务退化没有 |
| human gate（所有自迭代产出）| /evolve --generate 直接生成 | ECC 的 skill 聚类没有验证 |
| sandbox / 临时镜像 | 无 | ECC 直接改用户 .claude 目录 |
| 状态树 / project-flow | 无 | ECC 不能回滚不能对比 |
| deterministic verifier | 无（靠 LLM judgment）| ECC 无物理通用检查 |
| 回传白名单守门 | 无 | ECC 没有"agent 脑残了怎么办"的防线 |
| SKILL→蓝图从属 | 无（blueprint 是纯 Markdown skill）| ECC 没有执行模板概念 |
| 向量记忆库 + 8B reranker | 无（instinct 是文件系统）| ECC 不做大规模语义检索 |
| trust_level / provenance | 无 | ECC 的 instinct 来源不区分信任度 |
| data/instruction 隔离 | 无 | ECC 的 instinct 直接进 instruction |
| store routing | 无 | ECC 只有 project/global 两层 |
| 工作和自迭代分离 | 不分离（同一个 agent 同一个 session）| ECC 不需要分离 |
| Magnus job 集成 | 无 | ECC 是本地开发场景 |

### ECC 有但我们可以借鉴的

| ECC 机制 | 可借鉴内容 | 优先级 |
|---------|-----------|--------|
| hook 100% fire | 用确定性的机制触发经验提取，不依赖 agent 自觉 | 高 |
| SIGUSR1 cooldown | 防止短时间内重复触发治理 | 中 |
| tail 采样 | 自迭代只读最近 N 条 capsule，不全量读 | 高 |
| confidence 按频次初始赋值 | utility_score 初始值可按观察频次设 | 中 |
| /learn-eval 四裁决 | 自迭代 quality_gate 可借鉴 Save/Improve/Absorb/Drop | 高 |
| 5 层自循环过滤 | 防止自迭代 agent 观察自己产生的数据 | 高 |
| secret redaction 正则 + 8 秒看门狗 | 写入侧注入检测可借鉴 | 中 |
| 数据放 ~/.claude 外 | 避免敏感路径 guard 冲突 | 中 |
| shortId 防覆盖 | 用短 ID 而非递增序号避免合并冲突 | 低 |
| SUMMARY marker 幂等 | 检测标记避免重复处理 | 低 |
| blueprint adversarial review gate | theory_check 可借鉴对抗式审查 | 中 |
| blueprint cold-start brief | 每步 self-contained context | 中 |
| session-guardian 三门控 | 自迭代触发条件可借鉴时间窗/cooldown/idle | 低 |
| git worktree 并行化 | 远期并行跑多个论文复现可借鉴 | 低 |
| profile 三档控制 | 按 risk_level 控制 agent 自由度可借鉴 | 中 |
| plan-orchestrate agent chain | 按任务类型自动选 agent 链可借鉴 | 低 |

---

## ECC 的验证逻辑缺陷

ECC 的 /evolve 聚类是**字符串归一化**，不是语义聚类：

```python
trigger_key = trigger.lower()
for kw in ['when','creating','writing','adding','implementing','testing']:
    trigger_key = trigger_key.replace(kw, '').strip()
trigger_clusters[trigger_key].append(inst)
```

这意味着：
- "when doing COMSOL mode analysis" 和 "when performing COMSOL eigenvalue analysis" 不会被聚到一起
- 我们的向量记忆库 + 8B reranker 在聚类阶段也能派上用场

ECC 的 /evolve --generate 直接生成 SKILL.md，**没有 critic / schema validation / replay / human gate**。这正好是我们风险评审里说的"自迭代直接写长期工件"的经典反例。

---

## 对我们设计的验证

ECC 218k 星 + 10 个月日常使用，验证了以下方向可行：

1. ✅ 经验自动提取（hook → observation → instinct）有价值
2. ✅ confidence scoring + 频次初始赋值可行
3. ✅ instinct→skill 聚类路线可行
4. ✅ project→global 提升机制可行
5. ✅ 跨 session memory persistence 有价值
6. ✅ 轻量 SKILL.md 格式实用

ECC 同时验证了我们风险评审的担忧是真实的：

1. ⚠️ ECC 没有 replay → 长期使用必然 Library Drift
2. ⚠️ ECC 没有 human gate → /evolve 直接生成可能产出低质量 skill
3. ⚠️ ECC 没有 sandbox → 直接改用户目录
4. ⚠️ ECC 聚类是字符串归一化 → 漏聚同义 trigger

---

## 可直接借鉴的工程细节（15 条）

### 1. hook 100% fire 机制
用确定性的机制（hook/event listener）触发经验提取，不依赖 agent 自觉记录。我们用 workflow runner 每节点自动产 capsule 实现同样目标。

### 2. SIGUSR1 cooldown
防止治理在短时间内重复触发。我们的自迭代 workflow 触发条件可加 cooldown。

### 3. tail 采样
自迭代只读最近 N 条 capsule，不全量读。降低成本，避免 LLM 淹没在历史中。

### 4. confidence 按频次初始赋值
```text
1-2 次 → 0.3（tentative）
3-5 次 → 0.5（moderate）
6-10 次 → 0.7（strong）
11+ 次 → 0.85（very strong）
```
我们的 utility_score 初始值可参考。

### 5. /learn-eval 四裁决
```text
Save          → 独特、具体、scope 好 → 保存
Improve then Save → 有价值需打磨 → 列改进→修订→重评
Absorb into [X] → 应并入已有 skill → 展示 diff → 合并
Drop          → 琐碎/冗余/太抽象 → 丢弃
```
我们的自迭代 quality_gate 可直接借鉴。

### 6. 5 层自循环过滤
防止自迭代 agent 观察自己产生的数据。我们的回传白名单是更强的版本，但 5 层过滤的思路可借鉴。

### 7. secret redaction 正则 + 看门狗
```text
正则：(?i)(api[_-]?key|token|secret|password|authorization|credentials?|auth)...([A-Za-z0-9_\-/.+=]{8,256})
8 秒 SIGALRM 看门狗防 ReDoS
```
我们的写入侧注入检测可直接用这个正则。

### 8. 数据放 ~/.claude 外
避免敏感路径 guard 冲突。我们的 project-flow 状态树本来就在独立目录，但临时镜像内也要注意。

### 9. shortId 防覆盖
instinct/skill 用短 ID（kebab-case）而非递增序号，避免多分支合并冲突。我们的 project-flow 节点 ID 可借鉴。

### 10. SUMMARY marker 幂等
hook 检测 SUMMARY 标记避免重复处理同一 session。我们的 attempt_capsule 可加幂等标记。

### 11. blueprint adversarial review gate
最强模型 sub-agent 审查 + checklist + anti-pattern catalog。我们的 theory_check 可借鉴对抗式审查。

### 12. blueprint cold-start brief
每步 self-contained context brief，fresh agent 可 cold-start 执行。我们的每个 agent 节点 prompt 应包含完整上下文，不依赖前序 agent 的内部状态。

### 13. session-guardian 三门控
时间窗 + cooldown + idle 检测。自迭代触发条件可借鉴。

### 14. profile 三档控制
minimal / standard / strict。我们的 risk_level 可借鉴这个思路——不同风险等级的节点用不同 profile 控制 agent 自由度。

### 15. plan-orchestrate agent chain
按任务类型自动选 agent 链。远期可考虑按论文类型（解析/仿真/实验对比）自动选不同的 agent 链。

---

## 我们比 ECC 多做的

```text
1. deterministic verifier（物理通用检查）— ECC 完全没有
2. replay regression suite — ECC 完全没有
3. human gate — ECC 完全没有
4. sandbox / 临时镜像 — ECC 完全没有
5. 状态树 / project-flow — ECC 完全没有
6. 回传白名单守门 — ECC 完全没有
7. 向量记忆库 + 8B reranker — ECC 用文件系统
8. trust_level / provenance — ECC 不区分来源信任度
9. data/instruction 隔离 — ECC 的 instinct 直接进 instruction
10. SKILL→蓝图从属 — ECC 没有执行模板概念
11. 工作和自迭代分离 — ECC 合一（场景不同，不是缺陷）
12. Magnus job 集成 — ECC 是本地开发场景
```

这 12 项中，前 4 项是 ECC 明确的空白，也是我们的核心竞争力。

---

## 对项目定位的影响

```text
ECC 证明了"经验自动提取 + skill 聚类"在通用 coding 场景下有巨大价值（218k 星）。
但 ECC 的路线是"LLM judgment 够用 + 开放进化 + 无 gate"。
我们的路线是"deterministic verifier + 封闭治理 + human gate + 垂域可验证"。

两者不竞争，互补。
ECC 适合日常 coding（verifier 就是 go build/go test）。
我们适合科研复现（verifier 是能量守恒/光学定理）。

我们的差异化不是"也做了经验自动提取"，
而是"在需要物理正确性的垂域里，经验自动提取 + verifier + replay + gate 一起做"。
```
