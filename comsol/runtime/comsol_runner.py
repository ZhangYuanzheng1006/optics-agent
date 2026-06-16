from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path


IMPORT_CHECKS = ["numpy", "scipy", "pandas", "matplotlib", "h5py", "meshio", "mph", "jpype"]


class RunnerError(RuntimeError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Private COMSOL batch runner used by the Magnus blueprint.")
    parser.add_argument("--run-mode", choices=("env_check", "batch_java", "batch_mph", "batch_mfile"), required=True)
    parser.add_argument("--domain-preset", choices=("optics", "fluid", "generic"), default="generic")
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--license-mode", choices=("personal_storage", "server_env", "file_secret", "env_check_only"), default="personal_storage")
    parser.add_argument("--license-path", type=Path, required=True)
    parser.add_argument("--license-file-secret", default="")
    parser.add_argument("--case-bundle-secret", default="")
    parser.add_argument("--case-path", type=Path, default=None)
    parser.add_argument("--input-file", type=Path, default=None)
    parser.add_argument("--postprocess-file", type=Path, default=None)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", default="")
    return parser.parse_args()


def now_id() -> str:
    return os.environ.get("MAGNUS_JOB_ID") or time.strftime("%Y%m%d-%H%M%S")


def run(
    cmd: list[str],
    *,
    stdout: Path | None = None,
    stderr: Path | None = None,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess:
    out_fh = stdout.open("w", encoding="utf-8") if stdout else subprocess.PIPE
    err_fh = stderr.open("w", encoding="utf-8") if stderr else subprocess.PIPE
    try:
        result = subprocess.run(
            cmd,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=out_fh,
            stderr=err_fh,
            env=env,
            cwd=str(cwd) if cwd else None,
            check=False,
        )
    finally:
        if stdout:
            out_fh.close()
        if stderr:
            err_fh.close()
    return result


def read_text_tail(path: Path, limit: int = 4000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    return text[-limit:]


def batch_failure_context(raw_dir: Path, limit_per_file: int = 2000) -> str:
    parts: list[str] = []
    for name in (
        "compile.stdout.txt",
        "compile.stderr.txt",
        "stdout.txt",
        "stderr.txt",
        "comsol.log",
    ):
        path = raw_dir / name
        tail = read_text_tail(path, limit=limit_per_file)
        if tail:
            parts.append(f"--- {name} tail ---\n{tail}")
    return "\n".join(parts)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def import_report() -> dict[str, bool]:
    import importlib.util

    return {name: bool(importlib.util.find_spec(name)) for name in IMPORT_CHECKS}


def java_class_name(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("public class "):
            return line.split()[2].split("{", 1)[0].strip()
        if line.startswith("class "):
            return line.split()[1].split("{", 1)[0].strip()
    return path.stem


def prepare_batch_input(args: argparse.Namespace, raw_dir: Path, env: dict[str, str]) -> tuple[Path, dict]:
    if not args.input_file:
        raise RunnerError("INPUT_MISSING", "input_file is required for batch modes")
    if not args.input_file.exists():
        raise RunnerError("INPUT_MISSING", f"input_file does not exist: {args.input_file}")

    copied_input = raw_dir / args.input_file.name
    shutil.copy2(args.input_file, copied_input)

    compile_report: dict[str, object] = {"source": str(copied_input), "compiled": False}
    if args.run_mode != "batch_java":
        return copied_input, compile_report

    compile_stdout = raw_dir / "compile.stdout.txt"
    compile_stderr = raw_dir / "compile.stderr.txt"
    compile_result = run(["comsol", "compile", str(copied_input)], stdout=compile_stdout, stderr=compile_stderr, env=env)
    compile_report.update({
        "compiled": compile_result.returncode == 0,
        "returncode": compile_result.returncode,
        "stdout": str(compile_stdout),
        "stderr": str(compile_stderr),
    })
    if compile_result.returncode != 0:
        raise RunnerError("JAVA_COMPILE_FAILED", f"comsol compile exited with {compile_result.returncode}: {read_text_tail(compile_stderr)}")

    class_file = copied_input.with_name(java_class_name(copied_input) + ".class")
    if not class_file.exists():
        candidates = sorted(copied_input.parent.glob("*.class"))
        if candidates:
            class_file = candidates[0]
    if not class_file.exists():
        raise RunnerError("JAVA_CLASS_MISSING", f"comsol compile did not create a .class file for {copied_input}")
    compile_report["class_file"] = str(class_file)
    return class_file, compile_report


def canonicalize_output_mph(raw_dir: Path, output_mph: Path) -> Path | None:
    if output_mph.exists() and output_mph.stat().st_size > 0:
        return output_mph
    candidates = [p for p in raw_dir.glob("model_output*.mph") if p.is_file() and p.stat().st_size > 0]
    candidates.extend(p for p in raw_dir.glob("*.mph") if p.is_file() and p.stat().st_size > 0 and p not in candidates)
    if not candidates:
        return None
    selected = sorted(candidates, key=lambda p: p.stat().st_size, reverse=True)[0]
    if selected != output_mph:
        shutil.copy2(selected, output_mph)
    return output_mph


def success_markers(raw_dir: Path) -> list[str]:
    paths = [
        raw_dir / "stdout.txt",
        raw_dir / "stderr.txt",
        raw_dir / "comsol.log",
        raw_dir / "compile.stdout.txt",
        raw_dir / "compile.stderr.txt",
    ]
    text = "\n".join(read_text_tail(path, limit=20000) for path in paths)
    markers = []
    for line in text.splitlines():
        stripped = line.strip()
        if "_OK" in stripped:
            markers.append(stripped)
    return markers


def load_metrics(results_dir: Path, raw_dir: Path) -> dict:
    metrics_path = results_dir / "metrics.json"
    sidecar_names = [
        "metrics.json",
        "mie_scattering_metrics.json",
        "comsol_metrics.json",
    ]
    candidates = [metrics_path]
    candidates.extend(raw_dir / name for name in sidecar_names)
    candidates.extend(Path.cwd() / name for name in sidecar_names)

    for candidate in candidates:
        if not candidate.exists():
            continue
        try:
            metrics = json.loads(candidate.read_text(encoding="utf-8"))
        except Exception:
            continue
        if candidate != metrics_path:
            write_json(metrics_path, metrics)
        return metrics
    return {}


def receive_secret(secret: str, dest: Path) -> None:
    if not shutil.which("magnus"):
        raise RunnerError("FILE_SECRET_UNSUPPORTED", "magnus CLI is required for file secret downloads")
    dest.parent.mkdir(parents=True, exist_ok=True)
    result = run(["magnus", "receive", secret, "-o", str(dest)])
    if result.returncode != 0:
        raise RunnerError("FILE_SECRET_DOWNLOAD_FAILED", f"failed to receive {secret}")


def unpack_bundle(path: Path, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    name = path.name.lower()
    if name.endswith(".zip"):
        with zipfile.ZipFile(path) as zf:
            zf.extractall(target)
    elif name.endswith((".tar", ".tar.gz", ".tgz")):
        result = run(["tar", "-xf", str(path), "-C", str(target)])
        if result.returncode != 0:
            raise RunnerError("CASE_BUNDLE_UNPACK_FAILED", f"failed to unpack {path}")
    else:
        shutil.copy2(path, target / path.name)


def setup_license(args: argparse.Namespace, run_dir: Path) -> dict[str, str]:
    env = os.environ.copy()
    if args.license_mode == "env_check_only":
        return env
    if args.license_mode == "server_env":
        if not env.get("COMSOL_LICENSE_FILE") and not env.get("LM_LICENSE_FILE"):
            raise RunnerError("LICENSE_UNAVAILABLE", "server_env requires COMSOL_LICENSE_FILE or LM_LICENSE_FILE")
        return env
    if args.license_mode == "file_secret":
        if not args.license_file_secret:
            raise RunnerError("LICENSE_UNAVAILABLE", "license_mode=file_secret requires --license-file-secret")
        private_license = run_dir / "private" / "license.dat"
        receive_secret(args.license_file_secret, private_license)
        env["COMSOL_LICENSE_FILE"] = str(private_license)
        env["LM_LICENSE_FILE"] = str(private_license)
        return env
    if not args.license_path.exists():
        raise RunnerError("LICENSE_UNAVAILABLE", f"license file not found: {args.license_path}")
    env["COMSOL_LICENSE_FILE"] = str(args.license_path)
    env["LM_LICENSE_FILE"] = str(args.license_path)
    return env


def build_manifest(args: argparse.Namespace, status: str, run_dir: Path, failure: dict | None, comsol_version: str, extra: dict | None = None) -> dict:
    raw_dir = run_dir / "raw"
    manifest = {
        "status": status,
        "backend": args.run_mode,
        "domain_preset": args.domain_preset,
        "run_id": run_dir.name,
        "run_dir": str(run_dir),
        "timestamp_unix": int(time.time()),
        "comsol": {"version": comsol_version},
        "artifacts": {
            "manifest": str(run_dir / "manifest.json"),
            "command": str(run_dir / "command.json"),
            "env_report": str(run_dir / "env_report.json"),
            "batch_log": str(raw_dir / "comsol.log"),
            "stdout": str(raw_dir / "stdout.txt"),
            "stderr": str(raw_dir / "stderr.txt"),
            "output_mph": str(raw_dir / "model_output.mph"),
            "results_dir": str(run_dir / "results"),
        },
        "failure": failure,
    }
    if extra:
        manifest.update(extra)
    return manifest


def publish_result(manifest: dict, manifest_path: Path) -> None:
    write_json(manifest_path, manifest)
    result_path = os.environ.get("MAGNUS_RESULT")
    if result_path:
        write_json(Path(result_path), manifest)


def main() -> int:
    args = parse_args()
    run_id = args.run_id or now_id()
    run_dir = args.output_root / run_id
    raw_dir = run_dir / "raw"
    results_dir = run_dir / "results"
    errors_dir = run_dir / "errors"
    for path in (raw_dir, results_dir / "tables", results_dir / "figures", errors_dir):
        path.mkdir(parents=True, exist_ok=True)

    manifest_path = run_dir / "manifest.json"
    comsol_version = ""
    try:
        if not shutil.which("comsol"):
            raise RunnerError("COMSOL_NOT_FOUND", "comsol command is not available")

        version_result = run(["comsol", "-version"])
        comsol_version = (version_result.stdout or "").splitlines()[0] if version_result.stdout else ""

        write_json(run_dir / "command.json", {
            "run_mode": args.run_mode,
            "domain_preset": args.domain_preset,
            "code_root": str(args.code_root),
            "license_mode": args.license_mode,
            "license_path": str(args.license_path),
            "case_path": str(args.case_path) if args.case_path else "",
            "input_file": str(args.input_file) if args.input_file else "",
            "postprocess_file": str(args.postprocess_file) if args.postprocess_file else "",
            "output_root": str(args.output_root),
        })

        write_json(run_dir / "env_report.json", {
            "python": sys.version.split()[0],
            "comsol": comsol_version,
            "comsol_path": shutil.which("comsol"),
            "imports": import_report(),
            "license_mode": args.license_mode,
            "license_path_exists": args.license_path.exists(),
        })

        env = setup_license(args, run_dir)
        env["OPTICS_COMSOL_RUN_DIR"] = str(run_dir)
        env["OPTICS_COMSOL_RAW_DIR"] = str(raw_dir)
        env["OPTICS_COMSOL_RESULTS_DIR"] = str(results_dir)
        env["OPTICS_COMSOL_TABLES_DIR"] = str(results_dir / "tables")
        env["OPTICS_COMSOL_FIGURES_DIR"] = str(results_dir / "figures")
        env["OPTICS_COMSOL_METRICS_FILE"] = str(results_dir / "metrics.json")

        if args.case_path:
            if not args.case_path.exists():
                raise RunnerError("INPUT_MISSING", f"case_path does not exist: {args.case_path}")
            (run_dir / "case_path.txt").write_text(str(args.case_path), encoding="utf-8")

        if args.case_bundle_secret:
            bundle_path = run_dir / "raw" / "case_bundle"
            receive_secret(args.case_bundle_secret, bundle_path)
            unpack_bundle(bundle_path, run_dir / "case_bundle")

        if args.run_mode == "env_check":
            help_result = run(["comsol", "batch", "-help"], stdout=raw_dir / "comsol_batch_help.txt", stderr=raw_dir / "comsol_batch_help.err", env=env)
            if help_result.returncode != 0:
                raise RunnerError("BATCH_HELP_FAILED", "comsol batch -help failed")
            manifest = build_manifest(args, "completed", run_dir, None, comsol_version, {
                "capability": {
                    "comsol_available": True,
                    "batch_available": True,
                    "python_imports": import_report(),
                    "license_env": bool(env.get("COMSOL_LICENSE_FILE") or env.get("LM_LICENSE_FILE")),
                }
            })
            publish_result(manifest, manifest_path)
            return 0

        batch_input, compile_report = prepare_batch_input(args, raw_dir, env)
        write_json(run_dir / "compile.json", compile_report)
        output_mph = raw_dir / "model_output.mph"
        batch_cmd = ["comsol", "batch", "-inputfile", str(batch_input), "-outputfile", str(output_mph), "-batchlog", str(raw_dir / "comsol.log")]
        batch_result = run(batch_cmd, stdout=raw_dir / "stdout.txt", stderr=raw_dir / "stderr.txt", env=env, cwd=raw_dir)
        if batch_result.returncode != 0:
            raise RunnerError("BATCH_EXIT_NONZERO", f"comsol batch exited with {batch_result.returncode}: {read_text_tail(raw_dir / 'stderr.txt') or read_text_tail(raw_dir / 'comsol.log')}")
        if not canonicalize_output_mph(raw_dir, output_mph):
            context = batch_failure_context(raw_dir)
            if context:
                raise RunnerError("OUTPUT_MPH_MISSING", f"COMSOL did not create {output_mph}\n{context}")
            raise RunnerError("OUTPUT_MPH_MISSING", f"COMSOL did not create {output_mph}")

        if args.postprocess_file:
            if not args.postprocess_file.exists():
                raise RunnerError("POSTPROCESS_FAILED", f"postprocess file not found: {args.postprocess_file}")
            pp_result = run([sys.executable, str(args.postprocess_file), str(run_dir), str(output_mph)], stdout=raw_dir / "postprocess.stdout.txt", stderr=raw_dir / "postprocess.stderr.txt", env=env)
            if pp_result.returncode != 0:
                raise RunnerError("POSTPROCESS_FAILED", f"postprocess exited with {pp_result.returncode}")

        metrics = load_metrics(results_dir, raw_dir)
        manifest = build_manifest(args, "completed", run_dir, None, comsol_version, {
            "compile": compile_report,
            "metrics": metrics,
            "success_markers": success_markers(raw_dir),
        })
        publish_result(manifest, manifest_path)
        return 0
    except RunnerError as exc:
        failure = {"code": exc.code, "message": exc.message}
    except Exception as exc:
        failure = {"code": "INTERNAL_ERROR", "message": repr(exc)}

    write_json(errors_dir / "failure.json", failure)
    manifest = build_manifest(args, "failed", run_dir, failure, comsol_version)
    publish_result(manifest, manifest_path)
    print(f"[{failure['code']}] {failure['message']}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
