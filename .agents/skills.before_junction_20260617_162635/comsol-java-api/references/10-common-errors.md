# Common Errors

This file solves: diagnose common COMSOL Java API, headless batch, mesh, solver, and result extraction failures in optics_agent.

## Batch And Java Structure

| Symptom | Likely cause | Action |
|---|---|---|
| Java compiles but no output MPH | `run()` missing, model not returned, runner expects output filename, or `main()` did not save | Add `public static Model run()`, return model, and `if (args.length > 0) model.save(args[0]);` in `main()`. |
| `OUTPUT_MPH_MISSING` | COMSOL did not create the normalized MPH output | Inspect stdout/stderr and generated file names; use `BatchSafeModel.java` shape. |
| Sandbox/security exception | `System.getenv`, `System.getProperty`, or Java file IO inside `run()` | Move data transfer to stdout markers, COMSOL tables, or runner-side postprocessing. |
| Class execution error with helpers | Inner class or anonymous class not accepted by COMSOL runtime | Use one public class and static helper methods. |
| Empty stdout marker / runner manifest | Model crashed before marker, marker misspelled, or stdout parsing expected different prefix | Print a unique `CASE_OK` marker after solve and before exit. |

## Geometry And Selection

| Symptom | Likely cause | Action |
|---|---|---|
| Material/physics applied to wrong region | Hard-coded domain IDs changed after geometry edit | Use geometry-created named selections or re-query entities after `geom.run()`. |
| Boolean output wrong | Missing `input`/`input2`, wrong `keep`, or wrong feature order | Inspect geometry object names and feature status. |
| Boundary condition missing | Selection dimension mismatch | Confirm entity dimension: 2D domains use dim 2; boundaries use dim 1. |

## Mesh

| Symptom | Likely cause | Action |
|---|---|---|
| Physics-controlled mesh failed | Physics heuristics could not mesh thin/high-contrast geometry | Switch to explicit `FreeTri`/`FreeTet` with `Size` controls. |
| Mesh warning but solve continues | Some entities failed or quality is poor | Inspect `hasWarning()`, min quality, and mesh statistics. |
| Too many elements | Overly small global `hmax` | Apply local size selections near metal/gaps instead of globally. |

## Solver

| Symptom | Likely cause | Action |
|---|---|---|
| Eigensolver matrix factorization failed | Bad shift, singular/open domain, bad boundary/PML, wrong physics mode setup, bad material selections | Try isolated validation model, different shifts, explicit boundaries/PML, and GUI-exported mode-analysis settings. |
| No eigenvalues near expected branch | `shift` wrong or variable units mismatch | Set `shift` in the units/scale expected by the study; compare to GUI export. |
| Solver sequence missing | GUI export did not include a run command or hand-written file omitted solver | Use `createAutoSequence("std1")` and `runAll()`, or preserve GUI solver sequence. |
| Study type unsupported | Physics interface does not support chosen study | Confirm with GUI-exported Java or module documentation. |

## Results

| Symptom | Likely cause | Action |
|---|---|---|
| `emw.neff` / `ewfd.neff` not found or unreliable | Wrong physics interface, wrong study type, changed module tag, no mode-analysis variable, or variable not defined for that solution | Inspect COMSOL 6.3 GUI result expressions; verify whether the model exposes `neff`, `beta`, `kz`, or raw eigenvalue; do not invent variable names from the Java API Reference. |
| Empty table | Numerical feature not evaluated or wrong `data`/`table` property | Call `setResult()` or `getReal()` after setting `data`, `expr`, and solution selection. |
| Wrong sweep row order | Confused inner/outer solution numbers | Set `solnum`, `outersolnum`, `looplevel`, and record row mapping explicitly. |
| Complex result mishandled | Imaginary array allocated as zeros or expression is real | Check `isComplex()` before interpreting imaginary data. |

## Extra Manuals Needed

- Wave Optics Module User's Guide: required for production electromagnetic mode-analysis settings.
- RF Module User's Guide: required when using RF electromagnetic interfaces or boundary mode analysis.
- COMSOL Multiphysics Reference Manual: required for deep solver diagnostics and advanced solver feature semantics.
