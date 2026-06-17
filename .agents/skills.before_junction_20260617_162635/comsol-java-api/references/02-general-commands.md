# General Commands

This file solves: manage variables, functions, selections, materials, physics interfaces, and coupling operators in COMSOL Java.

## Property Access Pattern

Most COMSOL objects use the same set/get family:

```java
feature.set("size", new String[]{"w", "h"});
feature.set("pos", new String[]{"x0", "y0"});
String value = feature.getString("size");
```

Returned arrays are copies; mutating a returned array does not change the model.

## Variables

```java
model.variable().create("var1");
model.variable("var1").model("comp1");
model.variable("var1").set("epsr", "n_core^2");
model.variable("var1").selection().geom("geom1", 2);
model.variable("var1").selection().set(new int[]{1, 2});
```

| Method | Use |
|---|---|
| `model.variable().create(tag)` | Create a variable group. |
| `variable(tag).set(name, expr[, descr])` | Define expression. |
| `variable(tag).selection().named(sel)` | Scope to named selection. |
| `variable(tag).varnames()` | List variables. |

## Functions

```java
model.func().create("int1", "Interpolation");
model.func("int1").set("funcname", "nAu");
```

Common function types include analytic, interpolation, piecewise, rectangle, step, random, and file-backed functions. File-backed function import is risky in Magnus Java sandbox; prefer embedding short tables or load data on runner side.

## Materials

```java
model.material().create("mat1");
model.material("mat1").selection().set(new int[]{1});
model.material("mat1").propertyGroup("def").set("relpermittivity", "n_core^2");
```

Exact material property group names and tensor shapes are module/version-sensitive. Use GUI-exported Java to confirm `propertyGroup(...)` and property keys for real optical materials.

## Physics Interfaces

```java
model.physics().create("c", "CoefficientFormPDE", "geom1");
model.physics("c").feature("cfeq1").set("c", "1");
model.physics("c").create("dir1", "DirichletBoundary", 1);
model.physics("c").feature("dir1").selection().all();
```

| Call | Use |
|---|---|
| `model.physics().create(tag, physint, geomtag)` | Add physics interface on geometry. |
| `model.physics(tag).feature().create(ftag, feature[, dim])` | Add physics feature. |
| `physics(tag).feature(ftag).set(key, value)` | Set feature property. |
| `physics(tag).feature(ftag).selection().set(...)` | Scope feature to entities. |
| `physics(tag).field(fieldname).fieldname(...)` | Override dependent variable names. |

For Wave Optics/RF, the Java API reference does not provide enough module-specific detail. Confirm interface strings, boundary feature strings, and variable names from Wave Optics/RF docs or GUI-exported Java.

## Selections

```java
model.selection().create("sel_core");
model.selection("sel_core").geom("geom1", 2);
model.selection("sel_core").set(new int[]{3});
model.physics("c").feature("src1").selection().named("sel_core");
```

| Selection type | Useful keys |
|---|---|
| explicit | `geom(...)`, `set(...)`, `add(...)`, `remove(...)`, `entities(dim)` |
| ball | `entitydim`, `posx`, `posy`, `posz`, `r`, `condition` |
| box | `entitydim`, `xmin`, `xmax`, `ymin`, `ymax`, `zmin`, `zmax` |
| adjacent | `entitydim`, `outputdim`, `input` |

Selection/domain mismatch is a common source of silent wrong physics. After geometry changes, re-check entity numbers or use geometry-created named selections.

## Coupling Operators

```java
model.cpl().create("int1", "Integration", "geom1");
model.cpl("int1").selection().set(new int[]{1, 2});
model.cpl("int1").set("opname", "int_core");
```

Supported types from the manual: `GeneralExtrusion`, `LinearExtrusion`, `BoundarySimilarity`, `IdentityMapping`, `GeneralProjection`, `LinearProjection`, `Integration`, `Average`, `Maximum`, `Minimum`.

| Type | Typical use |
|---|---|
| `Integration` | Integrate field power, loss, or normalization over domains/boundaries. |
| `Average` | Average material or field quantities. |
| `Maximum` / `Minimum` | Field extrema or mesh/geometry diagnostics. |
| `GeneralExtrusion` / `Projection` | Mapping expressions between source and destination geometries. Validate carefully. |

## Notes And Common Errors

- Feature type strings are case-sensitive.
- Unit-bearing expressions should be strings, not raw doubles, when units matter.
- Module-specific physics keys can compile but be physically wrong; use GUI-exported Java for real Wave Optics models.
