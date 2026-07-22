"""Ressource : compte client (consommation, plans)."""

from __future__ import annotations

from . import _Resource


class Compte(_Resource):
    """Informations sur le compte et sa consommation."""

    def usage(self):
        """Consommation API réelle : quota journalier + totaux du mois."""
        return self._get("/v1/usage")

    def plans(self):
        """Catalogue public des plans et de leurs quotas."""
        return self._get("/v1/plans")
