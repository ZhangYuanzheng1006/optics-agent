# Batch Java Files

This file solves: structure COMSOL Java files so they compile and run under `comsol batch` and the optics_agent runner.

## Manual-Derived Java File Shape

```java
import com.comsol.model.*;
import com.comsol.model.util.*;

public class MyModel {
  public static void main(String[] args) throws Exception {
    run();
  }

  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    return model;
  }
}
```

For optics_agent, prefer `main()` to save `args[0]` if provided:

```java
public static void main(String[] args) throws Exception {
  Model model = run();
  if (args.length > 0) model.save(args[0]);
  System.out.println("MY_MODEL_OK");
}
```

## Compile And Run

Manual commands:

```text
comsol compile model.java
comsol batch -inputfile model.class
```

Current optics_agent runner compiles Java sources before `comsol batch` and normalizes COMSOL output MPH files. For runner details, use `optics-comsol-batch`.

## Batch-Safe Restrictions

Inside `run()`:

- Do not call `System.getenv(...)`.
- Do not call `System.getProperty(...)`.
- Do not use direct Java file IO (`File`, `FileWriter`, `PrintWriter`, etc.).
- Avoid inner classes and anonymous classes.
- Keep helper methods `static` and simple.
- Return the `Model`.

In `main()`:

- `model.save(args[0])` is acceptable for output MPH.
- `System.out.println(...)` markers are acceptable and useful.
- Avoid private local paths.

## Recommended Output Pattern

```java
public static Model run() throws Exception {
  Model model = ModelUtil.create("Model");
  // build geometry, mesh, study, solver, result
  return model;
}

public static void main(String[] args) throws Exception {
  Model model = run();
  if (args.length > 0) model.save(args[0]);
  System.out.println("CASE_OK key=value");
}
```

## Notes And Common Errors

- Java compile success is not enough. The runner still needs an MPH output and/or stdout markers.
- If the model was exported from GUI before solving, it may not contain `model.sol("sol1").runAll();`.
- COMSOL Desktop class-file execution and `comsol batch` are different environments; avoid Desktop-only assumptions.
