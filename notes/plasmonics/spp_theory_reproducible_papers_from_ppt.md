# PPT 提到的可用于 SPP/SPR 理论数值复现的论文筛选

来源文件：`notes/plasmonics/plasmonics_paper_refs_from_ppt_annotated.md`

筛选标准：

- 只从 PPT 已提到的论文/文献中选。
- 优先选择有免费原文的条目，arXiv 优先；Optics Express / New Journal of Physics / 作者主页 PDF / 机构仓储 PDF 也列入。
- Nature / Nature Photonics / Science 官网 PDF 不按“免费原文”处理，即使网页偶尔能打开，也不放入免费主表。
- 只选讨论具体 SPP/SPR 结构、色散、光谱、近场、散射或模式耦合的理论/数值计算文章；综述、新闻评论、纯实验展示不列入主表。
- “可复现价值”主要看是否能从文中提取几何、材料、入射条件、边界条件或计算模型，供 FDTD/FEM/COMSOL/CDA/DDA/TMM/GFM/GMM 复现。

## A. 免费原文优先：建议先读/复现

### 1. Theory of extraordinary optical transmission through subwavelength hole arrays

- PPT 条目：第二章周期性结构部分，`L. Martin-Moreno et al, PRL 86, 1114 (2001)`
- 作者：L. Martin-Moreno, F. J. Garcia-Vidal, H. J. Lezec, K. M. Pellerin, T. Thio, J. B. Pendry, T. W. Ebbesen
- 免费原文：<https://arxiv.org/abs/cond-mat/0008204>
- 期刊信息：Physical Review Letters 86, 1114 (2001)
- 类型：理论计算，异常透射，孔阵列，SPP 辅助隧穿
- 可复现点：三维亚波长孔阵列透射谱；金属膜上下表面 SPP 耦合；膜厚和孔阵列参数对透射峰的影响。
- 建议复现：COMSOL/FDTD 做周期边界孔阵列透射谱；再对比文中 minimal analytical model。
- 优先级：高。它直接解释 PPT 中 1998 Ebbesen 异常透射为什么由 SPP 耦合产生。

### 2. On the transmission of light through a single rectangular hole

- PPT 条目：第二章周期性结构部分，`Transmission of Light through a Single Rectangular Hole. PRL 95, 103901 (2005)`
- 作者：F. J. Garcia-Vidal, E. Moreno, J. A. Porto, L. Martin-Moreno
- 免费原文：<https://arxiv.org/abs/cond-mat/0503709>
- 期刊信息：Physical Review Letters 95, 103901 (2005)
- 类型：理论计算，单个矩形孔，透射共振，局域场增强
- 可复现点：矩形孔长宽比、孔内介质常数、偏振方向对透射峰和近场增强的影响。
- 建议复现：COMSOL/FDTD 建单孔金属膜模型，扫孔长宽比和偏振；输出透射谱与孔口近场。
- 优先级：高。结构简单，适合作为第一个孔/缝类 SPP 数值复现实例。

### 3. Sub-wavelength plasmonic modes in a conductor-gap-dielectric system with a nanoscale gap

- PPT 条目：第一章，`I. Avrutsky et al, Opt. Express 18 (2010) 348`
- 作者：I. Avrutsky et al.
- 免费原文：<https://doi.org/10.1364/OE.18.000348> （Optics Express 开放获取）
- 期刊信息：Optics Express 18, 348-363 (2010)
- 类型：理论/数值，conductor-gap-dielectric，纳米 gap SPP 模式
- 可复现点：导体-gap-介质体系中的亚波长 plasmonic mode；gap 厚度、介质折射率、金属材料对有效折射率、模式面积、传播长度的影响。
- 建议复现：COMSOL mode analysis，扫 gap 厚度和材料参数；输出 $n_{\mathrm{eff}}$、传播长度、模场分布。
- 优先级：高。和 PPT1 的 conductor-gap-dielectric / hybrid SPP 模式直接对应。

