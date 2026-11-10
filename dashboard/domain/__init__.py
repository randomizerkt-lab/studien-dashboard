"""Domain-Schicht: fachliche Klassen des Studien-Dashboards.

Die Klassen enthalten Daten und einfache fachliche Logik, aber keinerlei
Ein- und Ausgabe. Sie entsprechen dem Klassendiagramm aus Phase 2.
"""

from dashboard.domain.enums import Ampel, Pruefungsform, Pruefungsstatus
from dashboard.domain.modul import Modul
from dashboard.domain.pruefungsleistung import Pruefungsleistung
from dashboard.domain.semester import Semester
from dashboard.domain.student import Student
from dashboard.domain.studiengang import Studiengang
from dashboard.domain.ziele import Notenziel, Zeitziel, Ziel

__all__ = [
    "Ampel", "Pruefungsform", "Pruefungsstatus", "Modul", "Pruefungsleistung",
    "Semester", "Student", "Studiengang", "Ziel", "Zeitziel", "Notenziel",
]
