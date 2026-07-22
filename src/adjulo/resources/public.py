"""Ressource : endpoints publics (aucune clé API requise, hors quota)."""

from __future__ import annotations

from . import _Resource


class Public(_Resource):
    """Données publiques : tableau de bord, contrats récents, annonces, version."""

    def dashboard(self):
        """Chiffres agrégés du tableau de bord public."""
        return self._get("/v1/public/dashboard")

    def contrats_recents(self, **params):
        """Derniers contrats octroyés (vitrine publique)."""
        return self._get("/v1/public/contrats-recents", **params)

    def annonces(self):
        """Annonces produit publiques."""
        return self._get("/v1/public/annonces")

    def tendances(self):
        """Tendances sectorielles publiques."""
        return self._get("/v1/public/tendances")

    def version(self):
        """Version courante de l'API (semver + build)."""
        return self._get("/v1/public/version")

    def services_catalogue(self):
        """Catalogue des services Insights (piloté en base)."""
        return self._get("/v1/public/services-catalogue")
