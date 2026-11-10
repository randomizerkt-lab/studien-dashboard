"""Domain-Klasse Student."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from dashboard.domain.studiengang import Studiengang
from dashboard.domain.ziele import Notenziel, Zeitziel, Ziel


@dataclass
class Student:
    """Die studierende Person mit ihrem Studiengang und ihren Zielen.

    Die Ziele gehören per Komposition zum Studenten und werden über
    neues_zeitziel() bzw. neues_notenziel() erzeugt.
    """

    name: str
    matrikelnummer: str
    studiengang: Studiengang
    _ziele: list[Ziel] = field(default_factory=list, init=False)

    def neues_zeitziel(self, bezeichnung: str, zieldatum: date) -> Zeitziel:
        ziel = Zeitziel(bezeichnung, self.studiengang, zieldatum)
        self._ziele.append(ziel)
        return ziel

    def neues_notenziel(self, bezeichnung: str, zielnote: float) -> Notenziel:
        ziel = Notenziel(bezeichnung, self.studiengang, zielnote)
        self._ziele.append(ziel)
        return ziel

    @property
    def ziele(self) -> tuple[Ziel, ...]:
        return tuple(self._ziele)

    @property
    def zeitziel(self) -> Zeitziel | None:
        return next((z for z in self._ziele if isinstance(z, Zeitziel)), None)

    @property
    def notenziel(self) -> Notenziel | None:
        return next((z for z in self._ziele if isinstance(z, Notenziel)), None)
