"""Controller zwischen Oberfläche, Fachlogik und Speicherung."""

from __future__ import annotations

from datetime import date

from dashboard.domain import Pruefungsform, Pruefungsstatus, Student
from dashboard.dto import DashboardDatenDTO
from dashboard.repository import StudienRepository
from dashboard.service import KennzahlenService


class DashboardController:
    """Koordiniert den Ablauf der Anwendung.

    Der Controller kennt nur die abstrakte Klasse StudienRepository, nicht die
    konkrete JSON-Umsetzung. Welche Speicherart verwendet wird, entscheidet
    allein die DashboardApp beim Start.
    """

    def __init__(self, repository: StudienRepository, service: KennzahlenService):
        self._repository = repository
        self._service = service
        self._student: Student = repository.lade()

    # ------------------------------------------------------------ Anzeige
    def lade_dashboard_daten(self, stichtag: date) -> DashboardDatenDTO:
        """Berechnet alle Werte für die Anzeige zum angegebenen Stichtag."""
        sg = self._student.studiengang
        zeitziel = self._student.zeitziel
        notenziel = self._student.notenziel
        return DashboardDatenDTO(
            studiengang=f"{sg.bezeichnung} ({sg.abschluss})",
            studienbeginn=sg.studienbeginn,
            stichtag=stichtag,
            zieldatum=zeitziel.zieldatum if zeitziel else None,
            tage_bis_zieldatum=(zeitziel.zieldatum - stichtag).days if zeitziel else None,
            erreichte_ects=sg.erreichte_ects,
            eingereichte_ects=self._service.eingereichte_ects(sg),
            gesamt_ects=sg.gesamt_ects,
            prognose=zeitziel.prognostiziertes_abschlussdatum(stichtag) if zeitziel else None,
            ampel_zeitziel=zeitziel.bewerte_zielerreichung(stichtag) if zeitziel else None,
            zielnote=notenziel.zielnote if notenziel else None,
            notendurchschnitt=sg.notendurchschnitt,
            benoetigter_schnitt=notenziel.benoetigter_schnitt if notenziel else None,
            ampel_notenziel=notenziel.bewerte_zielerreichung(stichtag) if notenziel else None,
            status_anzahl=self._service.zaehle_status(sg),
            naechste_offene_leistung=self._service.naechste_offene_leistung(sg),
            semester=list(sg.semester),
        )

    def nicht_abgeschlossene_leistungen(self) -> list[tuple[str, str, Pruefungsform, Pruefungsstatus]]:
        """Auswahlliste für den Erfassungsdialog: (Kürzel, Titel, Form, Status)."""
        return [(m.kuerzel, m.titel, p.pruefungsform, p.status)
                for m in self._student.studiengang.alle_module()
                for p in m.pruefungsleistungen if not p.ist_abgeschlossen]

    # ------------------------------------------------------------ Änderungen
    def erfasse_einreichung(self, kuerzel: str, form: Pruefungsform, datum: date) -> None:
        leistung = self._student.studiengang.finde_modul(kuerzel).finde_pruefungsleistung(form)
        leistung.einreichen(datum)
        self._repository.speichere(self._student)

    def erfasse_bewertung(self, kuerzel: str, form: Pruefungsform, note: float | None, datum: date) -> None:
        leistung = self._student.studiengang.finde_modul(kuerzel).finde_pruefungsleistung(form)
        leistung.bewerten(note, datum)
        self._repository.speichere(self._student)
