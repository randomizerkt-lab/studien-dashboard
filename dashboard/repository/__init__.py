"""Repository-Schicht: Laden und Speichern der Studiendaten."""

from dashboard.repository.json_studien_repository import JsonStudienRepository
from dashboard.repository.studien_repository import DatenFehler, StudienRepository

__all__ = ["StudienRepository", "JsonStudienRepository", "DatenFehler"]
