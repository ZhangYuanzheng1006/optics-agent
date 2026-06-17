# Model Core

This file solves: create/load a COMSOL model, manage parameters and model containers, and keep Java model files compatible with optics_agent batch execution.

## Common API Pattern

```java
import com.comsol.model.*;
import com.comsol.model.util.*;

Model model = ModelUtil.create("Model");
model.modelNode().create("comp1");
model.param().set("lambda0", "1.55[um]");
model.param().set("k0", "2*pi/lambda0");
```

## `ModelUtil`

| Method | Use |
|---|---|
| `ModelUtil.create(tag)` | Create a model and return `Model`. Replaces an existing model with the same tag. |
| `ModelUtil.load(tag, filename)` | Load an MPH file. Avoid private paths in reusable templates. |
| `ModelUtil.model(tag)` | Get an existing model by tag. |
| `ModelUtil.remove(tag)`, `clear()`, `tags()` | Manage loaded model objects. |
| `ModelUtil.initStandalone(false)` | Standalone Java setup without GUI widgets. Usually not needed in `comsol batch` model files. |
| `ModelUtil.connect(host, port)`, `disconnect()` | Client/server mode. Not the default for Magnus batch jobs. |
| `ModelUtil.showProgress(...)` | GUI/file/stdout progress. Avoid file paths in sandboxed batch Java unless validated. |

## Parameters

| Call | Meaning |
|---|---|
| `model.param().set(name, expr)` | Define a global parameter expression. |
| `model.param().set(name, expr, descr)` | Define with description. |
| `model.param().get(name)` | Return expression string. |
| `model.param().varnames()` | List parameter names. |
| `model.param().remove(name)` | Remove parameter. |

Use COMSOL expressions with units as strings: `"36[nm]"`, `"1.55[um]"`, `"2*pi/lambda0"`.

## Model Containers

- The COMSOL 4.3 manual uses `model.modelNode().create("comp1")` as the model-node container.
- COMSOL 6.x GUI-exported Java may use `model.component().create("comp1", true)` and `model.component("comp1").geom(...)`.
- Preserve whichever style the target file already uses. Do not mechanically translate component-scoped GUI exports into global calls unless tested.

## Batch-Safe Shape

```java
public class MyModel {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
    System.out.println("MY_MODEL_OK");
  }
}
```

## Notes And Common Errors

- A Java file can compile but fail to produce an MPH if it only has `main()` and does not expose a COMSOL-compatible model path for the runner.
- Saving an MPH as Java only records sequences that were explicitly run. Add solver `runAll()` yourself when needed.
- Do not read environment variables, system properties, or local files inside `run()` in Magnus batch Java unless that exact pattern has been validated.
