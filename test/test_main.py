# test/run_all.py
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_script(script_path: Path) -> None:
    script_path = script_path.resolve()
    if not script_path.exists():
        raise SystemExit(f"Missing file: {script_path}")

    # run from the script's directory so relative paths inside the script work
    cwd = script_path.parent

    print(f"\n=== Running: {script_path.name} (cwd={cwd}) ===")
    p = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )

    if p.stdout:
        print(p.stdout)
    if p.returncode != 0:
        if p.stderr:
            print(p.stderr)
        raise SystemExit(f"FAILED: {script_path.name} (exit code {p.returncode})")
    if p.stderr:
        print(p.stderr)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    scripts = [
        project_root / "src" / "run_varying_EV.py",
        project_root / "src" / "run_varying_q.py",
        project_root / "tools" / "plot_varyingEV.py",
        project_root / "tools" / "plot_varyingQueue.py",
    ]

    for s in scripts:
        run_script(s)

    print("\nALL SCRIPTS RAN SUCCESSFULLY.")


if __name__ == "__main__":
    main()
