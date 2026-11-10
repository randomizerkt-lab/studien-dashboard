"""Domain-Klasse Modul."""

from __future__ import annotations

from dataclasses import dataclass, field

from dashboard.domain.enums import Pruefungsform, Pruefungsstatus
from dashboard.domain.pruefungsleistung import Pruefungsleistung


@dataclass
class Modul:
    """Ein Modul des Studiengangs mit seinen Prüfungsleistungen.

    Komposition: Prüfungsleistungen werden nur über neue_pruefungsleistung()
    vom Modul selbst erzeugt und nach außen nur lesend (als Tupel) herausgegeben.
    """

    kuerzel: str
    titel: str
    _pruefungsleistungen: list[Pruefungsleistung] = field(default_factory=list, init=False)

    def neue_pruefungsleistung(self, form: Pruefungsform, ects_anteil: int) -> Pruefungsleistung:
        leistung = Pruefungsleistung(form, ects_anteil)
        self._pruefungsleistungen.append(leistung)
        return leistung

    def finde_pruefungsleistung(self, form: Pruefungsform) -> Pruefungsleistung:
        for leistung in self._pruefungsleistungen:
            if leistung.pruefungsform is form:
                return leistung
        raise KeyError(f"{self.kuerzel} hat keine Prüfungsleistung der Form {form.value}.")

    @property
    def pruefungsleistungen(self) -> tuple[Pruefungsleistung, ...]:
        return tuple(self._pruefungsleistungen)

    @property
    def ects(self) -> int:
        """Abgeleitet: Summe der ECTS-Anteile aller Prüfungsleistungen."""
        return sum(p.ects_anteil for p in self._pruefungsleistungen)

    @property
    def ist_abgeschlossen(self) -> bool:
        return bool(self._pruefungsleistungen) and all(
            p.ist_abgeschlossen for p in self._pruefungsleistungen)

    @property
    def status(self) -> Pruefungsstatus:
        """Gesamtstatus: der am wenigsten fortgeschrittene Stand zählt."""
        stati = [p.status for p in self._pruefungsleistungen]
        for stand in (Pruefungsstatus.OFFEN, Pruefungsstatus.EINGEREICHT, Pruefungsstatus.BEWERTET):
            if stand in stati:
                return stand
        return Pruefungsstatus.ANERKANNT

    @property
    def note(self) -> float | None:
        """Nach ECTS gewichtete Modulnote, None solange keine Note vorliegt."""
        benotet = [p for p in self._pruefungsleistungen if p.ist_benotet]
        if not benotet:
            return None
        ects = sum(p.ects_anteil for p in benotet)
        return sum(p.note * p.ects_anteil for p in benotet) / ects
