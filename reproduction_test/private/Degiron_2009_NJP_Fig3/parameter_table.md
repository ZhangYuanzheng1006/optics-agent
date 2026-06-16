# Degiron 2009 NJP Fig. 3 Parameter Table

## Geometry

| Category | Parameter | Value Used | Source / Status |
|---|---|---:|---|
| coordinate system | transverse plane | `x-y` | Paper section 2 |
| coordinate system | propagation direction | `z` | Paper section 2 |
| BCB / SiO2 interface | `y` position | `0 um` | Fig. 1(b) |
| top BCB / air interface | `y` position | `t` | Fig. 1(b) |
| Au stripe | width | `4.6 um` | Fig. 1(b) caption |
| Au stripe | thickness | `36 nm = 0.036 um` | Fig. 1(b) caption |
| Au stripe | v1 coordinates | `x=[-4.6,0] um`, `y=[3.3,3.336] um` | Engineering interpretation of Fig. 1(b) |
| SU-8 waveguide | average width | `2.0 um` | Fig. 1(b) caption |
| SU-8 waveguide | average thickness | `1.5 um` | Fig. 1(b) caption |
| SU-8 waveguide | v1 shape | rectangle | Simplification |
| SU-8 waveguide | v1 coordinates | `x=[2.5,4.5] um`, `y=[3.3,4.8] um` | Engineering interpretation |
| gap | Au right edge to SU-8 left edge | `2.5 um` | Fig. 1(b) caption |
| waveguide height | distance from SiO2/BCB interface | `3.3 um` to waveguide/Au bottom | Fig. 1(b), v1 interpretation |
| BCB scan | smoke | `5.6, 6.6 um` | V1 smoke |
| BCB scan | sweep | `4.8-10.0 um` with dense points near `5.6 um` | Fig. 3 target |
| SiO2 | thickness | `4 um`, `y=[-4,0] um` | Section 2 |
| Si | lower substrate | optional, v1 `y=[-6,-4] um` | Engineering approximation |
| air | top region | `y=[t,t+4] um` | Engineering approximation |
| lateral computational window | x range | `[-12,12] um` | Engineering approximation |

## Materials

| Material | Parameter | Value Used | Source / Status |
|---|---|---:|---|
| wavelength | `lambda0` | `1.55 um` | Paper |
| Au | relative permittivity | `-132 + 12.65i` | Fig. 1(b) caption |
| SiO2 | refractive index | `1.444` | Fig. 1(b) caption |
| BCB | refractive index | `1.535` | Fig. 1(b) caption |
| SU-8 | refractive index | `1.57 + 8e-5 i` | Fig. 1(b) caption |
| Si | refractive index | `3.48`, lossless v1 | Not specified in paper section; engineering approximation |
| air | refractive index | `1.0` | Standard approximation |

## Calculation Type

| Item | Value Used | Source / Status |
|---|---|---|
| COMSOL form | 2D eigenmode / mode analysis | Paper section 2 |
| Primary physics | Wave Optics / RF electromagnetic waves, frequency domain | COMSOL v1 implementation choice |
| Eigenvalue | propagation wavevector `kz` | Paper section 2 |
| Output effective index | `neff = kz/k0` | Paper Fig. 3 |
| Number of modes | `6-8` requested, keep two hybrid TM-like branches | Engineering choice |
| Search region | `neff ~ 1.536` | Fig. 3 trend |
| Polarization target | TM-like, transverse magnetic field mainly `Hx` | Fig. 2 caption |

## Postprocessing

| Item | Value Used |
|---|---|
| Main CSV | `results/neff_sweep.csv` |
| Raw CSV | `results/tables/neff_sweep_raw.csv` |
| Main figure | `results/fig3_reproduction.png` |
| Branches | `symmetric`, `antisymmetric` |
| Branch classification v1 | `Hx` sign / field localization metric when available; otherwise coupled-mode continuity |
| Success target | stable two-branch sweep and anticrossing-like trend near `5.6 um` |
