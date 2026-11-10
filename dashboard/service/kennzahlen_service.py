"""Service-Klasse für Kennzahlen, die mehrere Domain-Objekte betreffen."""

from __future__ import annotations

from dashboard.domain import Pruefungsstatus, Studiengang


class KennzahlenService:
    """Berechnet Auswertungen über alle Prüfungsleistungen eines Studiengangs.

    Einfache Berechnungen, die eindeutig zu einem Objekt gehören (z. B. der
    Notendurchschnitt), bleiben in den Domain-Klassen. Hier liegen nur
    Auswertungen, die speziell für das Dashboard gebraucht werden.
    """

    def zaehle_status(self, sg: Studiengang) -> dict[Pruefungsstatus, int]:
        """Anzahl der Prüfungsleistungen je Bearbeitungsstand."""
        anzahl = {status: 0 for status in Pruefungsstatus}
        for leistung in sg.alle_pruefungsleistungen():
            anzahl[leistung.status] += 1
        return anzahl

    def eingereichte_ects(self, sg: Studiengang) -> int:
        """ECTS, die abgegeben sind, aber noch auf die Bewertung warten."""
        return sum(p.ects_anteil for p in sg.alle_pruefungsleistungen()
                   if p.status is Pruefungsstatus.EINGEREICHT)

    def naechste_offene_leistung(self, sg: Studiengang) -> str | None:
        """Die erste noch offene Prüfungsleistung in der Reihenfolge der Semester."""
        for modul in sg.alle_module():
            for leistung in modul.pruefungsleistungen:
                if leistung.status is Pruefungsstatus.OFFEN:
                    return f"{modul.titel} ({leistung.pruefungsform.value})"
        return None
