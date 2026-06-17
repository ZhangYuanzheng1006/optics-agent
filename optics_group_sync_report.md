# optics_agent 光学组同步技术报告

更新时间：2026-06-17

面向读者：光学组同学、PI、后续接手论文复现任务的人。

这份文档的目的不是替代代码文档，而是把目前 `optics_agent` 项目，尤其 Degiron 2009 NJP Fig. 3 的 v1/v2 复现情况，用中文集中说明。默认读者没有时间读 COMSOL Java、Magnus 脚本、英文报告和原始日志。

## 一句话结论

`optics_agent` 目前已经跑通“论文读取 -> 参数提取 -> COMSOL/Magnus 提交 -> 日志下载 -> CSV/画图 -> 技术报告”的工程流程，但 Degiron 2009 Fig. 3 还没有完成物理意义上的 COMSOL full-vector 复现。

当前主要问题不是 Magnus 平台封装，也不是 COMSOL license/image，而是缺少一个由 COMSOL 6.3 GUI 导出的、已知能输出正确 `neff` 的 Wave Optics/RF mode-analysis 模板。没有这个模板时，手写 Java API 可以把模型搭到“编译、网格、进入 eigensolver、保存 .mph”，但不能保证 COMSOL 内部 physics/study/solver/result 设置完全正确。

## 项目定位

`optics_agent` 当前是 zyz 的个人工作目录，不是课题组正式统一仓库，也不是最终版软件。

项目目标是探索一套可复用的论文数值复现 agent 工作流：

```text
论文读取
  -> 参数提取
  -> 缺失信息检查
  -> COMSOL 建模
  -> Magnus/COMSOL headless 运行
  -> 结果检查
  -> 失败修正
  -> 技术报告和交接材料
```

短期用例是 SPP / LR-SPP 相关光学论文的图像复现。长期目标不是只复刻某一张图，而是把复现经验沉淀为：

- 可复用的 scientific-computing blueprint；
- 可机器读取的参数表和 case/DSL；
- 自动提交、自动检查、自动迭代的工作流；
- 给光学组同学填写的“标准答案”格式。

## 当前工程状态

已经确认可用的部分：

| 模块 | 当前状态 |
|---|---|
| COMSOL headless runtime | 可运行，使用 `docker://magnus-local/comsol-runtime:latest`。 |
| Magnus 提交流程 | 可提交 CPU-only COMSOL job，可下载日志和结果。 |
| COMSOL Java batch | Java 模型可以编译、batch 运行、保存 `.mph`。 |
| 后处理 | 可以从 stdout 解析数值行，生成 CSV 和图。 |
| 报告体系 | v1/v2 均保留了参数表、假设表、失败记录、最终报告和交接报告。 |

必须明确区分三件事：

```text
Magnus job 成功
  != COMSOL 物理求解成功
  != 论文图像物理复现成功
```

v1/v2 中有些 job 在平台状态上是 `Success`，并且保存了 `.mph`，但这只说明“平台和文件流打通了”。如果没有正确输出物理可信的 `neff`，就不能称为 Fig. 3 复现成功。

## 复现目标：Degiron 2009 NJP Fig. 3

本轮主要测试对象是：

```text
Degiron et al., New Journal of Physics 11, 015002 (2009)
Fig. 3: Dispersion of the two eigenmodes as a function of the BCB thickness t
```

目标图计算的是一个 plasmonic/dielectric directional coupler 的两个耦合本征模。数值问题应为：

- 2D `x-y` 横截面；
- 传播方向为 `z`；
- 扫描 BCB 总厚度 `t`；
- 求传播常数 `kz`；
- 输出有效折射率：

```text
neff = kz / k0
```

目标观测量：

- symmetric mode 的 `Re(neff)` 和 `Im(neff)`；
- anti-symmetric mode 的 `Re(neff)` 和 `Im(neff)`；
- 在 `t ~= 5.6 um` 附近应看到 crossing / anticrossing / mode hybridization 相关趋势。

