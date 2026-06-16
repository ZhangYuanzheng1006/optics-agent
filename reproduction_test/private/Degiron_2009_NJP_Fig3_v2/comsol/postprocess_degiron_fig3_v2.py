from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


HEADER_PREFIX = "DEGIRON_V2_CSV_HEADER,"
ROW_PREFIX = "DEGIRON_V2_CSV_ROW,"
ERROR_PREFIX = "DEGIRON_V2_ERROR,"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Postprocess Degiron 2009 Fig. 3 v2 stdout CSV rows.")
    parser.add_argument("positional", nargs="*", help="Runner compatibility: run_dir [output_mph]")
    parser.add_argument("--run-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def resolve_run_dir(args: argparse.Namespace) -> Path:
    if args.run_dir is not None:
        return args.run_dir
    if args.positional:
        return Path(args.positional[0])
    raise SystemExit("run_dir is required")


def read_stdout(run_dir: Path) -> str:
    candidates = [
        run_dir / "raw" / "stdout.txt",
        run_dir / "stdout.txt",
    ]
    for path in candidates:
        if path.exists():
            return path.read_text(encoding="utf-8", errors="replace")
    return ""


def parse_rows(text: str) -> tuple[list[str], list[dict[str, str]], list[str]]:
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    errors: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(HEADER_PREFIX):
            header = next(csv.reader([line[len(HEADER_PREFIX):]]))
        elif line.startswith(ROW_PREFIX):
            values = next(csv.reader([line[len(ROW_PREFIX):]]))
            if header and len(values) == len(header):
                rows.append(dict(zip(header, values)))
        elif line.startswith(ERROR_PREFIX):
            errors.append(line[len(ERROR_PREFIX):])
    return header or [], rows, errors


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def safe_float(row: dict[str, str], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except Exception:
        return default


def make_figure(rows: list[dict[str, str]], figure_path: Path) -> bool:
    coupled = [r for r in rows if r.get("case_name") == "coupled" and r.get("branch") in {"coupled_candidate_1", "coupled_candidate_2"}]
    if not coupled:
        return False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return False

    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    colors = {"coupled_candidate_1": "tab:red", "coupled_candidate_2": "tab:blue"}
    labels = {
        "coupled_candidate_1": "candidate 1",
        "coupled_candidate_2": "candidate 2",
    }
    for branch in ("coupled_candidate_1", "coupled_candidate_2"):
        subset = [r for r in coupled if r.get("branch") == branch]
        subset.sort(key=lambda r: safe_float(r, "t_um"))
        if not subset:
            continue
        t = [safe_float(r, "t_um") for r in subset]
        re = [safe_float(r, "re_neff") for r in subset]
        im = [safe_float(r, "im_neff") for r in subset]
        axes[0].plot(t, re, marker="o", linewidth=1.4, markersize=3, color=colors[branch], label=labels[branch])
        axes[1].plot(t, im, marker="o", linewidth=1.4, markersize=3, color=colors[branch], label=labels[branch])

    axes[0].set_xlabel("BCB thickness t (um)")
    axes[0].set_ylabel("Re(neff)")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[1].set_xlabel("BCB thickness t (um)")
    axes[1].set_ylabel("Im(neff)")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    fig.suptitle("Degiron 2009 Fig. 3 v2 scalar TM-like PDE")
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)
    return True


def main() -> int:
    args = parse_args()
    run_dir = resolve_run_dir(args)
    out_dir = args.output_dir or (run_dir / "results")
    text = read_stdout(run_dir)
    fieldnames, rows, errors = parse_rows(text)
    if not fieldnames:
        fieldnames = [
            "case_name", "t_um", "mode_index", "branch", "re_neff", "im_neff",
            "lambda_re", "lambda_im", "method", "boundary", "extraction_note",
        ]

    raw_csv = run_dir / "raw" / "neff_v2_raw_from_stdout.csv"
    write_csv(raw_csv, rows, fieldnames)

    run_id = run_dir.name
    if "coupled-sweep" in run_id:
        final_name = "coupled_neff_sweep.csv"
        figure_name = "fig3_reproduction_v2.png"
    elif "ladder-smoke" in run_id:
        final_name = "ladder_smoke_neff.csv"
        figure_name = "ladder_smoke_neff.png"
    else:
        final_name = f"{run_id}_neff.csv"
        figure_name = f"{run_id}_neff.png"

    final_csv = out_dir / final_name
    write_csv(final_csv, rows, fieldnames)
    figure_path = out_dir / figure_name
    figure_written = make_figure(rows, figure_path)

    methods = sorted({r.get("method", "") for r in rows if r.get("method")})
    cases = sorted({r.get("case_name", "") for r in rows if r.get("case_name")})
    coupled_rows = [r for r in rows if r.get("case_name") == "coupled"]
    plausible_rows = [
        r for r in rows
        if 1.45 <= safe_float(r, "re_neff") <= 1.65 and 0.0 <= safe_float(r, "im_neff") <= 5.0e-2
    ]
    if "wave_optics_mode_analysis_probe" in methods:
        physical_status = "wave_optics_mode_analysis_probe"
    elif "scalar_tm_hx_pde" in methods:
        physical_status = "scalar_tm_hx_pde_candidate"
    else:
        physical_status = "no_physical_rows"

    metrics = {
        "run_dir": str(run_dir),
        "raw_csv": str(raw_csv),
        "final_csv": str(final_csv),
        "figure": str(figure_path) if figure_written else "",
        "row_count": len(rows),
        "error_count": len(errors),
        "errors": errors[:20],
        "methods": methods,
        "cases": cases,
        "coupled_row_count": len(coupled_rows),
        "plausible_row_count": len(plausible_rows),
        "physical_reproduction_complete": False,
        "physical_status": physical_status,
    }
    metrics_path = run_dir / "results" / "metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    if out_dir != metrics_path.parent:
        (out_dir / "postprocess_summary.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
