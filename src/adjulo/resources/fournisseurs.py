"""Ressource : fournisseurs (soumissionnaires / adjudicataires)."""

from __future__ import annotations

from . import _Resource


class Fournisseurs(_Resource):
    """Accès aux fournisseurs et à leurs métriques."""

    def top(self, *, tri="valeur", categorie=None, limit=20):
        """Top fournisseurs par valeur de contrats ou nombre de contrats.

        ``tri`` ∈ {valeur, nombre}."""
        return self._get("/v1/fournisseurs/top", tri=tri, categorie=categorie, limit=limit)

    def recherche(self, q, **params):
        """Recherche de fournisseurs par nom."""
        return self._get("/v1/fournisseurs/recherche", q=q, **params)

    def taux_succes(self, fournisseur_id):
        """Taux de succès réel (gagnés/soumis) et performance — plan Pro."""
        return self._get(f"/v1/fournisseurs/{fournisseur_id}/taux-succes")

    def concurrents(self, fournisseur_id):
        """Concurrents récurrents d'un fournisseur — plan Pro."""
        return self._get(f"/v1/fournisseurs/{fournisseur_id}/concurrents")

    def contrats(self, fournisseur_id, **params):
        """Contrats remportés par un fournisseur — plan Starter."""
        return self._get(f"/v1/fournisseurs/{fournisseur_id}/contrats", **params)

    def gold_profile(self, fournisseur_id):
        """Profil « gold » (identité CAE/SCIAN + catégories won/soumises)."""
        return self._get(f"/v1/fournisseurs/{fournisseur_id}/gold-profile")
