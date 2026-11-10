"""Domain-Klasse Semester."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from dashboard.domain.modul import Modul


@dataclass
class Semester:
    """Zeitraum, in dem Module tatsächlich belegt wurden.

    Aggregation: Module existieren unabhängig vom Semester und werden über
    belege() lediglich zugeordnet. Sie können auch wieder entfernt werden.
    """

    bezeichnung: str
    beginn: date
    ende: date
    module: list[Modul] = field(default_factory=list)

    def belege(self, modul: Modul) -> None:
        self.module.append(modul)

    def entferne(self, modul: Modul) -> None:
        self.module.remove(modul)

    @property
    def ects(self) -> int:
        return sum(m.ects for m in self.module)

    @property
    def ist_abgeschlossen(self) -> bool:
        return all(m.ist_abgeschlossen for m in self.module)
