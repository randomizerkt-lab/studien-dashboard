"""Enumerationen für feste Wertebereiche.

Der Wert jedes Eintrags ist der Text, der in der Oberfläche angezeigt wird.
In der JSON-Datei wird dagegen der Name gespeichert (z. B. "EINGEREICHT").
"""

from enum import Enum


class Pruefungsstatus(Enum):
    """Bearbeitungsstand einer Prüfungsleistung."""

    OFFEN = "offen"
    EINGEREICHT = "eingereicht"
    BEWERTET = "bewertet"
    ANERKANNT = "anerkannt"  # angerechnete Leistung, z. B. aus einem früheren Studium


class Pruefungsform(Enum):
    """Art der Prüfungsleistung an der IU."""

    KLAUSUR = "Klausur"
    PORTFOLIO = "Portfolio"
    PROJEKTBERICHT = "Projektbericht"
    HAUSARBEIT = "Hausarbeit"
    SEMINARARBEIT = "Seminararbeit"
    FACHPRAESENTATION = "Fachpräsentation"
    WORKBOOK = "Workbook"
    BACHELORARBEIT = "Bachelorarbeit"
    KOLLOQUIUM = "Kolloquium"
    NICHT_ERFASST = "nicht erfasst"  # für Altdaten aus dem Transcript ohne Angabe


class Ampel(Enum):
    """Zusammenfassende Bewertung einer Zielerreichung."""

    GRUEN = "grün"
    GELB = "gelb"
    ROT = "rot"