### 4. Identity of long-range surface plasmons along asymmetric structures and their potential for refractometric sensors

- PPT 条目：第一章，`F. Pigeon, J. Appl. Phys 90 (2001) 852`
- 作者：F. Pigeon
- 免费原文：<https://pubs.aip.org/aip/jap/article-pdf/90/2/852/19264611/852_1_online.pdf>
- 期刊信息：Journal of Applied Physics 90, 852 (2001)
- 类型：理论计算，非对称结构，long-range surface plasmons，折射率传感
- 可复现点：非对称薄膜结构中的长程 SPP 模式；上下介质折射率不同时的模式变化和传感灵敏度。
- 建议复现：COMSOL mode analysis 或自写 transfer-matrix dispersion solver，扫金属膜厚、上下介质折射率。
- 优先级：中高。适合复现 IMI/非对称 IMI 中“长程传播 vs 场局域”的关系。

### 5. Single-mode subwavelength waveguide with channel plasmon-polaritons in triangular grooves on a metal surface

- PPT 条目：第二章 SPP 波导部分，`D. K. Gramotnev and D. F. P. Pile, Appl. Phys. Lett. 85, 6323 (2004)`
- 作者：D. K. Gramotnev, D. F. P. Pile
- 免费原文：<https://pubs.aip.org/aip/apl/article-pdf/85/26/6323/18603836/6323_1_online.pdf>
- 期刊信息：Applied Physics Letters 85, 6323 (2004)
- 类型：理论/模式计算，三角槽 channel plasmon-polariton
- 可复现点：V 型/三角形金属槽中的单模 channel plasmon；槽角、槽深、波长对模式局域和损耗的影响。
- 建议复现：COMSOL 2D 截面本征模；输出模场分布、有效折射率、传播长度。
- 优先级：高。几何清晰，适合做槽形 SPP 波导复现。

### 6. Floating dielectric slab optical interconnection between metal-dielectric interface surface plasmon polariton waveguides

- PPT 条目：第二章 SPP 波导部分，`Minsu Kang et al, Optics Express 17, 676 (2009)`
- 作者：Minsu Kang et al.
- 免费原文：<https://doi.org/10.1364/OE.17.000676> （Optics Express 开放获取）
- 期刊信息：Optics Express 17, 676-687 (2009)
- 类型：理论/数值，介质 slab 与金属-介质界面 SPP 波导耦合
- 可复现点：浮置介质 slab 如何连接两个金属-介质 SPP 波导；耦合效率、模式匹配和传播损耗。
- 建议复现：COMSOL/FDTD 建两个金属界面波导加介质 slab，计算透射效率和场分布。
- 优先级：中高。适合学习“介质模式和 SPP 模式耦合”的设计。

### 7. Directional coupling between dielectric and long-range plasmon waveguides

- PPT 条目：第二章 SPP 波导部分，`Aloyse Degiron et al, New Journal of Physics 11 (2009)`
- 作者：Aloyse Degiron et al.
- 免费原文：<https://iopscience.iop.org/article/10.1088/1367-2630/11/1/015002/pdf>
- 期刊信息：New Journal of Physics 11, 015002 (2009)
- 类型：理论/实验结合，dielectric waveguide 与 long-range plasmon waveguide 定向耦合
- 可复现点：介质波导与 LRSP 波导之间的方向耦合；耦合长度、间距、相位匹配条件。
- 建议复现：COMSOL/FDTD 3D 或有效折射率模型，扫两波导间距和长度。
- 优先级：中。偏器件设计，适合做 SPP 与介质光波导接口。

### 8. Tuning of narrow geometric resonances in Ag/Au binary nanoparticle arrays

