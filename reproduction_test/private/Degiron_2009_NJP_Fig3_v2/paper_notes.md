# Degiron 2009 NJP Fig. 3 V2 Paper Notes

Paper:

```text
papers/private/Degiron_2009_New_J._Phys._11_015002.pdf
```

Target:

```text
Fig. 3: Dispersion of the two eigenmodes as a function of the BCB thickness t.
```

## What Fig. 3 Computes

Fig. 3 is a 2D cross-section eigenmode calculation for a dielectric waveguide / long-range plasmon directional coupler.

- Computational plane: `x-y`.
- Propagation direction: `z`.
- Eigenvalue: propagation wavevector amplitude `k`.
- Reported observable: complex effective index `neff = k/k0`.
- Scan variable: total BCB thickness `t`.
- Main physical effect: BCB thickness changes the slab-like confinement between the BCB/SiO2 lower interface and the BCB/air upper interface.

The two coupled modes are symmetric and antisymmetric. The target trend is an avoided crossing near `t ~= 5.6 um`, where the isolated Au LR-SPP and isolated SU-8 guided-mode dispersions cross.

## Relevant Figure Reading

Fig. 1(b) fixes the cross-section coordinate convention:

- BCB/SiO2 interface is at `y=0`.
- BCB/air upper interface is at `y=t`.
- Au stripe and SU-8 waveguide keep fixed absolute positions with respect to the bottom of BCB while `t` changes.
- The waveguides are positioned `3.3 um` above the SiO2/BCB interface.

Fig. 2 shows the transverse magnetic field of the two coupled eigenmodes at `t=5.6 um`.

- The modes are almost TM-polarized.
- The plotted field component is mainly horizontal `Hx`.
- The field reaches both BCB/air and BCB/SiO2 interfaces, so finite BCB thickness is not a small perturbation.

Fig. 3 shows:

- red: symmetric coupled eigenmode;
- blue: antisymmetric coupled eigenmode;
- gray dashed: isolated Au stripe LR-SPP;
- black dashed: isolated SU-8 waveguide mode.

Approximate visual target:

| Quantity | Visual range / trend |
|---|---|
| `Re(neff)` | about `1.530-1.541` |
| `Im(neff)` | about `0-5e-4` |
| anticrossing | near `t ~= 5.6 um` |
| large `t` | red branch is more SU-8-like, blue branch is more Au-like |
| small `t` | mode character swaps after anticrossing |

## V2 Interpretation

The most important modeling point is that `t` changes only the upper BCB/air boundary. The Au stripe and SU-8 guide stay fixed at the same height above the lower SiO2/BCB interface.

The v2 first executable model uses a scalar TM-like PDE for the plotted `Hx`-dominant mode:

```text
div((1/epsr) grad(Hx)) + (k0^2 - beta^2/epsr) Hx = 0
```

In COMSOL Coefficient Form PDE eigenvalue form, this is implemented as:

```text
-div((1/epsr) grad(u)) - k0^2 u = lambda (1/epsr) u
lambda = -beta^2
neff = beta/k0
```

This is not the final full-vector Wave Optics reproduction. It is a controlled scalar FEM mode-analysis approximation intended to avoid the v1 failure mode where guessed Wave Optics Java tags reached the eigensolver and failed matrix factorization.

## V2 Scope

V2 first attempts:

1. isolated SU-8 scalar mode smoke;
2. isolated Au scalar LR-SPP smoke;
3. coupled scalar smoke;
4. coupled scalar sweep only if the smoke produces plausible rows.

V2 does not claim full agreement with the paper unless the results are physically plausible and the limitation of the scalar approximation is explicitly discussed.

