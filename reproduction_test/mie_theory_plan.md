# Mie 理论复现 — 内部技术文档

## 目标

手动实现单球/多层球 Mie 散射 + 球点阵的半解析计算，构建有效介质折射率等物理量的基准数据集。

所有计算 Python 完成，论文 PDF 在 `papers/mie/`。

## 论文清单

| # | 简称 | 全名 | 获取方式 |
|---|------|------|---------|
| 1 | Akimov | Mie scattering theory: a review (2401.04146) | arXiv 免费 |
| 2 | Colas des Francs | Mie plasmons: modes volumes, quality factors (1112.2814) | arXiv 免费 |
| 3 | Tagviashvili | Epsilons Near Zero limits in Mie theory (0910.3305) | arXiv 免费 |
| 4 | Nieto-Vesperinas | Angle-Suppressed Scattering (1201.6146) | arXiv 免费 |
| 5 | Shamkhi | Transverse scattering and generalized Kerker (1808.10708) | arXiv 免费 |
| 6 | Gerasimov | Plasmonic lattice Kerker effect (2007.13317) | arXiv 免费 |
| 7 | Arruda | Toroidal dipole in core-shell spheres (2406.06800) | arXiv 免费 |
| 8 | Li J | Tuning geometric resonances in Ag/Au arrays (Opt. Express 2010) | 开放获取 |
| 9 | Rybin | Phase diagram PC to metamaterial (Nat. Commun. 2015) | 开放获取 CC |
| 10 | Tam | Mesoscopic nanoshells (JCP 127, 2007) | `papers/mie/204703_1_online.pdf` |
| 11 | Auguie & Barnes | Collective Resonances in Au NP Arrays (PRL 101, 2008) | `papers/mie/PhysRevLett.101.143902.pdf` |

## 执行顺序

### 第 1 周：单球 Mie 基础

论文：Akimov

产出：
- `code/mie_coefficients.py` — Mie 系数 \(a_n, b_n\) 计算
- `code/scattering.py` — 散射/吸收/消光截面
- 曲线：\(Q_{sca}(x)\)，\(x \in [0.1, 30]\)，\(n=1.5,2,3,4\)
- 多极分解图（前 3 阶电/磁贡献）

检验：瑞利极限 \(x^4\)、\(Q_{ext}\to2\)、\(C_{ext}=C_{sca}+C_{abs}\)

---

### 第 2 周：金属球 LSPR

论文：Colas des Francs

产出：
- `code/drude.py` — Au/Ag Drude 模型
- `code/lspr.py` — 金属球消光谱
- 曲线：LSPR 波长 vs 半径（\(R=10,20,50,100\) nm）
- Purcell 因子谱

检验：准静态 LSPR \(\varepsilon = -2\varepsilon_m\)

---

### 第 3 周：核壳结构 Mie

论文：Tam（PDF 在 papers/mie/），参考 Arruda

产出：
- `code/core_shell_mie.py` — 双层球 Mie
- 曲线：不同壳厚下的消光谱
- 壳厚-共振波长相图
- 比较准静态与完整 Mie

检验：壳厚→∞ 退化为单球，核→0 退化为单球

---

### 第 4 周：周期阵列集体共振（SLR）

论文：Auguie & Barnes（PDF 在 papers/mie/），参考 Gerasimov

产出：
- `code/coupled_dipole.py` — CDA 周期阵列消光谱
- 曲线：不同周期下的消光谱，标注 Rayleigh 异常和 SLR
- 共振线宽-周期曲线

检验：Rayleigh 异常位置 \(\lambda = P\cdot n_{\text{eff}}\)

---

### 第 5 周：二元阵列几何共振

论文：Li J

产出：
- `code/binary_cda.py` — 二元阵列 CDA
- 曲线：不同尺寸比下的消光谱
- 线宽-尺寸比曲线

检验：大周期退化为单颗粒结果

---

### 第 6 周：有效折射率提取与相图

论文：Rybin

产出：
- `code/effective_medium.py` — S 参数反演提取 \(\varepsilon_{\text{eff}}, \mu_{\text{eff}}\)
- `code/phase_diagram.py\) — 相图
- 曲线：\(n_{\text{eff}}\) 色散，\((\varepsilon, P/\lambda)\) 相图

检验：低填充率 → Maxwell-Garnett

---

### 选做

| 论文 | 内容 | 接入点 |
|------|------|--------|
| Tagviashvili | ENZ 极限 Mie 散射 | 连到有效介质 n_eff→0 |
| Shamkhi | 广义 Kerker 横向散射 | 连到阵列散射角分布 |
| Arruda | 核壳 toroidal 偶极 | 核壳深入拓展 |
| Nieto-Vesperinas | Si 球 Kerker 条件 | 单球定向散射 |

## 代码组织

```
reproduction_test/mie/
├── code/
│   ├── mie_coefficients.py
│   ├── scattering.py
│   ├── drude.py
│   ├── core_shell_mie.py
│   ├── coupled_dipole.py
│   ├── binary_cda.py
│   └── effective_medium.py
├── data/
├── figs/
└── notes/
```

## 检验标准

1. 能量守恒 \(C_{ext}=C_{sca}+C_{abs}\)
2. 瑞利极限 \(Q_{sca}\propto x^4\)
3. 大尺寸极限 \(Q_{sca}\to 2\)
4. 准静态 LSPR \(\varepsilon = -2\varepsilon_d\)
5. 低填充率 → Maxwell-Garnett

## 工作流接入点

所有代码和数据最终作为 agent 的 benchmark：
- `data/benchmark.yaml` — 标准答案（共振位置、有效折射率等）
- 后续 agent 的 COMSOL 计算结果与此对比，误差超阈值则判失败

注：arXiv 论文可直接访问，不用下载。Tam 和 Auguie 的 PDF 在 `papers/mie/`。
