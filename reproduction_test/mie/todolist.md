# Mie 复现任务清单（给 claude 用）

> 这份是给执行 agent（claude）看的任务列表。按顺序做，每个任务有明确的"完成条件"。
> 流程知识在 `.codex/skills/optics-mie-reproduction/SKILL.md`，论文清单在 `references/papers.md`，检验规则在 `references/verification.md`，benchmark 格式在 `references/benchmark_format.md`。
> 人看的总计划在 `reproduction_test/mie/mie_reproduction_plan-CN.md`。
> **关键：不要自己宣布成功。每个阶段跑完 3 层检验 + 等人工 gate 通过才算完成。**

## 全局规则（每个任务都遵守）

1. **特殊函数用 `scipy.special`**，不要自己实现球贝塞尔/勒让德函数。
2. **核心公式 $a_n, b_n$ 以教材为主源**（Bohren & Huffman 或 Kerker），Akimov 等 review 只做交叉。这 2-3 行必须写在推导笔记里等人工核对。
3. **单位统一用 SI（米）**，论文给 nm 要换算。参数表里写明每个量的单位。
4. **代码和测试同步写**（TDD）：物理约束测试值先写死，代码必须迁就测试。
5. **不信任 AI 自己的"looks good"**：成功判定看 verifier 脚本输出和量化误差数字。
6. **单次经验不写长期 skill**：阶段 1 产出的 skill 内容标 `status: candidate`，带 `applies_when` / `does_not_apply_when`。

## 阶段 0：环境与脚手架（最先做）

- [ ] **T0.1 确认教材**：问用户手头有没有 Bohren & Huffman 或 Kerker 的 PDF。没有就帮用户找。核心公式要对着教材核，不能只靠 review 论文。
- [ ] **T0.2 建 benchmark.yaml 骨架**：按 `references/benchmark_format.md` 建 `reproduction_test/mie/data/benchmark.yaml`，先放 stage 1 的 placeholder 条目，值标 `pending`。

## 阶段 1：单球 Mie 基础（主论文 Akimov 2401.04146）

- [ ] **T1.1 读论文 + 抽参数**：读 `papers/mie/2401.04146.pdf`，抽半径、折射率、波长范围、尺寸参数 $x$ 定义。写 `formalization/akimov_single_sphere.yaml`。
  - 完成条件：参数表含单位、$x$ 范围、折射率实部虚部、论文图源。
  - **人工 gate ①**：用户核对参数和单位。
- [ ] **T1.2 物理 formalization**：写结构化 spec——geometry（单球）、materials（复折射率）、equations（Maxwell + 球谐展开）、boundary conditions（切向分量连续）、sources（平面波）、solver（级数求和）、observables（$a_n,b_n$、$Q_{sca},Q_{ext},Q_{abs}$）、assumptions、missing_fields。
  - 完成条件：spec 字段齐全，代码将消费这个 spec。
  - **人工 gate ②**：用户核对 spec 是否匹配论文物理问题。
- [ ] **T1.3 推导 Mie 系数**：在 `notes/akimov_single_sphere.md` 写从 Maxwell 到 $a_n, b_n$ 的完整推导。**$a_1, b_1$ 表达式必须对着教材核**。
  - 完成条件：推导笔记含 $a_n, b_n$ 闭式表达 + 来源页码（教材或论文）。
  - **人工 gate ③**：用户对着教材核对 $a_n, b_n$ 那 2-3 行。**这是最关键的 gate**。
- [ ] **T1.4 实现 `code/mie_coefficients.py`**：函数 `mie_coefficients(m, x, n_max) -> (a, b)`，用 `scipy.special`。
  - 完成条件：导入无错，对一组 $(m, x)$ 返回有限复数。
- [ ] **T1.5 实现 `code/scattering.py`**：函数 `compute_cross_sections(m, x) -> (C_ext, C_sca, C_abs)`、`compute_Q_sca`、`compute_Q_ext`。级数截断 $n_{\max}$ 要够大（经验 $n_{\max}\approx x+4x^{1/3}+2$）。
  - 完成条件：函数签名和 verifier 脚本期望一致。
- [ ] **T1.6 写 `tests/test_energy_conservation.py`**：硬编码 $C_{ext}=C_{sca}+C_{abs}$ 容差 $10^{-10}$。
- [ ] **T1.7 写 `tests/test_rayleigh_limit.py`**：硬编码小 $x$ 下 $Q_{sca}\propto x^4$，斜率 $4\pm0.01$。
- [ ] **T1.8 跑 3 个物理 verifier**：用 skill 的 `scripts/check_energy_conservation.py`、`check_rayleigh_limit.py`、`check_large_size_limit.py`。
  - 完成条件：3 个都 PASS。任何一个 FAIL 停下来查 bug，不继续。
