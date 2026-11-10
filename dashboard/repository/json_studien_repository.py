"""Konkretes Repository, das die Daten in einer JSON-Datei ablegt."""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

from dashboard.domain import (
    Modul, Notenziel, Pruefungsform, Pruefungsleistung, Pruefungsstatus, Student, Studiengang,
    Zeitziel,
)
from dashboard.repository.studien_repository import DatenFehler, StudienRepository


def _datum(text: str | None) -> date | None:
    """JSON kennt keinen Datumstyp: Datumswerte stehen als Text im ISO-Format."""
    return date.fromisoformat(text) if text else None


def _text(datum: date | None) -> str | None:
    return datum.isoformat() if datum else None


class JsonStudienRepository(StudienRepository):
    """Speichert den gesamten Datenbestand eines Studenten in einer JSON-Datei."""

    def __init__(self, dateipfad: str | Path):
        self.dateipfad = Path(dateipfad)

    # ------------------------------------------------------------ Laden
    def lade(self) -> Student:
        if not self.dateipfad.exists():
            raise DatenFehler(f"Datendatei nicht gefunden: {self.dateipfad}")
        try:
            with self.dateipfad.open("r", encoding="utf-8") as datei:
                daten = json.load(datei)
            return self._aus_dict(daten)
        except json.JSONDecodeError as fehler:
            raise DatenFehler(f"Datendatei ist kein gültiges JSON: {fehler}") from fehler
        except (KeyError, ValueError, TypeError) as fehler:
            raise DatenFehler(f"Ungültiger Eintrag in der Datendatei: {fehler}") from fehler

    def _aus_dict(self, daten: dict) -> Student:
        sg_daten = daten["studiengang"]
        studiengang = Studiengang(
            bezeichnung=sg_daten["bezeichnung"],
            abschluss=sg_daten["abschluss"],
            gesamt_ects=sg_daten["gesamt_ects"],
            studienbeginn=_datum(sg_daten["studienbeginn"]),
        )
        for sem_daten in daten["semester"]:
            semester = studiengang.neues_semester(
                sem_daten["bezeichnung"], _datum(sem_daten["beginn"]), _datum(sem_daten["ende"]))
            for modul_daten in sem_daten["module"]:
                semester.belege(self._modul_aus_dict(modul_daten))

        student = Student(daten["student"]["name"], daten["student"]["matrikelnummer"], studiengang)
        for ziel in daten["ziele"]:
            if ziel["typ"] == "Zeitziel":
                student.neues_zeitziel(ziel["bezeichnung"], _datum(ziel["zieldatum"]))
            elif ziel["typ"] == "Notenziel":
                student.neues_notenziel(ziel["bezeichnung"], ziel["zielnote"])
            else:
                raise ValueError(f"Unbekannter Zieltyp: {ziel['typ']}")
        return student

    @staticmethod
    def _modul_aus_dict(modul_daten: dict) -> Modul:
        modul = Modul(modul_daten["kuerzel"], modul_daten["titel"])
        for pl in modul_daten["pruefungsleistungen"]:
            leistung = modul.neue_pruefungsleistung(Pruefungsform[pl["pruefungsform"]], pl["ects_anteil"])
            # Der Zustand wird über die fachlichen Methoden wiederhergestellt,
            # damit auch geladene Daten deren Prüfungen durchlaufen.
            status = Pruefungsstatus[pl["status"]]
            if status is Pruefungsstatus.EINGEREICHT or pl.get("einreichungsdatum"):
                leistung.einreichen(_datum(pl.get("einreichungsdatum")))
            if status is Pruefungsstatus.BEWERTET:
                leistung.bewerten(pl["note"], _datum(pl["bewertungsdatum"]))
            elif status is Pruefungsstatus.ANERKANNT:
                leistung.anerkennen(pl["note"], _datum(pl["bewertungsdatum"]))
        return modul

    # ------------------------------------------------------------ Speichern
    def speichere(self, student: Student) -> None:
        daten = self._als_dict(student)
        # Erst in eine temporäre Datei schreiben und dann ersetzen: bricht das
        # Programm beim Schreiben ab, bleibt die alte Datei unbeschädigt.
        temp = self.dateipfad.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8") as datei:
            json.dump(daten, datei, ensure_ascii=False, indent=2)
        os.replace(temp, self.dateipfad)

    @staticmethod
    def _als_dict(student: Student) -> dict:
        sg = student.studiengang
        ziele = []
        for ziel in student.ziele:
            if isinstance(ziel, Zeitziel):
                ziele.append({"typ": "Zeitziel", "bezeichnung": ziel.bezeichnung,
                              "zieldatum": _text(ziel.zieldatum)})
            elif isinstance(ziel, Notenziel):
                ziele.append({"typ": "Notenziel", "bezeichnung": ziel.bezeichnung,
                              "zielnote": ziel.zielnote})
        return {
            "student": {"name": student.name, "matrikelnummer": student.matrikelnummer},
            "studiengang": {"bezeichnung": sg.bezeichnung, "abschluss": sg.abschluss,
                            "gesamt_ects": sg.gesamt_ects, "studienbeginn": _text(sg.studienbeginn)},
            "ziele": ziele,
            "semester": [
                {"bezeichnung": s.bezeichnung, "beginn": _text(s.beginn), "ende": _text(s.ende),
                 "module": [
                     {"kuerzel": m.kuerzel, "titel": m.titel,
                      "pruefungsleistungen": [JsonStudienRepository._leistung_als_dict(p)
                                              for p in m.pruefungsleistungen]}
                     for m in s.module]}
                for s in sg.semester
            ],
        }

    @staticmethod
    def _leistung_als_dict(p: Pruefungsleistung) -> dict:
        return {
            "pruefungsform": p.pruefungsform.name,  # Enum als Name speichern
            "ects_anteil": p.ects_anteil,
            "status": p.status.name,
            "note": p.note,
            "einreichungsdatum": _text(p.einreichungsdatum),
            "bewertungsdatum": _text(p.bewertungsdatum),
        }
