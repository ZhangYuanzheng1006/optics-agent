# Results And Export

This file solves: create datasets, evaluate expressions, select solution numbers, use tables, and export results without relying on GUI interaction.

## Datasets

```java
model.result().dataset().create("dset1", "Solution");
model.result().dataset("dset1").set("solution", "sol1");
```

Common dataset feature types: `Solution`, `CutLine2D`, `CutLine3D`, `CutPlane`, `CutPoint1D`, `CutPoint2D`, `CutPoint3D`, `Average`, `Integral`, `Maximum`, `Minimum`, `Surface`, `Contour`, `Mesh`, `Parametric`.

## Numerical Evaluation

### Global Values

```java
model.result().numerical().create("gev1", "EvalGlobal");
model.result().numerical("gev1").set("data", "dset1");
model.result().numerical("gev1").set("expr", new String[]{"lambda"});
double[][] real = model.result().numerical("gev1").getReal();
double[][] imag = model.result().numerical("gev1").getImag(true, false);
```

### Field Values

```java
model.result().numerical().create("ev1", "Eval");
model.result().numerical("ev1").set("data", "dset1");
model.result().numerical("ev1").set("expr", new String[]{"u"});
double[][][] data = model.result().numerical("ev1").getData();
double[][] xyz = model.result().numerical("ev1").getCoordinates();
```

`Eval` is Java-API specific in the manual and does not appear as a normal GUI feature.

## Solution Selection Keys

| Key | Use |
|---|---|
| `solnum` | Inner solution number(s). |
| `solnumindices` | Alternate indexed selection. |
| `outersolnum` | Outer parametric solution index. |
| `outersolnumindices` | Alternate outer indexed selection. |
| `looplevel`, `looplevelinput` | Multi-level nested solution selection. |
| `t`, `interp` | Time interpolation or transient solution selection. |
| `solrepresentation` / `solrepresentat` | Whether selection is by solution info or explicit solnum; spelling differs in tables/versions, validate from GUI export. |

For parameter sweeps, be explicit about outer vs inner solution numbers before trusting result row order.

## Tables

```java
model.result().table().create("tbl1", "Table");
model.result().numerical("gev1").set("table", "tbl1");
model.result().numerical("gev1").setResult();
double[][] tableReal = model.result().table("tbl1").getReal();
```

Useful table methods: `setTableData`, `getReal`, `getImag`, `getTableData`, `getTableRow`, `clearTableData`.

## Exports

Manual export feature types include `Data`, `Plot`, `Animation`, `Image1D`, `Image2D`, `Image3D`, and `Mesh`.

```java
model.result().export().create("data1", "Data");
model.result().export("data1").set("data", "dset1");
model.result().export("data1").set("expr", new String[]{"u"});
```

For Magnus batch Java, prefer stdout markers or COMSOL tables unless the runner contract explicitly allows a known output path. Avoid Java file IO inside `run()`.

## Notes And Common Errors

- `result variable not found` means the expression is not in scope for the dataset, solution, physics interface, or solver type. For `emw.neff`/`ewfd.neff`, confirm the physics interface and mode-analysis study actually define that variable.
- `getImag()` can allocate zeros for real results; do not treat non-null imaginary arrays as proof of complex physics.
- Result row/column orientation changes with `columnwise`.
- Store a table when a later export or postprocessor needs stable column labels.
