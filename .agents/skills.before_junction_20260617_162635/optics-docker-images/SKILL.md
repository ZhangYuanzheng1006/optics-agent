---
name: optics-docker-images
description: Container image management for the optics_agent project. Use when the user mentions Docker, COMSOL runtime images, ACR, git.pku.edu.cn registry, docker save/load, image handoff to Magnus admins, or the active magnus-local/comsol-runtime image.
---

# Optics Docker Images

## Current COMSOL Image

- Active Magnus image: `docker://magnus-local/comsol-runtime:latest`.
- Reported size: about `1.38G`.
- Origin: administrator-imported local Magnus image, built/installed differently from the original local archive plan.
- Do not refresh, pull, overwrite, retag, rebuild, or replace this image unless the administrator explicitly asks.

Validated active-image jobs:

```text
de368ea77db7da7f  comsol-smoke-minimal                 Success
deb10848cb99128a  comsol-universal-licensemount-solve  Success
3681f26d40ccbf7b  comsol-Lmembrane-eigenmodes          Success
```

## Original COMSOL Archive

This remains for provenance/fallback only:

```text
/data/public/zhangyuanzheng/comsol-runtime-6.3-zyz-v1.docker.tar
sha256: 33c8dfb5df07722143d043e653e72299f3ac0d9b9145ac9736818f16e1ea55a4
size: 11451059712 bytes
```

Do not ask an admin to `docker load` this over the active image unless the user/admin explicitly requests replacement.

## Staging Files

```text
/data/public/zhangyuanzheng/
  README.md
  comsol-runtime-6.3-zyz-v1.docker.tar
  comsol/manifests/comsol-runtime-image-manifest.json
  Optics_COMSOL_Runtime_zyz.magnus
  comsol_blueprint_runtime_plan.md
  comsol/runtime/
```

Local copies:

```text
comsol/docs/admin/COMSOL_ADMIN_README.md
comsol/manifests/comsol-runtime-image-manifest.json
comsol/runtime/
comsol/blueprints/source/Optics_COMSOL_Runtime_zyz.magnus.py
.magnus/.blueprints/Optics_COMSOL_Runtime_zyz.magnus.blueprint.yaml
```

## Legacy Registries

- ACR staging image used during development:
  `crpi-32rssczyu25r10yu.cn-beijing.personal.cr.aliyuncs.com/zyz25/comsol-runtime:6.3-zyz-v1`.
- PKU target was blocked by `413 Request Entity Too Large`:
  `git.pku.edu.cn/rise-agi/comsol-runtime:6.3-zyz-v1`.
- Gustation cannot pull Aliyun ACR directly; the active solution is the administrator-imported `magnus-local` image.

## Safety Rules

- Use `docker image inspect` and `docker run` locally for read/test operations.
- Avoid `docker pull`, `docker push`, `docker tag`, `docker load`, `docker save`, or rebuild steps for the active Magnus image unless requested.
- Never bake COMSOL license files into an image.
- Keep license path external:
  `/data/public/zhangyuanzheng/comsol-runtime/secrets/comsol/license.dat`.
