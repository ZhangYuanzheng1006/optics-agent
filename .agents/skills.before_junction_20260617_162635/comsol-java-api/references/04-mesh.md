# Mesh

This file solves: create explicit mesh sequences, replace failed physics-controlled mesh, read mesh diagnostics, and avoid common headless meshing failures.

## Core Sequence

```java
model.mesh().create("mesh1", "geom1");
model.mesh("mesh1").automatic(false);
model.mesh("mesh1").feature().create("size1", "Size");
model.mesh("mesh1").feature("size1").set("hmax", "0.1[um]");
model.mesh("mesh1").feature().create("ftri1", "FreeTri");
model.mesh("mesh1").run();
```

## Mesh Feature Types

| Feature | Purpose |
|---|---|
| `FreeTri` | 2D free triangular mesh. |
| `FreeTet` | 3D free tetrahedral mesh. |
| `Size` | Element size control. Can be top-level or attribute feature. |
| `Distribution` | Number/distribution along edges. |
| `BndLayer`, `BndLayerProp` | Boundary layer mesh. |
| `Map` | Mapped mesh on structured domains/faces. |
| `Refine` | Refine existing mesh. |
| `Convert`, `Scale`, `Sweep` | Mesh operations for special workflows. |

## Physics-Controlled Mesh

```java
model.mesh("mesh1").automatic(true);
model.mesh("mesh1").autoMeshSize(4);
```

Physics-controlled mesh updates from active physics when built. It is useful for GUI-generated models, but in Degiron Fig. 3 it failed before solving. For headless probes, prefer explicit `FreeTri`/`FreeTet` with `Size` when mesh failure blocks solver diagnosis.

## Feature Status And Diagnostics

| Call | Use |
|---|---|
| `mesh(tag).feature(ftag).isBuilt()` | Built state. |
| `isEdited()`, `hasError()`, `hasWarning()` | Diagnose sequence state. |
| `mesh(tag).clearMesh()` | Clear mesh only. |
| `mesh(tag).feature().clear()` | Clear mesh features. |
| `mesh().clearMeshes()` | Clear all mesh data. |

Mesh statistics:

```java
int n = model.mesh("mesh1").getNumElem();
String[] types = model.mesh("mesh1").getTypes();
double minq = model.mesh("mesh1").getMinQuality();
double meanq = model.mesh("mesh1").getMeanQuality();
```

## Mesh Data Access

```java
double[][] vertices = model.mesh("mesh1").getVertex();
int[][] triangles = model.mesh("mesh1").getElem("tri");
int[] entity = model.mesh("mesh1").getElemEntity("tri");
```

Use mesh data APIs for diagnostics or transfer only. Do not build full custom mesh data unless needed; it is easy to break entity mapping.

## Boundary Layer Pattern

```java
model.mesh("mesh1").feature().create("ftri1", "FreeTri");
model.mesh("mesh1").feature().create("bl1", "BndLayer");
model.mesh("mesh1").feature("bl1").feature().create("blp1", "BndLayerProp");
model.mesh("mesh1").feature("bl1").feature("blp1").selection().set(new int[]{1, 2});
model.mesh("mesh1").run();
```

Exact boundary-layer settings are geometry-specific; check GUI-exported Java for `thickness`, `nlayer`, and stretching keys in COMSOL 6.3.

## Notes And Common Errors

- Add mesh features after geometry `run()` unless the GUI export shows a different dependency.
- `FreeTri`, `FreeTet`, and `FreeQuad` can produce `MeshError`/`MeshWarning` problem features. Inspect them instead of treating every failure as a solver problem.
- For optics, explicitly refine metal, gaps, sharp corners, and high-index interfaces.
- A mesh success does not imply physical boundary conditions are correct.
