# Degiron 2009 NJP Fig. 3 V2 Parameter Table

## Geometry

| Category | Parameter | V2 value | Source / status |
|---|---|---:|---|
| coordinate system | computational plane | `x-y` | Paper section 2 |
| coordinate system | propagation direction | `z` | Paper section 2 |
| lower interface | BCB/SiO2 | `y=0 um` | Fig. 1(b) |
| upper interface | BCB/air | `y=t` | Fig. 1(b) |
| Au stripe | width | `4.6 um` | Fig. 1(b) caption |
| Au stripe | thickness | `0.036 um` | Fig. 1(b) caption |
| Au stripe | v2 coordinates | `x=[-4.6,0] um`, `y=[3.3,3.336] um` | Fig. 1(b), rectangular interpretation |
| SU-8 guide | average width | `2.0 um` | Fig. 1(b) caption |
| SU-8 guide | average thickness | `1.5 um` | Fig. 1(b) caption |
| SU-8 guide | v2 shape | rectangle | Engineering simplification |
| SU-8 guide | v2 coordinates | `x=[2.5,4.5] um`, `y=[3.3,4.8] um` | Fig. 1(b), rectangular interpretation |
| lateral gap | Au right edge to SU-8 left edge | `2.5 um` | Fig. 1(b) caption |
| waveguide height | fixed distance above BCB/SiO2 interface | bottom/reference at `y=3.3 um` | Paper states fixed with respect to bottom BCB |
| SiO2 | thickness | `4 um` | Section 2 |
| Si | lower substrate | v2 truncated substrate below SiO2 | Engineering approximation |
| lateral window | `x` range | initially `[-8,8] um` | Engineering approximation |
| vertical window | `y` range | initially `[-4,t+2] um` | Engineering approximation |

## Materials

| Material | Parameter | V2 value | Source / status |
|---|---|---:|---|
| wavelength | `lambda0` | `1.55 um` | Paper |
| Au | relative permittivity | `-132 + 12.65i` | Paper |
| BCB | refractive index | `1.535` | Paper |
| SiO2 | refractive index | `1.444` | Paper |
| SU-8 | refractive index | `1.57 + 8e-5i` | Paper |
| air | refractive index | `1.0` | Standard approximation |
| Si | refractive index | `3.48`, lossless | Engineering approximation |

## Calculation Type

| Item | V2 value | Status |
|---|---|---|
| Intended paper physics | full electromagnetic eigenmode solve | Paper |
| V2 first executable physics | scalar TM-like `Hx` Coefficient Form PDE | Approximation |
| PDE dependent variable | `u ~= Hx` | Approximation |
| eigenvalue in COMSOL PDE | `lambda = -beta^2` | V2 definition |
| effective index conversion | `neff = sqrt(-lambda)/k0` | V2 postprocess |
| boundary condition | finite window with Dirichlet exterior | First approximation, boundary-sensitive |
| mesh | explicit FreeTri | Based on v1 mesh failure |

## Sweep Points

Smoke:

```text
t = 5.6, 6.6 um
```

Sweep, if smoke passes:

```text
4.8, 5.0, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0,
6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0,
8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0
```

## Validation Targets

| Output | Target |
|---|---|
| isolated SU-8 `Re(neff)` | between BCB and SU-8 index, around `1.536-1.540` at larger `t` |
| isolated Au `Re(neff)` | near BCB index, around `1.535-1.538` |
| coupled `Re(neff)` | two branches with avoided crossing near `t ~= 5.6 um` |
| coupled `Im(neff)` | positive, order `0-5e-4`; small-`t` branch trends must be checked explicitly |

