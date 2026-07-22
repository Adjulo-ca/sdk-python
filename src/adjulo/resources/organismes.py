"""Ressource : organismes donneurs d'ouvrage."""

from __future__ import annotations

from . import _Resource


class Organismes(_Resource):
    """Accès aux organismes publics."""

    def search(self, q, **params):
        """Recherche d'organismes par nom."""
        return self._get("/v1/organismes/search", q=q, **params)

    def search_semantique(self, q, *, limit=None):
        """Recherche sémantique d'organismes — plan Pro."""
        return self._get("/v1/organismes/search-semantique", q=q, limit=limit)

    def stats(self, organisme_id):
        """Statistiques d'un organisme (volume, secteurs, avenants) — plan Pro."""
        return self._get(f"/v1/organismes/{organisme_id}/stats")
