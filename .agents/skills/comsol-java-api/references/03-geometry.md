# Geometry

This file solves: build, edit, inspect, and debug COMSOL geometry sequences from Java.

## Core Sequence

```java
model.geom().create("geom1", 2);
model.geom("geom1").lengthUnit("um");
model.geom("geom1").feature().create("r1", "Rectangle");
model.geom("geom1").feature("r1").set("size", new String[]{"4", "2"});
model.geom("geom1").feature("r1").set("pos", new String[]{"-2", "-1"});
model.geom("geom1").run();
```

COMSOL 4.3 also accepts shorthand used in current probes:

```java
model.geom("geom1").create("r1", "Rectangle");
```

Preserve the style of the target file.

## Common Feature Types

| Category | Feature types |
|---|---|
| 2D primitives | `Rectangle`, `Circle`, `Ellipse`, `Polygon`, `BezierPolygon`, `Square` |
| 3D primitives | `Block`, `Sphere`, `Cylinder`, `Cone`, `Torus`, `Ellipsoid`, `Tetrahedron` |
| Booleans | `Union`, `Difference`, `Intersection`, `Compose` |
| Transforms | `Move`, `Rotate`, `Scale`, `Mirror`, `Array`, `Copy` |
| Work planes / 3D from 2D | `WorkPlane`, `Extrude`, `Revolve`, `Sweep` |
| Virtual operations | `CompositeEdges`, `CompositeFaces`, `CompositeDomains`, `IgnoreEdges`, `IgnoreFaces`, `FormCompositeFaces` |
| Geometry selections | `Selection` |

## Settings And Selections

| Key | Use |
|---|---|
| `size` | Rectangle/block dimensions. |
| `pos` | Feature position. |
| `r`, `semiaxes`, `p`, `table` | Circle/ellipse/polygon settings. |
| `input` | Objects for boolean/transform operations. |
| `input2` | Objects to subtract in `Difference`. |
| `keep` | Keep input objects for many operations. |
| `createselection` | Create named entity selections from geometry features. |
| `repairTol` | Boolean/repair tolerance; tune when close edges/faces cause build errors. |

Example boolean:

```java
model.geom("geom1").create("blk", "Rectangle");
model.geom("geom1").create("hole", "Circle");
model.geom("geom1").create("dif1", "Difference");
model.geom("geom1").feature("dif1").selection("input").set("blk");
model.geom("geom1").feature("dif1").selection("input2").set("hole");
model.geom("geom1").run();
```

## Build And Inspect

| Call | Use |
|---|---|
| `geom(tag).run(ftag)` | Build through a feature. |
| `geom(tag).runPre(ftag)` | Build all preceding features. |
| `geom(tag).runAll()` | Build before finalize. |
| `geom(tag).run()` | Build all features including finalize/virtual ops. |
| `geom(tag).feature(ftag).status()` | Check built/edited/warning/error status. |
| `geom(tag).feature(ftag).message()` | First error/warning message. |
| `geom(tag).feature(ftag).objectNames()` | Objects produced by a feature. |
| `geom(tag).objectNames()` | Objects in the sequence. |

## Work Planes

```java
model.geom().create("geom1", 3);
model.geom("geom1").feature().create("wp1", "WorkPlane");
model.geom("geom1").feature("wp1").set("quickplane", "xy");
model.geom("geom1").feature("wp1").geom().feature().create("r1", "Rectangle");
model.geom("geom1").run();
```

Work-plane subgeometry has its own 2D sequence. For headless reproducibility, keep tags explicit.

## Measurements And Entity Lookup

```java
model.geom("geom1").measure().selection().init(2);
model.geom("geom1").measure().selection().set("r1", new int[]{1});
double area = model.geom("geom1").measure().getVolume();
```

Use geometry-created selections or post-build entity lookup before assigning materials/physics. Entity numbers can change after booleans, arrays, or virtual operations.

## Export

Manual APIs include `geom(tag).exportFinal(filename)`, `geom(tag).export(filename)`, and STL/Parasolid options. Avoid geometry file export inside `run()` for Magnus templates unless the runner contract explicitly expects it.

## Notes And Common Errors

- Feature type strings are capitalized and case-sensitive.
- Boolean `Difference` needs `input` and `input2`; forgetting `input2` often builds the wrong domain.
- `createselection` can create stable named selections such as geometry feature domain/boundary selections; use this to avoid hard-coded domain IDs when possible.
- If a feature fails, inspect `message()` and problem details before changing mesh or solver.