- PPT 条目：第三章理论方法，`Li J, Gu Y, Gong QH, Optics Express 18, 17684-17698 (2010)`
- 作者：Jia Li, Ying Gu, Qihuang Gong
- 免费原文：<https://doi.org/10.1364/OE.18.017684> （Optics Express 开放获取）
- 期刊信息：Optics Express 18, 17684-17698 (2010)
- 类型：理论计算，CDA，Ag/Au 二元纳米颗粒阵列，几何共振
- 可复现点：周期阵列衍射级与单颗粒 SPR 耦合产生窄线宽几何共振；金/银颗粒尺寸和周期对谱线的调节。
- 建议复现：先用 CDA 复现消光谱，再用 COMSOL/FDTD 建有限或周期阵列验证近场。
- 优先级：高。与 PPT3 CDA 和几何共振内容直接对应。

### 9. Spectral response of plasmon resonant nanoparticles with a non-regular shape

- PPT 条目：第三章理论方法，`Jorg P. Kottmann et al, Optics Express 6, 213 (2000)`
- 作者：Jorg P. Kottmann, Olivier J. F. Martin et al.
- 免费原文：<https://doi.org/10.1364/OE.6.000213> （Optics Express 开放获取）
- 期刊信息：Optics Express 6, 213-219 (2000)
- 类型：理论/数值，Green tensor method，不规则金属纳米颗粒 SPR
- 可复现点：椭圆、三角等非规则纳米颗粒的消光谱和近场；入射偏振、形状和尺寸对共振峰的影响。
- 建议复现：COMSOL/FEM 或 GFM；先复现三角/椭圆颗粒的谱线和热点分布。
- 优先级：高。适合作为 GFM/FEM 复现复杂颗粒 SPR 的入门论文。

### 10. Controlling plasmonic resonances in binary metallic nanostructures

- PPT 条目：第三章理论方法，`Ying Gu, Jia Li, Olivier J. F. Martin, Qihuang Gong, J. Appl. Phys.`
- 作者：Ying Gu, Jia Li, Olivier J. F. Martin, Qihuang Gong
- 免费原文：<https://pubs.aip.org/aip/jap/article-pdf/doi/10.1063/1.3407527/13202594/114313_1_online.pdf>
- 期刊信息：Journal of Applied Physics 107, 114313 (2010)
- 类型：理论计算，Green matrix method，二元金属纳米结构，SPR 调控
- 可复现点：两种金属介电常数和几何结构如何控制共振位置、近场增强和模式分布。
- 建议复现：先按 GMM 思路复现实介电常数共振条件，再用 COMSOL/FEM 用真实金/银介电函数扫谱。
- 优先级：中高。适合连接 PPT3 的 GMM 和实际数值仿真。

### 11. Interplay of plasmon resonances in binary nanostructures

- PPT 条目：第三章理论方法，`Y. Gu, Y. Wang, J. Li, O. J. F. Martin, Q. Gong, Appl. Phys. B 98, 353-363 (2010)`
- 作者：Y. Gu, Y. Wang, J. Li, O. J. F. Martin, Q. Gong
- 免费原文：<http://infoscience.epfl.ch/record/164802>
- 期刊信息：Applied Physics B 98, 353-363 (2010)
- 类型：理论计算，binary nanostructures，等离激元共振相互作用
- 可复现点：二元纳米结构中不同材料/几何模式的耦合、分裂和近场增强。
- 建议复现：COMSOL/FEM 复现双材料纳米结构消光和近场；对照 GMM 结果。
- 优先级：中。比单金属结构复杂，适合第二阶段复现。

### 12. Mesoscopic nanoshells: Geometry-dependent plasmon resonances beyond the quasistatic limit

