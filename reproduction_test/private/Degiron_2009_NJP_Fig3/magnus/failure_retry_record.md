# Degiron 2009 Fig. 3 Failure And Retry Record

This file records the actual iteration path. It is intentionally technical because these are the details the self-iteration loop must learn from.

## Attempts

| Step | Run/job | Outcome | Diagnosis | Patch |
|---|---|---|---|---|
| 1 | `86ba0464acccc341` | Failed | runner reported `OUTPUT_MPH_MISSING`. | Added explicit model save path attempt. |
| 2 | `9dcd1c2ba84ab0a0` | Failed | same `OUTPUT_MPH_MISSING`. | Inspected runner behavior; suspected Java class needs COMSOL-compatible `run()`. |
| 3 | `156e85aaf072ea23` | Failed | COMSOL sandbox blocked `System.getenv("OPTICS_COMSOL_RUN_DIR")`. | Removed environment-variable reads from Java. |
| 4 | `32a558014ad79dc3` | Failed | job could not create `/data/public/.../runs`; permission denied. | Pre-created public run directory with write permission for Magnus job user. |
| 5 | `39a4a495753869e5` | Failed | COMSOL sandbox blocked `System.getProperty("user.dir")`. | Removed system-property reads. |
| 6 | `b31d809db736b329` | Failed | COMSOL sandbox blocked Java filesystem access to `"."`. | Removed Java file IO from `run()`; emit rows through stdout. |
| 7 | `789d92a82d93a72d` | Success but incomplete | `.mph` saved, but Java inner class `ModeRow` caused COMSOL-side error; no CSV rows. | Rewrote Java as a single public class with no inner/anonymous classes. |
| 8 | `457d6a631cc2ece0` | Success, fallback | stdout CSV and `.mph` generated; full-vector failed at physics-controlled mesh setup. | Replaced `autoMeshSize()` with explicit FreeTri mesh. |
| 9 | `48dee6cda1a4baa7` | Success, fallback | full-vector reached eigensolver, failed matrix factorization. | Added multiple eigenvalue shifts around beta/neff. |
| 10 | `228e43d047953613` | Success, fallback | all tested shifts still failed matrix factorization. | Stopped blind solver retries; recorded blocker. |
| 11 | `127fde3b1d9bcb34` | Success, fallback sweep | full `4.8-10.0 um` sweep generated as labelled `surrogate_fallback`. | Used for pipeline validation and report only, not physical reproduction. |

## Stable Lessons

- COMSOL batch Java on this Magnus runtime can compile and save `.mph`, but `run()` executes under a restricted COMSOL sandbox.
- Avoid Java-side env reads, system-property reads, direct file IO, inner classes, and anonymous classes.
- Use stdout markers and stdout CSV for case-specific data unless the runner performs postprocessing outside COMSOL's Java sandbox.
- The runner should include log tails on failure; this was added to `comsol/runtime/comsol_runner.py` and synced to `/data/public/zhangyuanzheng/comsol-runtime/comsol_runner.py`.
- Physical mode analysis needs a GUI-exported Java template or a simpler isolated-mode validation ladder before another coupled sweep.