主要参数：

| 项目 | 使用值 |
|---|---|
| wavelength | `1.55 um` |
| Au stripe | 宽 `4.6 um`，厚 `36 nm` |
| SU-8 waveguide | 矩形近似，宽 `2.0 um`，厚 `1.5 um` |
| Au-SU8 lateral gap | `2.5 um` |
| Au/SU8 底部高度 | 距 BCB/SiO2 interface 约 `3.3 um` |
| BCB thickness sweep | 约 `4.8-10.0 um`，在 `5.6 um` 附近加密 |
| Au permittivity | `-132 + 12.65i` |
| BCB index | `1.535` |
| SiO2 index | `1.444` |
| SU-8 index | `1.57 + 8e-5i` |

## V1 做了什么

v1 路径：

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/
```

v1 的目标是完整跑一遍从论文到 COMSOL/Magnus 再到报告的流程。它确实验证了很多工程环节：

- 读论文并整理 Fig. 3 参数；
- 写参数表和缺失信息表；
- 生成 COMSOL Java 模型；
- 通过 Magnus 提交 COMSOL batch job；
- 处理 Java wrapper、sandbox、mesh、eigensolver 等错误；
- 下载日志；
- 从 stdout 解析 CSV；
- 生成复现图；
- 写 `final_report.md` 和 `workflow_handoff_A.md`。

但是 v1 的最终图不是物理 COMSOL 复现。最终 sweep 使用的是 `surrogate_fallback`，即在 full-vector mode analysis 失败后，为了验证数据流和画图流程，输出了一个替代/示意性质的数据。

v1 结论：

| 层级 | 结论 |
|---|---|
| 论文到参数表 | 成功 |
| Magnus/COMSOL 工程流程 | 成功 |
| stdout 到 CSV/图 | 成功 |
| full-vector COMSOL mode analysis | 未成功 |
| Degiron Fig. 3 物理复现 | 未成功 |

v1 暴露的问题：

- 手写 COMSOL Java 中 `run()`、`.mph` 保存、sandbox 限制都需要严格处理；
- COMSOL batch sandbox 不允许随意使用 `System.getenv`、`System.getProperty`、直接 Java 文件 IO；
- physics-controlled mesh 在薄金属/高对比结构附近容易失败；
- 即使用显式网格绕过 mesh 问题，full-vector eigensolver 仍然失败；
- 只会写 Java API 语法，不等于知道 Wave Optics/RF mode-analysis 的完整内部设置。

## V2 做了什么

v2 路径：

```text
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/
```

v2 不是简单重复 v1，而是把验证拆成更小的 ladder：

1. 先审计 v1，明确哪些结果只是 workflow success；
2. 做 scalar TM-like PDE smoke；
3. 做 scalar coupled sweep；
4. 单独做 isolated SU-8 Wave Optics/RF mode-analysis probe；
5. 用这个 probe 判断问题到底在平台、封装、网格，还是 COMSOL mode-analysis 设置。

v2 的 scalar PDE 模型能跑完，但它不是 full-vector Wave Optics 模型。它使用的是类似：

```text
u ~= Hx
-div((1/epsr) grad(u)) - k0^2 u = lambda (1/epsr) u
lambda = -beta^2
neff = beta/k0
```

这个诊断模型得到的结果：

- `Re(neff)` 偏低；
- `Im(neff)` 基本为 0；
- 没有恢复 `t ~= 5.6 um` 附近清楚的 anticrossing；
- 小 `t` 区域 anti-symmetric branch 的损耗趋势没有复现。

所以 v2 scalar 结果只能说明“数值链路和 sweep 可以工作”，不能作为论文物理复现结果。

## V2 最关键的诊断结果

v2 做了一个 isolated SU-8 Wave Optics/RF mode-analysis probe，目的是先不碰 Au 和复杂耦合结构，只测试一个最小 dielectric waveguide 能否通过手写 COMSOL Java API 输出合理 `neff`。

结果：

| 测试 | 状态 | 意义 |
|---|---|---|
| Java 编译 | 通过 | COMSOL Java 语法和 batch wrapper 基本可用。 |
| 模型运行 | 通过 | Magnus/COMSOL runtime 可以执行该 job。 |
| 显式 mesh | 通过 | v1 的 mesh 阶段 blocker 可被 explicit mesh 绕开。 |
| 保存 `.mph` | 通过 | 模型文件可以保存。 |
| 进入 eigensolver | 通过 | 不是停在平台封装或 Java 编译阶段。 |
| 输出物理 `neff` | 失败，0 行 | eigensolver matrix factorization failed。 |

这说明当前问题已经被压缩到更具体的位置：

```text
手写 COMSOL Java mode-analysis 设置不完整或不正确
```

不是简单的：

```text
Magnus 不能跑
COMSOL license 有问题
Java 完全不会写
文件不能保存
```

更准确的判断是：

```text
COMSOL Java API 是官方接口；
但 Wave Optics/RF mode-analysis 是模块专用流程；
仅靠通用 Java API 手写，很容易漏掉 GUI 中自动配置的 physics/study/solver/result 细节。
```

## 当前 blocker

现在最缺的是一个已知正确的最小 COMSOL 6.3 GUI 导出模板。

需要光学组提供：

```text
一个 2D rectangular dielectric waveguide mode-analysis 模型
wavelength = 1.55 um
能在 COMSOL GUI 中输出至少一个正确 neff
然后导出 .java，或者直接提供 .mph
```

这个模板应包含：

- 使用的 COMSOL physics interface；
- propagation direction；
- mode-analysis study；
- solver sequence；
- eigenvalue/search shift 的变量和单位；
- boundary/PML/open-domain 设置；
- mesh 设置；
- `neff` 或 `beta` 的 result expression；
- 一个已知正确的输出数值，用于 smoke test。

有了这个模板后，agent 应该先保持 physics/study/solver/result 设置不动，只修改 geometry/material/sweep。这样才能判断问题是不是 Degiron 几何本身，而不是 COMSOL 模板写错。

## 光学组需要提供什么

后续如果希望 agent 复现更多论文图，光学组给的“标准答案”不能只写理论解释。至少需要下面这些信息。

| 类别 | 最低要求 |
|---|---|
| Figure target | 图号、横轴/纵轴、扫描变量、目标趋势、目标数值范围。 |
| Geometry | 坐标系、层结构、每个 object 尺寸、gap、参考平面、不确定形状。 |
| Materials | 波长、折射率/介电常数、复数损耗、数据来源、符号约定。 |
| Physics | COMSOL interface、维度、传播方向、求解变量、本征值定义。 |
| Boundary | PML/scattering/PEC/PMC/open boundary，计算窗口大小，substrate 截断方式。 |
| Mesh | 金属、gap、界面、bulk 的最大网格尺寸，边界层，单元阶数。 |
| Solver | study type、mode count、search shift、tolerance、是否需要特殊 solver sequence。 |
| Postprocess | `neff`/`beta` 表达式，branch sorting 方法，field profile 检查方式。 |
| Validation | 目标图、允许误差、必须复现的趋势、已知失败模式。 |

最有价值的训练材料是：

```text
COMSOL GUI 可运行 .mph 或 GUI-exported .java
  + 参数表
  + 一组已知正确输出
  + 哪些设置不能改的说明
