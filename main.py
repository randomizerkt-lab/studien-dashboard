"""Startet das Studien-Dashboard.

Aufruf:
    python main.py                          Dashboard mit heutigem Datum
    python main.py --stichtag 2026-11-07    Werte zu einem festen Datum anzeigen
    python main.py --daten pfad/datei.json  andere Datendatei verwenden
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from dashboard.app import DashboardApp
from dashboard.repository import DatenFehler

STANDARD_DATEN = Path(__file__).parent / "daten" / "studium.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Studien-Dashboard (Prototyp)")
    parser.add_argument("--daten", type=Path, default=STANDARD_DATEN, help="Pfad zur JSON-Datendatei")
    parser.add_argument("--stichtag", type=date.fromisoformat, default=date.today(),
                        help="Datum im Format JJJJ-MM-TT (Standard: heute)")
    argumente = parser.parse_args()

    try:
        DashboardApp(argumente.daten, argumente.stichtag).start()
    except DatenFehler as fehler:
        print(f"Fehler beim Laden der Daten: {fehler}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
