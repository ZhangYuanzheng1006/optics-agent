from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CASE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = CASE_ROOT / "results"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess Degiron 2009 Fig. 3 COMSOL/Magnus output.")
    parser.add_argument("--run-dir", type=Path, help="Downloaded Magnus run directory containing results/tables/neff_sweep_raw.csv.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--label", default="Degiron 2009 Fig. 3 v1")
    return parser.parse_args()


def find_raw_csv(run_dir: Path) -> Path:
    candidates = [
        run_dir / "results" / "tables" / "neff_sweep_raw.csv",
        run_dir / "results" / "neff_sweep_raw.csv",
        run_dir / "raw" / "neff_sweep_raw.csv",
        run_dir / "raw" / "neff_sweep_raw_from_stdout.csv",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    matches = sorted(run_dir.rglob("neff_sweep_raw.csv"))
    if matches:
        return matches[0]
    parsed = parse_stdout_csv(run_dir)
    if parsed:
        return parsed
    raise FileNotFoundError(f"Cannot find neff_sweep_raw.csv under {run_dir}")


def load_metrics(run_dir: Path) -> dict:
    for candidate in [run_dir / "results" / "metrics.json", run_dir / "raw" / "metrics.json", run_dir / "manifest.json"]:
        if candidate.exists():
            try:
                data = json.loads(candidate.read_text(encoding="utf-8"))
                stdout_metrics = parse_stdout_metrics(run_dir)
                if stdout_metrics and not data.get("method"):
                    data.update(stdout_metrics)
                return data
            except Exception:
                return {}
    return parse_stdout_metrics(run_dir)


def parse_stdout_csv(run_dir: Path) -> Path | None:
    stdout_path = run_dir / "raw" / "stdout.txt"
    if not stdout_path.exists():
        return None
    header = None
    rows: list[str] = []
    for line in stdout_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("DEGIRON_CSV_HEADER,"):
            header = line.split(",", 1)[1]
        elif line.startswith("DEGIRON_CSV_ROW,"):
            rows.append(line.split(",", 1)[1])
    if not header or not rows:
        return None
    out = run_dir / "raw" / "neff_sweep_raw_from_stdout.csv"
    out.write_text(header + "\n" + "\n".join(rows) + "\n", encoding="utf-8")
    return out


def parse_stdout_metrics(run_dir: Path) -> dict:
    stdout_path = run_dir / "raw" / "stdout.txt"
    if not stdout_path.exists():
        return {}
    metrics: dict[str, object] = {}
    for line in stdout_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("DEGIRON_METRIC,"):
            continue
        parts = line.split(",", 2)
        if len(parts) != 3:
            continue
        key, value = parts[1], parts[2]
        if value.lower() == "true":
            metrics[key] = True
        elif value.lower() == "false":
            metrics[key] = False
        elif value.isdigit():
            metrics[key] = int(value)
        else:
            metrics[key] = value
    return metrics


def write_figure(df: pd.DataFrame, output: Path, label: str, method: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.3), dpi=180)
    colors = {"symmetric": "#d62728", "antisymmetric": "#1f77b4"}
    for branch, part in df.groupby("branch"):
        part = part.sort_values("t_um")
        color = colors.get(str(branch), None)
        axes[0].plot(part["t_um"], part["re_neff"], marker="o", ms=3, lw=1.5, label=str(branch), color=color)
        axes[1].plot(part["t_um"], part["im_neff"], marker="o", ms=3, lw=1.5, label=str(branch), color=color)
    axes[0].axvline(5.6, ls="--", lw=1.0, color="0.45")
    axes[1].axvline(5.6, ls="--", lw=1.0, color="0.45")
    axes[0].set_xlabel("BCB thickness t (um)")
    axes[1].set_xlabel("BCB thickness t (um)")
    axes[0].set_ylabel("Re(neff)")
    axes[1].set_ylabel("Im(neff)")
    axes[0].set_title("Real effective index")
    axes[1].set_title("Imaginary effective index")
    axes[0].grid(True, alpha=0.25)
    axes[1].grid(True, alpha=0.25)
    axes[0].legend(frameon=False)
    axes[1].legend(frameon=False)
    fig.suptitle(f"{label} ({method})", fontsize=10)
    fig.tight_layout()
    fig.savefig(output)
    plt.close(fig)


def copy_profiles(run_dir: Path, output_dir: Path) -> None:
    target = output_dir / "mode_profiles"
    target.mkdir(parents=True, exist_ok=True)
    sources = []
    sources.extend(sorted((run_dir / "results" / "figures").glob("mode_profile_*.csv")))
    sources.extend(sorted((run_dir / "raw" / "figures").glob("mode_profile_*.csv")))
    for src in sources:
        shutil.copy2(src, target / src.name)


def main() -> int:
    args = parse_args()
    if not args.run_dir:
        raise SystemExit("--run-dir is required")
    run_dir = args.run_dir.resolve()
    output_dir = args.output_dir.resolve()
    raw_csv = find_raw_csv(run_dir)
    metrics = load_metrics(run_dir)
    method = str(metrics.get("method") or metrics.get("metrics", {}).get("method") or "unknown")

    df = pd.read_csv(raw_csv)
    expected = {"t_um", "branch", "re_neff", "im_neff", "method"}
    missing = expected - set(df.columns)
    if missing:
        raise SystemExit(f"raw CSV missing columns: {sorted(missing)}")
    df = df.sort_values(["t_um", "branch", "mode_index"])

    output_dir.mkdir(parents=True, exist_ok=True)
    final_csv = output_dir / "neff_sweep.csv"
    df.to_csv(final_csv, index=False)
    write_figure(df, output_dir / "fig3_reproduction.png", args.label, method)
    copy_profiles(run_dir, output_dir)
    summary = {
        "run_dir": str(run_dir),
        "raw_csv": str(raw_csv),
        "final_csv": str(final_csv),
        "figure": str(output_dir / "fig3_reproduction.png"),
        "row_count": int(len(df)),
        "method": method,
        "physical_reproduction_complete": bool(metrics.get("physical_reproduction_complete") or metrics.get("metrics", {}).get("physical_reproduction_complete")),
        "branches": sorted(str(x) for x in df["branch"].dropna().unique()),
    }
    (output_dir / "postprocess_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