```

## v1/v2 中哪些文件最值得读

如果时间很少，建议只读下面几份。

### v1

```text
reproduction_test/private/Degiron_2009_NJP_Fig3/final_report.md
reproduction_test/private/Degiron_2009_NJP_Fig3/workflow_handoff_A.md
reproduction_test/private/Degiron_2009_NJP_Fig3/magnus/failure_retry_record.md
```

含义：

- `final_report.md`：v1 做了什么、哪些 job 成功、为什么最终不是物理复现；
- `workflow_handoff_A.md`：从 v1 总结出的 agent 框架和光学组标准答案要求；
- `failure_retry_record.md`：v1 失败、修正、重试的完整诊断记录。

### v2

```text
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/README.md
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/final_report.md
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/workflow_handoff_A_v2.md
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/v1_experience_audit.md
reproduction_test/private/Degiron_2009_NJP_Fig3_v2/magnus/failure_retry_record.md
```

含义：

- `README.md`：v2 文件布局和状态入口；
- `final_report.md`：v2 的实际模型、job、结果、blocker；
- `workflow_handoff_A_v2.md`：给后续框架设计和光学组协作的交接；
- `v1_experience_audit.md`：为什么 v2 不再把 fallback 当成物理复现；
- `failure_retry_record.md`：v2 的 mesh/eigensolver/mode-analysis 失败证据。

## 不建议如何理解当前结果

不建议说：

```text
Fig. 3 已经复现了。
COMSOL 已经完全没问题。
只是数值还有一点偏差。
```

更准确的说法是：

```text
工程 workflow 已经跑通。
v1/v2 已经定位到 COMSOL Wave Optics/RF mode-analysis 设置是关键 blocker。
目前还没有得到物理可信的 Fig. 3 full-vector neff sweep。
下一步需要光学组提供一个 COMSOL GUI 导出的最小 mode-analysis 模板。
```

## 下一步建议

### 对光学组

1. 在 COMSOL 6.3 GUI 中搭建最小 2D dielectric waveguide mode-analysis 模型。
2. 确认 GUI 中能输出一个合理 `neff`。
3. 导出 Java，或直接提供 `.mph`。
4. 写明 `neff` 是哪个表达式，search shift 用的是 `neff`、`beta` 还是其他内部变量。
5. 给出 boundary/PML 和 mesh 的基本设置。

### 对 agent 工作流

1. 读取 GUI 导出的 Java，保留 physics/study/solver/result 设置。
2. 先复现 isolated SU-8。
3. 再复现 isolated Au LR-SPP。
4. 最后做 Au+SU8 coupled smoke，只算 `t ~= 5.6 um` 附近 1-2 个点。
5. 只有 isolated model 输出合理后，才做完整 BCB thickness sweep。

### 对项目文档

后续每次论文复现至少保留：

```text
paper_notes.md
parameter_table.md
assumptions_and_missing_info.md
comsol/model.java 或 GUI-exported model.java
magnus/submit_log.md
magnus/failure_retry_record.md
results/*.csv
results/*.png
final_report.md
workflow_handoff.md
```

这些文件比原始代码更适合给光学组同步，也更适合作为后续 agent 自迭代的训练材料。

## 最短同步版本

如果只需要给别人快速说明，可以直接使用下面这段：

```text
目前 optics_agent 已经跑通了从论文参数提取、COMSOL Java batch、Magnus 提交、日志下载、CSV/画图到技术报告的工程流程。Degiron 2009 Fig. 3 已做 v1/v2 两轮 rehearsal，但还没有完成物理意义上的 full-vector COMSOL 复现。

v1 证明了 workflow 能跑通，但最终图是 surrogate_fallback，不是物理结果。v2 做了更严格的 scalar diagnostic 和 isolated SU-8 Wave Optics/RF mode-analysis probe；scalar sweep 能跑但 Re(neff) 偏低、Im(neff) 基本为 0、没有恢复 anticrossing。isolated SU-8 probe 已经能编译、mesh、进入 eigensolver 并保存 .mph，但 eigensolver matrix factorization failed，输出 0 行物理 neff。

所以当前 blocker 不是 Magnus 封装或 license，而是缺少 COMSOL 6.3 GUI 导出的 mode-analysis 模板来固定 Wave Optics/RF 的 physics/study/solver/result 设置。下一步希望光学组提供一个最小 2D rectangular dielectric waveguide mode-analysis 的 .java 或 .mph，并给出一个已知正确 neff，用它作为后续自动复现的模板。
```
