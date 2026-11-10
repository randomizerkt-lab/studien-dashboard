"""Domain-Klassen für die überwachten Ziele (abstrakte Oberklasse und Unterklassen)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, timedelta

from dashboard.domain.enums import Ampel
from dashboard.domain.studiengang import Studiengang

# Ab wie vielen Tagen Verzug bzw. Notenabweichung die Ampel auf Rot springt
TOLERANZ_TAGE = 30
TOLERANZ_NOTE = 0.3


class Ziel(ABC):
    """Abstrakte Oberklasse: es gibt kein Ziel ohne konkrete Ausprägung.

    Jedes Ziel kennt den Studiengang, den es beobachtet (gerichtete Assoziation),
    und muss seine Zielerreichung als Ampelwert bewerten können.
    """

    def __init__(self, bezeichnung: str, studiengang: Studiengang):
        self.bezeichnung = bezeichnung
        self.studiengang = studiengang

    @abstractmethod
    def bewerte_zielerreichung(self, stichtag: date) -> Ampel:
        """Bewertet die Zielerreichung zum angegebenen Stichtag."""


class Zeitziel(Ziel):
    """Ziel: Abschluss aller ECTS-Punkte bis zu einem Zieldatum."""

    def __init__(self, bezeichnung: str, studiengang: Studiengang, zieldatum: date):
        super().__init__(bezeichnung, studiengang)
        self.zieldatum = zieldatum

    def prognostiziertes_abschlussdatum(self, stichtag: date) -> date | None:
        """Hochrechnung aus dem bisherigen Tempo (ECTS pro Tag seit Studienbeginn).

        Gibt None zurück, wenn noch keine Leistung abgeschlossen ist und daher
        kein Tempo berechnet werden kann.
        """
        sg = self.studiengang
        if sg.offene_ects == 0:
            return stichtag
        vergangene_tage = (stichtag - sg.studienbeginn).days
        if vergangene_tage <= 0 or sg.erreichte_ects == 0:
            return None
        ects_pro_tag = sg.erreichte_ects / vergangene_tage
        return stichtag + timedelta(days=round(sg.offene_ects / ects_pro_tag))

    def bewerte_zielerreichung(self, stichtag: date) -> Ampel:
        prognose = self.prognostiziertes_abschlussdatum(stichtag)
        if prognose is None:
            return Ampel.ROT
        verzug = (prognose - self.zieldatum).days
        if verzug <= 0:
            return Ampel.GRUEN
        return Ampel.GELB if verzug <= TOLERANZ_TAGE else Ampel.ROT


class Notenziel(Ziel):
    """Ziel: Gesamtnotendurchschnitt höchstens zielnote."""

    def __init__(self, bezeichnung: str, studiengang: Studiengang, zielnote: float):
        super().__init__(bezeichnung, studiengang)
        self.zielnote = zielnote

    @property
    def benoetigter_schnitt(self) -> float | None:
        """Durchschnitt, der in allen offenen ECTS mindestens erreicht werden muss.

        Vereinfachung: alle noch offenen Leistungen werden als benotet angenommen.
        Gibt None zurück, wenn keine ECTS mehr offen sind.
        """
        sg = self.studiengang
        if sg.offene_ects == 0:
            return None
        gesamt_benotet = sg.benotete_ects + sg.offene_ects
        return (self.zielnote * gesamt_benotet - sg.notensumme) / sg.offene_ects

    def bewerte_zielerreichung(self, stichtag: date) -> Ampel:
        benoetigt = self.benoetigter_schnitt
        if benoetigt is None:  # Studium abgeschlossen: nur noch der Endschnitt zählt
            schnitt = self.studiengang.notendurchschnitt
            return Ampel.GRUEN if schnitt is not None and schnitt <= self.zielnote else Ampel.ROT
        if benoetigt >= self.zielnote:  # Puffer: offene Module dürfen schlechter ausfallen
            return Ampel.GRUEN
        return Ampel.GELB if benoetigt >= self.zielnote - TOLERANZ_NOTE else Ampel.ROT
