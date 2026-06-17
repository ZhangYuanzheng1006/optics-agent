# API Patterns For Optics

This file solves: map COMSOL Java API layers to optics_agent waveguide, eigenmode, and paper-reproduction models, and identify where this Java API manual is insufficient.

## Source Split

- Manual-derived: generic Java API layers for geometry, mesh, study, solver, results.
- optics_agent-derived: Degiron 2009 Fig. 3 and COMSOL runtime probes exposed headless batch restrictions, mesh fallback needs, and mode-analysis gaps.

## Waveguide/Eigenmode API Layers

| Layer | API objects | Typical content |
|---|---|---|
| Parameters | `model.param()` | `lambda0`, `k0`, widths, gaps, thickness sweep, material constants. |
| Geometry | `model.geom()` | 2D cross-section, layer stack, metal, dielectric guide, air/substrate/domain truncation. |
| Selections | `model.selection()`, geometry `createselection` | Domains for materials; boundaries for scattering/PML/PEC/symmetry. |
| Materials | `model.material()` or variables | Complex permittivity/refractive index per domain. |
| Physics | `model.physics()` | Wave Optics/RF interface, mode-analysis feature, boundary conditions. |
| Mesh | `model.mesh()` | Explicit `FreeTri`/`FreeTet`, size controls near metal/gaps/interfaces. |
| Study | `model.study()` | `ModeAnalysis`/`BoundaryModeAnalysis`/`Eigenvalue`/`Frequency`, depending on module and dimension. |
| Solver | `model.sol()` | Auto sequence plus eigenvalue shift, number of modes, tolerances. |
| Results | `model.result()` | `neff`, `beta`, losses, field profiles, tables/stdout rows. |

## What The Java API Manual Does Not Provide

The Java API reference does not replace:

- Wave Optics Module User's Guide: exact electromagnetic interface options, mode-analysis settings, ports, scattering/PML boundaries, and variables such as `emw.neff`.
- RF Module User's Guide: RF interface strings and boundary mode analysis behavior.
- COMSOL Multiphysics Reference Manual: detailed solver theory, eigenvalue solver behavior, advanced solver errors, and version-specific changes.

Use GUI-exported Java for exact COMSOL 6.3 feature tags and setting keys.

## Degiron 2009 Fig. 3 Lessons

- Java API syntax is official, but hand-written Java is not equivalent to a correct GUI model.
- Mode analysis depends on physics feature, boundary, material, mesh, and solver sequence details that were not fully recoverable from the generic Java API manual.
- Physics-controlled mesh failed in the actual Degiron run; explicit `FreeTri` mesh was a useful fallback.
- Full-vector mode analysis reached the eigensolver but failed matrix factorization across shifts. That is a physical/numerical setup problem, not just a runner problem.
- `emw.neff` and `ewfd.neff` are not guaranteed to exist. They depend on the selected physics interface and study type.

## Degiron Debug Checklist

Use this order when a coupled Wave Optics mode-analysis model compiles/saves but fails in the eigensolver:

1. Confirm pipeline status separately from physics status. A Magnus job success or saved `.mph` only proves the platform contract; it does not prove physical reproduction.
2. Stop tuning surrogate/fallback data once the Java/batch path is proven. Use fallback only as a labeled pipeline test.
3. Build isolated SU-8 dielectric waveguide first. Validate domain size, boundary/PML, material selection, mesh, `shift`, and expected `neff`.
4. Build isolated Au LR-SPP stripe next. Validate complex metal material, boundary/PML, mesh near metal, loss sign, and expected real/imaginary effective index scale.
5. Build the coupled Au+SU8 system only after both isolated models return plausible modes.
6. Use a minimal COMSOL 6.3 GUI-exported Java mode-analysis template for the first isolated Wave Optics/RF model. Treat it as the source for physics feature tags, boundaries, study, solver sequence, and result variables.
7. Check all domain and boundary selections after every geometry change; do not rely on stale entity IDs.
8. Record whether each output is `neff`, `beta`, or raw eigenvalue before comparing branches.

## Notes And Common Errors

- Do not report a surrogate/fallback sweep as a physical COMSOL reproduction.
- If mode-analysis settings are unknown, explicitly request or generate a minimal GUI-exported Java template rather than guessing.
- Keep stdout CSV markers simple when COMSOL Java sandbox blocks file output.
