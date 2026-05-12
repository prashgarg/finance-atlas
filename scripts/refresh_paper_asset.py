from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "product_prospectus_graph/paper_v0/main.pdf"
DESTINATION = ROOT / "assets/finance-atlas-working-note.pdf"


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"Paper PDF not found: {SOURCE}")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE, DESTINATION)
    print(f"Wrote {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
