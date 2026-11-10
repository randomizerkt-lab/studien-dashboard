"""Tests der Domain-Klassen."""

import unittest
from datetime import date

from dashboard.domain import Ampel, Modul, Pruefungsform, Pruefungsleistung, Pruefungsstatus, Ziel
from tests.hilfen import baue_student


class PruefungsleistungTest(unittest.TestCase):
    def test_neue_leistung_ist_offen_und_ohne_note(self):
        p = Pruefungsleistung(Pruefungsform.KLAUSUR, 5)
        self.assertIs(p.status, Pruefungsstatus.OFFEN)
        self.assertIsNone(p.note)
        self.assertFalse(p.ist_benotet)

    def test_bewerten_setzt_note_und_status(self):
        p = Pruefungsleistung(Pruefungsform.KLAUSUR, 5)
        p.bewerten(1.7, date(2026, 1, 1))
        self.assertIs(p.status, Pruefungsstatus.BEWERTET)
        self.assertEqual(p.note, 1.7)
        self.assertTrue(p.ist_benotet)

    def test_ungueltige_note_wird_abgelehnt(self):
        p = Pruefungsleistung(Pruefungsform.KLAUSUR, 5)
        with self.assertRaises(ValueError):
            p.bewerten(1.5, date(2026, 1, 1))
        self.assertIs(p.status, Pruefungsstatus.OFFEN)

    def test_eingereichte_leistung_kann_nicht_erneut_eingereicht_werden(self):
        p = Pruefungsleistung(Pruefungsform.PORTFOLIO, 5)
        p.einreichen(date(2026, 1, 1))
        with self.assertRaises(ValueError):
            p.einreichen(date(2026, 1, 2))

    def test_note_ist_von_aussen_schreibgeschuetzt(self):
        p = Pruefungsleistung(Pruefungsform.KLAUSUR, 5)
        with self.assertRaises(AttributeError):
            p.note = 1.0

    def test_ects_anteil_muss_positiv_sein(self):
        with self.assertRaises(ValueError):
            Pruefungsleistung(Pruefungsform.KLAUSUR, 0)


class ModulTest(unittest.TestCase):
    def test_ects_und_note_werden_aus_teilleistungen_abgeleitet(self):
        ba = Modul("BA", "Bachelorarbeit")
        ba.neue_pruefungsleistung(Pruefungsform.BACHELORARBEIT, 9).bewerten(2.0, date(2027, 3, 1))
        ba.neue_pruefungsleistung(Pruefungsform.KOLLOQUIUM, 1).bewerten(1.0, date(2027, 3, 15))
        self.assertEqual(ba.ects, 10)
        self.assertAlmostEqual(ba.note, 1.9)  # (9 * 2,0 + 1 * 1,0) / 10
        self.assertTrue(ba.ist_abgeschlossen)

    def test_pruefungsleistungen_sind_von_aussen_nicht_erweiterbar(self):
        modul = Modul("M", "Modul")
        modul.neue_pruefungsleistung(Pruefungsform.KLAUSUR, 5)
        with self.assertRaises(AttributeError):
            modul.pruefungsleistungen.append(Pruefungsleistung(Pruefungsform.KLAUSUR, 5))


class StudiengangTest(unittest.TestCase):
    def setUp(self):
        self.sg = baue_student().studiengang

    def test_erreichte_und_offene_ects(self):
        self.assertEqual(self.sg.erreichte_ects, 15)
        self.assertEqual(self.sg.offene_ects, 165)

    def test_schnitt_ignoriert_unbenotete_leistungen(self):
        self.assertEqual(self.sg.benotete_ects, 10)
        self.assertAlmostEqual(self.sg.notendurchschnitt, 1.5)


class ZielTest(unittest.TestCase):
    def setUp(self):
        self.student = baue_student()

    def test_ziel_ist_abstrakt(self):
        with self.assertRaises(TypeError):
            Ziel("Ziel", self.student.studiengang)

    def test_zeitziel_prognose(self):
        # 15 ECTS in 200 Tagen, für 165 offene ECTS werden 2200 Tage benötigt
        stichtag = date(2026, 4, 19)
        prognose = self.student.zeitziel.prognostiziertes_abschlussdatum(stichtag)
        self.assertEqual((prognose - stichtag).days, 2200)
        self.assertIs(self.student.zeitziel.bewerte_zielerreichung(stichtag), Ampel.ROT)

    def test_notenziel_benoetigter_schnitt_und_ampel(self):
        # (2,0 * 175 - 15) / 165 = 2,03 > Ziel 2,0, also Puffer vorhanden
        notenziel = self.student.notenziel
        self.assertAlmostEqual(notenziel.benoetigter_schnitt, 335 / 165)
        self.assertIs(notenziel.bewerte_zielerreichung(date(2026, 4, 19)), Ampel.GRUEN)


if __name__ == "__main__":
    unittest.main()