- PPT 条目：第一章，`F. Tam et al, J. Chem. Phys. 127, 204703 (2007)`
- 作者：F. Tam et al.
- 免费原文：<https://pubs.aip.org/aip/jcp/article-pdf/doi/10.1063/1.2796169/15406365/204703_1_online.pdf>
- 期刊信息：Journal of Chemical Physics 127, 204703 (2007)
- 类型：理论/数值，nanoshell，Mie/multipole，超出准静态近似
- 可复现点：球壳半径、壳厚、介质环境对多极 SPR 的影响；准静态近似与完整电动力学结果的差异。
- 建议复现：Mie 理论脚本优先；也可用 COMSOL axisymmetric/3D 验证消光峰。
- 优先级：中。严格说更偏 LSPR/SPR，不是传播型 SPP，但很适合做数值基准。

### 13. Plasmonic Resonances of Closely Coupled Gold Nanosphere Chains

- PPT 条目：第三章理论方法，`Nadine Harris et al, J. Phys. Chem. C 2009, 113, 2784-2791`
- 作者：Nadine Harris et al.
- 免费原文：<https://opus.lib.uts.edu.au/bitstream/10453/8358/1/2008002312.pdf>
- 期刊信息：Journal of Physical Chemistry C 113, 2784-2791 (2009)
- 类型：理论/数值，紧耦合金纳米球链，TMM/多极耦合
- 可复现点：金纳米球链中间距、颗粒数、偏振方向对耦合共振和红移的影响。
- 建议复现：用 TMM/Mie 多球散射或 COMSOL 3D；对比 CDA 在小间距下的失效。
- 优先级：中高。适合 PPT3 中 TMM 与 CDA 区别的复现。

## B. 没有确认到合格免费原文：建议图书馆查找

这些条目满足“具体理论/数值问题”或很可能满足，但我没有确认到 arXiv/开放期刊/可靠作者 PDF。若后续能拿到原文，可以作为复现候选。

### 1. Surface-polariton-like waves guided by thin, lossy metal films

- PPT 条目：第一章，`J. J. Burke, G. I. Stegeman, Phys. Rev. B 33, 5186 (1986)`
- DOI：<https://doi.org/10.1103/PhysRevB.33.5186>
- 类型：理论，薄 lossy metal films 中的 guided surface-polariton-like waves
- 可复现价值：平面薄膜/IMI/MIM 模式色散的早期理论基准。

### 2. Plasmon-polariton waves guided by thin lossy metal films of finite width: Bound modes of asymmetric structures

- PPT 条目：第二章 SPP 波导部分，`Pierre Berini, Phys. Rev. B 63, 125417 (2001)`
- DOI：<https://doi.org/10.1103/PhysRevB.63.125417>
- 类型：理论，有限宽金属条波导，非对称结构束缚模
- 可复现价值：有限宽条形 SPP 波导的四类模式、有效折射率和损耗。

### 3. Modeling of complementary (void) plasmon waveguiding

- PPT 条目：第一章，`E. Feigenbaum, M. Orenstein, J. Lightwave Tech. 25, 2547 (2007)`
- DOI：<https://doi.org/10.1109/JLT.2007.903558>
- 类型：理论/数值，void/complementary plasmon waveguide
- 可复现价值：互补结构的 SPP 波导建模，可用于 COMSOL/FDTD 对比。

### 4. Channel Plasmon-Polariton Guiding by Subwavelength Metal Grooves

- PPT 条目：第二章 SPP 波导部分，`Sergey I. Bozhevolnyi et al, PRL 95, 046802 (2005)`
- DOI：<https://doi.org/10.1103/PhysRevLett.95.046802>
- 类型：理论/实验结合，金属沟槽 channel plasmon-polariton
- 可复现价值：沟槽 SPP 模式的几何依赖和传播特性。

### 5. Bends and splitters in metal-dielectric-metal subwavelength plasmonic waveguides

- PPT 条目：第二章 SPP 波导部分，`Georgios Veronis and Shanhui Fan, Appl. Phys. Lett. 87, 131102 (2005)`
- DOI：<https://doi.org/10.1063/1.2056594>
- 类型：FDTD/数值器件设计，MDM 波导弯曲和分束器
- 可复现价值：非常适合 COMSOL/FDTD 复现弯曲损耗、T 型分束和透射效率。