- [ ] **T1.9 画 $Q_{sca}(x)$ 曲线**：$x\in[0.1,30]$，$n=1.5,2,3,4$，存 `figs/akimov_Qsca_vs_x.png`。多极分解图（前 3 阶电/磁贡献）放第二阶段初，本阶段先不做。
- [ ] **T1.10 论文图量化对比**：数字化 Akimov 的 $Q_{sca}(x)$ 图，算 RMSE 和峰位误差。
  - 完成条件：误差数字写进 benchmark.yaml，不靠"看着像"。
  - **人工 gate ④**：用户看量化误差数字，决定 pass/fail。
- [ ] **T1.11 更新 benchmark.yaml**：把 `akimov_single_sphere` 条目的 `provenance`、`two_way_agreement`、`verifier_results`、`human_gate_4` 填上实际值。
- [ ] **T1.12 写阶段 1 skill 内容**：把本阶段学到的流程写进 `.codex/skills/optics-mie-reproduction`（如 verifier 用法、坑点），标 `status: candidate`，明确 `applies_when: 单球 Mie`，`does_not_apply_when: 核壳/阵列`。
- [ ] **T1.13 写阶段 1 汇报材料**：推导笔记 + 曲线 + 数据表 + 物理结论（如 Rayleigh/Mie/几何光学三区过渡），准备给老师汇报。

**阶段 1 完成定义**：T1.1-T1.13 全部 done，3 层检验全过，4 个人工 gate 全过，benchmark.yaml 条目 `two_way_agreement: pass`。

## 阶段 2：金属球 LSPR（主论文 Colas des Francs 1112.2814）

- [ ] **T2.1** 读论文 + 抽参数（Drude 参数 $\omega_p, \gamma$，Au/Ag，半径 10/20/50/100 nm）。人工 gate ①。
- [ ] **T2.2** 物理 formalization（Drude 色散 + Mie）。人工 gate ②。
- [ ] **T2.3** 推导 Drude 介电函数 + 准静态 LSPR 条件。人工 gate ③（核对 $\mathrm{Re}(\varepsilon)=-2\varepsilon_d$）。
- [ ] **T2.4** 实现 `code/drude.py`（Au/Ag Drude）。
- [ ] **T2.5** 实现 `code/lspr.py`（金属球消光谱 + Purcell 因子）。
- [ ] **T2.6** 检验：准静态 LSPR 峰位 vs 完整 Mie 峰位对比。
- [ ] **T2.7** 画 LSPR 波长 vs 半径、Purcell 因子谱。
- [ ] **T2.8** 论文图量化对比 + benchmark 追加。人工 gate ④。

## 阶段 3：介质球 Mie 模式（主论文待 Web of Science 补）

- [ ] **T3.1** 通过 Web of Science 找经典介质球 Mie 文献（García-Etxarri / Kuznetsov / Evlyukhin）。
- [ ] **T3.2-T3.8** 同阶段 2 套路：参数→formalization→推导→代码（复用 `mie_coefficients.py`）→检验（磁偶极模式、Kerker 条件）→画图→benchmark。

## 阶段 4：核壳结构 Mie（主论文 Tam，PDF 在 papers/mie/）

- [ ] **T4.1-T4.8** 同套路。关键检验：壳厚→∞ 退化为单球（核材料），核→0 退化为单球（壳材料）。
- [ ] **阶段 4 过后**：skill 从 `candidate` 升 `active`（已有单球 + 核壳两类证据）。

## 阶段 5：周期阵列 SLR（主论文 Auguie & Barnes，PDF 在 papers/mie/）

- [ ] **T5.1-T5.8** 同套路。关键检验：Rayleigh 异常 $\lambda=P\cdot n_{\text{eff}}$；大周期退化为单球。

## 阶段 6：二元阵列（主论文 Li J，PDF 在 papers/mie/）

- [ ] **T6.1-T6.8** 同套路。关键检验：大周期退化为单颗粒。

## 阶段 7：有效介质相图（主论文 Rybin，PDF 在 papers/mie/）

- [ ] **T7.1-T7.8** 同套路。关键检验：低填充率→Maxwell-Garnett。

## 选做（按兴趣和时间）

- Tagviashvili (0910.3305) ENZ 极限 → 接有效介质
- Shamkhi (1808.10708) 广义 Kerker → 接阵列角分布
- Arruda (2406.06800) 核壳 toroidal → 接核壳
- Nieto-Vesperinas (1201.6146) Si 球 Kerker → 接单球定向散射

## 每阶段汇报材料（给老师）

- 推导笔记（Markdown + PDF）
- 可复现代码
- 与论文对比的曲线图
- 标注共振位置和关键参数的数据表
- 该阶段物理结论总结（如金属 vs 介质模式差异、共振峰位规律、阵列耦合新机制）

## 红线（不要做）

- 不要自己实现特殊函数，用 `scipy.special`
- 不要只靠 review 论文推导核心公式，要教材交叉
- 不要跳过人工 gate 直接进下一阶段
- 不要把单阶段经验写进长期 skill 不带适用边界
- 不要用"看着像"判定论文图对比
- 不要在物理硬约束不满足时继续往下跑
