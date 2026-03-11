import argparse
import subprocess
import sys
from pathlib import Path
from typing import Callable

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import BASE_DIR, PROJECT_NAME


def _run_ingest() -> int:
    from bins.s01_ingest import orchestrator
    result = orchestrator.run()
    return 0 if result is None else int(result)


def _run_process() -> int:
    from bins.s02_processor import orchestrator
    result = orchestrator.run()
    return 0 if result is None else int(result)


def _run_analyze() -> int:
    from bins.s03_analysis import orchestrator
    result = orchestrator.run()
    return 0 if result is None else int(result)


PHASE_DISPATCH: dict[str, tuple[str, Callable[[], int]]] = {
    "ingest": ("Bin 01: Ingestion & Manifest Generation", _run_ingest),
    "process": ("Bin 02: Semantic MRI & Vectorization", _run_process),
    "analyze": ("Bin 03: Global Centroid & Friction Calculation", _run_analyze),
}


def main() -> int:

    # Run infrastructure verification first
    subprocess.run(["./scripts/startup_check.sh"], check=True)

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

    args = parser.parse_args()

    print(f"[*] Initializing system architecture at: {BASE_DIR}")

    phase_label, phase_runner = PHASE_DISPATCH[args.phase]
    print(f"[>] Routing to {phase_label}...")

    try:
        return phase_runner()

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