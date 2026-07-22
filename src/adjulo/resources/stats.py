"""Ressource : statistiques agrégées — plan Entreprise."""

from __future__ import annotations

from . import _Resource


class Stats(_Resource):
    """Statistiques transversales sur les marchés publics."""

    def avenants(self):
        """Statistiques sur les avenants (dépenses supplémentaires)."""
        return self._get("/v1/stats/avenants")

    def gre_a_gre(self):
        """Statistiques sur les contrats de gré à gré (attribution directe)."""
        return self._get("/v1/stats/gre-a-gre")

    def secteur_tendances(self, code):
        """Tendances temporelles d'un secteur (code UNSPSC/SCIAN)."""
        return self._get(f"/v1/stats/secteur/{code}/tendances")
