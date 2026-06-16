from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import magnus


CASE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = CASE_ROOT.parents[2]
SECRET_PATH = PROJECT_ROOT.parent / "secret.json"
BLUEPRINT_PATH = PROJECT_ROOT / "comsol" / "blueprints" / "source" / "Optics_COMSOL_Runtime_zyz.magnus.py"
BLUEPRINT_ID = "Optics_COMSOL_Runtime_zyz"
REMOTE_HOST = "zhangyuanzheng@Gustation"
REMOTE_CASE_DIR = "/data/public/zhangyuanzheng/comsol-runtime/cases/degiron_2009_fig3_v2"
CODE_ROOT = "/data/public/zhangyuanzheng/comsol-runtime"
OUTPUT_ROOT = "/data/public/zhangyuanzheng/comsol-runtime/runs"
CONTAINER_IMAGE = "docker://magnus-local/comsol-runtime:latest"
LICENSE_PATH = "/opt/comsol-license/license.dat"

ACTIVE_STATUSES = {"Preparing", "Pending", "Queued", "Running", "Paused"}
TERMINAL_STATUSES = {"Success", "Failed", "Terminated"}


@dataclass(frozen=True)
class DegironV2Case:
    name: str
    run_id: str
    java_file: str
    cpu_count: int = 8
    memory_demand: str = "32G"
    ephemeral_storage: str = "100G"
    max_wait_hours: float = 1.0

    @property
    def remote_input_file(self) -> str:
        return f"{REMOTE_CASE_DIR}/{self.java_file}"

    @property
    def output_dir(self) -> str:
        return f"{OUTPUT_ROOT}/{self.run_id}"


LADDER_SMOKE = DegironV2Case(
    "ladder_smoke",
    "degiron-2009-fig3-v2-ladder-smoke-v6",
    "Degiron2009Fig3V2ScalarPdeLadderSmoke.java",
    max_wait_hours=1.0,
)

COUPLED_SWEEP = DegironV2Case(
    "coupled_sweep",
    "degiron-2009-fig3-v2-coupled-sweep-v1",
    "Degiron2009Fig3V2ScalarPdeCoupledSweep.java",
    max_wait_hours=6.0,
)

MODE_SU8_SMOKE = DegironV2Case(
    "mode_su8_smoke",
    "degiron-2009-fig3-v2-mode-su8-smoke-v2",
    "Degiron2009Fig3V2ModeAnalysisSu8Smoke.java",
    max_wait_hours=1.0,
)


