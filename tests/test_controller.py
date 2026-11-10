"""Tests von Controller und Service."""

import unittest
from datetime import date

from dashboard.controller import DashboardController
from dashboard.domain import Ampel, Pruefungsform, Pruefungsstatus
from dashboard.service import KennzahlenService
from tests.hilfen import SpeicherRepository, baue_student


class DashboardControllerTest(unittest.TestCase):
    def setUp(self):
        self.repo = SpeicherRepository(baue_student())
        self.controller = DashboardController(self.repo, KennzahlenService())

    def test_dto_enthaelt_berechnete_kennzahlen(self):
        daten = self.controller.lade_dashboard_daten(date(2026, 4, 19))
        self.assertEqual(daten.erreichte_ects, 15)
        self.assertEqual(daten.eingereichte_ects, 5)
        self.assertEqual(daten.status_anzahl[Pruefungsstatus.OFFEN], 1)
        self.assertEqual(daten.status_anzahl[Pruefungsstatus.EINGEREICHT], 1)
        self.assertEqual(daten.naechste_offene_leistung, "Portfolio-Modul (Portfolio)")
        self.assertIs(daten.ampel_notenziel, Ampel.GRUEN)

    def test_bewertung_wird_eingetragen_und_gespeichert(self):
        self.controller.erfasse_bewertung("M4", Pruefungsform.PROJEKTBERICHT, 1.3, date(2026, 5, 1))
        daten = self.controller.lade_dashboard_daten(date(2026, 5, 1))
        self.assertEqual(daten.erreichte_ects, 20)
        self.assertEqual(self.repo.anzahl_speichervorgaenge, 1)

    def test_einreichung_wird_eingetragen(self):
        self.controller.erfasse_einreichung("M5", Pruefungsform.PORTFOLIO, date(2026, 5, 1))
        daten = self.controller.lade_dashboard_daten(date(2026, 5, 1))
        self.assertEqual(daten.status_anzahl[Pruefungsstatus.OFFEN], 0)
        self.assertIsNone(daten.naechste_offene_leistung)

    def test_unbekanntes_modul_loest_fehler_aus(self):
        with self.assertRaises(KeyError):
            self.controller.erfasse_einreichung("XYZ", Pruefungsform.PORTFOLIO, date(2026, 5, 1))
        self.assertEqual(self.repo.anzahl_speichervorgaenge, 0)


if __name__ == "__main__":
    unittest.main()
