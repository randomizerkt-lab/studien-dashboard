"""Abstrakte Repository-Klasse."""

from __future__ import annotations

from abc import ABC, abstractmethod

from dashboard.domain import Student


class DatenFehler(Exception):
    """Die Datenquelle fehlt, ist beschädigt oder enthält ungültige Werte."""


class StudienRepository(ABC):
    """Legt fest, welche Methoden ein Repository anbieten muss.

    Wie und wo die Daten gespeichert werden, bleibt bewusst offen. Der
    Controller kennt nur diese Abstraktion (Dependency Inversion Principle),
    sodass sich die Speicherart austauschen lässt, ohne ihn zu verändern.
    """

    @abstractmethod
    def lade(self) -> Student:
        """Lädt den Studenten mit Studiengang, Semestern, Modulen und Zielen."""

    @abstractmethod
    def speichere(self, student: Student) -> None:
        """Speichert den vollständigen Datenbestand."""
