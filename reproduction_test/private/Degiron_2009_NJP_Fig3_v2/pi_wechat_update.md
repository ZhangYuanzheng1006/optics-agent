# PI WeChat Update

老师好，我同步一下 optics_agent 论文复现这条线的进展。前面主要围绕 Degiron 2009 NJP 里 Fig. 3 做了一轮完整试跑，目标不是只画图，而是验证从论文读取、参数提取、COMSOL 建模、Magnus 提交、日志诊断、失败修正到报告交接的整个 agent 工作流。

目前已经打通的部分：COMSOL/Magnus 运行链路基本可用，Java 模型可以编译、batch 运行、保存 `.mph`，也可以通过 stdout/postprocess 自动生成 CSV 和图。v1 已经完成了论文参数表、缺失信息表、提交脚本、失败记录、最终报告和交接报告；v2 又单独放在新文件夹里重跑，补了更严格的验证记录。

但物理复现还没有成功。v1 最后能出类似曲线的图，但那是 `surrogate_fallback`，只能证明流程，不是 COMSOL 物理复现。v2 的标量 TM-like PDE 诊断也能跑完整 sweep，但结果显示 `Re(neff)` 偏低，`Im(neff)` 基本为 0，也没有恢复 Fig. 3 在 `t ≈ 5.6 um` 附近的反交叉趋势，所以不能当作论文复现成功。

当前定位到的主要问题不是 Magnus 封装，也不是 COMSOL license/image；更具体地说，是 Wave Optics/RF 的 full-vector mode analysis 还缺 COMSOL 6.3 里准确的物理接口、边界/PML、solver sequence、mode search 和 `neff/beta` 导出设置。我已经把问题缩小到孤立 SU-8 波导：模型能编译、显式网格能通过、能进入 eigensolver 并保存 `.mph`，但 eigensolver 仍然 matrix factorization failed，说明继续手写猜 Java API 意义不大。

下一步最需要光学组支持的是一个最小 COMSOL 6.3 GUI 导出的 mode-analysis 模板，`.java` 或 `.mph` 都可以：例如 2D 矩形 dielectric waveguide，在 1.55 µm 下能输出一个正确的 `neff`。同时希望他们给每个复现任务提供“标准答案”式信息：geometry/materials/physics/boundary/PML/mesh/solver/sweep/validation range/common failure notes。这样 agent 才能从模板稳定生成和自迭代，而不是靠猜 COMSOL 内部设置。

我这边已经把这次经验写进 AGENTS 和项目 skills，后续会强制区分三种状态：流程跑通、COMSOL job 成功、物理复现成功，避免把 fallback 或诊断结果误报成论文复现。