### 6. A hybrid plasmonic waveguide for subwavelength confinement and long-range propagation

- PPT 条目：第二章 SPP 波导部分，`R. F. Oulton et al, Nature Photon. 2, 496 (2008)`
- DOI：<https://doi.org/10.1038/nphoton.2008.131>
- 类型：理论/数值，hybrid plasmonic waveguide
- 可复现价值：介质波导模式与金属界面 SPP 模式杂化；gap 中强局域和长传播折中。
- 备注：Nature Photonics 原文不按免费原文处理。若能从图书馆获取，值得优先读。

### 7. Analysis of Hybrid Dielectric Plasmonic Waveguides

- PPT 条目：第二章 SPP 波导部分，`Ruben Salvador et al, IEEE JSTQE 14, 1496 (2008)`
- DOI：未在 PPT 清单中可靠给出
- 类型：理论/数值，hybrid dielectric plasmonic waveguide
- 可复现价值：和 Oulton hybrid waveguide 属同一类，可作为参数扫描和模式分析参考。

### 8. Design of a subwavelength bent C-aperture waveguide

- PPT 条目：第二章 SPP 波导部分，`Paul Hansen et al, Optics Letters 32, 1737 (2007)`
- DOI：<https://doi.org/10.1364/OL.32.001737>
- 类型：数值设计，C-aperture bent waveguide
- 可复现价值：C 形孔径波导、弯曲结构、亚波长传输。

### 9. Transition from localized surface plasmon resonance to extended surface plasmon-polariton as metallic nanoparticles merge to form a periodic hole array

- PPT 条目：第二章周期性结构部分，`PRB 69, 165407 (2004, Barnes)`
- DOI：<https://doi.org/10.1103/PhysRevB.69.165407>
- 类型：理论/实验结合，LSPR 到 extended SPP 的过渡
- 可复现价值：从孤立颗粒到周期孔阵列的模式转变；非常贴合 PPT 的“局域到扩展”主线。

### 10. Full Photonic Band Gap for Surface Modes in the Visible

- PPT 条目：第二章周期性结构部分，`Sambles Group, PRL 77, 2670 (1996)`
- DOI：<https://doi.org/10.1103/PhysRevLett.77.2670>
- 类型：理论/实验结合，周期金属表面上的 surface mode band gap
- 可复现价值：SPP/polaritonic crystal 带隙计算。

### 11. Collective Resonances in Gold Nanoparticle Arrays

- PPT 条目：第二章周期性结构部分，`Baptiste Auguie and William L. Barnes, PRL 101, 143902 (2008)`
- DOI：<https://doi.org/10.1103/PhysRevLett.101.143902>
- 类型：理论/实验结合，金纳米颗粒阵列集体共振
- 可复现价值：阵列衍射级与 LSPR 耦合产生窄线宽 collective resonance。

### 12. Theoretical studies of plasmon resonances in one-dimensional nanoparticle chains: narrow lineshapes with tunable widths

- PPT 条目：第三章理论方法，`Shengli Zou et al, Nanotechnology 17, 4758? (2006)`；PPT 写 `17/11/014`
- DOI：<https://doi.org/10.1088/0957-4484/17/11/014>
- 类型：理论计算，一维纳米颗粒链，窄线宽可调共振
- 可复现价值：CDA/多颗粒耦合模型，适合复现几何共振和线宽调节。

### 13. Tunable wavelength-division multiplexing based on metallic nanoparticle arrays

- PPT 条目：第三章理论方法，`Jia Li et al, Optics Letters 35, 4051 (2010)`
- DOI：<https://doi.org/10.1364/OL.35.004051>
- 类型：理论/器件设计，金属纳米颗粒阵列，WDM
- 可复现价值：用多个几何共振峰做波分复用，适合 CDA/FDTD 复现。

### 14. Surface plasmon polariton scattering by finite-size nanoparticles

