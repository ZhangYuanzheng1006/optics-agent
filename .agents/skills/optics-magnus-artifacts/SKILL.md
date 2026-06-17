---
name: optics-magnus-artifacts
description: Author and maintain Magnus platform artifacts for optics_agent. Use when working with magnus.skill.yaml, magnus.blueprint.yaml, .magnus.py/.magnus blueprint sources, platform import/export files, naming conventions, public/private boundaries, or packaging COMSOL Magnus blueprint knowledge into reusable skills.
---

# Optics Magnus Artifacts

Use this skill for Magnus file formats and artifact hygiene. Use `optics-magnus-platform` for live jobs, logs, mounts, FileSecret transfer, and resource behavior.

## Artifact Types

Treat Magnus artifacts as public, importable wrappers around smaller source files.

```text
*.magnus.py          raw Python blueprint source for editing
*.magnus.yaml        full Magnus blueprint import/export package
*.magnus.skill.yaml  full Magnus skill import/export package
*.magnus             current project compatibility suffix for raw blueprint source
```

New editable blueprint sources live under `comsol/blueprints/source/`. The official importable COMSOL blueprint package lives under `.magnus/.blueprints/`.

## magnus.skill.yaml

A platform skill package is YAML with this shape:

```yaml
kind: magnus/skill
version: "1.0"
payload:
  id: skill-id
  title: Human Skill Title
  description: Short platform-facing description
  files:
    - path: SKILL.md
      content: |
        ---
        name: skill-id
        description: Agent-facing trigger description.
        ---

        # Skill Body
exported_at: "2026-06-14T00:00:00.000Z"
```

Rules:

- Keep `payload.id` stable and machine-friendly.
- Put every packaged file under `payload.files[]` with `path` and `content`.
- Use one `SKILL.md` for small skills; add extra `.md` files for complex workflows.
- `content: |` may contain Codex/Codex-style `SKILL.md` frontmatter.
- Keep file paths relative; do not include local absolute paths.
- Do not include tokens, SSH keys, registry passwords, license content, or private logs.

## magnus.blueprint.yaml

A platform blueprint package is YAML with this shape:

```yaml
kind: magnus/blueprint
version: "1.0"
payload:
  id: blueprint-id
  title: Human Blueprint Title
  description: |-
    Human-facing description shown on the platform.
  code: |
    from typing import Annotated, Literal

    def blueprint(...):
        submit_job(...)
exported_at: "2026-06-14T00:00:00.000Z"
```

Rules:

- Put executable blueprint code only under `payload.code`.
- Keep the blueprint as a small public interface: typed parameters, light validation, `submit_job(...)`.
- Use `typing.Annotated` metadata for UI labels, descriptions, defaults, choices, and multiline inputs.
- Keep long runner logic in repository files or mounted runtime folders, not in the blueprint.
- Escape shell arguments before interpolating them into `entry_command`.

## Public And Private Boundaries

Assume platform blueprints and platform skills are visible to administrators or collaborators.

Public-safe:

```text
parameter names, labels, descriptions
image URI names when not secret
resource requests
mount declarations
runner script paths
output path conventions
```

Keep private:

```text
license files and license text
Magnus tokens and trust tokens
registry passwords
SSH private keys
personal API keys
large private case bundles
```

Use `C:\Users\27370\Desktop\project\secret.json` for local credentials. Use mounted server storage or FileSecret for private runtime inputs.

## COMSOL Blueprint Notes

For the active COMSOL runtime:

```text
blueprint id: Optics_COMSOL_Runtime_zyz
source: comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
package: .magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
active image: docker://magnus-local/comsol-runtime:latest
runtime folder: /data/public/zhangyuanzheng/comsol-runtime
output root: /home/magnus/data/optics_agent/comsol/runs
```

Do not refresh, replace, pull, rebuild, or retag the active image unless the user explicitly asks.

Prefer persistent mounts for COMSOL code, license, cases, and large outputs:

```text
/data/public/zhangyuanzheng:/data/public/zhangyuanzheng
/home/magnus/data:/home/magnus/data
$HOME/.comsol-container-license:/opt/comsol-license
```

Forward license variables into Apptainer containers from `system_entry_command`:

```bash
export APPTAINERENV_LM_LICENSE_FILE=/opt/comsol-license/license.dat
export APPTAINERENV_COMSOL_LICENSE_FILE=/opt/comsol-license/license.dat
```

Write small structured summaries to `$MAGNUS_RESULT`. Put durable outputs under `/home/magnus/data/...`. Use `$MAGNUS_ACTION` only for simple `magnus receive ... --output ...` download actions.

## Authoring Checklist

Before saving or exporting a Magnus artifact:

- Confirm whether the file is raw source (`.magnus.py` or `.magnus`) or full package (`.magnus.yaml`, `.magnus.skill.yaml`).
- Check that public files contain no token, SSH key, registry password, or license content.
- Keep blueprint UI text understandable to the target user; use Chinese labels for this project's COMSOL UI.
- Keep platform packages copy-paste importable: valid YAML, correct `kind`, `version`, `payload`, and `exported_at`.
- Preserve existing compatibility paths unless the user asks for a migration.
