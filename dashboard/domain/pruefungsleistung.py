"""Domain-Klasse Pruefungsleistung."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from dashboard.domain.enums import Pruefungsform, Pruefungsstatus

# An der IU vergebene Noten für bestandene Leistungen
ERLAUBTE_NOTEN = (1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0)


@dataclass
class Pruefungsleistung:
    """Eine Prüfungsleistung, die zu genau einem Modul gehört (Komposition).

    Status und Note sind als intern gekennzeichnet (Unterstrich) und nur über
    Properties lesbar. Geändert werden sie ausschließlich über die Methoden
    einreichen(), bewerten() und anerkennen(), die die fachlichen Regeln prüfen.
    """

    pruefungsform: Pruefungsform
    ects_anteil: int
    _status: Pruefungsstatus = field(default=Pruefungsstatus.OFFEN, init=False)
    _note: float | None = field(default=None, init=False)
    einreichungsdatum: date | None = field(default=None, init=False)
    bewertungsdatum: date | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.ects_anteil <= 0:
            raise ValueError("Der ECTS-Anteil muss größer als 0 sein.")

    # ------------------------------------------------------------ Properties
    @property
    def status(self) -> Pruefungsstatus:
        return self._status

    @property
    def note(self) -> float | None:
        return self._note

    @property
    def ist_abgeschlossen(self) -> bool:
        """Abgeschlossen sind bewertete und anerkannte Leistungen."""
        return self._status in (Pruefungsstatus.BEWERTET, Pruefungsstatus.ANERKANNT)

    @property
    def ist_benotet(self) -> bool:
        """Abgeleitetes Attribut: geht die Leistung in den Notenschnitt ein?"""
        return self.ist_abgeschlossen and self._note is not None

    # ------------------------------------------------------------ Methoden
    def einreichen(self, datum: date | None) -> None:
        """Markiert eine offene Prüfungsleistung als eingereicht (Datum optional)."""
        if self._status is not Pruefungsstatus.OFFEN:
            raise ValueError("Nur offene Prüfungsleistungen können eingereicht werden.")
        self._status = Pruefungsstatus.EINGEREICHT
        self.einreichungsdatum = datum

    def bewerten(self, note: float | None, datum: date) -> None:
        """Trägt das Ergebnis ein. note=None bedeutet: bestanden ohne Note."""
        if self._status is Pruefungsstatus.ANERKANNT:
            raise ValueError("Anerkannte Leistungen können nicht neu bewertet werden.")
        self._pruefe_note(note)
        self._note = note
        self._status = Pruefungsstatus.BEWERTET
        self.bewertungsdatum = datum

    def anerkennen(self, note: float | None, datum: date) -> None:
        """Erfasst eine angerechnete Leistung (z. B. aus einem früheren Studium)."""
        self._pruefe_note(note)
        self._note = note
        self._status = Pruefungsstatus.ANERKANNT
        self.bewertungsdatum = datum

    @staticmethod
    def _pruefe_note(note: float | None) -> None:
        if note is not None and note not in ERLAUBTE_NOTEN:
            raise ValueError(f"Ungültige Note: {note}. Erlaubt sind {ERLAUBTE_NOTEN}.")
