"""Gemeinsame Testdaten für alle Tests."""

from __future__ import annotations

from datetime import date

from dashboard.domain import Modul, Pruefungsform, Student, Studiengang
from dashboard.repository import StudienRepository


def baue_student() -> Student:
    """Kleiner, überschaubarer Studienverlauf mit bekannten Ergebnissen.

    180 ECTS gesamt, davon abgeschlossen: 10 ECTS mit Note 1,0 und 2,0
    sowie 5 ECTS ohne Note. Eine Leistung ist eingereicht, eine offen.
    """
    sg = Studiengang("Testinformatik", "B.Sc.", 180, date(2025, 10, 1))
    sem = sg.neues_semester("WS 2025/26", date(2025, 10, 1), date(2026, 3, 31))
    for kuerzel, note in (("M1", 1.0), ("M2", 2.0)):
        modul = Modul(kuerzel, f"Modul {kuerzel}")
        modul.neue_pruefungsleistung(Pruefungsform.KLAUSUR, 5).bewerten(note, date(2026, 1, 15))
        sem.belege(modul)
    ohne_note = Modul("M3", "Studium Generale")
    ohne_note.neue_pruefungsleistung(Pruefungsform.NICHT_ERFASST, 5).bewerten(None, date(2026, 1, 15))
    sem.belege(ohne_note)
    eingereicht = Modul("M4", "Projekt")
    eingereicht.neue_pruefungsleistung(Pruefungsform.PROJEKTBERICHT, 5).einreichen(date(2026, 2, 1))
    sem.belege(eingereicht)
    offen = Modul("M5", "Portfolio-Modul")
    offen.neue_pruefungsleistung(Pruefungsform.PORTFOLIO, 5)
    sem.belege(offen)

    student = Student("Test", "000", sg)
    student.neues_zeitziel("Abschluss", date(2028, 9, 30))
    student.neues_notenziel("Schnitt", 2.0)
    return student


class SpeicherRepository(StudienRepository):
    """Repository im Arbeitsspeicher, nur für Tests.

    Zeigt nebenbei den Nutzen der Repository-Abstraktion: Der Controller
    arbeitet damit, ohne dass eine Datei geschrieben wird.
    """

    def __init__(self, student: Student):
        self.student = student
        self.anzahl_speichervorgaenge = 0

    def lade(self) -> Student:
        return self.student

    def speichere(self, student: Student) -> None:
        self.student = student
        self.anzahl_speichervorgaenge += 1
