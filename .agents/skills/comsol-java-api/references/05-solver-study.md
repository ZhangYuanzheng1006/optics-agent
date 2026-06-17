# Study And Solver

This file solves: create study steps and solver sequences, run them safely, inspect eigenvalue settings, and retrieve solution data.

## Study Entry Points

```java
model.study().create("std1");
model.study("std1").feature().create("eig", "Eigenvalue");
model.study("std1").feature("eig").set("neigs", 6);
```

Current optics_agent probes also use:

```java
model.study("std1").create("eig", "Eigenvalue");
```

If a method fails, follow the exact style produced by COMSOL 6.3 GUI export.

| Study type | Use |
|---|---|
| `Stationary` | Static solve. |
| `Time` | Implicit time-dependent solve. |
| `Frequency` | Frequency-domain study. Manual notes this as generally allowed by physics. |
| `Eigenvalue` | Generic eigenvalue solve. |
| `BoundaryModeAnalysis`, `ModeAnalysis` | Wave Optics/RF mode-analysis names are module/version-specific; verify from GUI-exported Java. |

## Eigenvalue vs Mode Analysis

| Concept | What it means | How to validate |
|---|---|---|
| Generic `Eigenvalue` | Solver/study pattern for a PDE eigenproblem. `StudySolverEigenvalue.java` demonstrates this only with `CoefficientFormPDE`. | Java API Reference and a generic PDE smoke test are enough for syntax. |
| Wave Optics/RF `ModeAnalysis` or `BoundaryModeAnalysis` | Physics-module workflow for propagation modes, often returning propagation constant, effective index, and mode fields. | Must come from COMSOL 6.3 GUI-exported Java or Wave Optics/RF docs. |
| `lambda` / eigenvalue from `getPVals()` | Generic eigenvalue variable from the solver. | Check solver feature `eigname` and result dataset. |
| `beta`, `neff`, `emw.neff`, `ewfd.neff` | Module-defined mode-analysis variables, not guaranteed by the generic Java API. | Inspect GUI result expressions and variable list from the working COMSOL 6.3 model. |

Do not treat a successful generic eigenvalue template as proof that Wave Optics mode analysis is correct.

## Solver Sequence

```java
model.sol().create("sol1");
model.sol("sol1").study("std1");
model.sol("sol1").createAutoSequence("std1");
model.sol("sol1").runAll();
```

Manual entry points:

| Call | Use |
|---|---|
| `model.sol().create(tag)` | Create solution object. |
| `sol(tag).feature().create(ftag, oper)` | Add solver operation feature. |
| `sol(tag).createAutoSequence(studyTag)` | Generate solver sequence from study and active physics. |
| `sol(tag).run(ftag)`, `runFrom(ftag)`, `runAll()` | Execute solver sequence. |
| `sol(tag).clearSolution()` | Clear solution data, keep features. |
| `sol(tag).updateSolution()` | Update solution for current model. |

`createAutoSequence("std1")` is a useful first pass, but it is limited: it generates a default sequence from the study and active physics. It may omit or alter module-specific mode-analysis details, linearization settings, solver attributes, result variables, or boundary/PML assumptions that a GUI-created model needs. For production Wave Optics/RF work, preserve the GUI-exported solver sequence unless a specific simplification is being tested.

## Eigenvalue Solver Settings

```java
model.sol("sol1").feature().create("eig1", "Eigenvalue");
model.sol("sol1").feature("eig1").set("neigs", 6);
model.sol("sol1").feature("eig1").set("shift", "1.536");
model.sol("sol1").feature("eig1").set("rtol", "1e-4");
```

| Key | Meaning |
|---|---|
| `neigs` | Number of eigenvalues sought; manual default 6. |
| `shift` | Search location; can be real or complex scalar. Critical for mode problems. |
| `eigname` | Eigenvalue variable name; manual default `lambda`. |
| `eigref` | Linearization point for nonlinear eigenvalue problems. |
| `rtol` | Relative tolerance. |
| `linpmethod`, `linpsol`, `linpsoluse` | Linearization point settings. |
| `maxeigit`, `krylovdim` | Iteration/Krylov controls. |
| `solfile`, `solfileblock` | Store solution on temporary file; validate in headless runtime before relying on it. |

For Wave Optics mode analysis, these are only generic solver settings. The Java API manual does not define the complete physics-specific mode-analysis setup. Use Wave Optics/RF documentation or GUI-exported Java for propagation direction, mode variable, boundary, and solver-sequence details.

Shift unit risk:

- In a generic eigenvalue problem, `shift` is in the eigenvalue variable's scale.
- In mode analysis, the GUI may express search location as `neff`, `beta`, `kz`, or a module-specific transformed eigenvalue.
- Do not mix dimensionless `neff` with dimensional `beta = k0*neff` or `kz` shifts. Compare the GUI-exported Java setting and the study's eigenvalue variable before changing `shift`.
- For optics, record whether output is `neff`, `beta`, or raw eigenvalue, and convert explicitly in postprocessing.

## Stationary And Parametric

```java
model.sol("sol1").feature().create("stat1", "Stationary");
model.sol("sol1").feature("stat1").set("nonlin", "auto");
model.sol("sol1").feature("stat1").feature().create("par1", "Parametric");
model.sol("sol1").feature("stat1").feature("par1").set("pname", "w");
model.sol("sol1").feature("stat1").feature("par1").set("plistarr", new String[][]{{"1", "2", "3"}});
```

Common stationary keys: `control`, `nonlin`, `linpmethod`, `linpsol`, `linpsoluse`, `reacf`, `solnum`, `stol`, `storelinpoint`.

## Solution Data

| Call | Use |
|---|---|
| `sol(tag).getType()` | `Stationary`, `Parametric`, `Time`, or `Eigenvalue`. |
| `sol(tag).getPVals()` | Param values, times, or eigenvalues depending on solution type. |
| `getPValsImag()` | Imaginary eigenvalue/parameter values. |
| `getU()`, `getUImag()` | Solution vector data. |
| `getUBlock(...)` | Partial solution vector for large solves. |
| `getParamNames()`, `getParamVals()` | Parameter metadata. |
| `feature(ftag).getSparseMatrixVal("K")` | Assembled matrix values after an `Assemble`/matrix-producing feature. |

## Notes And Common Errors

- `createAutoSequence("std1")` is the fastest robust start, but GUI-exported Java is better for complex mode-analysis solver stacks.
- A solver can run and still return the wrong branch. Always validate output variables and expected ranges.
- `Failed to compute the matrix factorization in the eigensolver` may mean bad shift, bad boundary/PML, singular/open domain, wrong physics setup, or bad material/domain selections.