def load_secret(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig") as fh:
        data = json.load(fh)
    return data if isinstance(data, dict) else {}


def pick(data: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def configure_magnus(secret_path: Path) -> None:
    data = load_secret(secret_path)
    address = pick(data, "magnus_address-gu", "magnus_address")
    token = pick(data, "magnus_token-gu", "magnus_token")
    if not address or not token:
        raise SystemExit(f"Missing Magnus address/token in {secret_path}")
    magnus.configure(address=address, token=token)


def parse_memory_gb(value: str) -> float:
    match = re.fullmatch(r"([0-9.]+)\s*([kmgt]?b?)?", value.strip().lower())
    if not match:
        raise ValueError(f"cannot parse memory demand: {value}")
    number = float(match.group(1))
    unit = (match.group(2) or "g").rstrip("b")
    if unit in {"", "g"}:
        return number
    if unit == "m":
        return number / 1024.0
    if unit == "t":
        return number * 1024.0
    if unit == "k":
        return number / (1024.0 * 1024.0)
    raise ValueError(f"unknown memory unit: {value}")


def get_items(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict):
        items = response.get("items", [])
        return items if isinstance(items, list) else []
    if isinstance(response, list):
        return response
    return []


def status_of(job: dict[str, Any]) -> str:
    return str(job.get("status") or "")


def find_existing_job(run_id: str) -> dict[str, Any] | None:
    response = magnus.list_jobs(limit=100, search=run_id, timeout=20)
    for item in get_items(response):
        haystack = "\n".join(str(item.get(key, "")) for key in ("id", "task_name", "description", "entry_command"))
        if run_id in haystack:
            return item
    return None


def cluster_resource_snapshot() -> dict[str, Any]:
    stats = magnus.get_cluster_stats(timeout=20)
    resources = stats.get("resources", {}) if isinstance(stats, dict) else {}
    required = {"cpu_total", "cpu_free", "mem_total_mb", "mem_free_mb"}
    missing = sorted(required - set(resources))
    if missing:
        raise RuntimeError(f"cluster stats missing keys: {missing}")
    return stats


def check_resource_limit(case: DegironV2Case) -> dict[str, Any]:
    stats = cluster_resource_snapshot()
    resources = stats["resources"]
    cpu_total = int(resources["cpu_total"])
    cpu_free = int(resources["cpu_free"])
    mem_total_gb = float(resources["mem_total_mb"]) / 1024.0
    mem_free_gb = float(resources["mem_free_mb"]) / 1024.0
    cpu_used = cpu_total - cpu_free
    mem_used_gb = mem_total_gb - mem_free_gb
    planned_mem_gb = parse_memory_gb(case.memory_demand)
    cpu_after = cpu_used + case.cpu_count
    mem_after = mem_used_gb + planned_mem_gb
    return {
        "ok": cpu_after <= cpu_total * 0.5 and mem_after <= mem_total_gb * 0.5,
        "cpu_total": cpu_total,
        "cpu_free": cpu_free,
        "cpu_used": cpu_used,
        "cpu_after": cpu_after,
        "cpu_limit_half": cpu_total * 0.5,
        "mem_total_gb": round(mem_total_gb, 3),
        "mem_free_gb": round(mem_free_gb, 3),
        "mem_used_gb": round(mem_used_gb, 3),
        "mem_after_gb": round(mem_after, 3),
        "mem_limit_half_gb": round(mem_total_gb * 0.5, 3),
    }


def run(cmd: list[str], *, timeout: int = 120, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=timeout,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    return result


def stage_case_files(dry_run: bool) -> dict[str, Any]:
    files = [
        CASE_ROOT / "comsol" / "Degiron2009Fig3V2ScalarPdeLadderSmoke.java",
        CASE_ROOT / "comsol" / "Degiron2009Fig3V2ScalarPdeCoupledSweep.java",
        CASE_ROOT / "comsol" / "Degiron2009Fig3V2ModeAnalysisSu8Smoke.java",
        CASE_ROOT / "comsol" / "run_config_ladder_smoke.json",
        CASE_ROOT / "comsol" / "run_config_coupled_sweep.json",
        CASE_ROOT / "comsol" / "run_config_mode_su8_smoke.json",
        CASE_ROOT / "comsol" / "postprocess_degiron_fig3_v2.py",
    ]
    missing = [str(path) for path in files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing case files: {missing}")
    if dry_run:
        return {"dry_run": True, "remote_case_dir": REMOTE_CASE_DIR, "files": [str(p) for p in files]}
    run(["ssh", REMOTE_HOST, f"mkdir -p {REMOTE_CASE_DIR}"], timeout=60)
    for file in files:
        run(["scp", str(file), f"{REMOTE_HOST}:{REMOTE_CASE_DIR}/"], timeout=180)
    return {"dry_run": False, "remote_case_dir": REMOTE_CASE_DIR, "files": [str(p.name) for p in files]}


def save_blueprint(dry_run: bool) -> None:
    if dry_run:
        return
    code = BLUEPRINT_PATH.read_text(encoding="utf-8")
    magnus.save_blueprint(
        blueprint_id=BLUEPRINT_ID,
        title="Optics COMSOL Runtime zyz",
        description="COMSOL runtime launcher. Public blueprint, private runner and license live in server storage.",
        code=code,
    )


def blueprint_args(case: DegironV2Case) -> dict[str, Any]:
    return {
        "run_mode": "batch_java",
        "domain_preset": "optics",
        "code_root": CODE_ROOT,
        "license_mode": "server_env",
        "license_path": LICENSE_PATH,
        "input_file": case.remote_input_file,
        "case_path": REMOTE_CASE_DIR,
        "postprocess_file": f"{REMOTE_CASE_DIR}/postprocess_degiron_fig3_v2.py",
        "output_root": OUTPUT_ROOT,
        "run_id": case.run_id,
        "container_image": CONTAINER_IMAGE,
        "cpu_count": case.cpu_count,
        "memory_demand": case.memory_demand,
        "ephemeral_storage": case.ephemeral_storage,
        "priority": "B2",
        "execute_action": True,
    }


def launch_case(case: DegironV2Case) -> str:
    job_id = magnus.launch_blueprint(BLUEPRINT_ID, args=blueprint_args(case))
    if not isinstance(job_id, str):
        raise RuntimeError(f"unexpected launch_blueprint return: {job_id!r}")
    return job_id


def record(case: DegironV2Case, job_id: str, status: str, action: str, resource_check: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "case": case.name,
        "run_id": case.run_id,
        "job_id": job_id,
        "status": status,
        "dedupe_action": action,
        "input_file": case.remote_input_file,
        "output_dir": case.output_dir,
        "cpu_count": case.cpu_count,
        "memory_demand": case.memory_demand,
        "ephemeral_storage": case.ephemeral_storage,
        "gpu_type": "cpu",
        "gpu_count": 0,
        "resource_check": resource_check,
    }


def submit_or_reuse(case: DegironV2Case, *, dry_run: bool, force_rerun_failed: bool) -> dict[str, Any]:
    existing = find_existing_job(case.run_id)
    if existing:
        status = status_of(existing)
        job_id = str(existing.get("id", ""))
        if status in ACTIVE_STATUSES:
            return record(case, job_id, status, "reused_active", None)
        if status == "Success":
            return record(case, job_id, status, "reused_success", None)
        if status in {"Failed", "Terminated"} and not force_rerun_failed:
            return record(case, job_id, status, "skipped_failed", None)
    resource_check = check_resource_limit(case)
    if not resource_check["ok"]:
        return record(case, "", "Blocked", "blocked_resource", resource_check)
    if dry_run:
        return record(case, "", "DryRun", "would_submit", resource_check)
    return record(case, launch_case(case), "Submitted", "submitted", resource_check)


def safe_get_result(job_id: str) -> Any:
    try:
        return magnus.get_job_result(job_id, timeout=20)
    except Exception as exc:
        return {"result_error": repr(exc)}


def poll_interval(case: DegironV2Case, elapsed: float) -> int:
    if case.name == "ladder_smoke":
        return 60 if elapsed < 600 else 180
    return 300 if elapsed < 3600 else 900


def wait_for_case(case: DegironV2Case, rec: dict[str, Any]) -> dict[str, Any]:
    if not rec.get("job_id") or rec.get("dedupe_action") not in {"submitted", "reused_active"}:
        return rec
    started = time.time()
    while True:
        job = magnus.get_job(rec["job_id"], timeout=20)
        rec["status"] = status_of(job)
        rec["task_name"] = job.get("task_name", "")
        if rec["status"] in TERMINAL_STATUSES:
            rec["result"] = safe_get_result(rec["job_id"])
            return rec
        elapsed = time.time() - started
        if elapsed >= case.max_wait_hours * 3600:
            rec["status"] = "pending_or_timeout"
            return rec
        sleep_s = poll_interval(case, elapsed)
        print(f"[{case.name}] {rec['job_id']} status={rec['status']}; waiting {sleep_s}s")
        time.sleep(sleep_s)


def safe_remove_tree(path: Path) -> None:
    resolved = path.resolve()
    allowed = (CASE_ROOT / "magnus" / "raw_logs").resolve()
    if allowed not in resolved.parents and resolved != allowed:
        raise RuntimeError(f"refusing to delete outside raw_logs: {resolved}")
    if path.exists():
        shutil.rmtree(path)


def download_run(case: DegironV2Case, rec: dict[str, Any]) -> dict[str, Any]:
    local_dir = CASE_ROOT / "magnus" / "raw_logs" / case.run_id
    local_dir.parent.mkdir(parents=True, exist_ok=True)
    safe_remove_tree(local_dir)
    result = run(["scp", "-r", f"{REMOTE_HOST}:{case.output_dir}", str(local_dir)], timeout=600, check=False)
    rec["download"] = {
        "local_dir": str(local_dir),
        "returncode": result.returncode,
        "stderr_tail": result.stderr[-1000:],
    }
    return rec


def postprocess(local_run_dir: Path) -> dict[str, Any]:
    script = CASE_ROOT / "comsol" / "postprocess_degiron_fig3_v2.py"
    result = run(
        [sys.executable, str(script), "--run-dir", str(local_run_dir), "--output-dir", str(CASE_ROOT / "results")],
        timeout=180,
        check=False,
    )
    return {
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def write_markdown_report(records: list[dict[str, Any]], stage_info: dict[str, Any], path: Path) -> None:
    lines = [
        "# Degiron 2009 Fig. 3 V2 Magnus Submit Log",
        "",
        f"- Blueprint: `{BLUEPRINT_ID}`",
        f"- Image: `{CONTAINER_IMAGE}`",
        f"- Remote case dir: `{REMOTE_CASE_DIR}`",
        "- GPU: not used (`gpu_type=cpu`, `gpu_count=0`).",
        "- Method: `scalar_tm_hx_pde` plus isolated `wave_optics_mode_analysis_probe`; neither is full physical Fig. 3 reproduction unless validated separately.",
        "",
        "## Staging",
        "",
        "```json",
        json.dumps(stage_info, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Jobs",
        "",
        "| Case | Job ID | Status | Action | Output |",
        "|---|---|---|---|---|",
    ]
    for rec in records:
        lines.append(
            f"| `{rec['case']}` | `{rec.get('job_id','')}` | `{rec.get('status','')}` | "
            f"`{rec.get('dedupe_action','')}` | `{rec.get('output_dir','')}` |"
        )
    lines.extend(["", "## Raw Records", "", "```json", json.dumps(records, ensure_ascii=False, indent=2), "```", ""])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    (path.parent / "job_ids.md").write_text("\n".join(job_id_lines(records)), encoding="utf-8")


def job_id_lines(records: list[dict[str, Any]]) -> list[str]:
    lines = ["# Degiron 2009 Fig. 3 V2 Job IDs", ""]
    for rec in records:
        lines.append(f"- {rec['case']}: `{rec.get('job_id','')}` status=`{rec.get('status','')}` run_id=`{rec.get('run_id','')}`")
    lines.append("")
    return lines


def write_failure_record() -> None:
    path = CASE_ROOT / "magnus" / "failure_retry_record.md"
    if path.exists():
        return
    path.write_text(
        "\n".join([
            "# Degiron 2009 Fig. 3 V2 Failure And Retry Record",
            "",
            "No v2 job failure has been recorded yet.",
            "",
            "V2 starts with `scalar_tm_hx_pde` ladder smoke. This is a controlled scalar FEM approximation, not a full-vector Wave Optics reproduction.",
            "",
        ]),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage and submit Degiron 2009 Fig. 3 v2 COMSOL jobs.")
    parser.add_argument("--secret-json", type=Path, default=SECRET_PATH)
    parser.add_argument("--case", choices=("ladder", "sweep", "mode_su8", "all"), default="ladder")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--stage-only", action="store_true")
    parser.add_argument("--no-stage", action="store_true")
    parser.add_argument("--no-save-blueprint", action="store_true")
    parser.add_argument("--no-wait", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("--force-rerun-failed", action="store_true")
    return parser.parse_args()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = parse_args()
    configure_magnus(args.secret_json)
    write_failure_record()

    stage_info = {"skipped": True}
    if not args.no_stage:
        stage_info = stage_case_files(args.dry_run)
    if args.stage_only:
        write_markdown_report([], stage_info, CASE_ROOT / "magnus" / "submit_log.md")
        print(json.dumps(stage_info, ensure_ascii=False, indent=2))
        return 0

    if not args.no_save_blueprint:
        save_blueprint(args.dry_run)

    cases: list[DegironV2Case]
    if args.case == "ladder":
        cases = [LADDER_SMOKE]
    elif args.case == "sweep":
        cases = [COUPLED_SWEEP]
    elif args.case == "mode_su8":
        cases = [MODE_SU8_SMOKE]
    else:
        cases = [LADDER_SMOKE, MODE_SU8_SMOKE, COUPLED_SWEEP]

    records: list[dict[str, Any]] = []
    for case in cases:
        rec = submit_or_reuse(case, dry_run=args.dry_run, force_rerun_failed=args.force_rerun_failed)
        records.append(rec)
        write_markdown_report(records, stage_info, CASE_ROOT / "magnus" / "submit_log.md")
        if args.dry_run or args.no_wait:
            continue
        rec = wait_for_case(case, rec)
        records[-1] = rec
        if rec.get("status") == "Success" and not args.no_download:
            rec = download_run(case, rec)
            records[-1] = rec
            local = CASE_ROOT / "magnus" / "raw_logs" / case.run_id
            rec["postprocess"] = postprocess(local)
        write_markdown_report(records, stage_info, CASE_ROOT / "magnus" / "submit_log.md")
        if case.name == "ladder_smoke" and rec.get("status") != "Success" and args.case == "all":
            raise SystemExit("Ladder smoke did not reach Success; coupled sweep was not submitted.")

    print(json.dumps(records, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
