# Degiron 2009 NJP Fig. 3 Paper Notes

Paper: Aloyse Degiron et al., "Directional coupling between dielectric and long-range plasmon waveguides", New Journal of Physics 11, 015002 (2009).

Local PDF:

```text
papers/private/Degiron_2009_New_J._Phys._11_015002.pdf
```

## What Fig. 3 Computes

Fig. 3 is an eigenmode / mode-analysis calculation for a 2D cross section of a directional coupler. The structure is invariant along the propagation direction `z`, so the eigenvalue is the propagation wavevector `kz`. The plotted quantity is the effective index

$$
n_\mathrm{eff} = k_z / k_0,\qquad k_0 = 2\pi / \lambda_0.
$$

The purpose is to scan the total BCB thickness `t` and track two coupled eigenmodes:

- symmetric mode
- antisymmetric mode

The paper compares these coupled modes against isolated Au-stripe LR-SPP and isolated SU-8 waveguide modes. Around `t ~ 5.6 um`, the isolated modes cross, while the coupled modes show avoided crossing / anticrossing. That is the signature of strong hybridization and improved directional coupling.

## Relevant Reading Extract

The abstract states that the work designs and characterizes integrated directional couplers converting a dielectric waveguide mode into a long-range plasmon along a thin metal stripe. The central difficulty is weak coupling unless mode-matching conditions are carefully engineered.

The introduction frames LR-SPPs as low-loss plasmonic modes supported by thin metal stripes in a nearly homogeneous dielectric environment. Their low loss comes from weak confinement in metal, but that also causes momentum mismatch with ordinary dielectric waveguide modes.

Section 2 gives the model setup:

- Couplers are embedded in BCB and supported by Si with `4 um` thermal SiO2.
- The excitation wavelength is `1.55 um`.
- The 2D eigenmode problem is formulated in the `x-y` plane with propagation along `z`.
- COMSOL solves a weak-form finite-element eigenvalue problem where `k` is the eigenvalue.
- Loss is included, so `k` and `neff` are complex.
- Fig. 2 shows the transverse magnetic field, mainly `Hx`, for `t = 5.6 um`.

Fig. 3 plots:

- `Re(neff)` for symmetric and antisymmetric coupled eigenmodes.
- `Im(neff)` for the same modes.
- dashed reference curves for isolated Au stripe and isolated SU-8 waveguide.
- field-intensity line cuts above the Au stripe at selected thicknesses.

## Target Fig. 3 Trend

Approximate target from the rendered figure:

- `t` axis: about `4.8-10 um`.
- `Re(neff)` axis: about `1.530-1.541`.
- `Im(neff)` axis: about `0-5e-4`.
- The coupled branches anticross near `t ~ 5.6 um`.
- At large `t`, the symmetric branch is mainly SU-8-like and the antisymmetric branch is mainly Au LR-SPP-like.
- At small `t`, the mode character is exchanged.

## Fig. 1(b) Coordinate Interpretation

The paper caption states the couplers are positioned `3.3 um` above the SiO2 substrate. Fig. 1(b) labels the BCB/SiO2 interface as `y=0`, the Au stripe line at `y=3.3 um`, and the top BCB/air interface at `y=t`.

For the first reproducible model, this is interpreted as:

- BCB/SiO2 interface at `y=0`.
- Au and SU-8 bottom reference at `y=3.3 um`.
- SU-8 top at `y=4.8 um`.
- The minimum useful `t` is therefore near `4.8 um`.

This interpretation is consistent with the Fig. 3 scan starting just below `5 um`.

## What Is Not Reproduced In V1

This v1 target does not reproduce:

- fabrication process,
- SEM or microscope images,
- Fig. 5 coupling-length experiment,
- exact non-rectangular SU-8 cross section,
- exact isolated-mode dashed curves unless the coupled sweep succeeds first.

The purpose is to exercise the full paper-to-COMSOL-to-Magnus-to-report workflow and identify framework modules needed for optics_agent.
