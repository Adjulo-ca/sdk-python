"""Ressource : appels d'offres (SEAO + CanadaBuys)."""

from __future__ import annotations

from itertools import count

from . import _Resource


class AppelsOffres(_Resource):
    """Accès aux appels d'offres."""

    def list(
        self,
        *,
        page=1,
        per_page=50,
        statut=None,
        categorie=None,
        source=None,
        procurement_method=None,
        disposition=None,
        date_min=None,
        date_max=None,
        q=None,
    ):
        """Liste paginée d'appels d'offres.

        ``procurement_method`` ∈ {open, selective, limited, direct}.
        ``source`` ∈ {seao, canadabuys}. ``q`` = recherche plein texte (≥ 2 car.).
        """
        return self._get(
            "/v1/appels-offres",
            page=page,
            per_page=per_page,
            statut=statut,
            categorie=categorie,
            source=source,
            procurement_method=procurement_method,
            disposition=disposition,
            date_min=date_min,
            date_max=date_max,
            q=q,
        )

    def iter_all(self, *, per_page=50, max_pages=None, **filters):
        """Itère sur tous les appels d'offres en enchaînant les pages.

        Génère chaque appel d'offres (dict) un par un. ``max_pages`` borne le
        nombre de pages parcourues (défaut : aucune limite — s'arrête quand une
        page revient vide)."""
        for page in count(1):
            if max_pages is not None and page > max_pages:
                return
            data = self.list(page=page, per_page=per_page, **filters)
            items = _extract_items(data)
            if not items:
                return
            yield from items
            if len(items) < per_page:
                return

    def get(self, ao_id):
        """Détail d'un appel d'offres par identifiant."""
        return self._get(f"/v1/appels-offres/{ao_id}")

    def categories(self):
        """Liste des catégories disponibles."""
        return self._get("/v1/appels-offres/categories")

    def search(self, q, **params):
        """Recherche plein texte (MeiliSearch)."""
        return self._get("/v1/appels-offres/search", q=q, **params)

    def search_semantique(self, q, *, limit=None):
        """Recherche sémantique (embeddings e5)."""
        return self._get("/v1/appels-offres/search-semantique", q=q, limit=limit)

    def soumissionnaires(self, ao_id):
        """Soumissionnaires d'un AO — perdants inclus (SEAO uniquement)."""
        return self._get(f"/v1/appels-offres/{ao_id}/soumissionnaires")

    def contexte(self, ao_id):
        """Contexte terrain d'un AO (organisme × secteur) — plan Entreprise."""
        return self._get(f"/v1/appels-offres/{ao_id}/contexte")


def _extract_items(data):
    """Extrait la liste d'éléments d'une réponse paginée, quel que soit le nom
    de la clé (``items``/``resultats``/``data``…) ou une liste nue."""
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("items", "resultats", "results", "data", "appels_offres"):
            if isinstance(data.get(key), list):
                return data[key]
    return []
