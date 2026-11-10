"""DTO mit allen Werten, die das Dashboard anzeigt."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from dashboard.domain import Ampel, Pruefungsstatus, Semester


@dataclass(frozen=True)
class DashboardDatenDTO:
    """Vorbereitete Dashboard-Daten (Data Transfer Object).

    Enthält keine Logik, sondern beschreibt explizit, welche Daten der
    Controller an die View übergibt. frozen=True verhindert, dass die View
    die Werte versehentlich verändert.
    """

    # Kopfzeile
    studiengang: str
    studienbeginn: date
    stichtag: date
    # Ziel 1: Zeit
    zieldatum: date | None
    tage_bis_zieldatum: int | None
    erreichte_ects: int
    eingereichte_ects: int
    gesamt_ects: int
    prognose: date | None
    ampel_zeitziel: Ampel | None
    # Ziel 2: Note
    zielnote: float | None
    notendurchschnitt: float | None
    benoetigter_schnitt: float | None
    ampel_notenziel: Ampel | None
    # Kennzahl: Prüfungsstatus
    status_anzahl: dict[Pruefungsstatus, int]
    naechste_offene_leistung: str | None
    # Modulliste
    semester: list[Semester]