- PPT 条目：第三章理论方法，`A. B. Evlyukhin et al, Phys. Rev. B 76, 075426 (2007)`
- DOI：<https://doi.org/10.1103/PhysRevB.76.075426>
- 类型：理论/数值，有限尺寸纳米颗粒对 SPP 的散射
- 可复现价值：金属表面上纳米颗粒散射 SPP，和 PPT3 的 GFM/GTM 应用直接对应。

### 15. Resonance capacity of surface plasmon on subwavelength metallic structures

- PPT 条目：第三章理论方法，`Y. Gu et al, EPL 83, 27004 (2008)`
- DOI：<https://doi.org/10.1209/0295-5075/83/27004>
- 类型：理论方法，GMM/resonance capacity，亚波长金属结构 SPR
- 可复现价值：PPT3 GMM 的核心论文之一；适合理解共振容量如何筛选强近场模式。

### 16. A designer approach to plasmonic nanostructures: tuning their resonance from visible to near-infrared

- PPT 条目：第三章理论方法，`J. Li et al, Journal of Modern Optics 56, 1396-1402 (2009)`
- DOI：<https://doi.org/10.1080/09500340903171722>
- 类型：理论/设计，纳米结构 SPR 从可见到近红外调谐
- 可复现价值：GMM/数值设计金属纳米条或类似结构的共振调谐。

### 17. Plasmon Coupling in Nanorod Assemblies: Optical Absorption, Discrete Dipole Approximation Simulation, and Exciton-Coupling Model

- PPT 条目：第二章 SPR 应用部分，`Prashant K. Jain et al, J. Phys. Chem. B 110, 18243-18253 (2006)`
- DOI：<https://doi.org/10.1021/jp063879z>
- 类型：实验+理论，DDA simulation，金纳米棒组装体
- 可复现价值：DDA 计算纳米棒耦合吸收谱，适合复现平行/垂直耦合导致的红移/蓝移。

## C. 暂不建议作为第一批复现的条目

- 综述类：`Surface plasmon subwavelength optics`、`Nano-optics of surface plasmon polaritons`、`Surface plasmon resonance sensors: review`、`Plasmonics: Merging Photonics and Electronics at Nanoscale Dimensions` 等。适合读背景，不适合直接数值复现。
- 新闻/观点类：`The Case for Plasmonics`、`Plasmonics Goes Quantum`、`Quantum light switch` 等。适合理解领域趋势，不是具体计算任务。
- 纯实验或材料制备主导：`Shape-Controlled Synthesis of Gold and Silver Nanoparticles`、`Ultrasmooth Patterned Metals`、`Femtosecond laser reshaping...`、`Amino-acid- and peptide-directed synthesis...` 等。可作为应用背景，不作为理论复现首选。
- Nature/Science 具体实验：如 Ebbesen 1998 异常透射原始实验、bull's eye beaming、单光子/纠缠 SPP、石墨烯 plasmon 实验等。它们很重要，但通常不是最适合直接从零做 COMSOL 数值复现的第一批论文；若要复现，应先找对应理论文章。

## D. 建议复现顺序

1. **单孔/孔阵列异常透射**：先复现 `Theory of extraordinary optical transmission...` 和 `Transmission of Light through a Single Rectangular Hole`。这两篇有 arXiv，几何明确，和 PPT2 周期结构主线最贴合。
2. **波导本征模**：复现 conductor-gap-dielectric、三角槽 channel plasmon、floating dielectric slab。重点输出 $n_{\mathrm{eff}}$、传播长度和模场。
3. **周期颗粒阵列几何共振**：复现 Ag/Au binary nanoparticle arrays。先用 CDA 思路理解，再用 COMSOL/FDTD 做小阵列或周期边界验证。
4. **复杂颗粒/GFM/GMM**：复现非规则颗粒谱线、二元金属结构、紧耦合金纳米球链。这里更适合检验 FEM/DDA/TMM/GMM 方法差异。

