"""Domain-Klasse Studiengang."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from dashboard.domain.modul import Modul
from dashboard.domain.pruefungsleistung import Pruefungsleistung
from dashboard.domain.semester import Semester


@dataclass
class Studiengang:
    """Der Studiengang inklusive des individuellen Studienverlaufs.

    Komposition: Semester werden über neues_semester() vom Studiengang erzeugt.
    Alle Kennzahlen sind abgeleitete Attribute und werden bei jedem Zugriff
    aus den Prüfungsleistungen berechnet, nichts davon wird gespeichert.
    """

    bezeichnung: str
    abschluss: str
    gesamt_ects: int
    studienbeginn: date
    _semester: list[Semester] = field(default_factory=list, init=False)

    def neues_semester(self, bezeichnung: str, beginn: date, ende: date) -> Semester:
        semester = Semester(bezeichnung, beginn, ende)
        self._semester.append(semester)
        return semester

    @property
    def semester(self) -> tuple[Semester, ...]:
        return tuple(self._semester)

    def alle_module(self) -> list[Modul]:
        return [m for s in self._semester for m in s.module]

    def alle_pruefungsleistungen(self) -> list[Pruefungsleistung]:
        return [p for m in self.alle_module() for p in m.pruefungsleistungen]

    def finde_modul(self, kuerzel: str) -> Modul:
        for modul in self.alle_module():
            if modul.kuerzel == kuerzel:
                return modul
        raise KeyError(f"Kein Modul mit dem Kürzel {kuerzel} gefunden.")

    # ------------------------------------------------------------ Kennzahlen
    @property
    def erreichte_ects(self) -> int:
        return sum(p.ects_anteil for p in self.alle_pruefungsleistungen() if p.ist_abgeschlossen)

    @property
    def offene_ects(self) -> int:
        """ECTS, die bis zum Abschluss noch fehlen (eingereichte eingeschlossen)."""
        return max(self.gesamt_ects - self.erreichte_ects, 0)

    @property
    def benotete_ects(self) -> int:
        return sum(p.ects_anteil for p in self.alle_pruefungsleistungen() if p.ist_benotet)

    @property
    def notensumme(self) -> float:
        """Summe aus Note mal ECTS über alle benoteten Leistungen."""
        return sum(p.note * p.ects_anteil for p in self.alle_pruefungsleistungen() if p.ist_benotet)

    @property
    def notendurchschnitt(self) -> float | None:
        """Nach ECTS gewichteter Durchschnitt, None solange keine Note vorliegt."""
        if self.benotete_ects == 0:
            return None
        return self.notensumme / self.benotete_ects
