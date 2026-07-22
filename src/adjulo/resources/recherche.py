"""Ressource : recherches sémantiques transverses (embeddings e5) — plan Pro.

Regroupe les endpoints ``*/search-semantique`` qui ne portent pas sur les
appels d'offres (déjà couverts par ``client.appels_offres.search_semantique``)
ni les organismes (``client.organismes.search_semantique``)."""

from __future__ import annotations

from . import _Resource


class Recherche(_Resource):
    """Recherches sémantiques sur contrats, référentiels UNSPSC et SCIAN."""

    def contrats(self, q, *, limit=None):
        """Recherche sémantique de contrats."""
        return self._get("/v1/contrats/search-semantique", q=q, limit=limit)

    def unspsc(self, q, *, limit=None):
        """Recherche sémantique dans le référentiel UNSPSC."""
        return self._get("/v1/unspsc/search-semantique", q=q, limit=limit)

    def scian(self, q, *, limit=None):
        """Recherche sémantique dans le référentiel SCIAN."""
        return self._get("/v1/scian/search-semantique", q=q, limit=limit)
