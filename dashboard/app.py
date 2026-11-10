"""Application-Klasse: Startpunkt und Verdrahtung der Schichten (Composition Root)."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from dashboard.controller import DashboardController
from dashboard.repository import JsonStudienRepository
from dashboard.service import KennzahlenService
from dashboard.view import DashboardView


class DashboardApp:
    """Erzeugt alle Objekte und verbindet sie miteinander.

    Nur an dieser Stelle wird entschieden, welche konkreten Klassen verwendet
    werden. Soll statt der JSON-Datei z. B. eine Datenbank genutzt werden,
    muss nur hier ein anderes Repository erzeugt werden.
    """

    def __init__(self, datenpfad: Path, stichtag: date):
        self.datenpfad = datenpfad
        self.stichtag = stichtag

    def start(self) -> None:
        repository = JsonStudienRepository(self.datenpfad)
        service = KennzahlenService()
        controller = DashboardController(repository, service)
        view = DashboardView(controller, self.stichtag)

        view.zeige(controller.lade_dashboard_daten(self.stichtag))
        view.starte()
