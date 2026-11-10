"""Tests des JSON-Repositorys."""

import tempfile
import unittest
from pathlib import Path

from dashboard.domain import Pruefungsstatus
from dashboard.repository import DatenFehler, JsonStudienRepository
from tests.hilfen import baue_student

STARTDATEN = Path(__file__).parent.parent / "daten" / "studium.json"


class JsonStudienRepositoryTest(unittest.TestCase):
    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory()
        self.pfad = Path(self.ordner.name) / "test.json"

    def tearDown(self):
        self.ordner.cleanup()

    def test_speichern_und_laden_ergibt_dieselben_werte(self):
        original = baue_student()
        repo = JsonStudienRepository(self.pfad)
        repo.speichere(original)
        geladen = repo.lade()

        sg_alt, sg_neu = original.studiengang, geladen.studiengang
        self.assertEqual(sg_neu.erreichte_ects, sg_alt.erreichte_ects)
        self.assertAlmostEqual(sg_neu.notendurchschnitt, sg_alt.notendurchschnitt)
        self.assertEqual([p.status for p in sg_neu.alle_pruefungsleistungen()],
                         [p.status for p in sg_alt.alle_pruefungsleistungen()])
        self.assertEqual(geladen.zeitziel.zieldatum, original.zeitziel.zieldatum)
        self.assertEqual(geladen.notenziel.zielnote, original.notenziel.zielnote)

    def test_umlaute_bleiben_lesbar_in_der_datei(self):
        student = baue_student()
        student.studiengang.alle_module()[0].titel = "Prüfung"
        JsonStudienRepository(self.pfad).speichere(student)
        self.assertIn("Prüfung", self.pfad.read_text(encoding="utf-8"))

    def test_fehlende_datei_meldet_datenfehler(self):
        with self.assertRaises(DatenFehler):
            JsonStudienRepository(self.pfad).lade()

    def test_kaputte_datei_meldet_datenfehler(self):
        self.pfad.write_text("{ kein json", encoding="utf-8")
        with self.assertRaises(DatenFehler):
            JsonStudienRepository(self.pfad).lade()

    def test_mitgelieferte_startdaten_entsprechen_dem_transcript(self):
        sg = JsonStudienRepository(STARTDATEN).lade().studiengang
        self.assertEqual(sg.erreichte_ects, 125)
        self.assertAlmostEqual(sg.notendurchschnitt, 2.0045, places=4)
        eingereicht = [p for p in sg.alle_pruefungsleistungen() if p.status is Pruefungsstatus.EINGEREICHT]
        self.assertEqual(len(eingereicht), 6)


if __name__ == "__main__":
    unittest.main()
