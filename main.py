import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, PROJECT_NAME


def run_shell_check(script_relative_path: str) -> None:
    """
    Execute a project-local shell verification script and fail fast if it fails.
    """
    script_path = PROJECT_ROOT / script_relative_path
    subprocess.run([str(script_path)], check=True)


def _run_process() -> int:
    from bins.s02_processor import orchestrator

    result = orchestrator.run()
    return 0 if result is None else int(result)


def _run_analyze() -> int:
    from bins.s03_analysis import orchestrator

    result = orchestrator.run()
    return 0 if result is None else int(result)


PHASE_DISPATCH: dict[str, tuple[str, Callable[[], int]]] = {
    "process": ("Bin 02: Extraction, Cleaning, and Segmentation", _run_process),
    "analyze": ("Bin 03: Structured Export, Embeddings, and Metrics", _run_analyze),
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} - Master Orchestrator"
    )
    parser.add_argument(
        "--phase",
        type=str,
        choices=tuple(PHASE_DISPATCH.keys()),
        required=True,
        help="Specify the operational phase to execute.",
    )
    parser.add_argument(
        "--doctor",
        "--full-check",
        dest="doctor",
        action="store_true",
        help="Run the full workspace diagnostic before executing the phase.",
    )

    args = parser.parse_args()

    try:
        # Always run minimal infrastructure safety gate.
        run_shell_check("scripts/startup_check.sh")

        # Optionally run full workspace health diagnostic.
        if args.doctor:
            run_shell_check("scripts/doctor.sh")

        print(f"[*] Initializing system architecture at: {BASE_DIR}")

        phase_label, phase_runner = PHASE_DISPATCH[args.phase]
        print(f"[>] Routing to {phase_label}...")

        return phase_runner()

    except subprocess.CalledProcessError as exc:
        print(f"[FATAL] Preflight check failed with exit code {exc.returncode}.")
        return 1
    except ImportError as exc:
        print(f"[FATAL] Failed to import phase module for '{args.phase}': {exc}")
        return 1
    except AttributeError as exc:
        print(
            f"[FATAL] Phase module for '{args.phase}' is missing a required run() function: {exc}"
        )
        return 1
    except Exception as exc:
        print(f"[FATAL] Unhandled error during phase '{args.phase}': {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())