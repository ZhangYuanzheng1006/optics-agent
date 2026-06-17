# GUI-Exported Java

This file solves: read, trim, and reuse Java files exported from COMSOL Desktop without losing physics or solver details.

## What GUI Export Is Good For

- Treat COMSOL 6.3 GUI-exported Java as the highest-priority source for physics feature tags, boundary condition features, material/selection wiring, study steps, solver sequence, and result variables.
- Exact physics interface strings.
- Default feature tags and feature type names.
- Boundary and domain selections COMSOL accepted.
- Study-step and solver-sequence order.
- Result variable names and datasets.
- Version-specific COMSOL 6.3 API style.

When the Java API Reference and GUI-exported Java disagree for Wave Optics/RF mode-analysis details, follow the GUI-exported Java first and document the difference.

## What To Check First

1. Imports and public class name.
2. `public static Model run()` and whether it returns the model.
3. Geometry tags and whether geometry features were run.
4. Material/physics selections after geometry build.
5. Study feature tags and solver tags.
6. Whether `model.sol(...).runAll()` or `model.study(...).run()` is present.
7. Result numerical features and exported expressions.

## Headless Cleanup

Remove or ignore for Magnus batch:

- Swing/SWT GUI panels.
- GUI progress widgets.
- Java threads used only for GUI responsiveness.
- Desktop-only open dialogs or local absolute file paths.
- Plot-window setup that is not needed for result extraction.

Keep:

- Model creation and model-node/component setup.
- Parameters and units.
- Geometry, selections, material, physics, mesh.
- Study, solver, and result evaluation.
- Exact feature type strings and setting keys.

## Minimal Patch Pattern

```java
public static Model run() throws Exception {
  Model model = ModelUtil.create("Model");
  // keep GUI-exported model setup here
  model.sol("sol1").runAll();
  return model;
}

public static void main(String[] args) throws Exception {
  Model model = run();
  if (args.length > 0) model.save(args[0]);
  System.out.println("GUI_EXPORTED_MODEL_OK");
}
```

## Notes And Common Errors

- Do not simplify away selections unless you re-check entity IDs.
- Do not replace module-specific physics strings by guessed alternatives.
- If a GUI-exported file uses component-scoped calls, keep that style.
- GUI chapter content about custom Swing/SWT user interfaces is usually irrelevant to optics_agent headless batch.
